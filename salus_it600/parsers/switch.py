"""Switch device parsers."""

from __future__ import annotations

from typing import Any

from ..device_models import model_identifier, switch_device_class
from ..models import SensorDevice, SwitchDevice
from .common import _common_device_args


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
