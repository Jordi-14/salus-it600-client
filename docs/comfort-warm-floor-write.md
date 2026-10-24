# Experimental Comfort Warm Floor writes

This feature branch adds
`IT600Gateway.set_climate_device_comfort_warm_floor(device_id, level)`.
Levels are 0 (disabled), 1, 2 and 3. This beta is version `0.7.0b2.dev20261024`.

## Evidence and scope

A 2026-10-24 trial on SQ610RFNH firmware `00000054` observed app changes
Off -> 2 -> Off, followed by a computer-originated Off -> 3 change. The final
change was confirmed in both `Schedule`/`Status_2_d` and the vendor app.
The other advanced-settings bytes, weekly schedules, setpoint, mode and
keypad-lock state were compared before and after and did not change.

The new unit fixture strips device identity, gateway address and room names.
It contains the observed Off(counter 7) -> level 3(counter 8) command vector.
Earlier captures cover counters 0..9 and reported levels 0..3; this does not
prove all possible commands, counters, PIN configurations or firmware versions.

A subsequent authorized 25-change trial on each of three SQ610RFNH/00000054
devices confirmed **75/75 writes** over 12.54 minutes, with at least 30 seconds
between writes to the same device. All twelve directed level transitions
were covered. Read-backs took 6.47–18.58 seconds, and all devices ended at
their original levels. Other settings bytes, weekly schedules, setpoints,
mode and keypad-lock state were unchanged. Counter ranges were 8–33, 9–34
and 7–32; the 9→10, 15→16 and 31→32 boundaries were crossed successfully.
The 75 exact command/read-back vectors are anonymized in
`tests/fixtures/comfort_warm_floor_75.json` and tested individually.

No live fault required fallback. A separate private trial harness passed
nine offline checks, including lost-reply handling without replay, stop on
missing confirmation, a fresh-counter fallback and refusal to overwrite an
unrelated settings change. This is not a claim that every recovery scenario
has been exercised against physical hardware.

The initial encoder deliberately supports only:

- SQ610RFNH firmware `00000054`, heating mode and a paired wiring centre;
- no paired TRVs and no PIN-required flag;
- the 77-byte `72` settings layout, with matching `Schedule` and `Status_2_d`;
- a non-wrapping unsigned-byte counter: current 0..254, next 1..255;
- the observed counter-dependent bytes 40..41;
- `ff` padding at bytes 48..74 and `0000` at 75..76;
- a recognized successful `B11` response: a same-counter response must agree
  with current settings; an older counter may be stale, while a newer one
  blocks writing as pending.

**This is an experimental beta, not unrestricted production support.**
The separate beta branch deliberately extends beyond the upstream proposal's
measured range using the equations in [pyit600 PR54](https://github.com/epoplavskis/pyit600/pull/54).
A subsequent two-command operation confirmed counter 34 and 35 and left six
thermostats Off and one at level 1. Counters 36..255 are inferred from source,
not hardware-verified. Exhaustive tests cover every non-wrapping encoding,
which validates implementation consistency, not device acceptance.

Every fresh snapshot must match the expected counter-dependent pair. A mismatch
stops the command. At counter 255 writes become unavailable: the beta never
wraps or resets the counter. App-side rollover, alternate PINs and other firmware
still require captures. Reaching the limit does not change the heating mode or
setpoint; use the vendor app and report a fresh capture for analysis.

## Command framing

The request is written through `sIT600I.SetCommand_d`, under the standard
`requestAttr: write` envelope. The command is 63 bytes:

- `423131` (`B11`) prefix;
- a 60-byte body beginning with `73` instead of the read blob's `72`;
- incremented body byte 1, the new level at byte 39, and the observed
  counter-derived pair at 40..41;
- every other body byte copied from this thermostat's own fresh settings.

`CommandResponse_d` contains this command followed by `00`. That trailing
response status is not sent as part of the command. The remaining read-blob
tail is not blindly transmitted either.

The original pyit600 PR #54 uses a fixed footer `020000000100`. The trial
device's footer was `010000000100`; replacing it would change language byte
42. This encoder preserves the footer rather than copying that constant.

## Confirmation and failures

The client serializes these read/modify/write operations, reads the selected
device freshly and checks its identity/endpoint before writing. A mismatch
between the last command response and current settings blocks another write
while a command is pending. Do not edit settings concurrently in the vendor
app; the gateway provides no compare-and-swap operation against external writers.

Gateway acceptance does **not** prove the thermostat applied the setting.
In the trial, initial polls still showed Off, followed by level 3 after tens
of seconds. Consumers must keep polling and display reported state rather
than claiming an optimistic confirmation.

This command is never automatically retried on disconnect. A lost response
has an uncertain outcome: read state before deciding what to do next. With `before_write` supplied, the setter awaits a caller-provided durable backup
before dispatch; a backup failure prevents dispatch. With
`confirmation_timeout=120`, it holds its command lock and polls for the exact
settings blob plus successful command echo. Lost acknowledgements trigger
read-back, never replay. Unrelated configuration changes or an unexpected result
raise an error; they are never overwritten by automatic restoration.
The HA beta stores the latest pre-write snapshot per device in Home Assistant's
private `.storage` directory using an fsync-backed atomic write and disk read-back. Snapshots are retained after errors. Restoring a
previous comfort level requires a new validated command against fresh state.
Restoring a snapshot requires a fresh, valid command and counter; replaying an
old backup is not a verified restore mechanism.

## Beta distribution

The matching Home Assistant beta pins a SHA-256-verified pure-Python wheel
from this fork's GitHub prerelease. It requires no compiler or Git installation
on the Home Assistant host. Neither the client nor integration beta is uploaded
to PyPI or proposed as an upstream production dependency.
