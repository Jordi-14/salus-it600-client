# Salus iT600 Device Protocol Notes

This document describes the gateway payload shapes used by
`salus-it600-client`. The Salus gateway does not expose a public stable local
API, so these notes are based on observed UG600 local Wi-Fi payloads.

## Polling Flow

```text
readall
  -> summary payloads with protocol section hints
  -> one deviceid request for every device (falls back to one request per
     device family if the gateway rejects it or leaves devices out)
  -> detailed payloads parsed into library models
  -> internal state dictionaries replaced atomically
```

The gateway is sensitive to concurrent local commands, so the client serializes
encrypted requests with one `asyncio.Lock`.

## Device Signatures

| Device family | Readall signature | Detailed parser |
| --- | --- | --- |
| Gateway | `sGateway.NetworkLANMAC` | Gateway metadata |
| Climate | `sIT600TH` or `sTherS` | iT600 thermostat, SQ610, FC600 |
| Binary sensor | `sIASZS` or relay model ID | Contact, moisture, smoke, TRV/receiver relay |
| Sensor | `sTempS` | Temperature sensor |
| Switch | `sOnOffS` | Relay switch or outlet |
| Cover | `sLevelS` | Roller shutter/blind level |
| Wiring centre | `sIT600WC` | it600WC fault registers, no valve/relay state |

## Common Fields

Detailed device payloads normally include:

| Field | Meaning |
| --- | --- |
| `data.UniID` | Stable device identifier |
| `data.Endpoint` | Endpoint number for multi-endpoint devices |
| `sZDO.DeviceName` | JSON string containing `deviceName` |
| `sZDO.FirmwareVersion` | Device firmware version, when available |
| `sZDOInfo.OnlineStatus_i` | `1` when online, otherwise unavailable |
| `sBasicS.ManufactureName` | Manufacturer, usually `SALUS` |
| `DeviceL.ModelIdentifier_i` | Detailed model identifier |

`sIT600I.LastMessageRSSI_d` (dBm) and `sIT600I.LastMessageLQI_d` (0-255) appear
on several device families, but only for devices the coordinator heard from
directly on that particular poll. They are intermittently absent on otherwise
healthy, online devices; a missing value must not be treated as a fault or
reported as zero. Parsers therefore carry the last known reading forward for as
long as the parent device is reported, taking availability and the rest of the
child entity's metadata from the current poll, so the entity follows the parent
device rather than the presence of the field.

## Climate Fields

### iT600TH / SQ610

| Field | Meaning |
| --- | --- |
| `sIT600TH.LocalTemperature_x100` | Current temperature, divided by 100 |
| `sIT600TH.HeatingSetpoint_x100` | Heating setpoint, divided by 100 |
| `sIT600TH.MinHeatSetpoint_x100` | Minimum setpoint, divided by 100 |
| `sIT600TH.MaxHeatSetpoint_x100` | Maximum setpoint, divided by 100 |
| `sIT600TH.HoldType` | Preset/hold state |
| `sIT600TH.RunningState` | Current heating/cooling action |
| `sIT600TH.SunnySetpoint_x100` | SQ610 humidity, divided by 100 |

### SQ610 Advanced Settings (`Status_2_d` / `Schedule`)

The vendor app's per-thermostat "Advanced Settings" screen (~28 fields) has
no named JSON fields in the local gateway API. Every field is packed into a
single 77-byte blob exposed twice on `sIT600TH`, under two aliased keys that
always carry identical values: `Status_2_d` and `Schedule`. `Schedule` is a
misleading legacy name — the blob is not primarily schedule or timer data.
The client reads `Status_2_d`, falling back to `Schedule`, and exposes the
result as the read-only `ClimateDevice.advanced_settings` model.

Encoding: `byte = position / 2` into the 154-hex-char string. Each field's
hex characters are read as a **decimal digit string, not as hex** (`"15"` is
decimal 15, not 0x15 = 21). Multi-byte fields concatenate their digit
strings big-endian (`"1500"` -> 1500 -> 15.00 °C after /100). Byte 0 is a
constant `72` header.

The offsets were derived by live A/B toggling of individual settings in the
cloud app while diffing gateway captures of this blob, then confirmed
field-by-field against the settings-parsing table in the Salus cloud web
app's compiled Flutter JS (`main.dart.js` keeps JSON string-literal keys
readable even when minified). The two methods cross-validated exactly on the
fields checked by hand.

| Byte(s) | Field | Encoding |
| --- | --- | --- |
| 2 | Display Time on LCD | `00` hide, `01` show |
| 3-4 | Temperature Calibration | Sign-magnitude: first hex digit `8` negative / `0` positive, remaining 3 digits magnitude ×100 (`8350` = −3.5 °C, `0050` = +0.5 °C) |
| 5 | Display Humidity on LCD | `00` hide, `01` show |
| 6-7 | Standby Setpoint Heating | Decimal /100 = °C |
| 8-9 | Standby Setpoint Cooling | Decimal /100 = °C; `4050` and `0450` mean "Off", not a temperature |
| 10 | Temperature Scale | `TemperatureDisplayUnit` |
| 11 | Display Temp Resolution | `DISPLAY_RESOLUTION_DEGREES` (`00` = 0.5 °C, `01` = 0.1 °C) |
| 12 | Control Algorithm | `ControlAlgorithm`; values 3/4/6/7/8 are On-Off span variants on other models, kept raw |
| 13 | Cooling Control span | `COOLING_CONTROL_SPAN_DEGREES` (±0.25 to ±2.0 °C) |
| 14 | TRV Advanced Calibration | `TrvCalibrationMode` |
| 15 | S1/S2 Input | `S1S2Function` |
| 16-17 | Max Floor Temp for Heating | Decimal /100 = °C |
| 18-19 | Min Floor Temp for Heating | Decimal /100 = °C |
| 20-21 | Min Floor Temp for Cooling | Decimal /100 = °C |
| 22-23 | Maximum Setpoint for Heating | Decimal /100 = °C |
| 24-25 | Minimum Setpoint for Heating | Decimal /100 = °C |
| 26-27 | Maximum Setpoint for Cooling | Decimal /100 = °C |
| 28-29 | Minimum Setpoint for Cooling | Decimal /100 = °C |
| 30 | Valve Protection | `00` off, `01` on |
| 31 | Internal Relay | `InternalRelayFunction` |
| 32 | Relay Type | `RelayContactType` (`00` NO-COM, `01` NC-COM) |
| 33-34 | Min Off Time for Heating | Decimal seconds |
| 35-36 | Min Off Time for Cooling | Decimal seconds |
| 37 | Optimum Start | `00` off, `01` on |
| 38 | Optimum Stop | `00` off, `01` on |
| 39 | Comfort Warm Floor | `ComfortWarmFloorLevel` (Level 3 from the app's option list, not live-confirmed) |
| 42 | Language | Raw index into the app's language list (0 = English and 1 = Dansk observed; full list unconfirmed) |
| 43 | Unlock Thermostat Keys | `00` PIN not required, `01` PIN required |
| 45 | Display Floor Temperature on LCD | `00` hide, `01` show |
| 46 | Enable unlock from thermostat | `00` no, `01` yes |
| 47 | Allow adjust setpoint when buttons locked | `00` no, `01` yes |

Deliberately not decoded:

- **Byte 1** is a save-sequence counter that increments on every settings
  write regardless of what changed; it is not thermostat state.
- **Bytes 40-41** hold the thermostat PIN code, obfuscated against the save
  counter at byte 1 with an algorithm that was not fully
  reverse-engineered. Security-sensitive and unverified, so intentionally
  not decoded or exposed.
- **Bytes 44 and 48-76** are outside the confirmed settings table (a gap
  byte, then the schedule/holiday-hold payload region and `ff` padding).
- **Writes.** The decode is read-only; no encode path is implemented. The
  save-counter and PIN-obfuscation interactions with writes are not fully
  understood, and a subtly wrong write could corrupt a live thermostat's
  settings.

### FC600

| Field | Meaning |
| --- | --- |
| `sTherS.LocalTemperature_x100` | Current temperature, divided by 100 |
| `sTherS.HeatingSetpoint_x100` | Heating setpoint, divided by 100 |
| `sTherS.CoolingSetpoint_x100` | Cooling setpoint, divided by 100 |
| `sTherS.SystemMode` | Heat/cool/auto mode |
| `sTherS.RunningState` | Idle/heating/cooling action |
| `sComm.HoldType` | Preset/hold state |
| `sFanS.FanMode` | Fan speed |
| `sTherUIS.LockKey` | Child lock state |

## Wiring Centre (it600WC)

The it600WC has no valve/relay state of its own in its payload -- it is a
fault-register bank paired with SQ610-family thermostats on a hydronic
system, and the single point of failure for every zone it serves.

| Field | Meaning |
| --- | --- |
| `sIT600WC.Error10`..`Error20`, `Error26`..`Error29` | Fault register bank. The parser reports each active register with the vendor app's description (see `THERMOSTAT_ERROR_CODES` in `salus_it600/const.py`, shared with the thermostat-side Error01-32 codes) |
| `sIT600WC.ErrorCodeWC_d` | Hex-string summary fault code, `"0000"` at baseline. `bool("0000")` is `True` in Python -- check `str(value).strip("0")` instead, the same pattern `parse_climate_binary_sensor_devices` uses for `sComm.DeviceErrorCode` |

## Mini TRV (it600MINITRV)

The it600MINITRV is a slave actuator, normally paired to one thermostat but also
usable unpaired. Its payload has no `sIT600TH`/`sTherS` block, so it is
classified as a relay binary sensor.

| Field | Meaning |
| --- | --- |
| `sIT600I.RelayStatus` | `1` while the TRV is asked to heat |
| `sIT600I.Mode` | Operating mode: `0` Auto, `1` Manual On (open), `2` Manual Off (closed) (`MiniTrvMode`). The vendor app also labels `3` fail-safe and `4` adaptation, states the TRV enters on its own. Exposed raw as `BinarySensorDevice.mini_trv_mode` |
| `sIT600I.PairedThermostatShortID` | ZigBee short address of the paired thermostat; matches that thermostat's `sZDO.ShortID_d`. `0` and `65535` mean unpaired |
| `sIT600I.TRVError01`, `TRVError23`, `TRVError30`, `TRVError31` | Fault flags: hardware issue, message from unpaired TRV, gear issue, adaptation issue (`MINI_TRV_ERROR_CODES`) |
| `sIT600I.TRVError22` | Low battery |
| `sIT600I.CommandResponse_d` | Hex-encoded ASCII report. For a paired TRV, characters 28-39 are temperatures x100: paired thermostat temperature, TRV temperature, setpoint. An unpaired TRV holds only its own temperature (see the layout below). Decoded by `decode_mini_trv_report()` |

The report is the reply to the `B37` status request (see "Setting the mode"). The
evidence for this is the vendor app's per-model table, which pairs that request
with an expected `CommandResponse_d` start of hex `423337` (`B37`), and live
reports from two different TRVs, one paired and one unpaired, which both start
with `B37`.

A decoded report has this layout (short address and some trailing bytes replaced
in the paired example, trailing bytes shortened in the unpaired one):

| Characters | Field | Paired example | Unpaired example |
| --- | --- | --- | --- |
| 0-2 | Response ID, always `B37` | `B37` | `B37` |
| 3-6 | Short address (`FFFF` when unpaired) | `A1B2` | `FFFF` |
| 7-19 | Status digits, with mode flags at 15-17 | `4000000010020` | `0000000000000` |
| 20-23 | Valve position | `0328` | `0002` |
| 24-27 | Not decoded | `4068` | `4074` |
| 28-31 | Paired: thermostat temperature. Unpaired: TRV temperature | `1820` | `2418` |
| 32-35 | Paired: TRV temperature. Unpaired: the same reading repeated | `2025` | `2418` |
| 36-39 | Paired: setpoint. Unpaired: start of the undecoded tail | `1850` | `1500` |
| 40 onwards | Paired: `@` at 40, then an undecoded tail. Unpaired: rest of the tail | `@320236FF...` | `022032600000000` |

The paired example is thermostat 18.20 °C, TRV 20.25 °C and setpoint 18.50 °C,
checked against the vendor app, which rounds to 0.5 °C. The unpaired example is
TRV 24.18 °C, which matched the vendor app across a falling series of samples.
An unpaired report has no `@`, thermostat temperature or setpoint. Its repeat
must be read at character 28 rather than searched for: at 24.94 °C the string
holds `...4 2494 2494 1...`, which also contains the repeat `4249 4249` one
character earlier.

`CommandResponse_d` can carry other responses too: one SQ610RF payload holds
`42323000` (`B20` and a null byte), and the vendor app expects `B70` from the
it600WC and `B71` from the it600Receiver. So the decoder checks the whole layout
rather than searching for a reading, and an unrelated or truncated response
reports no reading.

The minimum tails (16 hex characters after a paired `@`, 19 from character 36 of
an unpaired report) are lower limits based on edited samples, not protocol rules.
The complete reports available, one paired from a real TRV and one unpaired
stored in the vendor app, are both 73 characters and hold hex letters in the
tail. Characters 49-50 are probably RSSI as a signed byte, which is not decoded;
`sIT600I.LastMessageRSSI_d` reports signal strength instead.

The valve position is checked for shape but not decoded. Two TRVs tested read
about 0 when closed and 2241-2247 when open. Each character is `'0' + n`, so
slightly past closed the last character drops below `0` in ASCII: `*` (`2A`) is
-6, `+` is -5, `,` is -4, `.` (`2E`) is -2 and `/` is -1. Characters 15-17, within the
status digits, follow the mode: `000` Auto, `111` Manual on, `020` Manual off.

In both layouts, a TRV temperature outside 0-60 °C (exclusive of 0) is treated
as a decoding error, and no reading is reported.

### Setting the mode

The it600MINITRV has no named write fields such as `SetHoldType`. Commands are
raw strings written to `sIT600I.SetCommand_d` as space-separated hex bytes of
ASCII text. `set_mini_trv_mode()` sends the same commands as the vendor app:

| Mode | `SetCommand_d` | ASCII |
| --- | --- | --- |
| `MiniTrvMode.AUTO` | `42 33 38 31` | `B381` |
| `MiniTrvMode.MANUAL_ON` | `42 33 38 37` | `B387` |
| `MiniTrvMode.MANUAL_OFF` | `42 33 38 38` | `B388` |

After a mode change the vendor app waits 4 seconds and then asks the TRV for a
status report by writing `42 33 37 00 00 00 00 00 00 00 00 78` (`B37`, eight
zero bytes, `x`). This client does the same with a 2 second wait, which still worked in testing.

Note: If users report issues with commands getting dropped/lost in future, consider upping request delay back up to 4 seconds, same as the vendor app.

In tests, writing the status request with no pause dropped the mode command.
This suggests `SetCommand_d` holds one command per device, with the last write
winning, so any two writes to the same TRV need a gap between them.

The gateway accepts any `SetCommand_d` string, so a wrong command fails
silently. Only the three modes above are accepted; fail-safe and adaptation
cannot be set.

## Protocol Enums

Use the enums in `salus_it600.const` rather than raw integers:

| Enum | Values |
| --- | --- |
| `HoldType` | `FOLLOW_SCHEDULE=0`, `TEMPORARY_HOLD=1`, `PERMANENT_HOLD=2`, `AWAY=6`, `STANDBY=7`, `ECO=10` |
| `SystemMode` | `AUTO=1`, `COOL=3`, `HEAT=4`, `EMERGENCY_HEAT=5` |
| `RunningState` | `IDLE=0`, `HEATING=1`, `COOLING=2`, `FAN_COIL_HEATING=33`, `FAN_COIL_COOLING=66` |
| `FanMode` | `OFF=0`, `LOW=1`, `MEDIUM=2`, `HIGH=3`, `AUTO=5` |
| `MiniTrvMode` | `AUTO=0`, `MANUAL_ON=1`, `MANUAL_OFF=2` |
| `ControlAlgorithm` | `ITLC_UNDERFLOOR=0`, `ITLC_RADIATORS=1`, `ITLC_ELECTRICAL=2`, `THB_ACTUATOR=5` |
| `TrvCalibrationMode` | `STANDARD_ON_OFF=3`, `AUTO_SELECTION=4`, `ADVANCED_SELF_LEARNING=5` |
| `S1S2Function` | `DISABLED=0`, `FLOOR_SENSOR=1`, `EXTERNAL_SENSOR=2`, `OCCUPANCY_SENSOR=3`, `RUN_ONETOUCH=4`, `CHANGEOVER=5` |
| `InternalRelayFunction` | `DISABLED=0`, `HEAT_AND_COOL=1`, `HEAT_ONLY=2`, `COOL_ONLY=3` |
| `RelayContactType` | `NO_COM=0`, `NC_COM=1` |
| `ComfortWarmFloorLevel` | `DISABLED=0`, `LEVEL_1=1`, `LEVEL_2=2`, `LEVEL_3=3` |
| `TemperatureDisplayUnit` | `CELSIUS=0`, `FAHRENHEIT=1` |

`HoldType.TEMPORARY_HOLD` is reported as `Schedule Override` when a thermostat
is already overriding its schedule. It is not advertised as a normal selectable
preset when the device is in follow-schedule, permanent-hold, away, or eco
states.

## Adding Device Support

Use [../CONTRIBUTING.md](../CONTRIBUTING.md) for the full contributor workflow. At the
protocol level, the checklist is:

1. Capture a `main.py --debug` payload from the gateway.
2. Add or update model constants in `salus_it600/device_models.py`.
3. Add or update the parser in the matching `salus_it600/parsers/` module.
4. Register the parser in `poll_status()` or an existing refresh method.
5. Add tests for valid payloads, missing fields, and malformed data.
6. Keep write command values in `salus_it600.const` or model-specific constants;
   do not introduce new magic integers inline.
