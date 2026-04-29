"""Salus device model and protocol helpers.

This module centralizes device model identifiers, protocol constants, and device
classification logic. It serves as the single source of truth for device-specific
behavior across the library and the Home Assistant integration.

## Adding a New Device Model

When adding support for a new Salus device model:

1. **Define model identifier constant**: Add `MODEL_XXXXX = "XXXXX"` following
   existing naming convention.

2. **Add to classification maps if applicable**:
   - If binary sensor: Add to `BINARY_SENSOR_DEVICE_CLASSES` with appropriate
     Home Assistant device class ("window", "moisture", "smoke", etc.)
   - If switch: Check if outlet or regular switch, add to `OUTLET_MODELS` if needed
   - If climate: Determine if SQ610-like (with cooling support) or simple heater

3. **Add protocol constants if unique**:
   - If climate with cooling: Add SQ610_MODE_* and SQ610_HOLD_* constants
   - Keep raw write property names private to gateway command methods

4. **Create parser function in `salus_it600/parsers/`**:
   - Place it in the module for the device family
   - Extract fields from gateway payload dict
   - Return Device model instance or None if invalid
   - Use `model_identifier()` helper to get model from payload

5. **Register parser in poll_status()**:
   - Add device type filter in `poll_status()` if new payload key pattern
   - Connect to `_refresh_device_collection()` with parser function

## SQ610 Quantum Thermostat Protocol Quirks

SQ610 devices expose heating and cooling setpoints and modes not present in
standard models. Key differences:

- **Humidity stored in unusual field**: SQ610 devices report relative humidity
  in the `SunnySetpoint_x100` field (normally a temperature setpoint). Some
  payloads already use percent units while others use x100; normalize both to
  a Home Assistant-style percent value.

- **Dual setpoints**: SQ610 exposes both `HeatingSetpoint_x100` and
  `CoolingSetpoint_x100` depending on system mode, plus separate
  `SystemMode` field (3=cool, 4=heat, 5=emergency).

- **Hold type variants**: SQ610 uses hold type 7 for standby (Off), but also
  supports hold type 0 (auto return to schedule).

- **Write property names**: SQ610 write property names differ from read names.
  Keep these names private to client gateway methods instead of exposing them to
  callers.

## Device Classification

Devices are classified by protocol signature in gateway payloads:

- **Climate**: Contains `sIT600TH` or `sTherS` sections with temperature data
- **Binary sensor**: Contains `sIASZS` alarm/contact data, or is MINITRV/Receiver
- **Sensor**: Contains `sTempS` with `MeasuredValue_x100` temperature
- **Switch**: Contains `sOnOffS` with `OnOff` relay state
- **Cover**: Contains `sLevelS` with `CurrentLevel` position data
- **Gateway**: Root gateway device with `sGateway` MAC address
"""

from __future__ import annotations

from typing import Any

from .const import HoldType, RunningState, SystemMode

MODEL_FC600 = "FC600"
MODEL_SP600 = "SP600"
MODEL_SPE600 = "SPE600"
MODEL_SW600 = "SW600"
MODEL_OS600 = "OS600"
MODEL_WLS600 = "WLS600"
MODEL_SMOKE_SENSOR = "SmokeSensor-EM"
MODEL_MINI_TRV = "it600MINITRV"
MODEL_RECEIVER = "it600Receiver"
MODEL_BUTTON = "SB600"
MODEL_SD600 = "SD600"
MODEL_TS600 = "TS600"
MODEL_RE600 = "RE600"
MODEL_RE10B = "RE10B"
MODEL_TRV3RF = "TRV3RF"

SQ610_MODEL_TOKEN = "SQ610"

BINARY_RELAY_MODELS = {MODEL_MINI_TRV, MODEL_RECEIVER}
BINARY_SENSOR_DEVICE_CLASSES = {
    MODEL_SW600: "window",
    MODEL_OS600: "window",
    MODEL_WLS600: "moisture",
    MODEL_SMOKE_SENSOR: "smoke",
    MODEL_MINI_TRV: "heat",
    MODEL_RECEIVER: "running",
}
OUTLET_MODELS = {MODEL_SP600, MODEL_SPE600}
SKIPPED_BINARY_SENSOR_MODELS = {MODEL_BUTTON}
BATTERY_OEM_MODELS = frozenset(
    {
        "SQ610RF",
        "SQ610RF(WB)",
        "SQ610RFNH",
        "SQ610RFNH(WB)",
    }
)
WINDOW_VOLTAGE_MODELS = frozenset({MODEL_SW600, MODEL_OS600})
DOOR_VOLTAGE_MODELS = frozenset(
    {
        MODEL_SMOKE_SENSOR,
        MODEL_WLS600,
        MODEL_TS600,
        MODEL_SD600,
    }
)
ENERGY_METER_VOLTAGE_MODELS = frozenset({MODEL_RE600, MODEL_RE10B})
TRV_VOLTAGE_MODELS = frozenset({MODEL_TRV3RF})

SQ610_MODE_AUTO = SystemMode.AUTO
SQ610_MODE_COOL = SystemMode.COOL
SQ610_MODE_HEAT = SystemMode.HEAT
SQ610_MODE_EMERGENCY_HEAT = SystemMode.EMERGENCY_HEAT

SQ610_HOLD_AUTO = HoldType.FOLLOW_SCHEDULE
SQ610_HOLD_PERMANENT = HoldType.PERMANENT_HOLD
SQ610_HOLD_STANDBY = HoldType.STANDBY

SQ610_RUNNING_HEAT = RunningState.HEATING
SQ610_RUNNING_COOL = RunningState.COOLING


def model_identifier(device_status: dict[str, Any]) -> str | None:
    """Return the device model identifier from a detailed gateway payload.

    Extracts model from the `DeviceL.ModelIdentifier_i` field in a device detail
    response (returned by the "deviceid" read request).

    Args:
        device_status: Device detail dict from gateway readall/deviceid response

    Returns:
        Model identifier string (e.g. "SQ610RF", "FC600") or None if missing/invalid
    """
    model = device_status.get("DeviceL", {}).get("ModelIdentifier_i")
    return model if isinstance(model, str) else None


def basic_model_identifier(device_status: dict[str, Any]) -> str | None:
    """Return the model identifier from a readall summary payload.

    Extracts model from the `sBasicS.ModelIdentifier` field in a readall response
    (not available in detailed deviceid responses).

    Args:
        device_status: Device summary dict from gateway readall response

    Returns:
        Model identifier string or None if missing/invalid
    """
    basic = device_status.get("sBasicS")
    if not isinstance(basic, dict):
        return None
    model = basic.get("ModelIdentifier")
    return model if isinstance(model, str) else None


def is_sq610_model(model: str | None) -> bool:
    """Return whether a model identifier is an SQ610 Quantum thermostat.

    SQ610 models are identified by the presence of "SQ610" in the model string
    (case-insensitive). Variants include SQ610, SQ610RF, etc.

    SQ610 thermostats have special protocol features:
    - Separate heating and cooling setpoints
    - Humidity reported in SunnySetpoint_x100 field
    - Extended hold type support (auto, permanent, standby)
    - SystemMode field for mode selection (3=cool, 4=heat, 5=emergency)

    Args:
        model: Model identifier string or None

    Returns:
        True if SQ610 variant, False otherwise

    See Also:
        Module docstring for SQ610 protocol quirks
    """
    return isinstance(model, str) and SQ610_MODEL_TOKEN in model.upper()


def is_fan_coil_model(model: str | None) -> bool:
    """Return whether a model identifier is an FC600 fan-coil thermostat.

    FC600 models have different protocol structure than standard iT600TH
    thermostats: they use `sTherS` (with separate cooling setpoint) +
    `sComm` (hold type) + `sFanS` (fan mode) instead of single `sIT600TH`.

    Args:
        model: Model identifier string or None

    Returns:
        True if FC600, False otherwise
    """
    return model == MODEL_FC600


def is_trv_model(model: str | None) -> bool:
    """Return whether a model identifier is a TRV climate device."""
    return model in TRV_VOLTAGE_MODELS


def is_binary_sensor_summary(device_status: dict[str, Any]) -> bool:
    """Return whether a readall entry describes a binary sensor.

    Binary sensors are identified by either:
    - Presence of `sIASZS` section (contact/alarm/motion sensors)
    - Model in BINARY_RELAY_MODELS (TRV or receiver relay)

    Typically detects: door/window contacts, moisture sensors, smoke detectors,
    mini TRVs with relay, wireless receivers.

    Args:
        device_status: Device summary dict from gateway readall response

    Returns:
        True if binary sensor protocol signature detected
    """
    return (
        "sIASZS" in device_status
        or basic_model_identifier(device_status) in BINARY_RELAY_MODELS
    )


def binary_sensor_device_class(model: str | None) -> str | None:
    """Return the Home Assistant-style binary sensor device class.

    Maps Salus model identifiers to standard Home Assistant binary sensor
    device classes for consistent icon and state display.

    Args:
        model: Salus model identifier (e.g. "SW600", "WLS600")

    Returns:
        Home Assistant device class string ("window", "moisture", "smoke", etc.)
        or None if model not in BINARY_SENSOR_DEVICE_CLASSES map

    Example:
        >>> binary_sensor_device_class("SW600")
        "window"
        >>> binary_sensor_device_class("WLS600")
        "moisture"
    """
    if model is None:
        return None
    return BINARY_SENSOR_DEVICE_CLASSES.get(model)


def switch_device_class(model: str | None) -> str:
    """Return the Home Assistant-style switch device class.

    Maps Salus model identifiers to Home Assistant switch device classes.
    Most switches are generic "switch", but power outlets (SP600, SPE600)
    are marked as "outlet" for icon distinction.

    Args:
        model: Salus model identifier (e.g. "SP600", "SPE600", "RS600")

    Returns:
        "outlet" for power outlet models, "switch" for others

    Example:
        >>> switch_device_class("SP600")
        "outlet"
        >>> switch_device_class("RS600")
        "switch"
    """
    return "outlet" if model in OUTLET_MODELS else "switch"
