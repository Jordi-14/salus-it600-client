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


_DEVICE_METADATA = frozenset((1, 40, 41))
_PROTECTED = (
    "HoldType", "SystemMode", "HeatingSetpoint_x100", "CoolingSetpoint_x100",
    "LockKey", "LockKey_a", "HeatingControl", "CoolingControl",
    "PairedWCNumber", "PairedTRVShortID", "ProgramOperationMode", "ScheduleType",
)


def _validated_settings(
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
        _validated_settings(status)
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
        _validated_settings(status, check_command=False)
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
    body[39] = level
    return "423131" + body.hex()


def _same_protected_settings(before: dict[str, Any], after: dict[str, Any]) -> bool:
    """Compare everything except comfort and device-maintained metadata."""
    base = _validated_settings(before, check_command=False)
    current = _validated_settings(after, check_command=False)
    return (
        before.get("data") == after.get("data")
        and all(base[i] == current[i] for i in range(77) if i not in _DEVICE_METADATA and i != 39)
        and before.get("sScheS") == after.get("sScheS")
        and all(before["sIT600TH"].get(key) == after["sIT600TH"].get(key) for key in _PROTECTED)
    )


def _command_applied(before: dict[str, Any], after: dict[str, Any], command: str) -> bool:
    """Confirm the requested level and protected data, not predicted counters."""
    current = _validated_settings(after, check_command=False)
    echo = str(after.get("sIT600I", {}).get("CommandResponse_d", "")).lower()
    return (
        current[39] == bytes.fromhex(command)[42]
        and _same_protected_settings(before, after)
        and echo in (command.lower() + "00", NON_SETTINGS_RESPONSE)
    )


def confirmed_comfort_warm_floor_change(before: dict[str, Any], after: dict[str, Any], level: int) -> bool:
    """Resolve a durable journal, including commands sent by older encoders.

    No command is reconstructed or replayed. Require the actual requested
    change, all protected settings and a successful matching settings echo.
    Only device-maintained metadata may differ in the old command echo.
    """
    if type(level) is not int or level not in range(4):
        return False
    base = _validated_settings(before, check_command=False)
    current = _validated_settings(after, check_command=False)
    if base[39] == level or current[39] != level or not _same_protected_settings(before, after):
        return False
    echo = after.get("sIT600I", {}).get("CommandResponse_d")
    if isinstance(echo, str) and echo.lower() == NON_SETTINGS_RESPONSE:
        return True
    if not isinstance(echo, str) or not re.fullmatch(r"42313173[0-9a-fA-F]{118}00", echo, re.IGNORECASE):
        return False
    body = bytes.fromhex(echo)[3:63]
    return all(body[i] == current[i] for i in range(1, 60) if i not in _DEVICE_METADATA)
