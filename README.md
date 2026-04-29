# salus-it600-client

Asynchronous Python client for Salus iT600 devices.

This package is maintained at
`https://github.com/Jordi-14/salus-it600-client`.

## For Home Assistant Users

Use `https://github.com/Jordi-14/homeassistant_salus` if you want the Home
Assistant integration. That integration installs this client package as a
dependency.

## About

This package allows Python applications to control and monitor Salus iT600 smart
home devices locally through a Salus gateway with Local WiFi Mode enabled.
Heating thermostats, TRV-style devices, binary sensors, temperature sensors,
covers, switches, and metering sensors are supported.

If you have another device and would like to contribute support, open an issue
or submit a pull request with redacted gateway diagnostics or `main.py --debug`
output.

## Installation

```bash
pip install salus-it600-client
```

## Migration From `pyit600`

`salus-it600-client` is a renamed maintained successor of `pyit600`. It does
not provide the old `pyit600` import namespace, so callers must update imports:

```python
from salus_it600.exceptions import IT600ConnectionError
from salus_it600.gateway import IT600Gateway
```

If another project depends on this package, replace the old dependency with:

```text
salus-it600-client>=0.1.0
```

The first maintained release is `0.1.0`. It keeps the public API close to
`pyit600 0.5.1`, while moving compatibility fixes for current Salus gateway
payloads into this library.

## Usage

Instantiate `IT600Gateway` with the local IP address and EUID of your gateway.
The EUID is normally printed on the bottom of the gateway, for example
`001E5E0D32906128`.

Status can be polled using `poll_status()`. Callbacks can be registered with
methods such as `add_climate_update_callback()` or
`add_sensor_update_callback()`.

### Basic Example

```python
from salus_it600.gateway import IT600Gateway

async with IT600Gateway(host=args.host, euid=args.euid) as gateway:
    await gateway.connect()
    await gateway.poll_status()

    climate_devices = gateway.get_climate_devices()

    print("All climate devices:")
    print(repr(climate_devices))

    for climate_device_id in climate_devices:
        print(f"Climate device {climate_device_id} status:")
        print(repr(climate_devices.get(climate_device_id)))

        print(f"Setting heating device {climate_device_id} temperature to 21 C")
        await gateway.set_climate_device_temperature(climate_device_id, 21)
```

## Supported Devices

Thermostats:

- HTRP-RF(50)
- TS600
- VS10WRF/VS10BRF
- VS20WRF/VS20BRF
- SQ610
- SQ610RF
- FC600

Binary sensors:

- SW600
- WLS600
- OS600
- SD600, when the gateway exposes the required information
- TRV10RFM, heating state only
- RX10RF, heating state only

Temperature sensors:

- PS600

Switch devices:

- SPE600
- RS600
- SR600

Cover devices:

- RS600
- SR600

## Unsupported Devices

Buttons perform actions only in the Salus Smart Home app:

- SB600
- CSB600

## Untested Devices

These switch devices have not been tested, but may work:

- SP600

These binary sensors have not been tested, but may work:

- MS600

## Troubleshooting

If you cannot connect using the EUID printed on the bottom of your gateway, try
using `0000000000000000` as the EUID.

Check that Local WiFi Mode is enabled:

1. Open the Salus Smart Home app.
2. Sign in.
3. Double tap your gateway to open the info screen.
4. Open the gateway settings.
5. Confirm `Disable Local WiFi Mode` is set to `No`.
6. Save settings.
7. Power-cycle the gateway.

## Development And Testing

Contributor documentation lives in [CONTRIBUTING.md](CONTRIBUTING.md).
It covers:

- parser architecture and device model extension;
- local quality checks;
- testing unreleased client changes with Home Assistant;
- coordinated client and integration branch testing before release;
- SQ610 protocol notes.

Release publishing is documented in [RELEASE.md](RELEASE.md).
Protocol notes live in [docs/device-protocol.md](docs/device-protocol.md).
Archived upstream issue notes for future maintenance live in
[docs/upstream-issues.md](docs/upstream-issues.md).

## Maintenance Notes

This package owns the reusable Salus gateway layer: connection handling,
encryption, request framing, protocol negotiation, payload parsing, device
models, and command payload construction.

Home Assistant config flows, entities, diagnostics, repairs, options,
translations, and HACS releases live in
`https://github.com/Jordi-14/homeassistant_salus`.

## Project Origin

This project is a maintained fork/successor of `epoplavskis/pyit600`.
It was renamed from the `pyit600` Python import namespace to `salus_it600`
to avoid collisions with the original unmaintained package while preserving
the original MIT license and attribution.

The maintained client also includes protocol and device-support work informed
by Leonard Pitzu's `https://github.com/leonardpitzu/homeassistant_salus` fork,
including UG800/new-firmware handling, broader parser coverage, TRV-related
state, SQ610-related behavior, smart-plug metering, and lock support. The goal
is to keep that low-level behavior reusable outside Home Assistant while the
Home Assistant integration exposes it through entities and UI.
