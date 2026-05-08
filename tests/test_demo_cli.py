"""Tests for the demo CLI utility."""

from __future__ import annotations

import unittest

import main as demo_cli


class FakeGateway:
    """Gateway fake that records demo CLI write calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    async def set_climate_device_temperature(
        self,
        device_id: str,
        temperature: float,
    ) -> None:
        self.calls.append(("set_temperature", device_id, temperature))

    async def set_climate_device_mode(self, device_id: str, mode: str) -> None:
        self.calls.append(("set_climate_mode", device_id, mode))

    async def set_climate_device_preset(self, device_id: str, preset: str) -> None:
        self.calls.append(("set_climate_preset", device_id, preset))

    async def set_climate_device_fan_mode(self, device_id: str, mode: str) -> None:
        self.calls.append(("set_fan_mode", device_id, mode))

    async def turn_on_switch_device(self, device_id: str) -> None:
        self.calls.append(("turn_on_switch", device_id))

    async def turn_off_switch_device(self, device_id: str) -> None:
        self.calls.append(("turn_off_switch", device_id))

    async def open_cover(self, device_id: str) -> None:
        self.calls.append(("open_cover", device_id))

    async def close_cover(self, device_id: str) -> None:
        self.calls.append(("close_cover", device_id))

    async def set_cover_position(self, device_id: str, position: int) -> None:
        self.calls.append(("set_cover_position", device_id, position))

    async def set_climate_device_locked(self, device_id: str, locked: bool) -> None:
        self.calls.append(("set_climate_locked", device_id, locked))


class TestDemoCli(unittest.IsolatedAsyncioTestCase):
    """Test read-only defaults and explicit write dispatch."""

    def test_default_command_is_read_only(self) -> None:
        args = demo_cli.parse_args(["--host", "192.0.2.10", "--euid", "euid"])

        self.assertFalse(demo_cli._write_requested(args))

    def test_write_command_requires_confirmation(self) -> None:
        with self.assertRaises(SystemExit):
            demo_cli.parse_args(
                [
                    "--host",
                    "192.0.2.10",
                    "--euid",
                    "euid",
                    "--set-temperature",
                    "climate-1",
                    "21.5",
                ]
            )

    async def test_temperature_write_dispatch(self) -> None:
        args = demo_cli.parse_args(
            [
                "--host",
                "192.0.2.10",
                "--euid",
                "euid",
                "--yes",
                "--set-temperature",
                "climate-1",
                "21.5",
            ]
        )
        gateway = FakeGateway()

        await demo_cli.run_write_action(gateway, args)

        self.assertEqual([("set_temperature", "climate-1", 21.5)], gateway.calls)

    async def test_cover_position_write_dispatch(self) -> None:
        args = demo_cli.parse_args(
            [
                "--host",
                "192.0.2.10",
                "--euid",
                "euid",
                "--yes",
                "--set-cover-position",
                "cover-1",
                "25",
            ]
        )
        gateway = FakeGateway()

        await demo_cli.run_write_action(gateway, args)

        self.assertEqual([("set_cover_position", "cover-1", 25)], gateway.calls)

    async def test_all_write_actions_dispatch(self) -> None:
        cases = [
            (
                ["--set-temperature", "climate-1", "21.5"],
                ("set_temperature", "climate-1", 21.5),
            ),
            (
                ["--set-climate-mode", "climate-1", "heat"],
                ("set_climate_mode", "climate-1", "heat"),
            ),
            (
                ["--set-climate-preset", "climate-1", "Permanent Hold"],
                ("set_climate_preset", "climate-1", "Permanent Hold"),
            ),
            (
                ["--set-fan-mode", "climate-1", "Auto"],
                ("set_fan_mode", "climate-1", "Auto"),
            ),
            (["--turn-on-switch", "switch-1"], ("turn_on_switch", "switch-1")),
            (["--turn-off-switch", "switch-1"], ("turn_off_switch", "switch-1")),
            (["--open-cover", "cover-1"], ("open_cover", "cover-1")),
            (["--close-cover", "cover-1"], ("close_cover", "cover-1")),
            (
                ["--set-cover-position", "cover-1", "25"],
                ("set_cover_position", "cover-1", 25),
            ),
            (
                ["--lock-climate", "climate-1"],
                ("set_climate_locked", "climate-1", True),
            ),
            (
                ["--unlock-climate", "climate-1"],
                ("set_climate_locked", "climate-1", False),
            ),
        ]

        for cli_args, expected_call in cases:
            with self.subTest(cli_args=cli_args):
                args = demo_cli.parse_args(
                    ["--host", "192.0.2.10", "--euid", "euid", "--yes", *cli_args]
                )
                gateway = FakeGateway()

                await demo_cli.run_write_action(gateway, args)

                self.assertEqual([expected_call], gateway.calls)


if __name__ == "__main__":
    unittest.main()
