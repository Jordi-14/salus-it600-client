"""Binary sensor parsers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..const import MINI_TRV_ERROR_CODES, TEMP_CELSIUS
from ..device_models import (
    BINARY_RELAY_MODELS,
    MODEL_MINI_TRV,
    SKIPPED_BINARY_SENSOR_MODELS,
    binary_sensor_device_class,
    model_identifier,
)
from ..models import BinarySensorDevice, ClimateDevice, SensorDevice
from .common import (
    _child_binary_sensor_device,
    _child_sensor_device,
    _common_device_args,
    _device_name,
    _signal_sensor_devices,
)
from .mini_trv import decode_mini_trv_report

# ZigBee short addresses that mean "not paired" rather than a real partner:
# 0x0000 is the coordinator (the gateway itself) and 0xFFFF is unassigned.
_UNPAIRED_SHORT_IDS = frozenset({0x0000, 0xFFFF})


def parse_binary_sensor_device(
    device_status: dict[str, Any],
    paired_thermostats: Mapping[int, ClimateDevice] | None = None,
) -> BinarySensorDevice | None:
    """Parse one binary sensor device from gateway payload.

    `paired_thermostats` maps climate devices by ZigBee short address. When
    given, an it600MINITRV's heat sensor names the thermostat that drives it
    in its attributes.
    """
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

    extra_state_attributes = None
    mini_trv_mode = None
    if model == MODEL_MINI_TRV:
        extra_state_attributes = _paired_thermostat_attributes(
            device_status,
            paired_thermostats or {},
        )
        mini_trv_mode = _mini_trv_mode(device_status)

    return BinarySensorDevice(
        **_common_device_args(device_status, unique_id),
        is_on=is_on == 1,
        device_class=binary_sensor_device_class(model),
        extra_state_attributes=extra_state_attributes,
        mini_trv_mode=mini_trv_mode,
    )


def _mini_trv_mode(device_status: dict[str, Any]) -> int | None:
    """Return the it600MINITRV's reported `sIT600I.Mode`, if any."""
    sit600i = device_status.get("sIT600I")
    if not isinstance(sit600i, dict):
        return None
    mode = sit600i.get("Mode")
    if isinstance(mode, bool) or not isinstance(mode, int):
        return None
    return mode


def _paired_thermostat_attributes(
    device_status: dict[str, Any],
    paired_thermostats: Mapping[int, ClimateDevice],
) -> dict[str, Any] | None:
    """Describe the thermostat an it600MINITRV is paired to."""
    sit600i = device_status.get("sIT600I")
    if not isinstance(sit600i, dict):
        return None

    short_id = sit600i.get("PairedThermostatShortID")
    if (
        isinstance(short_id, bool)
        or not isinstance(short_id, int)
        or short_id in _UNPAIRED_SHORT_IDS
    ):
        return None

    attributes: dict[str, Any] = {"paired_thermostat_short_id": short_id}
    thermostat = paired_thermostats.get(short_id)
    if thermostat is not None:
        attributes["paired_thermostat_id"] = thermostat.unique_id
        attributes["paired_thermostat_name"] = thermostat.name
    return attributes


def parse_binary_diagnostic_devices(
    device_status: dict[str, Any],
) -> list[BinarySensorDevice]:
    """Parse diagnostic child binary sensors from a binary-sensor payload."""
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return []

    model = model_identifier(device_status)
    parent_name = _device_name(device_status, unique_id)
    diagnostics: list[BinarySensorDevice] = []

    low_battery = device_status.get("sIASZS", {}).get("ErrorIASZSLowBattery")
    if low_battery is None:
        low_battery = device_status.get("sPowerS", {}).get("ErrorPowerSLowBattery")
    if low_battery is None and model in BINARY_RELAY_MODELS:
        low_battery = device_status.get("sIT600I", {}).get("TRVError22")

    if low_battery is not None:
        diagnostics.append(
            _child_binary_sensor_device(
                device_status,
                f"{unique_id}_low_battery",
                f"{parent_name} Low battery",
                is_on=low_battery == 1,
                device_class="battery",
                parent_unique_id=unique_id,
                entity_category="diagnostic",
            )
        )

    if model == MODEL_MINI_TRV:
        problem = _mini_trv_problem_device(device_status, unique_id, parent_name)
        if problem is not None:
            diagnostics.append(problem)

    return diagnostics


def _mini_trv_problem_device(
    device_status: dict[str, Any],
    unique_id: str,
    parent_name: str,
) -> BinarySensorDevice | None:
    """Aggregate the it600MINITRV `TRVErrorNN` fault flags into one sensor.

    Returns None when the payload reports none of the flags, so a device that
    does not expose them gets no problem sensor instead of a permanent "OK".
    """
    sit600i = device_status.get("sIT600I")
    if not isinstance(sit600i, dict):
        return None
    if not any(error_key in sit600i for error_key in MINI_TRV_ERROR_CODES):
        return None

    active_errors = [
        description
        for error_key, description in MINI_TRV_ERROR_CODES.items()
        if sit600i.get(error_key) == 1
    ]

    return _child_binary_sensor_device(
        device_status,
        f"{unique_id}_problem",
        f"{parent_name} Problem",
        is_on=bool(active_errors),
        device_class="problem",
        parent_unique_id=unique_id,
        entity_category="diagnostic",
        extra_state_attributes={"errors": active_errors},
    )


def parse_binary_relay_sensor_devices(
    device_status: dict[str, Any],
    previous_sensors: Mapping[str, SensorDevice] | None = None,
) -> list[SensorDevice]:
    """Parse child sensors of a relay-type binary sensor (MiniTRV, receiver).

    Returns the RSSI/LQI diagnostic sensors from `sIT600I` and, for an
    it600MINITRV, the TRV's own temperature decoded from
    `sIT600I.CommandResponse_d`.

    `previous_sensors` is the caller's sensor collection from the previous
    poll. Like the signal readings, the TRV temperature is carried forward when
    a poll omits `CommandResponse_d` or it does not decode, so the sensor does
    not flap to unavailable; availability still follows the parent device.
    """
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return []

    model = model_identifier(device_status)
    if model not in BINARY_RELAY_MODELS:
        return []

    parent_name = _device_name(device_status, unique_id)
    sensors: list[SensorDevice] = []

    if model == MODEL_MINI_TRV:
        temperature = _mini_trv_temperature_device(
            device_status, unique_id, parent_name, previous_sensors or {}
        )
        if temperature is not None:
            sensors.append(temperature)

    sensors.extend(
        _signal_sensor_devices(device_status, unique_id, parent_name, previous_sensors)
    )
    return sensors


def _mini_trv_temperature_device(
    device_status: dict[str, Any],
    unique_id: str,
    parent_name: str,
    previous_sensors: Mapping[str, SensorDevice],
) -> SensorDevice | None:
    """Return the it600MINITRV's own temperature reading, if known."""
    sensor_id = f"{unique_id}_temperature"
    sit600i = device_status.get("sIT600I")
    payload = sit600i if isinstance(sit600i, dict) else {}

    report = decode_mini_trv_report(payload.get("CommandResponse_d"))
    if report is not None:
        state: Any = report.trv_temperature
    else:
        previous = previous_sensors.get(sensor_id)
        if previous is None:
            return None
        state = previous.state

    return _child_sensor_device(
        device_status,
        sensor_id,
        f"{parent_name} Temperature",
        state=state,
        unit_of_measurement=TEMP_CELSIUS,
        device_class="temperature",
        parent_unique_id=unique_id,
    )
