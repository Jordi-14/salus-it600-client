# Experimental Comfort Warm Floor writes

This feature branch adds
`IT600Gateway.set_climate_device_comfort_warm_floor(device_id, level)`.
Levels are 0 (disabled), 1, 2 and 3. No new package version has been released.

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

The initial encoder deliberately supports only:

- SQ610RFNH firmware `00000054`, heating mode and a paired wiring centre;
- no paired TRVs and no PIN-required flag;
- the 77-byte `72` settings layout, with matching `Schedule` and `Status_2_d`;
- the observed save-counter range: current counter 0..8, next counter 1..9;
- the observed counter-dependent bytes 40..41;
- `ff` padding at bytes 48..74 and `0000` at 75..76;
- a recorded successful `B11` response that agrees with current settings.

**This is a guarded contribution prototype, not unrestricted production
support.** After counter 9 the setter refuses further changes. Use the vendor
app for unsupported states. Do not reset or wrap the counter to work around
this guard. Additional captures, especially across counter boundaries and
with different PIN configurations, are needed before expanding the range.

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
has an uncertain outcome: read state before deciding what to do next. The
method does not persist private configuration snapshots or automatically
restore them. For manual hardware trials, save a local pre-write read response.
Restoring a snapshot requires a fresh, valid command and counter; replaying an
old backup is not a verified restore mechanism.

## Integration release order

Publish a reviewed client release before pinning it in a real Home Assistant
integration release. Until then, use a separate test branch with the client
fork dependency as described in `CONTRIBUTING.md`. Do not merge a Git-branch
dependency into a production manifest.
