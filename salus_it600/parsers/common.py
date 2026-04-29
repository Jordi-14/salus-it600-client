"""Shared helpers for Salus iT600 gateway payload parsers."""

from __future__ import annotations

import json
import logging
from typing import Any

from ..const import (
    BATTERY_VOLTAGE_THRESHOLDS,
    TEMPERATURE_SCALE,
    HoldType,
    RunningState,
)
from ..device_models import (
    DOOR_VOLTAGE_MODELS,
    ENERGY_METER_VOLTAGE_MODELS,
    TRV_VOLTAGE_MODELS,
    WINDOW_VOLTAGE_MODELS,
    model_identifier,
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
