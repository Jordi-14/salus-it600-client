"""Two actual comfort-only writes, unlike the historical incrementing trial."""

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from salus_it600.comfort_warm_floor import (
    build_comfort_warm_floor_command,
    comfort_command_matches,
)
from tests.test_comfort_warm_floor import setup_gateway, status_fixture
from tests.test_floor_command_lifecycle import envelope

EVIDENCE = json.loads((Path(__file__).parent / 'fixtures/comfort_warm_floor_level_only.json').read_text())


def snapshot(vector, after=False):
    status = status_fixture()
    prefix = 'after' if after else 'before'
    status['sIT600TH']['Schedule'] = status['sIT600TH']['Status_2_d'] = vector[prefix]
    status['sIT600I']['CommandResponse_d'] = vector[prefix + 'RecordedCommand']
    return status


@pytest.mark.parametrize('vector', EVIDENCE['vectors'])
async def test_exact_hardware_level_only_write_and_device_counter_readback(monkeypatch, vector):
    before, after = snapshot(vector), snapshot(vector, True)
    command = build_comfort_warm_floor_command(before, vector['targetLevel'])
    assert command == vector['command']
    base = bytes.fromhex(vector['before'])
    body = bytes.fromhex(command)[3:]
    assert [i for i in range(60) if base[i] != body[i]] == [0, 39]
    assert bytes.fromhex(vector['after'])[1] == base[1] + 1
    gateway, _ = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(before), envelope(before)])
    await gateway.set_climate_device_comfort_warm_floor('device-1', vector['targetLevel'])
    assert comfort_command_matches(after, command)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == ['read', 'write']


async def test_next_command_uses_new_device_metadata():
    vectors = EVIDENCE['vectors']
    gateway, _ = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(snapshot(vectors[0])), envelope(snapshot(vectors[0])), envelope(snapshot(vectors[1])), envelope(snapshot(vectors[1]))])
    await gateway.set_climate_device_comfort_warm_floor('device-1', 1)
    await gateway.set_climate_device_comfort_warm_floor('device-1', 0)
    writes = [c.args[1]['id'][0]['sIT600I']['SetCommand_d'] for c in gateway._make_encrypted_request.call_args_list if c.args[0] == 'write']
    assert writes == [v['command'] for v in vectors]
