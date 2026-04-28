"""Salus iT600 smart device models."""

from __future__ import annotations

from typing import Any, NamedTuple

DeviceData = dict[str, Any]


class GatewayDevice(NamedTuple):
    name: str
    unique_id: str
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None


class ClimateDevice(NamedTuple):
    available: bool
    name: str
    unique_id: str
    temperature_unit: str
    precision: float
    current_temperature: float | None
    target_temperature: float
    max_temp: float
    min_temp: float
    current_humidity: float | None
    hvac_mode: str
    hvac_action: str
    hvac_modes: list[str]
    preset_mode: str
    preset_modes: list[str]
    fan_mode: str | None
    fan_modes: list[str] | None
    locked: bool | None
    supported_features: int
    device_class: str
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None


class BinarySensorDevice(NamedTuple):
    available: bool
    name: str
    unique_id: str
    is_on: bool
    device_class: str | None
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None


class SwitchDevice(NamedTuple):
    available: bool
    name: str
    unique_id: str
    is_on: bool
    device_class: str
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None


class CoverDevice(NamedTuple):
    available: bool
    name: str
    unique_id: str
    current_cover_position: int | None
    is_opening: bool | None
    is_closing: bool | None
    is_closed: bool
    supported_features: int
    device_class: str | None
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None


class SensorDevice(NamedTuple):
    available: bool
    name: str
    unique_id: str
    state: Any
    unit_of_measurement: str
    device_class: str
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None
