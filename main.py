#!/usr/bin/env python
"""Command-line demo utility for salus-it600-client."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from collections.abc import Mapping, Sequence
from typing import Any

from salus_it600.exceptions import IT600AuthenticationError, IT600ConnectionError
from salus_it600.gateway import IT600Gateway

WRITE_ACTIONS = (
    "set_temperature",
    "set_climate_mode",
    "set_climate_preset",
    "set_fan_mode",
    "turn_on_switch",
    "turn_off_switch",
    "open_cover",
    "close_cover",
    "set_cover_position",
    "lock_climate",
    "unlock_climate",
)


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
    """Parse command-line arguments and enforce write confirmation."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if _write_requested(args) and not args.yes:
        parser.error("write commands require --yes")
    return args


def _write_requested(args: argparse.Namespace) -> bool:
    """Return whether the parsed arguments include a write command."""
    return any(getattr(args, action) is not None for action in WRITE_ACTIONS)


async def _run_write_action(gateway: IT600Gateway, args: argparse.Namespace) -> None:
    """Run the selected write command, if any."""
    if args.set_temperature is not None:
        device_id, temperature = args.set_temperature
        await gateway.set_climate_device_temperature(device_id, float(temperature))
        print(f"Set {device_id} target temperature to {float(temperature):g} C")
        return

    if args.set_climate_mode is not None:
        device_id, mode = args.set_climate_mode
        await gateway.set_climate_device_mode(device_id, mode)
        print(f"Set {device_id} climate mode to {mode}")
        return

    if args.set_climate_preset is not None:
        device_id, preset = args.set_climate_preset
        await gateway.set_climate_device_preset(device_id, preset)
        print(f"Set {device_id} climate preset to {preset}")
        return

    if args.set_fan_mode is not None:
        device_id, mode = args.set_fan_mode
        await gateway.set_climate_device_fan_mode(device_id, mode)
        print(f"Set {device_id} fan mode to {mode}")
        return

    if args.turn_on_switch is not None:
        await gateway.turn_on_switch_device(args.turn_on_switch)
        print(f"Turned on switch {args.turn_on_switch}")
        return

    if args.turn_off_switch is not None:
        await gateway.turn_off_switch_device(args.turn_off_switch)
        print(f"Turned off switch {args.turn_off_switch}")
        return

    if args.open_cover is not None:
        await gateway.open_cover(args.open_cover)
        print(f"Opened cover {args.open_cover}")
        return

    if args.close_cover is not None:
        await gateway.close_cover(args.close_cover)
        print(f"Closed cover {args.close_cover}")
        return

    if args.set_cover_position is not None:
        device_id, position = args.set_cover_position
        await gateway.set_cover_position(device_id, int(position))
        print(f"Set {device_id} cover position to {int(position)}")
        return

    if args.lock_climate is not None:
        await gateway.set_climate_device_locked(args.lock_climate, True)
        print(f"Locked climate keypad {args.lock_climate}")
        return

    if args.unlock_climate is not None:
        await gateway.set_climate_device_locked(args.unlock_climate, False)
        print(f"Unlocked climate keypad {args.unlock_climate}")


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
            await _run_write_action(gateway, args)
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
