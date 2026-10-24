"""Beta counter boundaries and durable-backup/confirmation failure semantics."""
import copy
from unittest.mock import AsyncMock

import pytest

from salus_it600.comfort_warm_floor import (
    _counter_bytes,
    build_comfort_warm_floor_command,
)
from salus_it600.exceptions import (
    IT600CommandError,
    IT600ConnectionError,
    IT600ValidationError,
)
from tests.test_comfort_warm_floor import (
    replace_blob,
    setup_gateway,
    status_fixture,
)


def confirmed(status, command):
    result = copy.deepcopy(status)
    schedule = '72' + command[8:] + status['sIT600TH']['Schedule'][120:]
    result['sIT600TH']['Schedule'] = result['sIT600TH']['Status_2_d'] = schedule
    result['sIT600I']['CommandResponse_d'] = command + '00'
    return result


def envelope(status):
    return {'status': 'success', 'id': [status]}


@pytest.mark.parametrize('counter', range(255))
def test_all_nonwrapping_sequences_preserve_configuration(counter):
    status = status_fixture()
    replace_blob(status, 1, bytes([counter]).hex())
    replace_blob(status, 40, _counter_bytes(counter).hex())
    original = copy.deepcopy(status)
    body = bytes.fromhex(build_comfort_warm_floor_command(status, 2))[3:]
    assert body[1] == counter + 1
    assert body[39] == 2
    # Independent transcription of PR54's sequence-pair equations.
    assert body[40] == (2 * (counter + 1) - 1) % 256
    assert body[41] == 255 - ((counter + 1) // 4)
    base = bytes.fromhex(status['sIT600TH']['Schedule'])
    assert all(body[i] == base[i] for i in range(2, 60) if i not in (39, 40, 41))
    assert status == original


async def test_backup_failure_prevents_dispatch():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    backup = AsyncMock(side_effect=OSError('disk full'))
    with pytest.raises(OSError, match='disk full'):
        await gateway.set_climate_device_comfort_warm_floor('device-1', 3, before_write=backup)
    assert gateway._make_encrypted_request.call_count == 1
    backup.assert_awaited_once_with(status)


@pytest.mark.parametrize('lost_reply', [False, True])
async def test_durable_backup_then_single_send_and_exact_confirmation(monkeypatch, lost_reply):
    gateway, status = setup_gateway()
    command = build_comfort_warm_floor_command(status, 3)
    after = confirmed(status, command)
    backup = AsyncMock()
    calls = []

    async def request(kind, body, **kwargs):
        calls.append(kind)
        if kind == 'write':
            backup.assert_awaited_once_with(status)
            assert kwargs == {'retry_disconnect': False}
            if lost_reply:
                raise IT600ConnectionError('lost reply')
            return envelope(status)
        return envelope(status if len(calls) == 1 else after)

    gateway._make_encrypted_request = AsyncMock(side_effect=request)
    monkeypatch.setattr('salus_it600.gateway.asyncio.sleep', AsyncMock())
    await gateway.set_climate_device_comfort_warm_floor(
        'device-1', 3, before_write=backup, confirmation_timeout=1,
    )
    assert calls == ['read', 'write', 'read']


async def test_old_readback_followed_by_exact_confirmation(monkeypatch):
    gateway, status = setup_gateway()
    command = build_comfort_warm_floor_command(status, 3)
    pending = copy.deepcopy(status)
    pending['sIT600I']['CommandResponse_d'] = command + '00'
    after = confirmed(status, command)
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), envelope(status), envelope(pending), envelope(after)])
    monkeypatch.setattr('salus_it600.gateway.asyncio.sleep', AsyncMock())
    await gateway.set_climate_device_comfort_warm_floor('device-1', 3, confirmation_timeout=1)
    assert [call.args[0] for call in gateway._make_encrypted_request.call_args_list] == ['read', 'write', 'read', 'read']


@pytest.mark.parametrize('change', ['footer', 'weekly_program', 'setpoint', 'wrong_device', 'wrong_level', 'bad_pin'])
async def test_other_changes_stop_without_replay_or_blind_rollback(monkeypatch, change):
    gateway, status = setup_gateway()
    command = build_comfort_warm_floor_command(status, 3)
    after = confirmed(status, command)
    if change == 'footer':
        replace_blob(after, 42, '02')
    elif change == 'weekly_program':
        after['sScheS'] = {'changed': True}
    elif change == 'setpoint':
        after['sIT600TH']['HeatingSetpoint_x100'] += 100
    elif change == 'wrong_device':
        after['data']['UniID'] = 'other'
    elif change == 'wrong_level':
        replace_blob(after, 39, '01')
    else:
        replace_blob(after, 40, 'fe')
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), envelope(status), envelope(after)])
    monkeypatch.setattr('salus_it600.gateway.asyncio.sleep', AsyncMock())
    with pytest.raises(IT600CommandError):
        await gateway.set_climate_device_comfort_warm_floor('device-1', 3, confirmation_timeout=1)
    assert [call.args[0] for call in gateway._make_encrypted_request.call_args_list] == ['read', 'write', 'read']


async def test_confirmation_timeout_never_retries_or_blindly_restores():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    with pytest.raises(IT600CommandError, match='not confirmed'):
        await gateway.set_climate_device_comfort_warm_floor('device-1', 3, confirmation_timeout=0.01)
    assert [call.args[0] for call in gateway._make_encrypted_request.call_args_list] == ['read', 'write']


async def test_final_counter_255_can_be_confirmed_without_enabling_rollover(monkeypatch):
    gateway, status = setup_gateway()
    replace_blob(status, 1, 'fe')
    replace_blob(status, 40, _counter_bytes(254).hex())
    command = build_comfort_warm_floor_command(status, 1)
    after = confirmed(status, command)
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), envelope(status), envelope(after)])
    monkeypatch.setattr('salus_it600.gateway.asyncio.sleep', AsyncMock())
    await gateway.set_climate_device_comfort_warm_floor('device-1', 1, confirmation_timeout=1)
    with pytest.raises(IT600ValidationError, match='counter'):
        build_comfort_warm_floor_command(after, 0)
