# salus-it600-client

Asynchronous Python client for Salus iT600 devices.

## For end users
See https://github.com/Jordi-14/homeassistant_salus to use this in Home Assistant.

## About

This package allows you to control and monitor your Salus iT600 smart home devices locally through Salus UG600 universal gateway. Currently heating thermostats, binary sensors, temperature sensors, covers and switches are supported. You have any other devices and would like to contribute - you are welcome to create an issue or submit a pull request.

## Installation

```bash
pip install salus-it600-client
```

## Migration from `pyit600`

`salus-it600-client` is a renamed maintained successor of `pyit600`. It does
not provide the old `pyit600` import namespace, so callers must update imports:

```python
from salus_it600.gateway import IT600Gateway
from salus_it600.exceptions import IT600ConnectionError
```

If another project depends on this package, replace the old dependency with:

```text
salus-it600-client>=0.1.0
```

The first maintained release is `0.1.0`. It keeps the public API close to
`pyit600 0.5.1`, while moving compatibility fixes for current Salus gateway
payloads into this library.

## Usage
 - Instantiate the IT600Gateway device with local ip address and EUID of your gateway. You can find EUID written down on the bottom of your gateway (eg. `001E5E0D32906128`).
 - Status can be polled using the `poll_status()` command.
 - Callbacks to be notified of state updates can be added with the `add_climate_update_callback(method)` or `add_sensor_update_callback(method)` method.

### Basic example

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

		print(f"Setting heating device {climate_device_id} temperature to 21 degrees celsius")
		await gateway.set_climate_device_temperature(climate_device_id, 21)
```

### Supported devices

Thermostats:
* HTRP-RF(50)
* TS600
* VS10WRF/VS10BRF
* VS20WRF/VS20BRF
* SQ610
* SQ610RF
* FC600

Binary sensors:
* SW600
* WLS600
* OS600
* SD600 (sometimes gateway may not expose required information for these devices to be detected, reason is unknown)
* TRV10RFM (only heating state on/off)
* RX10RF (only heating state on/off)

Temperature sensors:
* PS600

Switch devices:
* SPE600
* RS600
* SR600

Cover devices:
* RS600

### Unsupported devices

Buttons perform actions only in Salus Smart Home app:
* SB600
* CSB600

### Untested devices

These switch devices have not been tested, but may work:
* SP600

These binary sensors have not been tested, but may work:
* MS600

### Troubleshooting

If you can't connect using EUID written down on the bottom of your gateway (which looks something like `001E5E0D32906128`), try using `0000000000000000` as EUID.

Also check if you have "Local Wifi Mode" enabled:
* Open Smart Home app on your phone
* Sign in
* Double tap your Gateway to open info screen
* Press gear icon to enter configuration
* Scroll down a bit and check if "Disable Local WiFi Mode" is set to "No"
* Scroll all the way down and save settings
* Restart Gateway by unplugging/plugging USB power


## Extending Device Support

### Architecture Overview

Device detection and parsing uses a layered pipeline:

```
poll_status() readall request
    ↓
Extract device-type-specific summaries (lambda filters)
    ↓
For each type: _refresh_device_collection()
    ├─ Make "deviceid" request for detailed payloads
    ├─ Validate gateway response
    ├─ Call type-specific parser for each device
    ├─ Catch parsing errors, log, continue
    └─ Update internal device dicts + callbacks
```

Detailed protocol notes are maintained in
[docs/device-protocol.md](docs/device-protocol.md).

Device models are identified by **protocol signatures** in the JSON payloads:

- **Climate**: `sIT600TH` or `sTherS` section present
- **Binary sensor**: `sIASZS` section, or model in `BINARY_RELAY_MODELS`
- **Sensor**: `sTempS.MeasuredValue_x100` present
- **Switch**: `sOnOffS.OnOff` present
- **Cover**: `sLevelS.CurrentLevel` present

### Adding a New Device Model

#### Step 1: Identify Protocol Signature

Use `main.py --debug` to capture a readall response. Find your device in the JSON output and note which payload sections it contains.

Example: A window contact sensor contains `sIASZS.ErrorIASZSAlarmed1` → binary sensor.

#### Step 2: Add Model to Registry

Edit `salus_it600/device_models.py`:

```python
# Define model identifier
MODEL_MYDEVICE = "MyDevice123"

# Add to classification if needed
BINARY_SENSOR_DEVICE_CLASSES = {
    # ...existing...
    MODEL_MYDEVICE: "custom_class",  # Use Home Assistant device class
}
```

#### Step 3: Create Parser Function

Add to the matching device-family module under `salus_it600/parsers/`:

```python
def _parse_mydevice_device(device_status: dict[str, Any]) -> MyDeviceModel | None:
    """Parse one MyDevice from gateway payload.
    
    Protocol fields:
    - `MyPayloadSection.StateField`: What this means (divide by what)
    
    Returns:
        MyDeviceModel or None if invalid/filtered
    """
    unique_id = device_status.get("data", {}).get("UniID")
    if unique_id is None:
        return None
    
    state_field = device_status.get("MyPayloadSection", {}).get("StateField")
    if state_field is None:
        return None
    
    return MyDeviceModel(
        **_common_device_args(device_status, unique_id),
        # device-specific fields...
    )
```

#### Step 4: Register Parser in Poll Loop

In `salus_it600/gateway.py`, update `poll_status()` or the relevant refresh
method if the new device needs a new payload filter:

```python
# Add filter for your device type
my_devices = list(
    filter(lambda x: "MyPayloadSection" in x, device_items)
)

# Connect to refresh pipeline
await self._refresh_device_collection(
    my_devices,
    device_type="mydevice",
    state_attr="_mydevice_devices",
    parser=_parse_mydevice_device,
    callback=self._send_mydevice_update_callback,
    send_callback=send_callback,
)
```

#### Step 5: Add Callback Methods

```python
async def add_mydevice_update_callback(
    self,
    method: Callable[[Any], Awaitable[None]],
) -> None:
    """Add listener for MyDevice state updates."""
    self._mydevice_update_callbacks.append(method)

async def _send_mydevice_update_callback(self, device_id: str) -> None:
    """Notify MyDevice update subscribers."""
    for callback in self._mydevice_update_callbacks:
        await callback(device_id=device_id)

def get_mydevice_devices(self) -> dict[str, MyDeviceModel]:
    """Return all MyDevice devices."""
    return self._mydevice_devices

def get_mydevice_device(self, device_id: str) -> MyDeviceModel | None:
    """Return one MyDevice device."""
    return self._mydevice_devices.get(device_id)
```

#### Step 6: Add Tests

Create `tests/test_mydevice.py`:

```python
async def test_parse_mydevice_valid():
    """Parse valid MyDevice payload."""
    payload = {
        "data": {"UniID": "device-1"},
        "MyPayloadSection": {"StateField": 123},
        # ...minimal required fields...
    }
    device = _parse_mydevice_device(payload)
    assert device is not None
    assert device.unique_id == "device-1"

async def test_parse_mydevice_missing_field():
    """Skip MyDevice with missing required field."""
    payload = {"data": {"UniID": "device-1"}}  # Missing MyPayloadSection
    device = _parse_mydevice_device(payload)
    assert device is None

async def test_refresh_mydevice_collection():
    """Refresh MyDevice via _refresh_device_collection."""
    # Use FakeSession, mock _make_encrypted_request, verify parsing
```

### SQ610 Quantum Thermostat Special Handling

SQ610 thermostats have unusual protocol features. **These are already handled by the library**, but here's what makes them special:

#### Humidity in Wrong Field

SQ610 doesn't report humidity normally. Instead, humidity is in `sIT600TH.SunnySetpoint_x100`:

```python
# Library does this automatically for SQ610:
if is_sq610_model(model):
    humidity = th.get("SunnySetpoint_x100") / 100
else:
    humidity = None
```

#### Dual Setpoints

SQ610 has separate heating and cooling setpoints depending on system mode:

```python
# iT600 (simple): Always use HeatingSetpoint_x100
# SQ610 (complex): Use Heating OR Cooling depending on SystemMode
is_heating = ther["SystemMode"] == 4
target = ther["HeatingSetpoint_x100"] if is_heating else ther["CoolingSetpoint_x100"]
```

#### Hold Type Extension

SQ610 supports hold type 0 (auto return to schedule), unavailable on standard models:

```python
SQ610_HOLD_AUTO = 0        # Return to schedule
SQ610_HOLD_PERMANENT = 2   # Keep setpoint
SQ610_HOLD_STANDBY = 7     # Off
```

#### Client Write Methods

When commanding SQ610 devices, use the semantic gateway methods. Raw SQ610 write
property names are intentionally private to the client:

```python
await gateway.set_sq610_device_temperature("thermostat_id", 21.5)
await gateway.set_sq610_device_temperature("thermostat_id", 24.0, cooling=True)
await gateway.set_sq610_device_hvac_mode("thermostat_id", "cool")
await gateway.set_sq610_device_preset("thermostat_id", "Follow Schedule")
```

Read-side SQ610 protocol constants and classification helpers are centralized in
`salus_it600/device_models.py`. Raw write property names stay inside
`salus_it600/gateway.py` so integrations do not need protocol field knowledge.

### Contributing

If you want to help to get your device supported, open GitHub issue and add your device model number and output of `main.py` program. Be sure to run this program with --debug option.

### Development Checks

Install development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Run the local verification set before opening a PR:

```bash
python3 -m ruff check salus_it600 tests main.py
python3 -m mypy
python3 -m unittest
python3 -m coverage run -m unittest
python3 -m coverage report
```

The test suite covers request validation, device parsing, complete mocked
polling cycles, callbacks, and write-command state transitions.

Release publishing is documented in [RELEASE.md](RELEASE.md).

## Project origin

This project is a maintained fork/successor of `epoplavskis/pyit600`.
It was renamed from the `pyit600` Python import namespace to `salus_it600`
to avoid collisions with the original unmaintained package while preserving
the original MIT license and attribution.
