"""Device-family parser entry points for Salus iT600 gateway payloads."""

from .advanced_settings import parse_advanced_settings
from .binary_sensor import (
    parse_binary_diagnostic_devices,
    parse_binary_sensor_device,
)
from .climate import (
    parse_climate_binary_sensor_devices,
    parse_climate_device,
    parse_climate_sensor_devices,
)
from .common import PARSING_EXCEPTIONS
from .cover import parse_cover_device
from .sensor import parse_meter_sensor_devices, parse_sensor_device, parse_sensor_devices
from .switch import parse_switch_device, parse_switch_sensor_devices

__all__ = [
    "PARSING_EXCEPTIONS",
    "parse_advanced_settings",
    "parse_binary_diagnostic_devices",
    "parse_binary_sensor_device",
    "parse_climate_binary_sensor_devices",
    "parse_climate_device",
    "parse_climate_sensor_devices",
    "parse_cover_device",
    "parse_meter_sensor_devices",
    "parse_sensor_device",
    "parse_sensor_devices",
    "parse_switch_device",
    "parse_switch_sensor_devices",
]
