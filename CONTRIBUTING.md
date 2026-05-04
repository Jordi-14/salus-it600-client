# Contributing

This document covers development, testing, and pull-request preparation for
`salus-it600-client`.

Public repositories:

- Client package: `https://github.com/Jordi-14/salus-it600-client`
- Home Assistant integration: `https://github.com/Jordi-14/homeassistant_salus`

Package usage lives in [README.md](README.md). Release policy lives in
[RELEASE.md](RELEASE.md). Low-level payload notes live in
[docs/device-protocol.md](docs/device-protocol.md). Historical upstream issue
notes live in [docs/upstream-issues.md](docs/upstream-issues.md).

## Repository Boundary

This repository contains the Python client:

- gateway connection and encrypted requests;
- Salus payload parsing;
- device models;
- public gateway read/write methods;
- low-level command behavior.

Home Assistant config flows, entities, translations, diagnostics, and repairs
belong in `homeassistant_salus`. If Home Assistant needs a new protocol feature,
add a narrow public client method here and test the request payload here.

## Fork Workflow

If you do not have permission to push branches to `Jordi-14/salus-it600-client`,
fork the repository and push your feature branch to your fork. Open the pull
request back to `Jordi-14/salus-it600-client`.

Some client tests require a temporary `homeassistant_salus` branch. If you do
not have permission to push to `Jordi-14/homeassistant_salus`, fork that
repository too and push the temporary integration test branch to your fork.

The branch-testing examples use owner placeholders:

- `<client-owner>`: `Jordi-14` for maintainers, or your GitHub username for
  client fork branches.
- `<integration-owner>`: `Jordi-14` for maintainers, or your GitHub username for
  integration fork branches.

## Local Checks

Install development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Run these before opening a pull request:

```bash
python3 -m ruff check salus_it600 tests main.py
python3 -m mypy
python3 -m pytest -q
python3 -m coverage run -m pytest
python3 -m coverage report
python3 -m compileall -q salus_it600 tests main.py
python3 -m build
python3 -m twine check dist/*
```

## Architecture

Device detection and parsing uses a layered pipeline:

```text
poll_status() readall request
  -> extract device-family summaries
  -> deviceid request for detailed payloads
  -> family parser in salus_it600/parsers/
  -> immutable public model
  -> internal device dictionaries and callbacks
```

Device families are identified by protocol signatures in the JSON payloads:

- **Climate:** `sIT600TH` or `sTherS`.
- **Binary sensor:** `sIASZS`, or relay model IDs.
- **Sensor:** `sTempS.MeasuredValue_x100`.
- **Switch:** `sOnOffS.OnOff`.
- **Cover:** `sLevelS.CurrentLevel`.

The gateway is sensitive to concurrent local commands, so encrypted gateway
requests are serialized with one `asyncio.Lock`.

## Adding Device Support

1. Capture a `main.py --debug` payload from a real gateway and redact private
   data before sharing it.
2. Identify the readall signature and detailed `deviceid` payload fields.
3. Add or update model constants and classification helpers in
   `salus_it600/device_models.py`.
4. Add or update the matching parser under `salus_it600/parsers/`.
5. Register the parser in `poll_status()` or an existing refresh method.
6. Add tests for valid payloads, missing optional fields, malformed required
   fields, callbacks, and write-command state transitions if commandable.
7. Confirm the Home Assistant mapping still works when the device is expected
   to appear in Home Assistant.

Use [docs/device-protocol.md](docs/device-protocol.md) for payload field notes.

## Design Rules

Parsers should prefer partial device snapshots over dropping a device entirely
when the missing field is optional. Required identity fields, such as `UniID`,
can still reject malformed payloads. Optional telemetry, such as current
temperature, should become `None` when the gateway does not provide it.

When a payload needs a defensive fallback, add a focused test that captures the
exact malformed or partial payload shape. Avoid broad behavior changes without a
fixture that explains why the parser needs the fallback.

The public device models remain `NamedTuple` classes for now. They are immutable
enough for callers, support the existing `_replace()` test and update pattern,
and avoid migration churn that does not currently remove parser complexity.

Keep raw gateway details out of Home Assistant entity classes. When an
integration needs protocol behavior that is not exposed by the client, add a
narrow public gateway method here.

Do not infer write payloads from UI names alone. Gateway command mistakes can
change heating or cooling behavior on real systems.

## SQ610 Notes

SQ610 thermostats have protocol quirks that should stay centralized in the
client:

- humidity is reported through `sIT600TH.SunnySetpoint_x100`;
- heating and cooling setpoints are separate;
- hold type `0` returns the thermostat to the Salus schedule;
- raw SQ610 write property names should stay private to `gateway.py`.

Home Assistant should use semantic methods such as:

```python
await gateway.set_climate_device_temperature("thermostat_id", 21.5)
await gateway.set_climate_device_mode("thermostat_id", "cool")
await gateway.set_climate_device_preset("thermostat_id", "Follow Schedule")
```

## Testing Client Changes With Home Assistant

Client changes can be tested in Home Assistant before publishing a PyPI release.
Run the local client checks first, then choose one of these approaches.

### Home Assistant Core Or Developer Environment

Use this when you control the Home Assistant Python environment.

```bash
python3 -m build
/path/to/homeassistant/python -m pip install --force-reinstall \
  "/path/to/salus-it600-client/dist/salus_it600_client-"*.whl
```

Restart Home Assistant and verify which client was imported:

```bash
/path/to/homeassistant/python -c \
  "import salus_it600; print(salus_it600.__version__, salus_it600.__file__)"
```

### Home Assistant OS Or Managed Environments

Use this when you cannot directly install a wheel into the Home Assistant Python
environment.

Create a temporary branch in `homeassistant_salus`:

```bash
git clone https://github.com/<integration-owner>/homeassistant_salus
cd homeassistant_salus
git switch -c test-client-branch
```

In that temporary branch only, point `custom_components/salus/manifest.json` at
the client feature branch:

```json
"requirements": [
  "salus-it600-client @ git+https://github.com/<client-owner>/salus-it600-client.git@<client-branch>"
]
```

Push the temporary integration branch, then install it manually in the test Home
Assistant config:

```bash
cd /config
mkdir -p custom_components
if [ -d custom_components/salus ]; then
  mv custom_components/salus custom_components/salus.backup-YYYYMMDDHHMM
fi
git clone --depth 1 --branch <temporary-integration-branch> \
  https://github.com/<integration-owner>/homeassistant_salus salus-branch-test
cp -R salus-branch-test/custom_components/salus custom_components/salus
```

Restart Home Assistant after changing custom component files or dependencies.
Reloading the config entry is not enough for dependency changes.

Do not merge or release a manifest that points at a Git branch. The real
integration release must pin a published `salus-it600-client` version.

## Testing Both Repositories Together

Use this when client and integration branches must be validated together before
either PR is merged.

1. Run the client checks on the client feature branch.
2. Run the integration checks on the integration feature branch.
3. Create a temporary test branch from the integration feature branch.
4. In that temporary branch, set the manifest requirement to the client branch
   using the Git requirement format above.
5. Push the temporary integration branch.
6. Install it manually in the test Home Assistant config.
7. Restart Home Assistant and run a real-gateway smoke test.
8. Delete or discard the temporary test branch after testing.

After the client PR is merged and `salus-it600-client` is published, switch the
integration manifest back to the published package pin before opening or merging
the integration PR.

## Real-Gateway Checklist

At minimum, verify:

- Home Assistant starts without dependency or custom component errors.
- The Salus config entry reloads cleanly.
- Entities become available after polling.
- One safe command succeeds.
- Diagnostics download works.
- Logs contain no raw tracebacks, dependency install failures, duplicate entity
  warnings, unclosed sessions, or repeated polling failures.
