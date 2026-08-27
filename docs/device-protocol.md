# Salus iT600 Device Protocol Notes

This document describes the gateway payload shapes used by
`salus-it600-client`. The Salus gateway does not expose a public stable local
API, so these notes are based on observed UG600 local Wi-Fi payloads.

## Polling Flow

```text
readall
  -> summary payloads with protocol section hints
  -> one deviceid request per supported device family
  -> detailed payloads parsed into library models
  -> internal state dictionaries replaced atomically
  -> optional update callbacks per refreshed device
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

## Protocol Enums

Use the enums in `salus_it600.const` rather than raw integers:

| Enum | Values |
| --- | --- |
| `HoldType` | `FOLLOW_SCHEDULE=0`, `TEMPORARY_HOLD=1`, `PERMANENT_HOLD=2`, `AWAY=6`, `STANDBY=7`, `ECO=10` |
| `SystemMode` | `AUTO=1`, `COOL=3`, `HEAT=4`, `EMERGENCY_HEAT=5` |
| `RunningState` | `IDLE=0`, `HEATING=1`, `COOLING=2`, `FAN_COIL_HEATING=33`, `FAN_COIL_COOLING=66` |
| `FanMode` | `OFF=0`, `LOW=1`, `MEDIUM=2`, `HIGH=3`, `AUTO=5` |
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
5. Add tests for valid payloads, missing fields, malformed data, and callback
   behavior.
6. Keep write command values in `salus_it600.const` or model-specific constants;
   do not introduce new magic integers inline.
