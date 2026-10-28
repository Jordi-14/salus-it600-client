"""it600MINITRV report decoding.

The it600MINITRV is a slave actuator: it has no `sIT600TH`/`sTherS` block, so
the gateway reports no temperature or setpoint for it in named fields. The
TRV's own temperature reading, which the vendor app shows, is only available
packed into `sIT600I.CommandResponse_d`.

`CommandResponse_d` is an ASCII string encoded as hex. Once decoded, the last
three 4-digit decimal groups before the first `@` are temperatures x100, in
this order: the paired thermostat's temperature, the TRV's own temperature,
and the setpoint. For example::

    A1B2C3D400000001002003284068 1820 2025 1850 @320236FF...

(spaces added) decodes to thermostat 18.20, TRV 20.25 and setpoint 18.50,
which was checked against the vendor app (which rounds to 0.5 degrees).

An unpaired TRV (characters 3-6 are `FFFF`, the unpaired short address) uses a
different layout with no `@`. Its own temperature is the 4-digit group at
character 28, written twice in a row, with no thermostat temperature or
setpoint::

    B37FFFF0000000000000000 2407 4 2418 2418 150 0022...

(spaces added) decodes to TRV 24.18, which matched the vendor app across a
falling series of samples. The position matters: at 24.94 the string holds
`...4 2494 2494 1...`, which also contains the repeat `4249 4249` one
character earlier. The rest of the string is not decoded.
"""

from __future__ import annotations

import re
from typing import Any, NamedTuple

from ..const import TEMPERATURE_SCALE

_REPORT_PATTERN = re.compile(r"(\d{4})(\d{4})(\d{4})@")
_UNPAIRED_PATTERN = re.compile(r"(\d{4})\1")
_UNPAIRED_TEMPERATURE_OFFSET = 28
_UNPAIRED_SHORT_ID = "FFFF"
_SHORT_ID_SLICE = slice(3, 7)

# A TRV temperature outside this range is treated as a decoding error rather
# than a reading. The upper bound is far above any room temperature but still
# rejects the larger values a misaligned 4-digit group would produce.
_MIN_TRV_TEMPERATURE = 0.0
_MAX_TRV_TEMPERATURE = 60.0


class MiniTrvReport(NamedTuple):
    """Temperatures decoded from an it600MINITRV `CommandResponse_d`."""

    thermostat_temperature: float | None
    trv_temperature: float
    setpoint: float | None


def _plausible(temperature: float) -> bool:
    return _MIN_TRV_TEMPERATURE < temperature <= _MAX_TRV_TEMPERATURE


def _decode_unpaired(text: str) -> MiniTrvReport | None:
    """Return the TRV temperature from an unpaired TRV's report."""
    if text[_SHORT_ID_SLICE].upper() != _UNPAIRED_SHORT_ID:
        return None
    match = _UNPAIRED_PATTERN.match(text, _UNPAIRED_TEMPERATURE_OFFSET)
    if match is None:
        return None
    trv = int(match.group(1)) / TEMPERATURE_SCALE
    if not _plausible(trv):
        return None
    return MiniTrvReport(
        thermostat_temperature=None,
        trv_temperature=trv,
        setpoint=None,
    )


def decode_mini_trv_report(value: Any) -> MiniTrvReport | None:
    """Decode the temperatures packed into `sIT600I.CommandResponse_d`.

    Returns None when the value is missing, is not hex-encoded ASCII, matches
    neither the paired (`<4 digits x3>@`) nor the unpaired layout, or holds an
    implausible TRV temperature.
    """
    if not isinstance(value, str) or not value:
        return None

    try:
        text = bytes.fromhex(value).decode("ascii")
    except ValueError:
        # Covers both invalid hex and UnicodeDecodeError.
        return None

    match = _REPORT_PATTERN.search(text)
    if match is None:
        return _decode_unpaired(text)

    thermostat, trv, setpoint = (
        int(group) / TEMPERATURE_SCALE for group in match.groups()
    )
    if not _plausible(trv):
        return None

    return MiniTrvReport(
        thermostat_temperature=thermostat,
        trv_temperature=trv,
        setpoint=setpoint,
    )
