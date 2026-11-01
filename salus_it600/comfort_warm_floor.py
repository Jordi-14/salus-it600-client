"""Conservative SQ610 Comfort Warm Floor command encoder.

Only the SQ610RFNH/00000054 profile is enabled. Hardware captures confirm that
counter metadata is copied unchanged and the device updates its own read-back.
"""

from __future__ import annotations

import re
from typing import Any

from .exceptions import IT600ValidationError

_PROFILE = ("SQ610RFNH", "00000054")
_HEX_SETTINGS = re.compile(r"72[0-9a-fA-F]{152}\Z")
# Observed on two online devices after app-side changes. This is a different
# command family, not a B11 settings acknowledgement. Its meaning is not assumed.
NON_SETTINGS_RESPONSE = "4233344c"
COMFORT_PENDING_SECONDS = 120.0


_DEVICE_METADATA = frozenset((1, 40, 41))


def comfort_command_response(status: dict[str, Any]) -> str:
    """Return a normalized shared command response, including missing sections."""
    section = status.get("sIT600I")
    return str(section.get("CommandResponse_d", "")).lower() if isinstance(section, dict) else ""


def validated_comfort_settings(
    status: dict[str, Any], *, check_command: bool = True,
) -> bytes:
    """Validate the complete read snapshot before allowing any encoding."""
    sections = ("data", "DeviceL", "sZDO", "sIT600TH")
    for section in (*sections, "sIT600I") if check_command else sections:
        if not isinstance(status.get(section), dict):
            raise IT600ValidationError("Incomplete SQ610 settings response")
    if status["data"].get("Endpoint") != 9 or status["data"].get("DeviceType") != 100:
        raise IT600ValidationError("Unverified SQ610 endpoint or device type")
    model = status.get("DeviceL", {}).get("ModelIdentifier_i")
    firmware = status.get("sZDO", {}).get("FirmwareVersion")
    if (model, firmware) != _PROFILE:
        raise IT600ValidationError("Comfort Warm Floor writes are not verified for this model/firmware")
    th = status.get("sIT600TH", {})
    schedule = th.get("Schedule")
    if not isinstance(schedule, str) or not _HEX_SETTINGS.fullmatch(schedule):
        raise IT600ValidationError("Unrecognized SQ610 advanced-settings layout")
    alias = th.get("Status_2_d")
    if not isinstance(alias, str) or not _HEX_SETTINGS.fullmatch(alias) or alias.lower() != schedule.lower():
        raise IT600ValidationError("SQ610 advanced-settings aliases do not agree")
    base = bytes.fromhex(schedule)
    if base[48:] != b"\xff" * 27 + b"\x00\x00":
        raise IT600ValidationError("Unverified schedule/holiday tail; use the Salus app")
    trv = th.get("PairedTRVShortID")
    if not isinstance(trv, str) or not re.fullmatch(r"F{24}", trv, re.IGNORECASE):
        raise IT600ValidationError("Comfort Warm Floor requires a verified non-TRV installation")
    wiring_centre = th.get("PairedWCNumber")
    if type(wiring_centre) is not int or wiring_centre < 1:
        raise IT600ValidationError("Comfort Warm Floor requires an underfloor wiring centre")
    if th.get("SystemMode") != 4:
        raise IT600ValidationError("Comfort Warm Floor is only verified in heating mode")
    if base[39] not in range(4) or base[43] != 0:
        raise IT600ValidationError("Unsupported comfort level or PIN-protected settings")
    # Bytes 1,40,41 belong to the device. Never calculate, increment or reset
    # them, including at 255. Keep the separate PIN-required flag guarded above.
    if not check_command:
        return base
    recorded = status.get("sIT600I", {}).get("CommandResponse_d")
    if isinstance(recorded, str) and recorded.lower() == NON_SETTINGS_RESPONSE:
        return base
    if not isinstance(recorded, str) or not re.fullmatch(r"42313173[0-9a-fA-F]{118}00", recorded, re.IGNORECASE):
        raise IT600ValidationError("Settings command is pending or its recorded layout is unverified")
    response_bytes = bytes.fromhex(recorded)
    # A same-counter echo with a different requested setting is in flight.
    # Different counter values cannot be ordered: the hardware increments its
    # read counter independently, and it may wrap. Pending local writes are
    # additionally tracked and checked against complete settings in the gateway.
    if response_bytes[4] == base[1] and response_bytes[4:63] != base[1:60]:
        raise IT600ValidationError("Settings command is pending or its recorded layout is unverified")
    return base


def supports_comfort_warm_floor_write(status: dict[str, Any]) -> bool:
    """Return whether this snapshot satisfies the verified write profile."""
    try:
        validated_comfort_settings(status)
    except (IT600ValidationError, AttributeError, TypeError, ValueError):
        return False
    return True


def supports_comfort_warm_floor_profile(status: dict[str, Any]) -> bool:
    """Keep a supported readable entity available during an external command.

    Command echoes describe write readiness, not whether the last reported
    setting can be displayed. The setter still validates the echo freshly.
    Model, firmware, settings layout and the PIN-required flag remain guarded.
    """
    try:
        validated_comfort_settings(status, check_command=False)
    except (IT600ValidationError, AttributeError, TypeError, ValueError):
        return False
    return True


def build_comfort_warm_floor_command(
    status: dict[str, Any], level: int, *, check_command: bool = True,
) -> str | None:
    """Encode one level change, preserving every other settings byte.

    Return None when the requested level is already reported. Never invent a
    footer, retransmit the read blob, or include the response's trailing status.
    """
    if isinstance(level, bool) or not isinstance(level, int):
        raise TypeError("comfort warm floor level must be an integer")
    if level not in range(4):
        raise IT600ValidationError("comfort warm floor level must be 0, 1, 2 or 3")
    base = validated_comfort_settings(status, check_command=check_command)
    if base[39] == level:
        return None
    body = bytearray(base[:60])
    body[0] = 0x73
    body[39] = level
    return "423131" + body.hex()



def comfort_command_matches(status: dict[str, Any], command: str) -> bool:
    """Match the fields B11 controls, ignoring live HVAC fields and shared echo.

    The caller checks fresh identity/online status. Device-owned metadata and
    the read/write marker differ legitimately. B11 writes the first 60 bytes;
    runtime setpoints, hold mode and weekly schedules are not part of that body.
    """
    current = validated_comfort_settings(status, check_command=False)
    try:
        frame = bytes.fromhex(command)
    except (TypeError, ValueError):
        return False
    if len(frame) != 63 or frame[:4] != bytes.fromhex("42313173"):
        return False
    body = frame[3:]
    return all(current[i] == body[i] for i in range(60) if i not in _DEVICE_METADATA and i != 0)
