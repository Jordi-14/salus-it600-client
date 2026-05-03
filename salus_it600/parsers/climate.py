"""Climate device parsers."""

from __future__ import annotations

from typing import Any

from ..const import (
    BATTERY_ERROR_CODES,
    BATTERY_LEVEL_MAP,
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
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    TEMP_CELSIUS,
    TEMPERATURE_SCALE,
    THERMOSTAT_ERROR_CODES,
    FanMode,
    HoldType,
    RunningState,
    SystemMode,
)
from ..device_models import BATTERY_OEM_MODELS, is_sq610_model, model_identifier
from ..models import BinarySensorDevice, ClimateDevice, SensorDevice
from .common import (
    DEFAULT_RUNNING_STATE,
    _common_device_args,
    _hold_type,
    _humidity_percent,
    _temperature_from_x100,
    _temperature_from_x100_or_default,
    _voltage_to_battery_pct,
)


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


def _thermostat_locked(
    device_status: dict[str, Any],
    th: dict[str, Any] | None = None,
) -> bool | None:
    """Return thermostat keypad lock state when the payload exposes it."""
    ther_ui = device_status.get("sTherUIS")
    if isinstance(ther_ui, dict) and "LockKey" in ther_ui:
        return ther_ui.get("LockKey") == 1

    if th is not None and "LockKey" in th:
        return th.get("LockKey") == 1

    return None


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
        locked=_thermostat_locked(device_status, th),
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
        locked=_thermostat_locked(device_status),
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
