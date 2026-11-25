"""One actual display-resolution round trip, with all device identity removed."""

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from salus_it600.display_resolution import (
    build_display_resolution_command,
    display_resolution_applied,
)
from tests.test_display_resolution import ACK, envelope, setup_gateway, status_fixture

FIXTURE = Path(__file__).parent / "fixtures/display_resolution_round_trip.json"
EVIDENCE = json.loads(FIXTURE.read_text())


def snapshot(vector, after=False):
    status = status_fixture()
    prefix = "after" if after else "before"
    status["sIT600TH"]["Schedule"] = status["sIT600TH"]["Status_2_d"] = vector[prefix]
    status["sIT600I"]["CommandResponse_d"] = vector[prefix + "RecordedCommand"]
    return status


@pytest.mark.parametrize("vector", EVIDENCE["vectors"])
async def test_exact_hardware_resolution_write_and_device_counter_readback(vector):
    before, after = snapshot(vector), snapshot(vector, True)
    command = build_display_resolution_command(before, vector["targetResolution"])
    assert command == vector["command"]
    base = bytes.fromhex(vector["before"])
    body = bytes.fromhex(command)[3:]
    assert [i for i in range(60) if base[i] != body[i]] == [0, 11]
    assert bytes.fromhex(vector["after"])[1] == base[1] + 1
    assert bytes.fromhex(vector["after"])[11] == vector["targetResolution"]
    gateway, _ = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(
        side_effect=[envelope(before), ACK],
    )
    await gateway.set_climate_device_display_resolution(
        "device-1",
        vector["targetResolution"],
    )
    assert display_resolution_applied(after, command)
    calls = gateway._make_encrypted_request.call_args_list
    assert [c.args[0] for c in calls] == ["read", "write"]


async def test_round_trip_uses_new_device_metadata():
    vectors = EVIDENCE["vectors"]
    gateway, _ = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(side_effect=[
        envelope(snapshot(vectors[0])),
        ACK,
        envelope(snapshot(vectors[1])),
        ACK,
    ])
    await gateway.set_climate_device_display_resolution("device-1", 0)
    await gateway.set_climate_device_display_resolution("device-1", 1)
    writes = [
        c.args[1]["id"][0]["sIT600I"]["SetCommand_d"]
        for c in gateway._make_encrypted_request.call_args_list
        if c.args[0] == "write"
    ]
    assert writes == [v["command"] for v in vectors]
