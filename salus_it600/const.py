"""Constants for the Salus iT600 smart devices."""

from enum import IntEnum

# Degree units
DEGREE = "°"

# Temperature units
TEMP_CELSIUS = f"{DEGREE}C"
TEMPERATURE_SCALE = 100

# Cover positions
COVER_POSITION_MIN = 0
COVER_POSITION_MAX = 100

# States
STATE_UNKNOWN = "unknown"

# Supported climate features
SUPPORT_TARGET_TEMPERATURE = 1
SUPPORT_FAN_MODE = 8
SUPPORT_PRESET_MODE = 16

# Supported cover features
SUPPORT_OPEN = 1
SUPPORT_CLOSE = 2
SUPPORT_SET_POSITION = 4

# HVAC modes
HVAC_MODE_OFF = "off"
HVAC_MODE_HEAT = "heat"
HVAC_MODE_COOL = "cool"
HVAC_MODE_AUTO = "auto"

# HVAC states
CURRENT_HVAC_OFF = "off"
CURRENT_HVAC_HEAT = "heating"
CURRENT_HVAC_HEAT_IDLE = "heating (idling)"
CURRENT_HVAC_COOL = "cooling"
CURRENT_HVAC_COOL_IDLE = "cooling (idling)"
CURRENT_HVAC_IDLE = "idle"

# Supported presets
PRESET_FOLLOW_SCHEDULE = "Follow Schedule"
PRESET_PERMANENT_HOLD = "Permanent Hold"
PRESET_SCHEDULE_OVERRIDE = "Schedule Override"
PRESET_ECO = "Eco"
PRESET_OFF = "Off"
PRESET_AWAY = "Away"

# Supported fan modes
FAN_MODE_AUTO = "Auto"
FAN_MODE_HIGH = "High"
FAN_MODE_MEDIUM = "Medium"
FAN_MODE_LOW = "Low"
FAN_MODE_OFF = "Off"


class HoldType(IntEnum):
    """Gateway hold/preset values."""

    FOLLOW_SCHEDULE = 0
    TEMPORARY_HOLD = 1
    PERMANENT_HOLD = 2
    AWAY = 6
    STANDBY = 7
    ECO = 10


class SystemMode(IntEnum):
    """Gateway HVAC system mode values."""

    AUTO = 1
    COOL = 3
    HEAT = 4
    EMERGENCY_HEAT = 5


class RunningState(IntEnum):
    """Gateway HVAC running-state values seen across supported devices."""

    IDLE = 0
    HEATING = 1
    COOLING = 2
    FAN_COIL_HEATING = 33
    FAN_COIL_COOLING = 66


class FanMode(IntEnum):
    """Gateway fan-speed values."""

    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    AUTO = 5


BATTERY_LEVEL_MAP: dict[int, int] = {
    0: 0,
    1: 10,
    2: 25,
    3: 50,
    4: 75,
    5: 100,
}

BATTERY_VOLTAGE_THRESHOLDS: dict[str, list[tuple[float, int, str]]] = {
    "window": [
        (2.6, 100, "full"),
        (2.3, 50, "half"),
        (2.1, 25, "low"),
        (0.0, 0, "critical"),
    ],
    "door": [
        (2.9, 100, "full"),
        (2.8, 50, "half"),
        (2.2, 25, "low"),
        (0.0, 0, "critical"),
    ],
    "energy_meter": [
        (5.2, 100, "full"),
        (4.6, 50, "half"),
        (4.2, 25, "low"),
        (0.0, 0, "critical"),
    ],
    "trv": [
        (2.7, 100, "full"),
        (2.4, 50, "half"),
        (2.2, 25, "low"),
        (0.0, 0, "critical"),
    ],
}


# Shared vendor Error01..Error32 fault-register bank. Thermostats (`sIT600TH`)
# report a subset of this table directly; the it600WC wiring centre
# (`sIT600WC`) reports the rest of it (Error10-20, Error26-29) -- the two
# device-side numbering ranges never overlap. Error06/Error24 already show
# thermostats referencing "Wiring Center" faults from their own side of the
# link, so this is one shared register table read from two device types
# rather than two coincidentally-similar ones.
#
# The it600WC's own range (Error10-20, Error26-29) has no documented meaning
# anywhere the client has found, unlike the thermostat-side codes below, so
# those entries intentionally say only that -- the parser must not guess at
# specific fault descriptions for a device that is a hydronic system's single
# point of failure.
THERMOSTAT_ERROR_CODES: dict[str, str] = {
    "Error01": "Paired TRV hardware issue",
    "Error02": "Floor sensor overheating",
    "Error03": "Floor sensor open",
    "Error04": "Floor sensor short",
    "Error05": "Lost link with ZigBee Coordinator",
    "Error06": "Lost link with Wiring Center KL08RF",
    "Error07": "Lost link with TRV",
    "Error08": "Lost link with RX10RF (RX1)",
    "Error09": "Lost link with RX10RF (RX2)",
    "Error10": "Undocumented wiring centre fault (Error10)",
    "Error11": "Undocumented wiring centre fault (Error11)",
    "Error12": "Undocumented wiring centre fault (Error12)",
    "Error13": "Undocumented wiring centre fault (Error13)",
    "Error14": "Undocumented wiring centre fault (Error14)",
    "Error15": "Undocumented wiring centre fault (Error15)",
    "Error16": "Undocumented wiring centre fault (Error16)",
    "Error17": "Undocumented wiring centre fault (Error17)",
    "Error18": "Undocumented wiring centre fault (Error18)",
    "Error19": "Undocumented wiring centre fault (Error19)",
    "Error20": "Undocumented wiring centre fault (Error20)",
    "Error21": "Paired TRV lost link with Coordinator",
    "Error22": "Paired TRV low battery",
    "Error23": "Message from unpaired TRV",
    "Error24": "Rejected by Wiring Centre",
    "Error25": "Lost link with Parent",
    "Error26": "Undocumented wiring centre fault (Error26)",
    "Error27": "Undocumented wiring centre fault (Error27)",
    "Error28": "Undocumented wiring centre fault (Error28)",
    "Error29": "Undocumented wiring centre fault (Error29)",
    "Error30": "Paired TRV gear issue",
    "Error31": "Paired TRV adaptation issue",
    "Error32": "Low battery",
}

BATTERY_ERROR_CODES: frozenset[str] = frozenset({"Error22", "Error32"})
