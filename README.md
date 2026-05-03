# salus-it600-client

An asynchronous Python client for **local** control and monitoring of [Salus iT600](https://salus-controls.com/) smart home devices through UGE600 or UG800 gateways — thermostats, TRVs, smart plugs, roller shutters, sensors, and more, all without cloud dependency.

## Features

### Climate (thermostats & TRVs)

| Device family | Capabilities |
|---|---|
| **iT600 / SQ610** | Heat/off/auto modes, Follow Schedule / Permanent Hold / Off presets, humidity (SQ610), floor temperature (external probe), battery level, 0.1 °C precision |
| **FC600 fan-coil** | Heat/cool/auto modes, five presets, fan modes (auto/high/medium/low/off), separate heating/cooling setpoints |
| **TRV3RF** | Heat/off/auto modes, valve opening %, battery (voltage curve), open-window detection, error code diagnostics |

### Sensors

| Sensor | Source |
|---|---|
| Temperature | Standalone sensors (TS600, PS600) and thermostat readings |
| Humidity | SQ610 (`SunnySetpoint_x100`) and standalone multi-sensors |
| Floor temperature | SQ610 with external floor probe (`OUTSensorProbe`) |
| Battery | Status_d (SQ610RF) and voltage curves (TRV, window/door sensors) |
| Power (W) | Smart plug (`sMeteringS`) and energy meter ECM600 (`sMeterS`) |
| Energy (kWh) | Smart plug (`sMeteringS`) and energy meter ECM600 (`sMeterS`) |

### Binary sensors

| Sensor | Source |
|---|---|
| Window / Door | SW600, OS600 (`sIASZS`) |
| Water leak | WLS600 |
| Smoke | SmokeSensor-EM |
| TRV relay (heat) | it600MINITRV (`sIT600I.RelayStatus`) |
| Receiver relay | it600Receiver |
| Low battery | Diagnostic child on battery-powered sensors and TRVs |
| Thermostat problem | Aggregated error flags (Error01–Error32) with descriptions |
| Battery problem | Battery-specific error flags (battery models only) |
| Open window | TRV open-window detection (`sComm.OpenWindowStatus`) |

### Covers

Roller shutters and blinds (RS600): open, close, set position (0-100 %).

### Switches

Smart plugs and relays (SP600, SPE600, SR600, and RS600 relay endpoints): on/off control. Dual-endpoint devices exposed as separate entities.

### RS600 / SR600 notes

RS600 is a multifunction physical device. Depending on gateway payloads and installation mode, it can expose a cover surface through `sLevelS` and separate relay switch endpoints through `sOnOffS`. The client keeps these capabilities separate so Home Assistant can decide how to present them.

SR600 is treated as a dry relay switch, not as a cover device. If an SR600 relay payload includes both `sOnOffS` and `sLevelS`, the relay state is still parsed as a switch and the payload is not exposed as a cover.

## Installation

```bash
pip install salus-it600-client
```

## Usage

```python
from salus_it600.gateway import IT600Gateway

async with IT600Gateway(host="192.168.1.100", euid="001E5E0D32906128") as gw:
    await gw.connect()
    await gw.poll_status()

    for device_id, device in gw.get_climate_devices().items():
        print(f"{device.name}: {device.current_temperature}°C → {device.target_temperature}°C")

    # Set temperature
    await gw.set_climate_device_temperature("device_001", 21.5)
```

## Encryption & protocol support

Salus gateways encrypt all local API traffic. The library **auto-detects** the correct protocol by trying each one in order during connection.

| | Legacy AES-CBC | AES-CCM (newer firmware) |
|---|---|---|
| **Gateways** | UGE600, older UG800 firmware | UG800 with newer firmware |
| **Cipher** | AES-256-CBC (fallback: AES-128-CBC) | AES-256-CCM (authenticated encryption) |
| **Key derivation** | `MD5("Salus-{euid}")` — static, derived from the gateway EUID | EUID bytes + hardcoded suffix — 32-byte key |
| **IV / nonce** | Fixed 16-byte IV | 8-byte random nonce (3 random + 2-byte counter + 3-byte timestamp) |
| **Authentication** | None | 8-byte MAC tag (CBC-MAC) |
| **Padding** | PKCS7 | None (CCM handles arbitrary lengths) |
| **Wire format** | Block-aligned encrypted HTTP body | `[ciphertext + 8-byte MAC][8-byte nonce]` |

Protocol auto-detection order:
1. **AES-256-CBC** — legacy iT600 / UGE600 gateways
2. **AES-128-CBC** — intermediate firmware variant
3. **AES-CCM** — newer UG800 firmware

Rejected attempts are identified by a characteristic 33-byte reject frame (trailer byte `0xAE`).

## Supported devices

SQ610RF, SQ610RF(WB), SQ610RFNH, SQ610RFNH(WB), FC600, TRV3RF, it600MINITRV, it600Receiver, SP600, SPE600, SR600, RS600, SW600, OS600, WLS600, SmokeSensor-EM, SD600, TS600, RE600, RE10B, PS600, ECM600.

### Unsupported

Buttons (SB600, CSB600) — actions only work through the Salus Smart Home app.

## Troubleshooting

- If you can't connect using the EUID on your gateway, try `0000000000000000` as EUID.
- Make sure **Local WiFi Mode** is enabled:
  1. Open the Salus Smart Home app and sign in.
  2. Double-tap your gateway to open the info screen.
  3. Press the gear icon to enter configuration.
  4. Check that **Disable Local WiFi Mode** is set to **No**.
  5. Save and power-cycle the gateway.

## Development

```bash
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture details and contribution guidelines.

## Migration from `pyit600`

This package replaces the unmaintained `pyit600`. Update imports:

```python
# Old
from pyit600.gateway import IT600Gateway

# New
from salus_it600.gateway import IT600Gateway
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Project origin

This project is a maintained fork of [epoplavskis/pyit600](https://github.com/epoplavskis/pyit600). It incorporates protocol, device-support, and parser work from [leonardpitzu/homeassistant_salus](https://github.com/leonardpitzu/homeassistant_salus).
