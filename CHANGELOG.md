# Changelog

## Unreleased

- Add it600MINITRV entities: the TRV's own temperature (decoded from
  `sIT600I.CommandResponse_d`), RSSI and LQI diagnostic sensors, and a problem
  binary sensor for the `TRVError01`/`23`/`30`/`31` fault flags. The TRV
  temperature is decoded for both paired and unpaired TRVs, and keeps its last
  reading when a poll omits the report, as the
  signal sensors already do. it600Receiver also gets RSSI and LQI sensors when
  its payload carries them.
- The it600MINITRV heat sensor's attributes name the paired thermostat
  (`paired_thermostat_short_id`, plus `paired_thermostat_id` and
  `paired_thermostat_name` when that thermostat is on the same gateway).
- Add `IT600Gateway.set_mini_trv_mode()` and the `MiniTrvMode` enum to set an
  it600MINITRV to Auto, Manual On (open) or Manual Off (closed). The reported
  `sIT600I.Mode` is exposed as `BinarySensorDevice.mini_trv_mode`.
- Export `decode_mini_trv_report()`, `MiniTrvReport` and `device_short_id()`
  from `salus_it600.parsers`.

## 0.7.0 - 2026-10-26

- Promote the tested 0.7.0b1 beta to stable with no runtime changes.

## 0.7.0b1 - 2026-10-22

Breaking changes (release as 0.7.0):

- Remove the unused update-callback API (`add_*_update_callback()` and
  `poll_status(send_callback=...)`). Call `poll_status()` and read the
  `get_*_devices()` caches instead.

Improvements:

- Add `IT600ValidationError` (also a `ValueError`) for command arguments the
  target device does not support, and `IT600DeviceNotFoundError` (also a
  `KeyError`) for device IDs missing from the cache. Existing `except
  ValueError` / `except KeyError` handlers keep working. `IT600Error` and both
  new exceptions are exported from `salus_it600`.
- `connect()` reuses an already-detected protocol instead of probing again.
- Fetch every device's details in one `deviceid` request per poll instead of
  one per device family (usually 2 requests per poll instead of up to 9). If
  the gateway rejects the combined request, leaves devices out, or drops it 3
  times in a row, the client goes back to per-family requests and logs this
  once at info level. `IT600Gateway.combined_detail_requests` shows which mode
  is active.
- Retry read requests once after the gateway drops the connection, as writes
  already were.
- Log timeouts, rejected commands and invalid JSON at debug level; the raised
  exceptions carry the detail. Log a device parse failure's traceback once,
  then at debug level, and warn about implausible SQ610 humidity only once.
- Use the vendor's fault descriptions for the it600WC wiring centre registers.

## 0.6.2 - 2026-10-07

- Add RSSI and LQI diagnostic sensors for thermostats, retaining the last reading
  when a poll omits these fields and following the parent device's availability.
- Add diagnostic-only connectivity, fault, RSSI and LQI data for it600WC wiring
  centres.
- Decode SQ610 advanced settings into a typed read-only model. PIN bytes and
  unverified fields remain excluded, with no write path.

## 0.6.1 - 2026-06-28

Bug fixes:

- Treat `RunningState` as a bitmask when deriving active heat/cool state, so
  FC600 fan-stage values such as `6`, `34`, and `66` report cooling instead of
  idle.
- Cover additional FC600 values observed during beta testing, including
  `129`/`193` for heat demand and `192` for no demand.

## 0.6.0 - 2026-05-23

Device support:

- Add SQ610 Away hold support.
- Report SQ610 and FC600 temporary schedule overrides as `Schedule Override`.
- Expose `Schedule Override` only while the gateway reports hold type `1`;
  selecting it is treated as a reported-state no-op rather than a command.

## 0.5.1 - 2026-05-08

Best-practice hardening:

- Use aiohttp response context managers with explicit per-request
  `ClientTimeout` handling for gateway probes, protocol detection, and
  encrypted command requests.
- Replace protocol-detection string matching with typed protocol errors for
  rejected or unsupported frames, HTTP errors, decrypt failures, and invalid
  decrypted responses.
- Make the demo CLI read-only by default, require `--yes` for write commands,
  and document the safe read-only and explicit write flows.
- Mark the package as typed with `py.typed` and include the marker in wheel and
  source distributions.

## 0.5.0 - 2026-05-04

Normalized climate model:

- Expose one richer `ClimateDevice` model for SQ610, FC600, TRV, and standard
  thermostats, including hold/system/running state, heat/cool setpoints,
  active ranges, controls, cooling capability source, online status, and
  whitelisted diagnostic fields.
- Route generic climate temperature, mode, preset, and lock writes through the
  correct device-family protocol path, removing the SQ610-specific public write
  methods.
- Select active heat/cool setpoints and ranges through shared normalized helper
  logic so all thermostat families follow the same rules where their protocol
  data overlaps.
- Treat `CoolingControl: 0` as valid proof that an SQ610 supports cooling; the
  value means cooling control is currently inactive, not unsupported.
- Include shared climate support fields for diagnostics across thermostat
  families without requiring Home Assistant to call `fetch_sq610_properties()`
  during normal polling.

## 0.4.9 - 2026-05-03

Bug fixes:

- Parse SQ610/SQ610NH keypad lock state from `sIT600TH.LockKey` so Home
  Assistant can create lock entities for Quantum thermostats.
- Send SQ610/SQ610NH keypad lock writes through `sIT600TH.SetLockKey` instead
  of the FC600-style `sTherUIS` path.

## 0.4.8 - 2026-05-03

Device support:

- Treat SR600 as a dry relay switch instead of a cover device.
- Keep RS600 cover payloads as covers while preserving separate RS600 relay
  endpoints as switches when the gateway exposes them.
- Allow SR600 relay payloads that also include level data to parse as switches
  rather than being skipped as cover-like payloads.

## 0.4.7 - 2026-05-03

Device support:

- Add ECM600 energy meter parsing from `sMeterS` payloads, exposing per-endpoint
  power, energy, and diagnostic battery sensors.
- Treat FC600 model variants such as `FC600NH` as fan-coil thermostats for
  parsing and climate write commands.

## 0.4.6 - 2026-05-02

Bug fixes:

- Send FC600 fan mode writes as `sFanS.SetFanMode`, matching the official
  Salus local app payload.

## 0.4.4 - 2026-04-29

Device metadata:

- Mark RS600/SR600 cover devices as Home Assistant `shutter` covers.

## 0.4.3 - 2026-04-29

P3 command reliability:

- Retry a transient gateway server disconnect once for encrypted write requests.
  Read requests are not retried, and writes still fail after the single retry.

## 0.4.2 - 2026-04-29

P2 maintainability:

- Add higher-level SQ610 client write methods for setpoint, HVAC mode, and
  preset/hold state so Home Assistant does not need to pass raw gateway
  property names.
- Remove the public raw SQ610 property write helper; SQ610 writes now go through
  semantic client methods only.
- Split gateway detail payload parsing into device-family modules under
  `salus_it600.parsers`.
- Add realistic JSON payload fixtures and parser regression tests for SQ610,
  FC600, TRV3RF, WLS600, TS600, SPE600, and RS600 devices.
- Document the model-shape decision to keep public device models as
  `NamedTuple` classes for now.

## 0.4.1 - 2026-04-29

P1 near-term hardening:

- Normalize ongoing gateway request failures before decrypting responses:
  non-200 HTTP responses now raise `IT600ConnectionError`, fixed-length gateway
  protocol frames now raise `IT600UnsupportedFirmwareError`, and decrypt
  failures now raise `IT600CommandError`.
- Add unit coverage for ongoing request HTTP errors, protocol frames, and
  decrypt failures.
- Add a GitHub issue form for client protocol, parsing, and command support
  reports.

P0 release hardening for the current `salus-it600-client 0.4.0` client line.

- Require the full Ruff check in CI instead of only syntax-critical rules.
- Require strict mypy in CI and the PyPI publish workflow.
- Tighten protocol connect typing by validating decrypted protocol responses
  are JSON objects before returning them.
