"""Wiring centre (it600WC) parsers.

The it600WC is a hydronic wiring/pump-relay centre paired with SQ610-family
thermostats. On a hydronic system it is the single point of failure for every
zone, yet its payload carries no valve/relay state of its own -- only a
fault-register bank (`sIT600WC`), identity fields, and the `sIT600I`
signal-quality block shared with other device families. It is therefore
modeled as diagnostic-only entities: a connectivity indicator (the closest
thing it has to a primary reading), an aggregated problem sensor, and
signal-quality children.
"""

from __future__ import annotations

from typing import Any

from ..const import THERMOSTAT_ERROR_CODES
from ..models import BinarySensorDevice, SensorDevice
from .common import (
    _child_binary_sensor_device,
    _common_device_args,
    _device_name,
    _online,
    _signal_sensor_devices,
)


def parse_wiring_centre_device(
    device_status: dict[str, Any],
) -> BinarySensorDevice | None:
    """Parse the connectivity indicator for an it600WC wiring centre."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None

    if not isinstance(device_status.get("sIT600WC"), dict):
        return None

    return BinarySensorDevice(
        **_common_device_args(device_status, unique_id),
        is_on=_online(device_status),
        device_class="connectivity",
        entity_category="diagnostic",
    )


def parse_wiring_centre_binary_sensor_devices(
    device_status: dict[str, Any],
) -> list[BinarySensorDevice]:
    """Parse the aggregated fault-register problem sensor for an it600WC.

    Reuses the same `THERMOSTAT_ERROR_CODES` table and aggregation shape
    `parse_climate_binary_sensor_devices` already uses for thermostats,
    rather than a parallel fault mechanism: the it600WC's `sIT600WC` payload
    reports its own Error10-20/Error26-29 slice of that same vendor register
    bank. `.get(error_key) == 1` on `wc` naturally ignores the thermostat-only
    keys, since a wiring centre payload never carries them.

    `ErrorCodeWC_d` is a hex string ("0000" at baseline). A bare
    `bool(error_code)` check would report a permanent fault on every healthy
    unit, since a non-empty "0000" string is truthy. Strip zero digits the
    same way `parse_climate_binary_sensor_devices` already does for the
    FC600/TRV `sComm.DeviceErrorCode` register.
    """
    base_unique_id = device_status.get("data", {}).get("UniID")
    wc = device_status.get("sIT600WC")
    if base_unique_id is None or not isinstance(wc, dict):
        return []

    parent_name = _device_name(device_status, base_unique_id)
    active_errors = [
        description
        for error_key, description in THERMOSTAT_ERROR_CODES.items()
        if wc.get(error_key) == 1
    ]

    error_code = wc.get("ErrorCodeWC_d", "")
    has_error_code = bool(error_code and str(error_code).strip("0"))

    return [
        _child_binary_sensor_device(
            device_status,
            f"{base_unique_id}_problem",
            f"{parent_name} Problem",
            is_on=bool(active_errors) or has_error_code,
            device_class="problem",
            parent_unique_id=base_unique_id,
            entity_category="diagnostic",
            extra_state_attributes={
                "errors": active_errors,
                "error_code_wc": error_code,
            },
        )
    ]


def parse_wiring_centre_sensor_devices(
    device_status: dict[str, Any],
) -> list[SensorDevice]:
    """Parse RSSI/LQI diagnostic sensors for an it600WC wiring centre."""
    base_unique_id = device_status.get("data", {}).get("UniID")
    if base_unique_id is None or not isinstance(device_status.get("sIT600WC"), dict):
        return []

    parent_name = _device_name(device_status, base_unique_id)
    return _signal_sensor_devices(device_status, base_unique_id, parent_name)
