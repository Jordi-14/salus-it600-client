"""Conservative SQ610 Comfort Warm Floor command encoder.

Only the SQ610RFNH/00000054 profile and save counters captured in hardware
are enabled. This is not a general advanced-settings or PIN encoder.
"""

from __future__ import annotations

import re
from typing import Any

from .exceptions import IT600ValidationError

_PROFILE = ("SQ610RFNH", "00000054")
_HEX_SETTINGS = re.compile(r"72[0-9a-fA-F]{152}\Z")


def _counter_bytes(counter: int) -> bytes:
    """Return the counter-dependent pair observed with this profile."""
    if counter == 0:
        return b"\xff\xff"
    return bytes(((2 * counter - 1) & 0xFF, 255 - (counter >> 2)))


def _validated_settings(status: dict[str, Any]) -> bytes:
    """Validate the complete read snapshot before allowing any encoding."""
    for section in ("data", "DeviceL", "sZDO", "sIT600TH", "sIT600I"):
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
    if th.get("Status_2_d") != schedule:
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
    # Captures cover counters 0..9. Do not extrapolate beyond those captures.
    if base[1] > 8 or base[40:42] != _counter_bytes(base[1]):
        raise IT600ValidationError("Unverified save counter or PIN encoding; use the Salus app")
    recorded = status.get("sIT600I", {}).get("CommandResponse_d")
    expected = "42313173" + base[1:60].hex() + "00"
    if not isinstance(recorded, str) or recorded.lower() != expected:
        raise IT600ValidationError("Settings command is pending or its recorded layout is unverified")
    return base


def supports_comfort_warm_floor_write(status: dict[str, Any]) -> bool:
    """Return whether this snapshot satisfies the verified write profile."""
    try:
        _validated_settings(status)
    except (IT600ValidationError, AttributeError, TypeError, ValueError):
        return False
    return True


def build_comfort_warm_floor_command(status: dict[str, Any], level: int) -> str | None:
    """Encode one level change, preserving every other settings byte.

    Return None when the requested level is already reported. Never invent a
    footer, retransmit the read blob, or include the response's trailing status.
    """
    if isinstance(level, bool) or not isinstance(level, int):
        raise TypeError("comfort warm floor level must be an integer")
    if level not in range(4):
        raise IT600ValidationError("comfort warm floor level must be 0, 1, 2 or 3")
    base = _validated_settings(status)
    if base[39] == level:
        return None
    body = bytearray(base[:60])
    body[0] = 0x73
    body[1] += 1
    body[39] = level
    body[40:42] = _counter_bytes(body[1])
    return "423131" + body.hex()
