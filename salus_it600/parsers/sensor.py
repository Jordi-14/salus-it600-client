"""Standalone sensor parsers."""

from __future__ import annotations

from typing import Any

from ..const import TEMP_CELSIUS, TEMPERATURE_SCALE
from ..device_models import model_identifier
from ..models import SensorDevice
from .common import (
    _child_sensor_device,
    _common_device_args,
    _device_name,
    _voltage_to_battery_pct,
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


def parse_sensor_devices(device_status: dict[str, Any]) -> list[SensorDevice]:
    """Parse a standalone sensor payload into primary and child sensors."""
    base_unique_id = device_status.get("data", {}).get("UniID")
    if base_unique_id is None:
        return []

    model = model_identifier(device_status)
    parent_name = _device_name(device_status, base_unique_id)
    sensors: list[SensorDevice] = []

    temperature = device_status.get("sTempS", {}).get("MeasuredValue_x100")
    if temperature is not None:
        sensors.append(
            SensorDevice(
                **_common_device_args(device_status, f"{base_unique_id}_temp"),
                state=temperature / TEMPERATURE_SCALE,
                unit_of_measurement=TEMP_CELSIUS,
                device_class="temperature",
            )
        )

    humidity_raw = device_status.get("sRelativeHumidity", {}).get(
        "MeasuredValue_x100"
    )
    if humidity_raw is not None:
        sensors.append(
            _child_sensor_device(
                device_status,
                f"{base_unique_id}_humidity",
                f"{parent_name} Humidity",
                state=humidity_raw / TEMPERATURE_SCALE,
                unit_of_measurement="%",
                device_class="humidity",
                parent_unique_id=base_unique_id,
            )
        )

    voltage_raw = device_status.get("sPowerS", {}).get("BatteryVoltage_x10")
    if voltage_raw is not None:
        pct = _voltage_to_battery_pct(voltage_raw / 10, model)
        if pct is not None:
            sensors.append(
                _child_sensor_device(
                    device_status,
                    f"{base_unique_id}_battery",
                    f"{parent_name} Battery",
                    state=pct,
                    unit_of_measurement="%",
                    device_class="battery",
                    parent_unique_id=base_unique_id,
                    entity_category="diagnostic",
                )
            )

    return sensors


def parse_meter_sensor_devices(device_status: dict[str, Any]) -> list[SensorDevice]:
    """Parse an energy meter (ECM600) payload into power/energy sensors.

    The ECM600 uses ZCL Metering cluster exposed as ``sMeterS`` with
    ``Multiplier`` / ``Divisor`` scaling and standard attributes
    ``InstantaneousDemand`` (W) and ``CurrentSummationDelivered`` (kWh).
    Each clamp is a separate endpoint.
    """
    base_unique_id = device_status.get("data", {}).get("UniID")
    endpoint = device_status.get("data", {}).get("Endpoint")
    if base_unique_id is None or endpoint is None:
        return []

    unique_id = f"{base_unique_id}_{endpoint}"
    metering = device_status.get("sMeterS")
    if not isinstance(metering, dict):
        return []

    multiplier = metering.get("Multiplier", 1)
    divisor = metering.get("Divisor", 1)
    scale = multiplier / divisor if divisor else 1

    model = model_identifier(device_status)
    parent_name = _device_name(device_status, base_unique_id)
    sensors: list[SensorDevice] = []

    power_raw = metering.get("InstantaneousDemand")
    if power_raw is not None:
        sensors.append(
            _child_sensor_device(
                device_status,
                f"{unique_id}_power",
                f"{parent_name} Power",
                state=round(power_raw * scale, 2),
                unit_of_measurement="W",
                device_class="power",
                parent_unique_id=unique_id,
            )
        )

    energy_raw = metering.get("CurrentSummationDelivered")
    if energy_raw is not None:
        sensors.append(
            _child_sensor_device(
                device_status,
                f"{unique_id}_energy",
                f"{parent_name} Energy",
                state=round(energy_raw * scale, 2),
                unit_of_measurement="kWh",
                device_class="energy",
                parent_unique_id=unique_id,
            )
        )

    # Battery from sPowerS (ECM600 is battery-powered with mains backup)
    voltage_raw = device_status.get("sPowerS", {}).get("BatteryVoltage_x10")
    if voltage_raw is not None:
        pct = _voltage_to_battery_pct(voltage_raw / 10, model)
        if pct is not None:
            sensors.append(
                _child_sensor_device(
                    device_status,
                    f"{unique_id}_battery",
                    f"{parent_name} Battery",
                    state=pct,
                    unit_of_measurement="%",
                    device_class="battery",
                    parent_unique_id=unique_id,
                    entity_category="diagnostic",
                )
            )

    return sensors
