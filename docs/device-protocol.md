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
| `sIT600WC.Error10`..`Error20`, `Error26`..`Error29` | Fault register bank. Meanings are not documented anywhere the client has found; the parser reports them by register name (see `THERMOSTAT_ERROR_CODES` in `salus_it600/const.py`, shared with the thermostat-side Error01-32 codes) |
| `sIT600WC.ErrorCodeWC_d` | Hex-string summary fault code, `"0000"` at baseline. `bool("0000")` is `True` in Python -- check `str(value).strip("0")` instead, the same pattern `parse_climate_binary_sensor_devices` uses for `sComm.DeviceErrorCode` |

## Protocol Enums

Use the enums in `salus_it600.const` rather than raw integers:

| Enum | Values |
| --- | --- |
| `HoldType` | `FOLLOW_SCHEDULE=0`, `TEMPORARY_HOLD=1`, `PERMANENT_HOLD=2`, `AWAY=6`, `STANDBY=7`, `ECO=10` |
| `SystemMode` | `AUTO=1`, `COOL=3`, `HEAT=4`, `EMERGENCY_HEAT=5` |
| `RunningState` | `IDLE=0`, `HEATING=1`, `COOLING=2`, `FAN_COIL_HEATING=33`, `FAN_COIL_COOLING=66` |
| `FanMode` | `OFF=0`, `LOW=1`, `MEDIUM=2`, `HIGH=3`, `AUTO=5` |

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
