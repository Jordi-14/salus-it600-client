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
PRESET_TEMPORARY_HOLD = "Temporary Hold"
PRESET_ECO = "Eco"
PRESET_OFF = "Off"

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
