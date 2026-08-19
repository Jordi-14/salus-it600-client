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
    PRESET_AWAY,
    PRESET_ECO,
    PRESET_FOLLOW_SCHEDULE,
    PRESET_OFF,
    PRESET_PERMANENT_HOLD,
    PRESET_SCHEDULE_OVERRIDE,
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
from ..models import (
    BinarySensorDevice,
    ClimateDevice,
    SensorDevice,
    active_climate_system_mode,
    active_climate_setpoint,
    active_temperature_range,
    climate_diagnostic_fields,
    normalized_running_state,
    normalized_system_mode,
    running_state_is_cooling,
    running_state_is_heating,
    sq610_cooling_capability_source,
    sq610_supports_cooling,
)
from .common import (
    _child_binary_sensor_device,
    _child_sensor_device,
    _common_device_args,
    _hold_type,
    _humidity_percent,
    _signal_sensor_devices,
    _temperature_from_x100,
    _voltage_to_battery_pct,
)

# Field offsets into the sIT600TH "Status_d" status string (fixed vendor firmware
# layout). The floor-temperature reading is the 4 digits at [12:16] scaled by
# TEMPERATURE_SCALE; the battery level is the single digit at index 99.
STATUS_D_FLOOR_TEMPERATURE_SLICE = slice(12, 16)
STATUS_D_BATTERY_INDEX = 99


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


def _payload_int(value: Any) -> int | None:
    """Return an integer payload value, rejecting bools and non-integers."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _online_status(device_status: dict[str, Any]) -> int | None:
    """Return the raw online status value when the payload exposes it."""
    zdo_info = device_status.get("sZDOInfo")
    if not isinstance(zdo_info, dict):
        return None
    return _payload_int(zdo_info.get("OnlineStatus_i"))


def _sq610_hvac_mode(
    *,
    hold_type: int,
    system_mode: int | None,
    running_state: int | None,
) -> str:
    """Return the SQ610 Home Assistant-style HVAC mode."""
    if hold_type == HoldType.STANDBY:
        return HVAC_MODE_OFF
    if system_mode == SystemMode.COOL or running_state_is_cooling(running_state):
        return HVAC_MODE_COOL
    return HVAC_MODE_HEAT


def _sq610_hvac_action(
    *,
    hold_type: int,
    running_state: int | None,
) -> str:
    """Return the SQ610 current action from its hold and running state."""
    if hold_type == HoldType.STANDBY:
        return CURRENT_HVAC_OFF
    if running_state_is_heating(running_state):
        return CURRENT_HVAC_HEAT
    if running_state_is_cooling(running_state):
        return CURRENT_HVAC_COOL
    return CURRENT_HVAC_IDLE


def _sq610_preset_mode(hold_type: int) -> str:
    """Return the SQ610 preset corresponding to HoldType."""
    if hold_type == HoldType.STANDBY:
        return PRESET_OFF
    if hold_type == HoldType.AWAY:
        return PRESET_AWAY
    if hold_type == HoldType.TEMPORARY_HOLD:
        return PRESET_SCHEDULE_OVERRIDE
    if hold_type == HoldType.PERMANENT_HOLD:
        return PRESET_PERMANENT_HOLD
    return PRESET_FOLLOW_SCHEDULE


def _normalized_preset_modes(
    base_modes: tuple[str, ...],
    active_preset: str,
) -> tuple[str, ...]:
    """Return presets with the active reported preset included once."""
    modes = list(base_modes)
    if active_preset in modes:
        return tuple(modes)
    if active_preset == PRESET_SCHEDULE_OVERRIDE and PRESET_FOLLOW_SCHEDULE in modes:
        modes.insert(modes.index(PRESET_FOLLOW_SCHEDULE) + 1, active_preset)
    else:
        modes.append(active_preset)
    return tuple(modes)


def _sq610_preset_modes(hold_type: int) -> tuple[str, ...]:
    """Return SQ610 presets, adding Schedule Override only while active."""
    return _normalized_preset_modes(
        (
            PRESET_FOLLOW_SCHEDULE,
            PRESET_PERMANENT_HOLD,
            PRESET_AWAY,
            PRESET_OFF,
        ),
        _sq610_preset_mode(hold_type),
    )


def _fan_coil_hvac_mode(system_mode: int | None) -> str:
    """Return the FC600 Home Assistant-style HVAC mode."""
    if system_mode == SystemMode.HEAT:
        return HVAC_MODE_HEAT
    if system_mode == SystemMode.COOL:
        return HVAC_MODE_COOL
    return HVAC_MODE_AUTO


def _fan_coil_hvac_action(
    *,
    hold_type: int,
    system_mode: int | None,
    running_state: int | None,
) -> str:
    """Return the FC600 current action from system and running state."""
    if hold_type == HoldType.STANDBY:
        return CURRENT_HVAC_OFF
    if running_state == RunningState.IDLE:
        return CURRENT_HVAC_IDLE
    if running_state_is_heating(running_state):
        return CURRENT_HVAC_HEAT
    if running_state_is_cooling(running_state):
        return CURRENT_HVAC_COOL
    if system_mode == SystemMode.HEAT:
        return CURRENT_HVAC_HEAT_IDLE
    if system_mode == SystemMode.COOL:
        return CURRENT_HVAC_COOL_IDLE
    return CURRENT_HVAC_IDLE


def _fan_coil_preset_mode(hold_type: int) -> str:
    """Return the FC600 preset corresponding to HoldType."""
    if hold_type == HoldType.STANDBY:
        return PRESET_OFF
    if hold_type == HoldType.PERMANENT_HOLD:
        return PRESET_PERMANENT_HOLD
    if hold_type == HoldType.ECO:
        return PRESET_ECO
    if hold_type == HoldType.TEMPORARY_HOLD:
        return PRESET_SCHEDULE_OVERRIDE
    return PRESET_FOLLOW_SCHEDULE


def _fan_coil_preset_modes(hold_type: int) -> tuple[str, ...]:
    """Return FC600 presets, adding Schedule Override only while active."""
    return _normalized_preset_modes(
        (
            PRESET_FOLLOW_SCHEDULE,
            PRESET_PERMANENT_HOLD,
            PRESET_ECO,
            PRESET_OFF,
        ),
        _fan_coil_preset_mode(hold_type),
    )


def _fan_coil_fan_mode(fan_mode: Any) -> str:
    """Return the FC600 fan mode corresponding to the raw fan value."""
    if fan_mode == FanMode.OFF:
        return FAN_MODE_OFF
    if fan_mode == FanMode.HIGH:
        return FAN_MODE_HIGH
    if fan_mode == FanMode.MEDIUM:
        return FAN_MODE_MEDIUM
    if fan_mode == FanMode.LOW:
        return FAN_MODE_LOW
    return FAN_MODE_AUTO


def _heat_only_hvac_mode(hold_type: int) -> str:
    """Return the Home Assistant-style HVAC mode for heat-only devices."""
    if hold_type == HoldType.STANDBY:
        return HVAC_MODE_OFF
    if hold_type == HoldType.PERMANENT_HOLD:
        return HVAC_MODE_HEAT
    return HVAC_MODE_AUTO


def _heat_only_running_action(
    *,
    hold_type: int,
    running_state: int | None,
    heat_on_non_idle: bool,
) -> str:
    """Return current action for heat-only thermostat and TRV families."""
    if hold_type == HoldType.STANDBY:
        return CURRENT_HVAC_OFF
    if running_state is None or running_state == RunningState.IDLE:
        return CURRENT_HVAC_IDLE
    if heat_on_non_idle or running_state % 2 != 0:
        return CURRENT_HVAC_HEAT
    return CURRENT_HVAC_IDLE


def _heat_only_preset_mode(hold_type: int) -> str:
    """Return the Home Assistant-style preset for heat-only devices."""
    if hold_type == HoldType.STANDBY:
        return PRESET_OFF
    if hold_type == HoldType.PERMANENT_HOLD:
        return PRESET_PERMANENT_HOLD
    return PRESET_FOLLOW_SCHEDULE


def _climate_diagnostic_payload(
    device_status: dict[str, Any],
    *payloads: dict[str, Any],
) -> dict[str, Any]:
    """Return merged support fields for climate diagnostics."""
    diagnostic_payload: dict[str, Any] = {}

    for section_name, field_names in (
        ("data", ("UniID",)),
        ("sZDO", ("DeviceName", "FirmwareVersion")),
        ("DeviceL", ("ModelIdentifier_i",)),
        ("sTempS", ("MeasuredValue_x100",)),
    ):
        section = device_status.get(section_name)
        if not isinstance(section, dict):
            continue
        diagnostic_payload.update(
            {
                field_name: section[field_name]
                for field_name in field_names
                if field_name in section
            }
        )

    for payload in payloads:
        diagnostic_payload.update(payload)

    ther_ui = device_status.get("sTherUIS")
    if isinstance(ther_ui, dict):
        diagnostic_payload.update(ther_ui)

    online_status = _online_status(device_status)
    if online_status is not None:
        diagnostic_payload["OnlineStatus_i"] = online_status

    return diagnostic_payload


def _parse_sq610_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    th: dict[str, Any],
) -> ClimateDevice:
    """Parse one SQ610 thermostat from gateway payload."""
    s_temp = device_status.get("sTempS", {})
    current_temperature = _temperature_from_x100(
        th.get("LocalTemperature_x100"),
        s_temp.get("MeasuredValue_x100") if isinstance(s_temp, dict) else None,
    )
    hold_type = _hold_type(th, unique_id)
    system_mode = normalized_system_mode(th.get("SystemMode"))
    running_state = normalized_running_state(th.get("RunningState"))
    heating_setpoint = _temperature_from_x100(th.get("HeatingSetpoint_x100"))
    cooling_setpoint = _temperature_from_x100(th.get("CoolingSetpoint_x100"))
    min_heat_temp = _temperature_from_x100(th.get("MinHeatSetpoint_x100"))
    max_heat_temp = _temperature_from_x100(th.get("MaxHeatSetpoint_x100"))
    min_cool_temp = _temperature_from_x100(th.get("MinCoolSetpoint_x100"))
    max_cool_temp = _temperature_from_x100(th.get("MaxCoolSetpoint_x100"))
    hvac_mode = _sq610_hvac_mode(
        hold_type=hold_type,
        system_mode=system_mode,
        running_state=running_state,
    )
    active_system_mode = active_climate_system_mode(
        system_mode=system_mode,
        hvac_mode=hvac_mode,
        running_state=running_state,
    )
    active_setpoint = active_climate_setpoint(
        system_mode=active_system_mode,
        heating_setpoint=heating_setpoint,
        cooling_setpoint=cooling_setpoint,
    )
    min_temp, max_temp = active_temperature_range(
        system_mode=active_system_mode,
        min_heat_temp=min_heat_temp,
        max_heat_temp=max_heat_temp,
        min_cool_temp=min_cool_temp,
        max_cool_temp=max_cool_temp,
    )
    cooling_control = _payload_int(th.get("CoolingControl"))
    cooling_capability_source = sq610_cooling_capability_source(
        cooling_control=cooling_control,
        system_mode=system_mode,
        running_state=running_state,
    )
    supports_cooling = sq610_supports_cooling(
        cooling_control=cooling_control,
        system_mode=system_mode,
        running_state=running_state,
    )
    online_status = _online_status(device_status)
    diagnostic_payload = _climate_diagnostic_payload(device_status, th)

    hvac_modes = (
        (HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL)
        if supports_cooling
        else (HVAC_MODE_OFF, HVAC_MODE_HEAT)
    )

    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=_humidity_percent(th.get("SunnySetpoint_x100")),
        current_temperature=current_temperature,
        target_temperature=active_setpoint if active_setpoint is not None else 20.0,
        max_temp=max_temp if max_temp is not None else 35.0,
        min_temp=min_temp if min_temp is not None else 5.0,
        hvac_mode=hvac_mode,
        hvac_action=_sq610_hvac_action(
            hold_type=hold_type,
            running_state=running_state,
        ),
        hvac_modes=hvac_modes,
        preset_mode=_sq610_preset_mode(hold_type),
        preset_modes=_sq610_preset_modes(hold_type),
        fan_mode=None,
        fan_modes=None,
        locked=_thermostat_locked(device_status, th),
        supported_features=SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE,
        hold_type=hold_type,
        system_mode=system_mode,
        running_state=running_state,
        heating_setpoint=heating_setpoint,
        cooling_setpoint=cooling_setpoint,
        min_heat_temp=min_heat_temp,
        max_heat_temp=max_heat_temp,
        min_cool_temp=min_cool_temp,
        max_cool_temp=max_cool_temp,
        heating_control=_payload_int(th.get("HeatingControl")),
        cooling_control=cooling_control,
        supports_cooling=supports_cooling,
        supports_fan=False,
        supports_heat=True,
        online_status=online_status,
        cooling_capability_source=cooling_capability_source,
        diagnostic_fields=climate_diagnostic_fields(diagnostic_payload),
    )


def _parse_it600th_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    th: dict[str, Any],
) -> ClimateDevice:
    """Parse one standard iT600 thermostat from gateway payload."""
    s_temp = device_status.get("sTempS", {})
    current_temperature = _temperature_from_x100(
        th.get("LocalTemperature_x100"),
        s_temp.get("MeasuredValue_x100") if isinstance(s_temp, dict) else None,
    )
    hold_type = _hold_type(th, unique_id)
    running_state = normalized_running_state(th.get("RunningState"))
    heating_setpoint = _temperature_from_x100(th.get("HeatingSetpoint_x100"))
    min_heat_temp = _temperature_from_x100(th.get("MinHeatSetpoint_x100"))
    max_heat_temp = _temperature_from_x100(th.get("MaxHeatSetpoint_x100"))
    online_status = _online_status(device_status)
    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=None,
        current_temperature=current_temperature,
        target_temperature=heating_setpoint if heating_setpoint is not None else 20.0,
        max_temp=max_heat_temp if max_heat_temp is not None else 35.0,
        min_temp=min_heat_temp if min_heat_temp is not None else 5.0,
        hvac_mode=_heat_only_hvac_mode(hold_type),
        hvac_action=_heat_only_running_action(
            hold_type=hold_type,
            running_state=running_state,
            heat_on_non_idle=False,
        ),
        hvac_modes=(HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO),
        preset_mode=_heat_only_preset_mode(hold_type),
        preset_modes=_normalized_preset_modes(
            (
                PRESET_FOLLOW_SCHEDULE,
                PRESET_PERMANENT_HOLD,
                PRESET_OFF,
            ),
            _heat_only_preset_mode(hold_type),
        ),
        fan_mode=None,
        fan_modes=None,
        locked=_thermostat_locked(device_status, th),
        supported_features=SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE,
        hold_type=hold_type,
        system_mode=normalized_system_mode(th.get("SystemMode")),
        running_state=running_state,
        heating_setpoint=heating_setpoint,
        min_heat_temp=min_heat_temp,
        max_heat_temp=max_heat_temp,
        heating_control=_payload_int(th.get("HeatingControl")),
        supports_cooling=False,
        supports_fan=False,
        supports_heat=True,
        online_status=online_status,
        cooling_capability_source="none",
        diagnostic_fields=climate_diagnostic_fields(
            _climate_diagnostic_payload(device_status, th),
        ),
    )


def _parse_fan_coil_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    ther: dict[str, Any],
    scomm: dict[str, Any],
    sfans: dict[str, Any],
) -> ClimateDevice:
    """Parse one FC600 fan-coil thermostat from gateway payload."""
    system_mode = normalized_system_mode(ther["SystemMode"])
    fan_mode = sfans.get("FanMode", FanMode.AUTO)
    hold_type = _hold_type(scomm, unique_id)
    running_state = normalized_running_state(ther.get("RunningState"))
    heating_setpoint = _temperature_from_x100(ther.get("HeatingSetpoint_x100"))
    cooling_setpoint = _temperature_from_x100(ther.get("CoolingSetpoint_x100"))
    min_heat_temp = _temperature_from_x100(ther.get("MinHeatSetpoint_x100"))
    max_heat_temp = _temperature_from_x100(ther.get("MaxHeatSetpoint_x100"))
    min_cool_temp = _temperature_from_x100(ther.get("MinCoolSetpoint_x100"))
    max_cool_temp = _temperature_from_x100(ther.get("MaxCoolSetpoint_x100"))
    hvac_mode = _fan_coil_hvac_mode(system_mode)
    active_system_mode = active_climate_system_mode(
        system_mode=system_mode,
        hvac_mode=hvac_mode,
        running_state=running_state,
    )
    active_setpoint = active_climate_setpoint(
        system_mode=active_system_mode,
        heating_setpoint=heating_setpoint,
        cooling_setpoint=cooling_setpoint,
    )
    min_temp, max_temp = active_temperature_range(
        system_mode=active_system_mode,
        min_heat_temp=min_heat_temp,
        max_heat_temp=max_heat_temp,
        min_cool_temp=min_cool_temp,
        max_cool_temp=max_cool_temp,
    )
    online_status = _online_status(device_status)
    diagnostic_payload = _climate_diagnostic_payload(device_status, ther, scomm)

    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=None,
        current_temperature=_temperature_from_x100(ther.get("LocalTemperature_x100")),
        target_temperature=active_setpoint if active_setpoint is not None else 20.0,
        max_temp=max_temp if max_temp is not None else 40.0,
        min_temp=min_temp if min_temp is not None else 5.0,
        hvac_mode=hvac_mode,
        hvac_action=_fan_coil_hvac_action(
            hold_type=hold_type,
            system_mode=system_mode,
            running_state=running_state,
        ),
        hvac_modes=(HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO),
        preset_mode=_fan_coil_preset_mode(hold_type),
        preset_modes=_fan_coil_preset_modes(hold_type),
        fan_mode=_fan_coil_fan_mode(fan_mode),
        fan_modes=(
            FAN_MODE_AUTO,
            FAN_MODE_HIGH,
            FAN_MODE_MEDIUM,
            FAN_MODE_LOW,
            FAN_MODE_OFF,
        ),
        locked=_thermostat_locked(device_status),
        supported_features=(
            SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE | SUPPORT_FAN_MODE
        ),
        hold_type=hold_type,
        system_mode=system_mode,
        running_state=running_state,
        heating_setpoint=heating_setpoint,
        cooling_setpoint=cooling_setpoint,
        min_heat_temp=min_heat_temp,
        max_heat_temp=max_heat_temp,
        min_cool_temp=min_cool_temp,
        max_cool_temp=max_cool_temp,
        heating_control=_payload_int(ther.get("HeatingControl")),
        cooling_control=_payload_int(ther.get("CoolingControl")),
        supports_cooling=True,
        supports_fan=True,
        supports_heat=True,
        online_status=online_status,
        cooling_capability_source="known_model",
        diagnostic_fields=climate_diagnostic_fields(diagnostic_payload),
    )


def _parse_trv_climate_device(
    device_status: dict[str, Any],
    unique_id: str,
    ther: dict[str, Any],
    scomm: dict[str, Any],
) -> ClimateDevice:
    """Parse one TRV-style heating-only climate device."""
    hold_type = _hold_type(scomm, unique_id)
    running_state = normalized_running_state(ther.get("RunningState"))
    heating_setpoint = _temperature_from_x100(ther.get("HeatingSetpoint_x100"))
    min_heat_temp = _temperature_from_x100(ther.get("MinHeatSetpoint_x100"))
    max_heat_temp = _temperature_from_x100(ther.get("MaxHeatSetpoint_x100"))
    online_status = _online_status(device_status)
    trv_attrs: dict[str, Any] = {}
    sit6zb = device_status.get("sIT6ZB")
    if isinstance(sit6zb, dict) and sit6zb.get("TRVOutputPercentage") is not None:
        trv_attrs["valve_opening"] = sit6zb["TRVOutputPercentage"]

    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=None,
        current_temperature=_temperature_from_x100(ther.get("LocalTemperature_x100")),
        target_temperature=heating_setpoint if heating_setpoint is not None else 20.0,
        max_temp=max_heat_temp if max_heat_temp is not None else 35.0,
        min_temp=min_heat_temp if min_heat_temp is not None else 5.0,
        hvac_mode=_heat_only_hvac_mode(hold_type),
        hvac_action=_heat_only_running_action(
            hold_type=hold_type,
            running_state=running_state,
            heat_on_non_idle=True,
        ),
        hvac_modes=(HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO),
        preset_mode=_heat_only_preset_mode(hold_type),
        preset_modes=_normalized_preset_modes(
            (
                PRESET_FOLLOW_SCHEDULE,
                PRESET_PERMANENT_HOLD,
                PRESET_OFF,
            ),
            _heat_only_preset_mode(hold_type),
        ),
        fan_mode=None,
        fan_modes=None,
        locked=_thermostat_locked(device_status),
        supported_features=SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE,
        extra_state_attributes=trv_attrs or None,
        hold_type=hold_type,
        system_mode=normalized_system_mode(ther.get("SystemMode")),
        running_state=running_state,
        heating_setpoint=heating_setpoint,
        min_heat_temp=min_heat_temp,
        max_heat_temp=max_heat_temp,
        heating_control=_payload_int(ther.get("HeatingControl")),
        supports_cooling=False,
        supports_fan=False,
        supports_heat=True,
        online_status=online_status,
        cooling_capability_source="none",
        diagnostic_fields=climate_diagnostic_fields(
            _climate_diagnostic_payload(device_status, ther, scomm),
        ),
    )


def parse_climate_sensor_devices(
    device_status: dict[str, Any],
    climate_device: ClimateDevice,
) -> list[SensorDevice]:
    """Parse child sensors exposed by a climate payload."""
    unique_id = climate_device.unique_id
    model = climate_device.model
    sensors: list[SensorDevice] = _signal_sensor_devices(
        device_status, unique_id, climate_device.name
    )

    if climate_device.current_humidity is not None:
        sensors.append(
            _child_sensor_device(
                device_status,
                f"{unique_id}_humidity",
                f"{climate_device.name} Humidity",
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
                floor_temp_raw = int(status_d[STATUS_D_FLOOR_TEMPERATURE_SLICE])
            except (ValueError, IndexError):
                floor_temp_raw = 0
            if 0 < floor_temp_raw <= 10000:
                sensors.append(
                    _child_sensor_device(
                        device_status,
                        f"{unique_id}_floor_temperature",
                        f"{climate_device.name} Floor temperature",
                        state=floor_temp_raw / TEMPERATURE_SCALE,
                        unit_of_measurement=TEMP_CELSIUS,
                        device_class="temperature",
                        parent_unique_id=unique_id,
                    )
                )

        if model in BATTERY_OEM_MODELS and isinstance(status_d, str) and len(status_d) > STATUS_D_BATTERY_INDEX:
            try:
                raw_battery = int(status_d[STATUS_D_BATTERY_INDEX])
            except (ValueError, IndexError):
                raw_battery = -1
            if 0 <= raw_battery <= 5:
                sensors.append(
                    _child_sensor_device(
                        device_status,
                        f"{unique_id}_battery",
                        f"{climate_device.name} Battery",
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
                    _child_sensor_device(
                        device_status,
                        f"{unique_id}_battery",
                        f"{climate_device.name} Battery",
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
            _child_binary_sensor_device(
                device_status,
                f"{unique_id}_problem",
                f"{climate_device.name} Problem",
                is_on=bool(active_problems),
                device_class="problem",
                parent_unique_id=unique_id,
                entity_category="diagnostic",
                extra_state_attributes={"errors": active_problems},
            )
        )

        if model in BATTERY_OEM_MODELS:
            sensors.append(
                _child_binary_sensor_device(
                    device_status,
                    f"{unique_id}_battery_error",
                    f"{climate_device.name} Battery problem",
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
            _child_binary_sensor_device(
                device_status,
                f"{unique_id}_problem",
                f"{climate_device.name} Problem",
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
                _child_binary_sensor_device(
                    device_status,
                    f"{unique_id}_open_window",
                    f"{climate_device.name} Open window",
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
        if is_sq610_model(model_identifier(device_status)):
            return _parse_sq610_climate_device(device_status, unique_id, th)
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
