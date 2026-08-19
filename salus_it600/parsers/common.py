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
from ..models import BinarySensorDevice, SensorDevice

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


def _child_sensor_device(
    device_status: dict[str, Any],
    unique_id: str,
    name: str,
    *,
    state: Any,
    unit_of_measurement: str,
    device_class: str | None,
    parent_unique_id: str,
    entity_category: str | None = None,
) -> SensorDevice:
    """Return a child sensor using shared parent device metadata."""
    return SensorDevice(
        **{**_common_device_args(device_status, unique_id), "name": name},
        state=state,
        unit_of_measurement=unit_of_measurement,
        device_class=device_class,
        parent_unique_id=parent_unique_id,
        entity_category=entity_category,
    )


def _signal_sensor_devices(
    device_status: dict[str, Any],
    base_unique_id: str,
    parent_name: str,
) -> list[SensorDevice]:
    """Return RSSI/LQI diagnostic sensors when the gateway reports them.

    `sIT600I.LastMessageRSSI_d` / `LastMessageLQI_d` are only populated for
    devices the coordinator heard from directly on a given poll, so they are
    intermittently absent even on healthy, online devices. A missing value
    must not be reported as a fault or coerced to zero -- the sensor is simply
    omitted from that refresh.
    """
    sit600i = device_status.get("sIT600I")
    if not isinstance(sit600i, dict):
        return []

    sensors: list[SensorDevice] = []

    rssi = sit600i.get("LastMessageRSSI_d")
    if isinstance(rssi, int) and not isinstance(rssi, bool):
        sensors.append(
            _child_sensor_device(
                device_status,
                f"{base_unique_id}_rssi",
                f"{parent_name} Signal strength",
                state=rssi,
                unit_of_measurement="dBm",
                device_class="signal_strength",
                parent_unique_id=base_unique_id,
                entity_category="diagnostic",
            )
        )

    lqi = sit600i.get("LastMessageLQI_d")
    if isinstance(lqi, int) and not isinstance(lqi, bool):
        sensors.append(
            _child_sensor_device(
                device_status,
                f"{base_unique_id}_lqi",
                f"{parent_name} Link quality",
                state=lqi,
                unit_of_measurement="",
                device_class=None,
                parent_unique_id=base_unique_id,
                entity_category="diagnostic",
            )
        )

    return sensors


def _child_binary_sensor_device(
    device_status: dict[str, Any],
    unique_id: str,
    name: str,
    *,
    is_on: bool,
    device_class: str,
    parent_unique_id: str,
    entity_category: str | None = None,
    extra_state_attributes: dict[str, Any] | None = None,
) -> BinarySensorDevice:
    """Return a child binary sensor using shared parent device metadata."""
    return BinarySensorDevice(
        **{**_common_device_args(device_status, unique_id), "name": name},
        is_on=is_on,
        device_class=device_class,
        parent_unique_id=parent_unique_id,
        entity_category=entity_category,
        extra_state_attributes=extra_state_attributes,
    )
