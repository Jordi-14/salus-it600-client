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

    async def set_cover_position(self, device_id: str, position: int) -> None:
        self.calls.append(("set_cover_position", device_id, position))


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

        await demo_cli._run_write_action(gateway, args)

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

        await demo_cli._run_write_action(gateway, args)

        self.assertEqual([("set_cover_position", "cover-1", 25)], gateway.calls)


if __name__ == "__main__":
    unittest.main()
