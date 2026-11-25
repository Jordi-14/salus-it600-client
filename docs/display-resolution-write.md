# Experimental display resolution control

Display resolution sets the step in which an SQ610 shows and reports
temperatures: 0.5 °C (0) or 0.1 °C (1). Only SQ610RFNH firmware 00000054 is
enabled. Call set_climate_device_display_resolution(device_id, resolution).
The method reads fresh settings and returns after gateway acknowledgement.
Normal polling supplies the actual value in
`advanced_settings.display_resolution`, and
`ClimateDevice.supports_display_resolution` shows whether it is supported.

## Encoding and evidence

The device has no separate resolution command. The write uses the B11
settings frame: copy the fresh settings body, change marker 72 to 73 and
display resolution byte 11 only. Preserve all other bytes, including
device-maintained metadata at 1, 40 and 41.

The fixture keeps one anonymized round trip (0.1 -> 0.5 -> 0.1 °C). Each write
was acknowledged and read back with only byte 11 changed, apart from the
device updating its own metadata. Other firmware, PIN-protected settings
(blocked) and device-counter rollover remain unobserved.

## Readiness and pending commands

The write is refused for an unverified model, firmware or settings layout,
PIN-protected settings, an unknown reported resolution, or a recorded
settings command with the current counter that the device has not applied.

A local write stays pending until the device reports the requested
resolution or 120 seconds pass; a second write is refused meanwhile. The
settings body also carries other settings. Two writes of different settings
at the same moment, from this library or the Salus app, can overwrite each
other.
