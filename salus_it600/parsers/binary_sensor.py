"""Binary sensor parsers."""

from __future__ import annotations

from typing import Any

from ..device_models import (
    BINARY_RELAY_MODELS,
    SKIPPED_BINARY_SENSOR_MODELS,
    binary_sensor_device_class,
    model_identifier,
)
from ..models import BinarySensorDevice
from .common import _common_device_args, _device_name


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
