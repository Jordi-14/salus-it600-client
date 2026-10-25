# Experimental Comfort Warm Floor writes

Version `0.7.0b2.dev20261025+floor4`, for SQ610RFNH firmware `00000054` only.
Use `IT600Gateway.set_climate_device_comfort_warm_floor(device_id, level)`;
levels are Off (0), 1, 2 and 3.

## Hardware evidence and the counter correction

On 2026-10-25, commands transmitting counter values 254, 255 and 0 were echoed
and applied the requested comfort levels, while read-back counters advanced
normally instead of taking the transmitted values. This did not force the
device's stored counter to 254 or exercise its actual rollover.

A subsequent two-write test changed only comfort: Off → 1 → Off. Outgoing
counter bytes were copied unchanged (40, then 41); read-back counters became
41 and 42. Bytes 40–41 were also copied unchanged in each outgoing command.
Complete settings, weekly schedules, mode, setpoints and keypad lock were
checked. Both changes and the final Off state were confirmed by fresh reads.
The two anonymized vectors are in
`tests/fixtures/comfort_warm_floor_level_only.json`.

The old encoder incorrectly incremented byte 1, calculated bytes 40–41 and
predicted an identical read-back. This version treats all three as opaque,
device-maintained metadata. No counter is incremented, reset, wrapped or
re-encoded by the client, and there is no artificial write cutoff at 255.
**Actual device-counter rollover has not been observed on hardware.** Simulated
255→0 tests verify that client arithmetic and comparisons do not block it;
they cannot prove what every firmware reports at that boundary.

The earlier 75-write trial covered all 12 level transitions on three devices,
using the old incrementing strategy. Its vectors remain regression inputs for
preserving other settings, not evidence of 75 comfort-only writes. Supported
models and firmware have not been broadened by this change.

## Write frame and guards

Each command uses `sIT600I.SetCommand_d` in the normal `requestAttr: write`
envelope, with prefix `423131` (B11) and a 60-byte body. Copy the selected
thermostat's fresh settings, change body marker 72 to 73, and set byte 39 to
the requested comfort level. Every other body byte, including 1, 40 and 41,
is copied unchanged. Preserve the thermostat's own footer and language; never
use the original proposal's fixed footer. The trailing `00` in a command echo
is response status and is not sent in the command.

Guards remain for device identity, endpoint 9/type 100, online state, heating
mode, paired wiring centre, no TRVs, no PIN-required flag, recognized 77-byte
settings layout and tail, and matching Schedule/Status_2_d aliases. Unknown
profiles, partial data and unrecognized command framing block writes.
The separate PIN-required flag is checked; counter metadata is never guessed
from an assumed PIN/counter formula.

## Confirmation, pending commands and failures

Gateway acceptance is not device confirmation. With `confirmation_timeout`
enabled, the client waits for the requested level, the complete protected
settings and weekly schedules, plus an exact successful command echo or the
specifically observed B34L shared response (`4233344c`). Metadata bytes may
change independently; every other setting must match the pre-write snapshot.
An unexpected level or unrelated setting change stops confirmation.

A same-counter echo carrying a different configuration blocks a new write as
pending. Counter values are not numerically ordered to infer pending state:
the device's read-back counter is independently maintained. Unconfirmed local
commands remain remembered and block further dispatch until their actual
result matches. For B34L, two unchanged fresh snapshots two seconds apart are
required before dispatch. Unknown shared-response markers remain blocked.
External writers have no compare-and-swap protection: do not edit the same
thermostat concurrently in the app while testing or writing locally.

The caller's `before_write` backup is awaited before dispatch. Backup failure
prevents the write. Writes are never automatically retried after disconnect;
lost replies trigger reads, not replay. The HA integration retains durable
pre-write backups and uncertainty across restarts. An error never blindly
replays an old backup or overwrites an unrelated change. Restoration means
changing the comfort level against a fresh validated snapshot.

Known reported levels remain readable during pending app changes or missing
command echoes; write readiness is checked separately. A real offline or
unsupported device remains unavailable.

## Distribution and limits

The matching HA beta pins a SHA-256-verified pure-Python wheel from this fork's
GitHub prerelease. No PyPI publishing is performed. This is still a guarded,
firmware-specific beta. Other firmware, PIN-required installations and real
device-counter rollover require additional evidence.
