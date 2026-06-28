"""Salus iT600 smart device models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, NamedTuple

from .const import HVAC_MODE_COOL, HVAC_MODE_HEAT, HoldType, RunningState, SystemMode

DeviceData = dict[str, Any]
ClimateModeList = tuple[str, ...]
CoolingCapabilitySource = Literal[
    "cooling_control",
    "active_system_mode",
    "active_running_state",
    "known_model",
    "none",
]

CLIMATE_DIAGNOSTIC_FIELD_NAMES = frozenset(
    {
        "UniID",
        "DeviceName",
        "ModelIdentifier_i",
        "FirmwareVersion",
        "LocalTemperature_x100",
        "MeasuredValue_x100",
        "HeatingSetpoint_x100",
        "CoolingSetpoint_x100",
        "MinHeatSetpoint_x100",
        "MaxHeatSetpoint_x100",
        "MinCoolSetpoint_x100",
        "MaxCoolSetpoint_x100",
        "SunnySetpoint_x100",
        "SystemMode",
        "RunningState",
        "HoldType",
        "LockKey",
        "LockKey_a",
        "HeatingControl",
        "CoolingControl",
        "OnlineStatus_i",
    }
)


def _int_value(value: Any) -> int | None:
    """Return an integer payload value, rejecting bools and non-integers."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _has_int_value(value: Any) -> bool:
    """Return whether a payload field is present as an integer value."""
    return _int_value(value) is not None


def normalized_hold_type(
    value: Any,
    *,
    default: int | None = int(HoldType.PERMANENT_HOLD),
) -> int | None:
    """Return a hold type, using the documented fallback for missing values."""
    hold_type = _int_value(value)
    return hold_type if hold_type is not None else default


def normalized_system_mode(value: Any) -> int | None:
    """Return a system mode, or None when the payload does not prove one."""
    return _int_value(value)


def normalized_running_state(
    value: Any,
    *,
    default: int | None = int(RunningState.IDLE),
) -> int | None:
    """Return a running state, using the documented idle/unknown fallback."""
    running_state = _int_value(value)
    return running_state if running_state is not None else default


def running_state_is_heating(value: Any) -> bool:
    """Return whether the running-state heating bit is set."""
    running_state = normalized_running_state(value, default=None)
    return running_state is not None and running_state >= 0 and bool(
        running_state & int(RunningState.HEATING)
    )


def running_state_is_cooling(value: Any) -> bool:
    """Return whether the running-state cooling bit is set."""
    running_state = normalized_running_state(value, default=None)
    return running_state is not None and running_state >= 0 and bool(
        running_state & int(RunningState.COOLING)
    )


def normalized_temperature_value(
    value: Any,
    *,
    default: float | None = None,
) -> float | None:
    """Return a Celsius value, rejecting bools and non-numeric payloads."""
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def normalized_temperature_range(
    min_value: Any,
    max_value: Any,
    *,
    default_min: float | None = None,
    default_max: float | None = None,
) -> tuple[float | None, float | None]:
    """Return normalized min/max temperatures with explicit fallbacks."""
    return (
        normalized_temperature_value(min_value, default=default_min),
        normalized_temperature_value(max_value, default=default_max),
    )


def active_climate_system_mode(
    *,
    system_mode: Any,
    hvac_mode: Any = None,
    running_state: Any = None,
) -> int | None:
    """Return the heat/cool system mode implied by normalized climate state."""
    normalized_mode = normalized_system_mode(system_mode)
    if (
        normalized_mode == int(SystemMode.COOL)
        or hvac_mode == HVAC_MODE_COOL
        or running_state_is_cooling(running_state)
    ):
        return int(SystemMode.COOL)
    if (
        normalized_mode in {int(SystemMode.HEAT), int(SystemMode.EMERGENCY_HEAT)}
        or hvac_mode == HVAC_MODE_HEAT
        or running_state_is_heating(running_state)
    ):
        return int(SystemMode.HEAT)
    return normalized_mode


def active_climate_setpoint(
    *,
    system_mode: Any,
    heating_setpoint: float | None,
    cooling_setpoint: float | None,
    hvac_mode: Any = None,
    running_state: Any = None,
) -> float | None:
    """Return the active heat/cool setpoint for a normalized climate state."""
    if (
        active_climate_system_mode(
            system_mode=system_mode,
            hvac_mode=hvac_mode,
            running_state=running_state,
        )
        == int(SystemMode.COOL)
    ):
        return cooling_setpoint if cooling_setpoint is not None else heating_setpoint
    return heating_setpoint if heating_setpoint is not None else cooling_setpoint


def active_temperature_range(
    *,
    system_mode: Any,
    min_heat_temp: float | None,
    max_heat_temp: float | None,
    min_cool_temp: float | None,
    max_cool_temp: float | None,
    hvac_mode: Any = None,
    running_state: Any = None,
) -> tuple[float | None, float | None]:
    """Return the active heat/cool temperature range."""
    if (
        active_climate_system_mode(
            system_mode=system_mode,
            hvac_mode=hvac_mode,
            running_state=running_state,
        )
        == int(SystemMode.COOL)
    ):
        return (
            min_cool_temp if min_cool_temp is not None else min_heat_temp,
            max_cool_temp if max_cool_temp is not None else max_heat_temp,
        )
    return (
        min_heat_temp if min_heat_temp is not None else min_cool_temp,
        max_heat_temp if max_heat_temp is not None else max_cool_temp,
    )


def sq610_cooling_capability_source(
    *,
    cooling_control: Any = None,
    system_mode: Any = None,
    running_state: Any = None,
    known_model_supports_cooling: bool = False,
) -> CoolingCapabilitySource:
    """Return the observed source proving SQ610 cooling support."""
    if _has_int_value(cooling_control):
        return "cooling_control"
    if normalized_system_mode(system_mode) == int(SystemMode.COOL):
        return "active_system_mode"
    if running_state_is_cooling(running_state):
        return "active_running_state"
    if known_model_supports_cooling:
        return "known_model"
    return "none"


def sq610_supports_cooling(
    *,
    cooling_control: Any = None,
    system_mode: Any = None,
    running_state: Any = None,
    known_model_supports_cooling: bool = False,
) -> bool:
    """Return whether a reliable signal proves SQ610 cooling support."""
    return (
        sq610_cooling_capability_source(
            cooling_control=cooling_control,
            system_mode=system_mode,
            running_state=running_state,
            known_model_supports_cooling=known_model_supports_cooling,
        )
        != "none"
    )


def climate_diagnostic_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Return whitelisted climate support fields for diagnostics."""
    return {
        key: value
        for key, value in payload.items()
        if key in CLIMATE_DIAGNOSTIC_FIELD_NAMES
    }


class GatewayDevice(NamedTuple):
    name: str
    unique_id: str
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ClimateDevice:
    """Normalized climate device state.

    Common convenience fields stay alongside richer normalized fields. Mode
    collections are stored as tuples so a frozen device snapshot is not
    accidentally mutated by consumers.
    """

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
    hvac_modes: ClimateModeList
    preset_mode: str
    preset_modes: ClimateModeList
    fan_mode: str | None
    fan_modes: ClimateModeList | None
    locked: bool | None
    supported_features: int
    device_class: str
    data: DeviceData
    manufacturer: str
    model: str | None
    sw_version: str | None
    extra_state_attributes: dict[str, Any] | None = None
    hold_type: int | None = None
    system_mode: int | None = None
    running_state: int | None = None
    heating_setpoint: float | None = None
    cooling_setpoint: float | None = None
    min_heat_temp: float | None = None
    max_heat_temp: float | None = None
    min_cool_temp: float | None = None
    max_cool_temp: float | None = None
    heating_control: int | None = None
    cooling_control: int | None = None
    supports_cooling: bool = False
    supports_fan: bool = False
    supports_heat: bool = True
    online_status: int | None = None
    cooling_capability_source: CoolingCapabilitySource = "none"
    diagnostic_fields: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Normalize mutable constructor inputs for a frozen snapshot."""
        object.__setattr__(self, "hvac_modes", tuple(self.hvac_modes))
        object.__setattr__(self, "preset_modes", tuple(self.preset_modes))
        object.__setattr__(
            self,
            "fan_modes",
            None if self.fan_modes is None else tuple(self.fan_modes),
        )
        object.__setattr__(self, "data", dict(self.data))
        if self.extra_state_attributes is not None:
            object.__setattr__(
                self,
                "extra_state_attributes",
                dict(self.extra_state_attributes),
            )
        if self.diagnostic_fields is not None:
            object.__setattr__(
                self,
                "diagnostic_fields",
                dict(self.diagnostic_fields),
            )


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
    parent_unique_id: str | None = None
    entity_category: str | None = None
    extra_state_attributes: dict[str, Any] | None = None


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
    parent_unique_id: str | None = None
    entity_category: str | None = None
