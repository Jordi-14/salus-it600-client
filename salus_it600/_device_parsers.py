"""Private device parser helpers for Salus iT600 gateway payloads."""

from __future__ import annotations

import json
import logging
from typing import Any

from .const import (
    BATTERY_ERROR_CODES,
    BATTERY_LEVEL_MAP,
    BATTERY_VOLTAGE_THRESHOLDS,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_COOL_IDLE,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_HEAT_IDLE,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    FAN_MODE_AUTO,
    FAN_MODE_HIGH,
    FAN_MODE_LOW,
    FAN_MODE_MEDIUM,
    FAN_MODE_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_ECO,
    PRESET_FOLLOW_SCHEDULE,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
    PRESET_TEMPORARY_HOLD,
    SUPPORT_CLOSE,
    SUPPORT_FAN_MODE,
    SUPPORT_OPEN,
    SUPPORT_PRESET_MODE,
    SUPPORT_SET_POSITION,
    SUPPORT_TARGET_TEMPERATURE,
    TEMP_CELSIUS,
    TEMPERATURE_SCALE,
    THERMOSTAT_ERROR_CODES,
    FanMode,
    HoldType,
    RunningState,
    SystemMode,
)
from .device_models import (
    BATTERY_OEM_MODELS,
    BINARY_RELAY_MODELS,
    DOOR_VOLTAGE_MODELS,
    ENERGY_METER_VOLTAGE_MODELS,
    SKIPPED_BINARY_SENSOR_MODELS,
    TRV_VOLTAGE_MODELS,
    WINDOW_VOLTAGE_MODELS,
    binary_sensor_device_class,
    is_sq610_model,
    model_identifier,
    switch_device_class,
)
from .models import (
    BinarySensorDevice,
    ClimateDevice,
    CoverDevice,
    SensorDevice,
    SwitchDevice,
)

_LOGGER = logging.getLogger("salus_it600")

DEFAULT_HOLD_TYPE = HoldType.PERMANENT_HOLD
DEFAULT_RUNNING_STATE = RunningState.IDLE
PARSING_EXCEPTIONS = (KeyError, TypeError, ValueError)
_MISSING_HOLD_TYPE_WARNED: set[str] = set()


def _numeric_value(value: Any) -> float | None:
    """Return a numeric payload value, rejecting bools and non-numeric values."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _temperature_from_x100(*values: Any) -> float | None:
    """Return the first available x100 temperature value in Celsius."""
    for value in values:
        numeric_value = _numeric_value(value)
        if numeric_value is not None:
            return numeric_value / TEMPERATURE_SCALE
    return None


def _temperature_from_x100_or_default(value: Any, default: float) -> float:
    """Return a scaled x100 temperature value, or the supplied fallback."""
    temperature = _temperature_from_x100(value)
    return temperature if temperature is not None else default


def _humidity_percent(raw_humidity: Any) -> float | None:
    """Return SQ610 humidity as a percent, accepting raw percent and x100 forms."""
    humidity = _numeric_value(raw_humidity)
    if humidity is None:
        return None

    if humidity > 100:
        humidity /= TEMPERATURE_SCALE

    if 0 <= humidity <= 100:
        return humidity

    _LOGGER.warning("Ignoring implausible SQ610 humidity value: %s", raw_humidity)
    return None


def _device_name(device_status: dict[str, Any], unique_id: str | None) -> str:
    """Return a device name from a raw Salus gateway payload."""
    default_name = unique_id or "Unknown"
    raw_name = device_status.get("sZDO", {}).get(
        "DeviceName",
        json.dumps({"deviceName": default_name}),
    )

    try:
        device_name = json.loads(raw_name)["deviceName"]
        return device_name if isinstance(device_name, str) else default_name
    except (KeyError, TypeError, ValueError):
        return default_name


def _hold_type(payload: dict[str, Any], unique_id: str) -> int:
    """Return HoldType, defaulting broken payloads to permanent hold."""
    if "HoldType" not in payload and unique_id not in _MISSING_HOLD_TYPE_WARNED:
        _LOGGER.warning(
            "Salus climate device %s is missing HoldType in the gateway payload; "
            "treating it as Permanent Hold so the device can load",
            unique_id,
        )
        _MISSING_HOLD_TYPE_WARNED.add(unique_id)

    return int(payload.get("HoldType", DEFAULT_HOLD_TYPE))


def _online(device_status: dict[str, Any]) -> bool:
    """Return whether a device is marked online in a gateway payload."""
    status = device_status.get("sZDOInfo", {}).get("OnlineStatus_i", 1)
    return bool(status == 1)


def _voltage_to_battery_pct(voltage: float, model: str | None) -> int | None:
    """Convert a voltage reading to a coarse battery percentage."""
    if model in WINDOW_VOLTAGE_MODELS:
        curve = "window"
    elif model in DOOR_VOLTAGE_MODELS:
        curve = "door"
    elif model in ENERGY_METER_VOLTAGE_MODELS:
        curve = "energy_meter"
    elif model in TRV_VOLTAGE_MODELS:
        curve = "trv"
    else:
        curve = "door"

    thresholds = BATTERY_VOLTAGE_THRESHOLDS.get(curve)
    if thresholds is None:
        return None

    for threshold_v, pct, _status in thresholds:
        if voltage >= threshold_v:
            return pct
    return 0


def _firmware_version(device_status: dict[str, Any]) -> str | None:
    """Return the common firmware version field from a gateway payload."""
    version = device_status.get("sZDO", {}).get("FirmwareVersion")
    return version if isinstance(version, str) else None


def _common_device_args(
    device_status: dict[str, Any],
    unique_id: str,
) -> dict[str, Any]:
    """Return constructor args shared by most device models."""
    model = model_identifier(device_status)
    return {
        "available": _online(device_status),
        "name": _device_name(device_status, unique_id),
        "unique_id": unique_id,
        "data": device_status["data"],
        "manufacturer": device_status.get("sBasicS", {}).get(
            "ManufactureName",
            "SALUS",
        ),
        "model": model,
        "sw_version": _firmware_version(device_status),
    }


def parse_cover_device(device_status: dict[str, Any]) -> CoverDevice | None:
    """Parse one cover (roller shutter/blind) device from gateway payload.

    Extracts position, movement state, and capability info from cover-specific
    protocol fields. Skips endpoints disabled via sButtonS.Mode.

    Protocol fields:
    - `sLevelS.CurrentLevel`: Current position (0-100), 0=closed, 100=open
    - `sLevelS.MoveToLevel_f`: Target position as hex string (first 2 chars)
    - `sButtonS.Mode`: Endpoint enabled state (0=disabled)
    """
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    if device_status.get("sButtonS", {}).get("Mode") == 0:
        return None

    current_position = device_status.get("sLevelS", {}).get("CurrentLevel")
    move_to_level = device_status.get("sLevelS", {}).get("MoveToLevel_f")
    if move_to_level is not None and len(move_to_level) >= 2:
        set_position = int(move_to_level[:2], 16)
    else:
        set_position = None

    return CoverDevice(
        **_common_device_args(device_status, unique_id),
        current_cover_position=current_position,
        is_opening=None if set_position is None else current_position < set_position,
        is_closing=None if set_position is None else current_position > set_position,
        is_closed=current_position == 0,
        supported_features=SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION,
        device_class=None,
    )


def parse_switch_device(device_status: dict[str, Any]) -> SwitchDevice | None:
    """Parse one switch (relay) device from gateway payload."""
    base_unique_id = device_status.get("data", {}).get("UniID")
    if base_unique_id is None:
        return None

    unique_id = f"{base_unique_id}_{device_status['data']['Endpoint']}"
    if device_status.get("sLevelS") is not None:
        return None

    is_on = device_status.get("sOnOffS", {}).get("OnOff")
    if is_on is None:
        return None

    model = model_identifier(device_status)
    return SwitchDevice(
        **_common_device_args(device_status, unique_id),
        is_on=is_on == 1,
        device_class=switch_device_class(model),
    )


def parse_switch_sensor_devices(device_status: dict[str, Any]) -> list[SensorDevice]:
    """Parse derived power/energy sensors from a switch payload."""
    base_unique_id = device_status.get("data", {}).get("UniID")
    endpoint = device_status.get("data", {}).get("Endpoint")
    if base_unique_id is None or endpoint is None:
        return []

    if device_status.get("sLevelS") is not None:
        return []

    unique_id = f"{base_unique_id}_{endpoint}"
    metering = device_status.get("sMeteringS")
    if not isinstance(metering, dict):
        return []

    parent = _common_device_args(device_status, unique_id)
    sensors: list[SensorDevice] = []

    power_raw = metering.get("InstantaneousDemand")
    if power_raw is not None:
        sensors.append(
            SensorDevice(
                **{
                    **parent,
                    "name": f"{parent['name']} Power",
                    "unique_id": f"{unique_id}_power",
                },
                state=power_raw,
                unit_of_measurement="W",
                device_class="power",
                parent_unique_id=unique_id,
            )
        )

    energy_raw = metering.get("CurrentSummationDelivered")
    if energy_raw is not None:
        sensors.append(
            SensorDevice(
                **{
                    **parent,
                    "name": f"{parent['name']} Energy",
                    "unique_id": f"{unique_id}_energy",
                },
                state=energy_raw / 1000,
                unit_of_measurement="kWh",
                device_class="energy",
                parent_unique_id=unique_id,
            )
        )

    return sensors


def parse_sensor_device(device_status: dict[str, Any]) -> SensorDevice | None:
    """Parse one temperature sensor device from gateway payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    temperature = device_status.get("sTempS", {}).get("MeasuredValue_x100")
    if temperature is None:
        return None

    unique_id = f"{unique_id}_temp"
    return SensorDevice(
        **_common_device_args(device_status, unique_id),
        state=temperature / TEMPERATURE_SCALE,
        unit_of_measurement=TEMP_CELSIUS,
        device_class="temperature",
    )


def parse_sensor_devices(device_status: dict[str, Any]) -> list[SensorDevice]:
    """Parse a standalone sensor payload into primary and child sensors."""
    base_unique_id = device_status.get("data", {}).get("UniID")
    if base_unique_id is None:
        return []

    model = model_identifier(device_status)
    parent_name = _device_name(device_status, base_unique_id)
    sensors: list[SensorDevice] = []

    temperature = device_status.get("sTempS", {}).get("MeasuredValue_x100")
    if temperature is not None:
        sensors.append(
            SensorDevice(
                **_common_device_args(device_status, f"{base_unique_id}_temp"),
                state=temperature / TEMPERATURE_SCALE,
                unit_of_measurement=TEMP_CELSIUS,
                device_class="temperature",
            )
        )

    humidity_raw = device_status.get("sRelativeHumidity", {}).get(
        "MeasuredValue_x100"
    )
    if humidity_raw is not None:
        sensors.append(
            SensorDevice(
                **{
                    **_common_device_args(
                        device_status, f"{base_unique_id}_humidity"
                    ),
                    "name": f"{parent_name} Humidity",
                },
                state=humidity_raw / TEMPERATURE_SCALE,
                unit_of_measurement="%",
                device_class="humidity",
                parent_unique_id=base_unique_id,
            )
        )

    voltage_raw = device_status.get("sPowerS", {}).get("BatteryVoltage_x10")
    if voltage_raw is not None:
        pct = _voltage_to_battery_pct(voltage_raw / 10, model)
        if pct is not None:
            sensors.append(
                SensorDevice(
                    **{
                        **_common_device_args(
                            device_status, f"{base_unique_id}_battery"
                        ),
                        "name": f"{parent_name} Battery",
                    },
                    state=pct,
                    unit_of_measurement="%",
                    device_class="battery",
                    parent_unique_id=base_unique_id,
                    entity_category="diagnostic",
                )
            )

    return sensors


def parse_binary_sensor_device(
    device_status: dict[str, Any],
) -> BinarySensorDevice | None:
    """Parse one binary sensor device from gateway payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    model = model_identifier(device_status)
    if model in SKIPPED_BINARY_SENSOR_MODELS:
        return None

    if model in BINARY_RELAY_MODELS:
        is_on = device_status.get("sIT600I", {}).get("RelayStatus")
    else:
        is_on = device_status.get("sIASZS", {}).get("ErrorIASZSAlarmed1")

    if is_on is None:
        return None

    return BinarySensorDevice(
        **_common_device_args(device_status, unique_id),
        is_on=is_on == 1,
        device_class=binary_sensor_device_class(model),
    )


def parse_binary_diagnostic_devices(
    device_status: dict[str, Any],
) -> list[BinarySensorDevice]:
    """Parse diagnostic child binary sensors from a binary-sensor payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return []

    model = model_identifier(device_status)
    parent_name = _device_name(device_status, unique_id)
    low_battery = device_status.get("sIASZS", {}).get("ErrorIASZSLowBattery")
    if low_battery is None:
        low_battery = device_status.get("sPowerS", {}).get("ErrorPowerSLowBattery")
    if low_battery is None and model in BINARY_RELAY_MODELS:
        low_battery = device_status.get("sIT600I", {}).get("TRVError22")

    if low_battery is None:
        return []

    return [
        BinarySensorDevice(
            **{
                **_common_device_args(device_status, f"{unique_id}_low_battery"),
                "name": f"{parent_name} Low battery",
            },
            is_on=low_battery == 1,
            device_class="battery",
            parent_unique_id=unique_id,
            entity_category="diagnostic",
        )
    ]


def _climate_common_args(
    device_status: dict[str, Any],
    unique_id: str,
) -> dict[str, Any]:
    """Return constructor args shared by climate devices."""
    return {
        **_common_device_args(device_status, unique_id),
        "temperature_unit": TEMP_CELSIUS,
        "precision": 0.1,
        "device_class": "temperature",
    }


def _parse_it600th_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    th: dict[str, Any],
) -> ClimateDevice:
    """Parse one iT600 or SQ610 thermostat from gateway payload."""
    model = model_identifier(device_status)
    s_temp = device_status.get("sTempS", {})
    current_humidity = (
        _humidity_percent(th.get("SunnySetpoint_x100"))
        if is_sq610_model(model)
        else None
    )
    current_temperature = _temperature_from_x100(
        th.get("LocalTemperature_x100"),
        s_temp.get("MeasuredValue_x100") if isinstance(s_temp, dict) else None,
    )
    hold_type = _hold_type(th, unique_id)
    running_state = th.get("RunningState", DEFAULT_RUNNING_STATE)
    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=current_humidity,
        current_temperature=current_temperature,
        target_temperature=_temperature_from_x100_or_default(
            th.get("HeatingSetpoint_x100"),
            20.0,
        ),
        max_temp=_temperature_from_x100_or_default(
            th.get("MaxHeatSetpoint_x100"), 35.0
        ),
        min_temp=_temperature_from_x100_or_default(th.get("MinHeatSetpoint_x100"), 5.0),
        hvac_mode=HVAC_MODE_OFF
        if hold_type == HoldType.STANDBY
        else HVAC_MODE_HEAT
        if hold_type == HoldType.PERMANENT_HOLD
        else HVAC_MODE_AUTO,
        hvac_action=CURRENT_HVAC_OFF
        if hold_type == HoldType.STANDBY
        else CURRENT_HVAC_IDLE
        if running_state % 2 == 0
        else CURRENT_HVAC_HEAT,
        hvac_modes=[HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO],
        preset_mode=PRESET_OFF
        if hold_type == HoldType.STANDBY
        else PRESET_PERMANENT_HOLD
        if hold_type == HoldType.PERMANENT_HOLD
        else PRESET_FOLLOW_SCHEDULE,
        preset_modes=[PRESET_FOLLOW_SCHEDULE, PRESET_PERMANENT_HOLD, PRESET_OFF],
        fan_mode=None,
        fan_modes=None,
        locked=(
            device_status["sTherUIS"].get("LockKey", 0) == 1
            if "sTherUIS" in device_status
            else None
        ),
        supported_features=SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE,
    )


def _parse_fan_coil_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    ther: dict[str, Any],
    scomm: dict[str, Any],
    sfans: dict[str, Any],
) -> ClimateDevice:
    """Parse one FC600 fan-coil thermostat from gateway payload."""
    is_heating = ther["SystemMode"] == SystemMode.HEAT
    fan_mode = sfans.get("FanMode", FanMode.AUTO)
    hold_type = _hold_type(scomm, unique_id)
    running_state = ther.get("RunningState", DEFAULT_RUNNING_STATE)

    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=None,
        current_temperature=_temperature_from_x100(ther.get("LocalTemperature_x100")),
        target_temperature=_temperature_from_x100_or_default(
            ther.get("HeatingSetpoint_x100"),
            20.0,
        )
        if is_heating
        else _temperature_from_x100_or_default(
            ther.get("CoolingSetpoint_x100"),
            20.0,
        ),
        max_temp=_temperature_from_x100_or_default(
            ther.get("MaxHeatSetpoint_x100"), 40.0
        )
        if is_heating
        else _temperature_from_x100_or_default(ther.get("MaxCoolSetpoint_x100"), 40.0),
        min_temp=_temperature_from_x100_or_default(
            ther.get("MinHeatSetpoint_x100"), 5.0
        )
        if is_heating
        else _temperature_from_x100_or_default(ther.get("MinCoolSetpoint_x100"), 5.0),
        hvac_mode=HVAC_MODE_HEAT
        if ther["SystemMode"] == SystemMode.HEAT
        else HVAC_MODE_COOL
        if ther["SystemMode"] == SystemMode.COOL
        else HVAC_MODE_AUTO,
        hvac_action=CURRENT_HVAC_OFF
        if hold_type == HoldType.STANDBY
        else CURRENT_HVAC_IDLE
        if running_state == RunningState.IDLE
        else CURRENT_HVAC_HEAT
        if is_heating and running_state == RunningState.FAN_COIL_HEATING
        else CURRENT_HVAC_HEAT_IDLE
        if is_heating
        else CURRENT_HVAC_COOL
        if running_state == RunningState.FAN_COIL_COOLING
        else CURRENT_HVAC_COOL_IDLE,
        hvac_modes=[HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO],
        preset_mode=PRESET_OFF
        if hold_type == HoldType.STANDBY
        else PRESET_PERMANENT_HOLD
        if hold_type == HoldType.PERMANENT_HOLD
        else PRESET_ECO
        if hold_type == HoldType.ECO
        else PRESET_TEMPORARY_HOLD
        if hold_type == HoldType.TEMPORARY_HOLD
        else PRESET_FOLLOW_SCHEDULE,
        preset_modes=[
            PRESET_OFF,
            PRESET_PERMANENT_HOLD,
            PRESET_ECO,
            PRESET_TEMPORARY_HOLD,
            PRESET_FOLLOW_SCHEDULE,
        ],
        fan_mode=FAN_MODE_OFF
        if fan_mode == FanMode.OFF
        else FAN_MODE_HIGH
        if fan_mode == FanMode.HIGH
        else FAN_MODE_MEDIUM
        if fan_mode == FanMode.MEDIUM
        else FAN_MODE_LOW
        if fan_mode == FanMode.LOW
        else FAN_MODE_AUTO,
        fan_modes=[
            FAN_MODE_AUTO,
            FAN_MODE_HIGH,
            FAN_MODE_MEDIUM,
            FAN_MODE_LOW,
            FAN_MODE_OFF,
        ],
        locked=device_status.get("sTherUIS", {}).get("LockKey", 0) == 1,
        supported_features=(
            SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE | SUPPORT_FAN_MODE
        ),
    )


def _parse_trv_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    ther: dict[str, Any],
    scomm: dict[str, Any],
) -> ClimateDevice:
    """Parse one TRV-style heating-only climate device."""
    hold_type = _hold_type(scomm, unique_id)
    running_state = ther.get("RunningState", DEFAULT_RUNNING_STATE)
    trv_attrs: dict[str, Any] = {}
    sit6zb = device_status.get("sIT6ZB")
    if isinstance(sit6zb, dict) and sit6zb.get("TRVOutputPercentage") is not None:
        trv_attrs["valve_opening"] = sit6zb["TRVOutputPercentage"]

    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=None,
        current_temperature=_temperature_from_x100(ther.get("LocalTemperature_x100")),
        target_temperature=_temperature_from_x100_or_default(
            ther.get("HeatingSetpoint_x100"),
            20.0,
        ),
        max_temp=_temperature_from_x100_or_default(
            ther.get("MaxHeatSetpoint_x100"), 35.0
        ),
        min_temp=_temperature_from_x100_or_default(ther.get("MinHeatSetpoint_x100"), 5.0),
        hvac_mode=HVAC_MODE_OFF
        if hold_type == HoldType.STANDBY
        else HVAC_MODE_HEAT
        if hold_type == HoldType.PERMANENT_HOLD
        else HVAC_MODE_AUTO,
        hvac_action=CURRENT_HVAC_OFF
        if hold_type == HoldType.STANDBY
        else CURRENT_HVAC_IDLE
        if running_state == RunningState.IDLE
        else CURRENT_HVAC_HEAT,
        hvac_modes=[HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO],
        preset_mode=PRESET_OFF
        if hold_type == HoldType.STANDBY
        else PRESET_PERMANENT_HOLD
        if hold_type == HoldType.PERMANENT_HOLD
        else PRESET_FOLLOW_SCHEDULE,
        preset_modes=[PRESET_FOLLOW_SCHEDULE, PRESET_PERMANENT_HOLD, PRESET_OFF],
        fan_mode=None,
        fan_modes=None,
        locked=(
            device_status["sTherUIS"].get("LockKey", 0) == 1
            if "sTherUIS" in device_status
            else None
        ),
        supported_features=SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE,
        extra_state_attributes=trv_attrs or None,
    )


def parse_climate_sensor_devices(
    device_status: dict[str, Any],
    climate_device: ClimateDevice,
) -> list[SensorDevice]:
    """Parse child sensors exposed by a climate payload."""
    unique_id = climate_device.unique_id
    model = climate_device.model
    sensors: list[SensorDevice] = []

    if climate_device.current_humidity is not None:
        sensors.append(
            SensorDevice(
                **{
                    **_common_device_args(device_status, f"{unique_id}_humidity"),
                    "name": f"{climate_device.name} Humidity",
                },
                state=climate_device.current_humidity,
                unit_of_measurement="%",
                device_class="humidity",
                parent_unique_id=unique_id,
            )
        )

    th = device_status.get("sIT600TH")
    if isinstance(th, dict):
        status_d = th.get("Status_d", "")
        if th.get("OUTSensorProbe") == 1 and isinstance(status_d, str):
            try:
                floor_temp_raw = int(status_d[12:16])
            except (ValueError, IndexError):
                floor_temp_raw = 0
            if 0 < floor_temp_raw <= 10000:
                sensors.append(
                    SensorDevice(
                        **{
                            **_common_device_args(
                                device_status, f"{unique_id}_floor_temperature"
                            ),
                            "name": f"{climate_device.name} Floor temperature",
                        },
                        state=floor_temp_raw / TEMPERATURE_SCALE,
                        unit_of_measurement=TEMP_CELSIUS,
                        device_class="temperature",
                        parent_unique_id=unique_id,
                    )
                )

        if model in BATTERY_OEM_MODELS and isinstance(status_d, str) and len(status_d) > 99:
            try:
                raw_battery = int(status_d[99])
            except (ValueError, IndexError):
                raw_battery = -1
            if 0 <= raw_battery <= 5:
                sensors.append(
                    SensorDevice(
                        **{
                            **_common_device_args(
                                device_status, f"{unique_id}_battery"
                            ),
                            "name": f"{climate_device.name} Battery",
                        },
                        state=BATTERY_LEVEL_MAP[raw_battery],
                        unit_of_measurement="%",
                        device_class="battery",
                        parent_unique_id=unique_id,
                        entity_category="diagnostic",
                    )
                )

    if not any(sensor.unique_id == f"{unique_id}_battery" for sensor in sensors):
        voltage_raw = device_status.get("sPowerS", {}).get("BatteryVoltage_x10")
        if voltage_raw is not None:
            pct = _voltage_to_battery_pct(voltage_raw / 10, model)
            if pct is not None:
                sensors.append(
                    SensorDevice(
                        **{
                            **_common_device_args(device_status, f"{unique_id}_battery"),
                            "name": f"{climate_device.name} Battery",
                        },
                        state=pct,
                        unit_of_measurement="%",
                        device_class="battery",
                        parent_unique_id=unique_id,
                        entity_category="diagnostic",
                    )
                )

    return sensors


def parse_climate_binary_sensor_devices(
    device_status: dict[str, Any],
    climate_device: ClimateDevice,
) -> list[BinarySensorDevice]:
    """Parse diagnostic child binary sensors exposed by a climate payload."""
    unique_id = climate_device.unique_id
    model = climate_device.model
    sensors: list[BinarySensorDevice] = []
    th = device_status.get("sIT600TH")
    ther = device_status.get("sTherS")
    scomm = device_status.get("sComm")

    if isinstance(th, dict):
        active_problems: list[str] = []
        active_battery: list[str] = []
        for error_key, description in THERMOSTAT_ERROR_CODES.items():
            if th.get(error_key) == 1:
                if error_key in BATTERY_ERROR_CODES:
                    active_battery.append(description)
                else:
                    active_problems.append(description)

        if model not in BATTERY_OEM_MODELS:
            active_problems.extend(active_battery)
            active_battery = []

        sensors.append(
            BinarySensorDevice(
                **{
                    **_common_device_args(device_status, f"{unique_id}_problem"),
                    "name": f"{climate_device.name} Problem",
                },
                is_on=bool(active_problems),
                device_class="problem",
                parent_unique_id=unique_id,
                entity_category="diagnostic",
                extra_state_attributes={"errors": active_problems},
            )
        )

        if model in BATTERY_OEM_MODELS:
            sensors.append(
                BinarySensorDevice(
                    **{
                        **_common_device_args(
                            device_status, f"{unique_id}_battery_error"
                        ),
                        "name": f"{climate_device.name} Battery problem",
                    },
                    is_on=bool(active_battery),
                    device_class="battery",
                    parent_unique_id=unique_id,
                    entity_category="diagnostic",
                    extra_state_attributes={"errors": active_battery},
                )
            )

    if isinstance(ther, dict) and isinstance(scomm, dict) and not isinstance(th, dict):
        error_code = scomm.get("DeviceErrorCode", "")
        has_error = bool(error_code and str(error_code).strip("0"))
        sensors.append(
            BinarySensorDevice(
                **{
                    **_common_device_args(device_status, f"{unique_id}_problem"),
                    "name": f"{climate_device.name} Problem",
                },
                is_on=has_error,
                device_class="problem",
                parent_unique_id=unique_id,
                entity_category="diagnostic",
                extra_state_attributes={"error_code": error_code},
            )
        )

        open_window = scomm.get("OpenWindowStatus")
        if open_window is not None:
            sensors.append(
                BinarySensorDevice(
                    **{
                        **_common_device_args(
                            device_status, f"{unique_id}_open_window"
                        ),
                        "name": f"{climate_device.name} Open window",
                    },
                    is_on=open_window != 0,
                    device_class="window",
                    parent_unique_id=unique_id,
                )
            )

    return sensors


def parse_climate_device(device_status: dict[str, Any]) -> ClimateDevice | None:
    """Parse one climate device detail payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    th = device_status.get("sIT600TH")
    if isinstance(th, dict):
        return _parse_it600th_climate_device(device_status, unique_id, th)

    ther = device_status.get("sTherS")
    scomm = device_status.get("sComm")
    sfans = device_status.get("sFanS")
    if isinstance(ther, dict) and isinstance(scomm, dict) and isinstance(sfans, dict):
        return _parse_fan_coil_climate_device(
            device_status,
            unique_id,
            ther,
            scomm,
            sfans,
        )
    if isinstance(ther, dict) and isinstance(scomm, dict):
        return _parse_trv_climate_device(device_status, unique_id, ther, scomm)

    return None
