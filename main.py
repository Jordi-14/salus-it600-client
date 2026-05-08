#!/usr/bin/env python
"""Command-line demo utility for salus-it600-client."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from salus_it600.exceptions import IT600AuthenticationError, IT600ConnectionError
from salus_it600.gateway import IT600Gateway


@dataclass(frozen=True, slots=True)
class WriteAction:
    """A parsed CLI write action mapped to a gateway method."""

    method_name: str
    arguments: Callable[[Any], tuple[Any, ...]]
    message: str


def _single_device(value: str) -> tuple[str]:
    """Return one device ID argument."""
    return (value,)


def _device_and_text(value: Sequence[str]) -> tuple[str, str]:
    """Return a device ID plus a text argument."""
    device_id, text = value
    return device_id, text


def _device_and_float(value: Sequence[str]) -> tuple[str, float]:
    """Return a device ID plus a float argument."""
    device_id, number = value
    return device_id, float(number)


def _device_and_int(value: Sequence[str]) -> tuple[str, int]:
    """Return a device ID plus an integer argument."""
    device_id, number = value
    return device_id, int(number)


def _lock_device(value: str) -> tuple[str, bool]:
    """Return a device ID plus a lock state."""
    return value, True


def _unlock_device(value: str) -> tuple[str, bool]:
    """Return a device ID plus an unlock state."""
    return value, False


WRITE_ACTIONS: dict[str, WriteAction] = {
    "set_temperature": WriteAction(
        "set_climate_device_temperature",
        _device_and_float,
        "Set {0} target temperature to {1:g} C",
    ),
    "set_climate_mode": WriteAction(
        "set_climate_device_mode",
        _device_and_text,
        "Set {0} climate mode to {1}",
    ),
    "set_climate_preset": WriteAction(
        "set_climate_device_preset",
        _device_and_text,
        "Set {0} climate preset to {1}",
    ),
    "set_fan_mode": WriteAction(
        "set_climate_device_fan_mode",
        _device_and_text,
        "Set {0} fan mode to {1}",
    ),
    "turn_on_switch": WriteAction(
        "turn_on_switch_device",
        _single_device,
        "Turned on switch {0}",
    ),
    "turn_off_switch": WriteAction(
        "turn_off_switch_device",
        _single_device,
        "Turned off switch {0}",
    ),
    "open_cover": WriteAction(
        "open_cover",
        _single_device,
        "Opened cover {0}",
    ),
    "close_cover": WriteAction(
        "close_cover",
        _single_device,
        "Closed cover {0}",
    ),
    "set_cover_position": WriteAction(
        "set_cover_position",
        _device_and_int,
        "Set {0} cover position to {1}",
    ),
    "lock_climate": WriteAction(
        "set_climate_device_locked",
        _lock_device,
        "Locked climate keypad {0}",
    ),
    "unlock_climate": WriteAction(
        "set_climate_device_locked",
        _unlock_device,
        "Unlocked climate keypad {0}",
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """Return the command-line parser for the demo utility."""
    parser = argparse.ArgumentParser(
        description=(
            "Read Salus iT600 gateway state and optionally run one explicit "
            "write command."
        )
    )
    parser.add_argument(
        "--host",
        required=True,
        metavar="HOST",
        help="network address of the Salus UGE600/UG800 gateway",
    )
    parser.add_argument(
        "--euid",
        required=True,
        metavar="EUID",
        help="gateway EUID from the label, or 0000000000000000 if needed",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug logging and raw gateway request/response logging",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="confirm that the selected write command should be executed",
    )

    write_group = parser.add_mutually_exclusive_group()
    write_group.add_argument(
        "--set-temperature",
        nargs=2,
        metavar=("DEVICE_ID", "CELSIUS"),
        help="set a climate device target temperature",
    )
    write_group.add_argument(
        "--set-climate-mode",
        nargs=2,
        metavar=("DEVICE_ID", "MODE"),
        help="set a climate device HVAC mode, for example heat, cool, off, or auto",
    )
    write_group.add_argument(
        "--set-climate-preset",
        nargs=2,
        metavar=("DEVICE_ID", "PRESET"),
        help="set a climate preset, for example 'Permanent Hold'",
    )
    write_group.add_argument(
        "--set-fan-mode",
        nargs=2,
        metavar=("DEVICE_ID", "MODE"),
        help="set an FC600 fan mode, for example Auto, High, Medium, Low, or Off",
    )
    write_group.add_argument(
        "--turn-on-switch",
        metavar="DEVICE_ID",
        help="turn on a switch device",
    )
    write_group.add_argument(
        "--turn-off-switch",
        metavar="DEVICE_ID",
        help="turn off a switch device",
    )
    write_group.add_argument(
        "--open-cover",
        metavar="DEVICE_ID",
        help="open a cover device",
    )
    write_group.add_argument(
        "--close-cover",
        metavar="DEVICE_ID",
        help="close a cover device",
    )
    write_group.add_argument(
        "--set-cover-position",
        nargs=2,
        metavar=("DEVICE_ID", "POSITION"),
        help="set a cover position from 0 to 100",
    )
    write_group.add_argument(
        "--lock-climate",
        metavar="DEVICE_ID",
        help="lock a climate device keypad",
    )
    write_group.add_argument(
        "--unlock-climate",
        metavar="DEVICE_ID",
        help="unlock a climate device keypad",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = build_parser()
    return parser.parse_args(argv)


def _write_requested(args: argparse.Namespace) -> bool:
    """Return whether the parsed arguments include a write command."""
    return _selected_write_action(args) is not None


def _write_confirmation_missing(args: argparse.Namespace) -> bool:
    """Return whether a write command needs explicit confirmation."""
    return _write_requested(args) and not args.yes


def _selected_write_action(
    args: argparse.Namespace,
) -> tuple[WriteAction, Any] | None:
    """Return the selected write action and raw parser value, if any."""
    for name, action in WRITE_ACTIONS.items():
        value = getattr(args, name)
        if value is not None:
            return action, value
    return None


async def run_write_action(gateway: IT600Gateway, args: argparse.Namespace) -> None:
    """Run the selected write command, if any."""
    selected = _selected_write_action(args)
    if selected is None:
        return

    action, value = selected
    method_args = action.arguments(value)
    method = getattr(gateway, action.method_name)
    await method(*method_args)
    print(action.message.format(*method_args))


def _print_devices(title: str, devices: Mapping[str, Any]) -> None:
    """Print one gateway device collection."""
    print(f"\n{title}")
    if not devices:
        print("  None found")
        return

    for device_id, device in sorted(devices.items()):
        name = getattr(device, "name", device_id)
        model = getattr(device, "model", None) or "unknown model"
        available = getattr(device, "available", None)
        print(f"  - {device_id}: {name} ({model}), available={available}")
        print(f"    {device!r}")


def _print_gateway_state(gateway: IT600Gateway) -> None:
    """Print the currently cached gateway state."""
    gateway_device = gateway.get_gateway_device()
    if gateway_device is not None:
        print(
            "Gateway: "
            f"{gateway_device.name} ({gateway_device.model or 'unknown model'}), "
            f"id={gateway_device.unique_id}"
        )

    _print_devices("Climate devices", gateway.get_climate_devices())
    _print_devices("Binary sensor devices", gateway.get_binary_sensor_devices())
    _print_devices("Switch devices", gateway.get_switch_devices())
    _print_devices("Cover devices", gateway.get_cover_devices())
    _print_devices("Sensor devices", gateway.get_sensor_devices())


async def async_main(argv: Sequence[str] | None = None) -> int:
    """Run the demo utility."""
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if _write_confirmation_missing(args):
        print("Command error: write commands require --yes", file=sys.stderr)
        return 3

    async with IT600Gateway(host=args.host, euid=args.euid, debug=args.debug) as gateway:
        try:
            await gateway.connect()
            await gateway.poll_status()
        except IT600ConnectionError:
            print(
                "Connection error: check the gateway IP address and Local WiFi Mode.",
                file=sys.stderr,
            )
            return 1
        except IT600AuthenticationError:
            print("Authentication error: check the gateway EUID.", file=sys.stderr)
            return 2

        _print_gateway_state(gateway)

        if not _write_requested(args):
            print("\nNo write command selected; gateway state was read only.")
            return 0

        try:
            await run_write_action(gateway, args)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"Command error: {exc}", file=sys.stderr)
            return 3

        print("\nPolling after write command...")
        await gateway.poll_status()
        _print_gateway_state(gateway)
        return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the async demo utility from a synchronous entry point."""
    return asyncio.run(async_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
