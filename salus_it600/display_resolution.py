"""Conservative SQ610 display resolution encoder.

Display resolution is how the thermostat reports and shows temperatures:
0.5 °C or 0.1 °C steps. It lives at byte 11 of the advanced-settings body, and
the device has no separate command for it: a write sends the complete B11
settings body back with that byte changed.

Only the SQ610RFNH/00000054 profile is enabled. Hardware captures confirm that
device metadata is copied unchanged and the device updates its own read-back.
"""

from __future__ import annotations

import re
from typing import Any

from .const import DISPLAY_RESOLUTION_DEGREES
from .exceptions import IT600ValidationError

_PROFILE = ("SQ610RFNH", "00000054")
_HEX_SETTINGS = re.compile(r"72[0-9a-fA-F]{152}\Z")
# A different command family recorded after app-side changes. It is not a B11
# settings acknowledgement, and its meaning is not assumed.
_NON_SETTINGS_RESPONSE = "4233344c"
DISPLAY_RESOLUTION_PENDING_SECONDS = 120.0

_DISPLAY_RESOLUTION_BYTE = 11
_PIN_REQUIRED_BYTE = 43


def is_non_settings_response(response: str) -> bool:
    """Return whether a normalized recorded command is the non-settings family."""
    return response == _NON_SETTINGS_RESPONSE


def settings_command_response(status: dict[str, Any]) -> str:
    """Return the normalized recorded command, including missing sections."""
    section = status.get("sIT600I")
    return str(section.get("CommandResponse_d", "")).lower() if isinstance(section, dict) else ""


def validated_display_settings(
    status: dict[str, Any], *, check_command: bool = True,
) -> bytes:
    """Validate the complete read snapshot before allowing any encoding."""
    sections = ("data", "DeviceL", "sZDO", "sIT600TH")
    for section in (*sections, "sIT600I") if check_command else sections:
        if not isinstance(status.get(section), dict):
            raise IT600ValidationError("Incomplete SQ610 settings response")
    if status["data"].get("Endpoint") != 9 or status["data"].get("DeviceType") != 100:
        raise IT600ValidationError("Unverified SQ610 endpoint or device type")
    model = status["DeviceL"].get("ModelIdentifier_i")
    firmware = status["sZDO"].get("FirmwareVersion")
    if (model, firmware) != _PROFILE:
        raise IT600ValidationError("Display resolution writes are not verified for this model/firmware")
    th = status["sIT600TH"]
    schedule = th.get("Schedule")
    if not isinstance(schedule, str) or not _HEX_SETTINGS.fullmatch(schedule):
        raise IT600ValidationError("Unrecognized SQ610 advanced-settings layout")
    alias = th.get("Status_2_d")
    if not isinstance(alias, str) or not _HEX_SETTINGS.fullmatch(alias) or alias.lower() != schedule.lower():
        raise IT600ValidationError("SQ610 advanced-settings aliases do not agree")
    base = bytes.fromhex(schedule)
    if base[48:] != b"\xff" * 27 + b"\x00\x00":
        raise IT600ValidationError("Unverified schedule/holiday tail; use the Salus app")
    if base[_DISPLAY_RESOLUTION_BYTE] not in DISPLAY_RESOLUTION_DEGREES:
        raise IT600ValidationError("Unsupported display resolution in settings")
    # Bytes 1,40,41 belong to the device. Never calculate, increment or reset
    # them, including at 255.
    if check_command:
        _check_recorded_command(status, base)
    return base


def _check_recorded_command(status: dict[str, Any], base: bytes) -> None:
    """Reject a recorded B11 echo that shows a settings command in flight."""
    recorded = status["sIT600I"].get("CommandResponse_d")
    if isinstance(recorded, str) and recorded.lower() == _NON_SETTINGS_RESPONSE:
        return
    if not isinstance(recorded, str) or not re.fullmatch(r"42313173[0-9a-fA-F]{118}00", recorded, re.IGNORECASE):
        raise IT600ValidationError("Settings command is pending or its recorded layout is unverified")
    response_bytes = bytes.fromhex(recorded)
    # A same-counter echo with a different requested body is in flight.
    # Different counter values cannot be ordered: the device increments its
    # read counter independently, and it may wrap.
    if response_bytes[4] == base[1] and response_bytes[4:63] != base[1:60]:
        raise IT600ValidationError("Settings command is pending or its recorded layout is unverified")


def supports_display_resolution(status: dict[str, Any]) -> bool:
    """Return whether the reported resolution comes from a verified settings layout.

    PIN protection and command echoes describe write readiness, not support.
    The setter checks both freshly.
    """
    try:
        validated_display_settings(status, check_command=False)
    except (IT600ValidationError, AttributeError, TypeError, ValueError):
        return False
    return True


def build_display_resolution_command(
    status: dict[str, Any], resolution: int, *, check_command: bool = True,
) -> str | None:
    """Encode one resolution change, preserving every other settings byte.

    Codes follow `DISPLAY_RESOLUTION_DEGREES`: 0 is 0.5 °C, 1 is 0.1 °C.
    Return None when the requested resolution is already reported.
    """
    if isinstance(resolution, bool) or not isinstance(resolution, int):
        raise TypeError("display resolution must be an integer")
    if resolution not in DISPLAY_RESOLUTION_DEGREES:
        raise IT600ValidationError("display resolution must be 0 or 1")
    base = validated_display_settings(status, check_command=check_command)
    if base[_PIN_REQUIRED_BYTE] != 0:
        raise IT600ValidationError("PIN-protected settings")
    if base[_DISPLAY_RESOLUTION_BYTE] == resolution:
        return None
    body = bytearray(base[:60])
    body[0] = 0x73
    body[_DISPLAY_RESOLUTION_BYTE] = resolution
    return "423131" + body.hex()


def display_resolution_applied(status: dict[str, Any], command: str) -> bool:
    """Return whether the device reports the resolution a command requested.

    Other settings bytes may change independently, for example from the Salus
    app, so only byte 11 is compared.
    """
    current = validated_display_settings(status, check_command=False)
    try:
        frame = bytes.fromhex(command)
    except (TypeError, ValueError):
        return False
    if len(frame) != 63 or frame[:4] != bytes.fromhex("42313173"):
        return False
    return current[_DISPLAY_RESOLUTION_BYTE] == frame[3 + _DISPLAY_RESOLUTION_BYTE]
