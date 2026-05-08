# Demo CLI

`main.py` is a small command-line utility for manually checking a Salus gateway
with `salus-it600-client`.

By default it is read-only: it connects to the gateway, polls device state, and
prints the discovered devices. It does not change thermostat setpoints, switch
states, cover positions, or keypad locks unless you provide an explicit write
command with `--yes`.

## Setup

Run commands from the `salus-it600-client` repository root.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Replace these placeholders in the examples:

- `HOST`: gateway IP address or hostname, for example `192.168.1.100`
- `EUID`: 16-character gateway EUID, or `0000000000000000` if the printed EUID
  does not work
- `DEVICE_ID`: an ID printed by the read-only command

## Read-Only Device Check

Use this first. It is safe to run because it only reads gateway state.

```bash
python main.py --host HOST --euid EUID
```

Use debug logging when collecting protocol or parser information:

```bash
python main.py --host HOST --euid EUID --debug
```

Copy the `DEVICE_ID` values from this output before running write examples.

## Write Commands

Every write command requires `--yes`.

Set a climate target temperature:

```bash
python main.py --host HOST --euid EUID --yes --set-temperature DEVICE_ID 21.5
```

Set a climate mode:

```bash
python main.py --host HOST --euid EUID --yes --set-climate-mode DEVICE_ID heat
python main.py --host HOST --euid EUID --yes --set-climate-mode DEVICE_ID cool
python main.py --host HOST --euid EUID --yes --set-climate-mode DEVICE_ID off
```

Set a climate preset. Quote presets that contain spaces:

```bash
python main.py --host HOST --euid EUID --yes --set-climate-preset DEVICE_ID "Permanent Hold"
python main.py --host HOST --euid EUID --yes --set-climate-preset DEVICE_ID "Follow Schedule"
```

Set an FC600 fan mode:

```bash
python main.py --host HOST --euid EUID --yes --set-fan-mode DEVICE_ID Auto
python main.py --host HOST --euid EUID --yes --set-fan-mode DEVICE_ID Medium
python main.py --host HOST --euid EUID --yes --set-fan-mode DEVICE_ID Off
```

Turn a switch on or off:

```bash
python main.py --host HOST --euid EUID --yes --turn-on-switch DEVICE_ID
python main.py --host HOST --euid EUID --yes --turn-off-switch DEVICE_ID
```

Open, close, or position a cover:

```bash
python main.py --host HOST --euid EUID --yes --open-cover DEVICE_ID
python main.py --host HOST --euid EUID --yes --close-cover DEVICE_ID
python main.py --host HOST --euid EUID --yes --set-cover-position DEVICE_ID 25
```

Lock or unlock a climate device keypad:

```bash
python main.py --host HOST --euid EUID --yes --lock-climate DEVICE_ID
python main.py --host HOST --euid EUID --yes --unlock-climate DEVICE_ID
```

## Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | Completed successfully. |
| `1` | Could not connect to the gateway. |
| `2` | Gateway rejected the EUID. |
| `3` | The selected write command failed validation or referenced an unknown device. |

## Notes

- The utility polls before a write so the client has the current device cache.
- After a successful write, it polls again and prints the refreshed state.
- Only one write command can be selected per run.
