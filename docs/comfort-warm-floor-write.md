# Experimental Comfort Warm Floor control

Only the SQ610RFNH / firmware 00000054 heating/wiring-centre profile is enabled.
Call set_climate_device_comfort_warm_floor(device_id, level) for Off (0), 1, 2, 3.
The method reads fresh settings and returns after gateway acknowledgement.
Acknowledgement is not device confirmation: normal polling supplies the actual
comfort level. No confirmation loop or durable journal is part of this client.

## Encoding and evidence

B11 uses sIT600I.SetCommand_d with prefix 423131 and a 60-byte body. Copy the
fresh settings body, change marker 72 to 73 and comfort byte 39 only. Preserve
all other bytes, including opaque device-maintained metadata at 1, 40 and 41.
Do not calculate a counter or PIN encoding, reset metadata, replay a failed
transport request or restore an old snapshot.

Two anonymized comfort-only hardware captures confirm Off -> 1 -> Off with
unchanged outgoing metadata and the expected device read-back. The earlier
75-write trial used the older incrementing encoder: its fixtures provide
historical protected-settings evidence, not 75 comfort-only writes. Actual
stored-counter rollover and other firmware/PIN profiles remain unobserved.

## Readiness and bounded pending commands

Fresh identity, availability, model/firmware, layout, heating/wiring-centre and
PIN/profile guards run before writing. A recognized shared B34L response needs
two stable fresh reads, two seconds apart. Unknown external command framing
and changed settings block dispatch.

Local pending writes resolve from the comfort byte and settings body actually
written by B11. Live HVAC setpoints/hold fields and later command echoes do not
have to equal their old values. Pending commands expire lazily after 120 seconds,
so an unapplied or lost write cannot permanently block later explicit requests.
Expiry does not resend the old command. A known expired local echo requires two
stable fresh reads before a new requested level is encoded from current data.
An unknown external echo does not get that exception. Transport disconnects
never replay the B11 write (retry_disconnect=False).

The public comfort_command_matches helper checks that controlled body; it is
not a general transactional guarantee against an app editing settings later.
All protocol tests are simulated except the documented anonymized captures.
