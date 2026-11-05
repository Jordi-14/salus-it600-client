"""Device-family parser entry points for Salus iT600 gateway payloads."""

from .advanced_settings import parse_advanced_settings
from .binary_sensor import (
    parse_binary_diagnostic_devices,
    parse_binary_relay_sensor_devices,
    parse_binary_sensor_device,
)
from .climate import (
    parse_climate_binary_sensor_devices,
    parse_climate_device,
    parse_climate_sensor_devices,
)
from .common import PARSING_EXCEPTIONS, device_short_id
from .cover import parse_cover_device
from .mini_trv import MiniTrvReport, decode_mini_trv_report
from .sensor import (
    parse_meter_sensor_devices,
    parse_sensor_device,
    parse_sensor_devices,
)
from .switch import parse_switch_device, parse_switch_sensor_devices
from .wiring_centre import (
    parse_wiring_centre_binary_sensor_devices,
    parse_wiring_centre_device,
    parse_wiring_centre_sensor_devices,
)

__all__ = [
    "PARSING_EXCEPTIONS",
    "MiniTrvReport",
    "decode_mini_trv_report",
    "device_short_id",
    "parse_advanced_settings",
    "parse_binary_diagnostic_devices",
    "parse_binary_relay_sensor_devices",
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
    "parse_wiring_centre_binary_sensor_devices",
    "parse_wiring_centre_device",
    "parse_wiring_centre_sensor_devices",
]
