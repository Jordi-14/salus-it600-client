"""Shared helpers for Salus iT600 gateway payload parsers."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any, NamedTuple

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
    unit_of_measurement: str | None,
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


class _SignalSensorSpec(NamedTuple):
    """Static description of one `sIT600I` signal-quality child sensor."""

    id_suffix: str
    payload_field: str
    name_suffix: str
    unit_of_measurement: str | None
    device_class: str | None


_SIGNAL_SENSOR_SPECS: tuple[_SignalSensorSpec, ...] = (
    _SignalSensorSpec(
        id_suffix="rssi",
        payload_field="LastMessageRSSI_d",
        name_suffix="Signal strength",
        unit_of_measurement="dBm",
        device_class="signal_strength",
    ),
    _SignalSensorSpec(
        id_suffix="lqi",
        payload_field="LastMessageLQI_d",
        name_suffix="Link quality",
        # Link quality is a bare 0-255 index: no unit, and no Home Assistant
        # sensor device class matches it.
        unit_of_measurement=None,
        device_class=None,
    ),
)


def _signal_reading(payload: dict[str, Any], field: str) -> int | None:
    """Return an integer signal reading, rejecting bools and non-integers."""
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _signal_sensor_devices(
    device_status: dict[str, Any],
    base_unique_id: str,
    parent_name: str,
    previous_sensors: Mapping[str, SensorDevice] | None = None,
) -> list[SensorDevice]:
    """Return the RSSI/LQI diagnostic sensors for one parent device.

    `sIT600I.LastMessageRSSI_d` / `LastMessageLQI_d` are only populated for
    devices the coordinator heard from directly on a given poll, so they are
    intermittently absent even on healthy, online devices. A missing value must
    not be reported as a fault or coerced to zero, and dropping the sensor for
    that one refresh would make it flap between a value and `unavailable`, so
    the last known reading from `previous_sensors` is carried forward instead.

    Everything else -- availability above all -- is rebuilt from this poll's
    parent payload, so these sensors track the parent device rather than the
    presence of the field. They disappear only with the parent itself: callers
    rebuild their collection every poll and never reach this helper for a
    parent the gateway no longer reports.
    """
    sit600i = device_status.get("sIT600I")
    payload = sit600i if isinstance(sit600i, dict) else {}
    retained = previous_sensors if previous_sensors is not None else {}

    sensors: list[SensorDevice] = []
    for spec in _SIGNAL_SENSOR_SPECS:
        unique_id = f"{base_unique_id}_{spec.id_suffix}"
        state: Any = _signal_reading(payload, spec.payload_field)
        if state is None:
            previous = retained.get(unique_id)
            if previous is None:
                continue
            state = previous.state

        sensors.append(
            _child_sensor_device(
                device_status,
                unique_id,
                f"{parent_name} {spec.name_suffix}",
                state=state,
                unit_of_measurement=spec.unit_of_measurement,
                device_class=spec.device_class,
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
