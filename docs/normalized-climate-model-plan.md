# Normalized Climate Model Plan

## Goal

Refactor climate parsing so the client exposes a richer normalized thermostat
model instead of collapsing every device into the current smallest common
shape. The end state must preserve every feature currently exposed by the
client and Home Assistant integration, while removing the need for Home
Assistant to re-fetch raw SQ610 properties after each poll.

This branch does not need public API backwards compatibility. Prefer a clean,
well-typed model that future volunteer maintainers can understand over adapter
layers that preserve old positional construction, transitional fallbacks, or
legacy SQ610-specific public methods. Preserve old behavior, names, or wrappers
only when doing so does not make the implementation or future maintenance even
slightly harder.

The protocol-specific payload paths should remain inside the client:

- FC600 reads and writes use `sTherS`, `sComm`, `sFanS`, and `sTherUIS`.
- SQ610 reads and writes use `sIT600TH`.
- TRV-style devices use `sTherS` plus `sComm`.
- Older iT600 thermostats use `sIT600TH`.

Above those protocol adapters, callers should see one normalized climate model.

## Current Problem

The current `ClimateDevice` model has only one active target temperature and
one min/max range. That works for heat-only devices, but it loses information
for richer devices:

In this plan, a protocol path such as `sIT600TH` or `sTherS` means the named
gateway payload section that contains device-specific raw register names. A
normalized field is the caller-facing value derived from those registers, such
as `current_humidity` rather than `SunnySetpoint_x100`. SQ610 currently gets
those richer values by asking Home Assistant to re-fetch and flatten the raw
`sIT600TH` detail payload. For example, SQ610 humidity is currently recovered
from `sIT600TH.SunnySetpoint_x100`, even though callers should only need a
normalized humidity field.

- SQ610 has `SystemMode`, `HeatingSetpoint_x100`, `CoolingSetpoint_x100`,
  `HoldType`, `RunningState`, current-temperature fields, humidity, lock state,
  battery diagnostics, online status, and optional floor-probe data.
- FC600 has `SystemMode`, separate heat/cool setpoints, `HoldType`, fan mode,
  lock state, and fan-coil running states.

FC600 is parsed through a richer device-family path, but SQ610 is parsed through
the generic `sIT600TH` path and then patched in Home Assistant with an extra raw
detail request. That makes SQ610 look much more special than it should.

## Non-Negotiable Behavior Parity

Do not merge the implementation until these current behaviors still work:

- Standard iT600 thermostats expose heat/off/auto style behavior.
- SQ610 exposes heat/off, conditional cooling, Follow Schedule, Permanent Hold,
  humidity, floor temperature, battery, problem sensors, child lock, current
  action, and separate heating/cooling setpoints when available.
- FC600 exposes heat/cool/off behavior, Follow Schedule, Permanent Hold, Eco,
  fan modes, child lock, current action, and separate heating/cooling setpoints.
- FC600 variants such as `FC600NH` continue to use the fan-coil path.
- TRV3RF exposes heat/off/auto behavior, valve opening, battery, problem state,
  open-window state, and setpoint control.
- Home Assistant entity and device identifiers should stay stable when that is
  free or nearly free: climate IDs, lock IDs, and child IDs such as `_humidity`,
  `_floor_temperature`, `_battery`, `_problem`, `_battery_error`, and
  `_open_window`. If a cleaner physical-device model requires an identifier
  change, document that as an intentional breaking migration rather than adding
  adapter code.
- Home Assistant-facing convenience fields such as `current_temperature`,
  `target_temperature`, `min_temp`, `max_temp`, `hvac_mode`, `hvac_action`,
  `hvac_modes`, `preset_mode`, `preset_modes`, `fan_mode`, `fan_modes`,
  `locked`, `current_humidity`, and
  `extra_state_attributes` are still available where they are useful, but they
  are derived from the normalized state rather than treated as
  backwards-compatibility constraints.

## Proposed Model Additions

Replace the old narrow `ClimateDevice` shape with a maintainable normalized
state model. A frozen dataclass with keyword construction is preferred over a
large positional `NamedTuple`; if `NamedTuple` stays temporarily, do not optimize
for old positional callers.

Candidate additions:

```python
hold_type: int | None = None
system_mode: int | None = None
running_state: int | None = None

heating_setpoint: float | None = None
cooling_setpoint: float | None = None

min_heat_temp: float | None = None
max_heat_temp: float | None = None
min_cool_temp: float | None = None
max_cool_temp: float | None = None

heating_control: int | None = None
cooling_control: int | None = None

supports_cooling: bool = False
supports_fan: bool = False
supports_heat: bool = True

online_status: int | None = None
cooling_capability_source: str | None = None
diagnostic_fields: dict[str, Any] | None = None
```

Convenience fields should be derived from these values:

- `target_temperature`: active heating or cooling setpoint based on
  `system_mode`.
- `min_temp` and `max_temp`: active heat/cool range based on `system_mode`.
- `hvac_mode`: Home Assistant-facing normalized mode.
- `preset_mode`: Home Assistant-facing normalized hold state.

Command validation should use the same active range derivation as the
convenience fields. A cooling setpoint write must validate against
`min_cool_temp` / `max_cool_temp`, while a heating setpoint write validates
against `min_heat_temp` / `max_heat_temp`. Do not keep the old single-range
validation if it makes heat/cool routing ambiguous.

If the model is a frozen dataclass, avoid mutable defaults and avoid exposing
mutable internals by accident. Prefer tuples for mode lists where practical, and
copy or intentionally document any nested payload dictionaries that remain
mutable, such as `data` and `diagnostic_fields`.

SQ610 cooling support must not be inferred from `CoolingSetpoint_x100` alone:
known heat-only payloads can still include cooling setpoint/range fields. Prefer
`CoolingControl`, active cool `SystemMode`, active cool `RunningState`, or a
model/fixture signal that proves cooling is usable.

`cooling_capability_source` should be a small documented vocabulary rather than
an arbitrary string. Suggested values:

- `cooling_control`: `CoolingControl` proves cooling is available.
- `active_system_mode`: current `SystemMode` is cool.
- `active_running_state`: current `RunningState` is cooling.
- `known_model`: a fixture-backed model identifier proves cooling support.
- `none`: no reliable cooling capability signal was observed.

`diagnostic_fields` should also be a documented whitelist of non-sensitive
support fields, not a flattened raw payload. Include only fields that Home
Assistant diagnostics or support workflows actually need, such as `SystemMode`,
`RunningState`, `HoldType`, `LockKey`, `LockKey_a`, `HeatingControl`,
`CoolingControl`, and `OnlineStatus_i`.

Missing values should have explicit semantics:

- Missing `HoldType` may continue to fall back to Permanent Hold if that keeps
  broken payloads loadable, but this should be implemented in one helper and
  logged only once per device.
- Missing `SystemMode` should not imply cooling or auto support.
- Missing `RunningState` should mean idle/unknown according to the device family,
  without hiding standby/off state when `HoldType` is present.
- Missing setpoints or ranges should use device-family defaults only as
  last-resort convenience values; the normalized raw field should remain `None`
  so callers can distinguish real data from fallback behavior.

## Implementation Phases

1. Add model fields and helper tests.
   - Convert `ClimateDevice` to a keyword-friendly typed model, or at minimum
     stop relying on positional construction in tests and parsers.
   - Replace test/helper use of `NamedTuple._replace()` with dataclass-friendly
     construction or a small fixture helper.
   - Add small helper functions for setpoint/range derivation.
   - Add helper functions for SQ610 cooling capability detection.
   - Add helper functions for missing/unknown hold, system, running, setpoint,
     and range values so each parser does not invent its own fallback behavior.
   - Decide whether mode lists are tuples and whether payload dictionaries are
     copied before storing them on frozen model instances.
   - Keep existing tests green before changing parser behavior.

2. Split SQ610 parsing from generic `sIT600TH` parsing.
   - Add an internal SQ610 parser path selected by `is_sq610_model(model)`.
   - Populate the richer normalized fields from `sIT600TH`.
   - Preserve humidity parsing from `SunnySetpoint_x100`.
   - Populate `HeatingControl` and `CoolingControl` when present.
   - Preserve current-temperature fallback from `LocalTemperature_x100` to
     `MeasuredValue_x100`.
   - Preserve floor temperature, battery, lock, and problem child sensors.
   - Expose support/diagnostic fields needed by Home Assistant diagnostics,
     including online status and raw support fields such as `SystemMode`,
     `RunningState`, `HoldType`, `LockKey`, and `LockKey_a`, without requiring
     `fetch_sq610_properties()`.
   - Expose normalized active range fields so Home Assistant does not need to
     know whether heat or cool range is currently active.
   - Do not treat `CoolingSetpoint_x100`, `MinCoolSetpoint_x100`, or
     `MaxCoolSetpoint_x100` as cooling-capability proof by themselves.

3. Normalize FC600 parsing into the same richer fields.
   - Populate `hold_type`, `system_mode`, `running_state`, heat/cool setpoints,
     heat/cool min/max ranges, fan fields, lock state, and derived convenience
     fields.
   - Ensure `is_fan_coil_model()` covers `FC600NH` and similar variants.

4. Normalize TRV and standard thermostat parsing.
   - Populate heat-only normalized fields where available.
   - Keep unsupported fields as `None` or `False`.

5. Move generic climate writes toward semantic routing.
   - Let `set_climate_device_temperature()` choose heat/cool writes using the
     normalized active mode for both FC600 and SQ610.
   - Validate writes against the matching heat or cool range before sending the
     gateway command.
   - Let `set_climate_device_mode()` route SQ610 heat/cool writes to
     `sIT600TH.SetSystemMode`, while standby/off remains a hold/preset write to
     `sIT600TH.SetHoldType`.
   - Let `set_climate_device_preset()` route SQ610 hold writes through
     `sIT600TH.SetHoldType` so Home Assistant does not need a special SQ610
     preset method.
   - Keep protocol write sections private to `gateway.py`.
   - Remove SQ610-specific public methods unless they remain clearly useful as
     small wrappers around the generic semantic methods.

6. Retire raw SQ610 property fetch from consumers.
   - Expose every field Home Assistant currently reads from
     `fetch_sq610_properties()` through `ClimateDevice`.
   - Delete `fetch_sq610_properties()` from normal workflows. If a raw fetch is
     still useful for support diagnostics, keep it as an explicit diagnostic
     helper that is not called during normal polling.
   - Keep any remaining diagnostic helper clearly outside the normal model path;
     it should not become a compatibility layer for missing normalized fields.

## Test Plan

Client tests must cover:

- Existing fixture tests for SQ610, FC600, TRV3RF, and standard thermostats.
- SQ610 heat mode uses heating setpoint and heat range.
- SQ610 cool mode uses cooling setpoint and cool range.
- SQ610 current temperature uses `LocalTemperature_x100` and falls back to
  `MeasuredValue_x100`.
- SQ610 scheduled heat/cool preserves `HoldType.FOLLOW_SCHEDULE`.
- SQ610 standby maps to off without losing the last active hold state for
  consumers that need resume behavior.
- SQ610 `RunningState.HEATING`, `RunningState.COOLING`, idle, standby, and
  `SystemMode.EMERGENCY_HEAT` map to correct actions/modes.
- SQ610 unknown hold/system/running values fall back predictably and log only
  where useful.
- SQ610 humidity accepts raw percent and x100 values.
- SQ610 cooling support respects `CoolingControl`/`HeatingControl` and does not
  treat `CoolingSetpoint_x100` by itself as proof of cooling capability.
- SQ610 heat-only payloads that include cooling setpoint/range fields still do
  not expose cooling unless another capability signal proves it.
- SQ610 missing `HoldType`, `SystemMode`, `RunningState`, setpoints, or ranges
  follow the documented fallback semantics.
- SQ610 lock state reads from `sIT600TH.LockKey` and writes
  `sIT600TH.SetLockKey`.
- SQ610 generic mode, preset, and temperature commands use the same `sIT600TH`
  write paths as the old SQ610-specific methods.
- SQ610 heat and cool temperature writes validate against the matching heat/cool
  min/max range.
- SQ610 diagnostic/support fields needed by Home Assistant are present without
  calling `fetch_sq610_properties()`.
- FC600 and FC600NH heat/cool setpoint writes still use `sTherS`.
- FC600 fan mode writes still use `sFanS.SetFanMode`.
- TRV writes still use `sComm`/`sTherS` as appropriate.
- Climate, lock, and child entity identifiers remain stable where that does not
  add adapter complexity; any intentional identifier change is documented as a
  breaking migration.

## Migration Safety

Implement this in small commits. Since this branch is a clean replacement, delete
obsolete compatibility paths once their normalized replacements are tested. After
each phase, run:

```bash
pytest
ruff check .
mypy
```

Do not merge until the integration branch consumes the normalized fields and no
normal Home Assistant state path depends on raw SQ610 polling.

Before release, update `device-protocol.md`, the README/changelog, and the
package version so the new model contract and any remaining diagnostic raw-fetch
helper are documented together.
