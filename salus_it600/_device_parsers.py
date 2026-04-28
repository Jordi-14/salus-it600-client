"""Private device parser helpers for Salus iT600 gateway payloads."""

from __future__ import annotations

import json
import logging
from typing import Any

from .const import (
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
    FanMode,
    HoldType,
    RunningState,
    SystemMode,
)
from .device_models import (
    BINARY_RELAY_MODELS,
    SKIPPED_BINARY_SENSOR_MODELS,
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
    raw_humidity = th.get("SunnySetpoint_x100")
    current_humidity = (
        raw_humidity / TEMPERATURE_SCALE
        if is_sq610_model(model) and isinstance(raw_humidity, int | float)
        else None
    )
    hold_type = _hold_type(th, unique_id)
    running_state = th.get("RunningState", DEFAULT_RUNNING_STATE)
    return ClimateDevice(
        **_climate_common_args(device_status, unique_id),
        current_humidity=current_humidity,
        current_temperature=th.get("LocalTemperature_x100", 2000) / TEMPERATURE_SCALE,
        target_temperature=th.get("HeatingSetpoint_x100", 2000) / TEMPERATURE_SCALE,
        max_temp=th.get("MaxHeatSetpoint_x100", 3500) / TEMPERATURE_SCALE,
        min_temp=th.get("MinHeatSetpoint_x100", 500) / TEMPERATURE_SCALE,
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
        locked=None,
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
        current_temperature=ther.get("LocalTemperature_x100", 2000) / TEMPERATURE_SCALE,
        target_temperature=(ther.get("HeatingSetpoint_x100", 2000) / TEMPERATURE_SCALE)
        if is_heating
        else (ther.get("CoolingSetpoint_x100", 2000) / TEMPERATURE_SCALE),
        max_temp=(ther.get("MaxHeatSetpoint_x100", 4000) / TEMPERATURE_SCALE)
        if is_heating
        else (ther.get("MaxCoolSetpoint_x100", 4000) / TEMPERATURE_SCALE),
        min_temp=(ther.get("MinHeatSetpoint_x100", 500) / TEMPERATURE_SCALE)
        if is_heating
        else (ther.get("MinCoolSetpoint_x100", 500) / TEMPERATURE_SCALE),
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

    return None
