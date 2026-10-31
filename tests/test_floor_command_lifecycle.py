"""Bounded pending writes, acknowledgement-only setters and body confirmation."""

import copy
from unittest.mock import AsyncMock

import pytest

from salus_it600.comfort_warm_floor import (
    COMFORT_PENDING_SECONDS,
    NON_SETTINGS_RESPONSE,
    build_comfort_warm_floor_command,
    comfort_command_matches,
)
from salus_it600.exceptions import IT600ConnectionError, IT600ValidationError
from tests.test_comfort_warm_floor import replace_blob, setup_gateway, status_fixture


def envelope(status):
    return {"status": "success", "id": [status]}


def confirmed(status, command):
    after = copy.deepcopy(status)
    blob = bytearray.fromhex("72" + command[8:] + status["sIT600TH"]["Schedule"][120:])
    blob[1] = (blob[1] + 1) % 256
    blob[40:42] = b"\xa5\x5a"  # Opaque simulated device metadata.
    after["sIT600TH"]["Schedule"] = after["sIT600TH"]["Status_2_d"] = blob.hex()
    after["sIT600I"]["CommandResponse_d"] = command + "00"
    return after


@pytest.mark.parametrize("counter", range(256))
def test_all_counter_values_are_copied_unchanged(counter):
    status = status_fixture()
    replace_blob(status, 1, bytes([counter]).hex())
    replace_blob(status, 40, "a55a")
    body = bytes.fromhex(build_comfort_warm_floor_command(status, 2))[3:]
    original = bytes.fromhex(status["sIT600TH"]["Schedule"])
    assert all(body[i] == original[i] for i in range(1, 60) if i != 39)
    assert body[39] == 2


async def test_setter_returns_on_ack_without_confirmation_poll():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == ["read", "write"]


@pytest.mark.parametrize("runtime", ["HeatingSetpoint_x100", "HoldType", "sScheS"])
async def test_schedule_changes_and_replaced_echo_do_not_trap_pending(runtime, monkeypatch):
    gateway, status = setup_gateway()
    command = build_comfort_warm_floor_command(status, 3)
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), IT600ConnectionError("lost")])
    with pytest.raises(IT600ConnectionError):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    after = confirmed(status, command)
    if runtime == "sScheS":
        after["sScheS"] = {"schedule": "changed by the device"}
    else:
        after["sIT600TH"][runtime] = 2200 if runtime == "HeatingSetpoint_x100" else 1
    after["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    assert comfort_command_matches(after, command)
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(after))
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    await gateway.set_climate_device_comfort_warm_floor("device-1", 1)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == ["read", "read", "write"]


@pytest.mark.parametrize("record_echo", [False, True])
async def test_unapplied_write_expires_then_new_request_uses_fresh_body(monkeypatch, record_echo):
    gateway, status = setup_gateway()
    clock = [0]
    monkeypatch.setattr(gateway, "_comfort_floor_time", lambda: clock[0])
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), IT600ConnectionError("lost")])
    with pytest.raises(IT600ConnectionError):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    if record_echo:
        status["sIT600I"]["CommandResponse_d"] = build_comfort_warm_floor_command(status, 3) + "00"
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    with pytest.raises(IT600ValidationError, match="still pending"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 1)
    clock[0] = COMFORT_PENDING_SECONDS
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    gateway._make_encrypted_request.reset_mock()
    await gateway.set_climate_device_comfort_warm_floor("device-1", 1)
    writes = [c for c in gateway._make_encrypted_request.call_args_list if c.args[0] == "write"]
    assert len(writes) == 1
    assert bytes.fromhex(writes[0].args[1]["id"][0]["sIT600I"]["SetCommand_d"])[42] == 1


async def test_shared_echo_requires_stable_settings(monkeypatch):
    gateway, status = setup_gateway()
    status["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    changed = copy.deepcopy(status)
    replace_blob(changed, 42, "02")
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), envelope(changed)])
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    with pytest.raises(IT600ValidationError, match="changed during"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 1)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == ["read", "read"]


def test_matching_ignores_echo_but_not_the_written_settings():
    status = status_fixture()
    command = build_comfort_warm_floor_command(status, 1)
    after = confirmed(status, command)
    after["sIT600I"]["CommandResponse_d"] = "another command"
    assert comfort_command_matches(after, command)
    replace_blob(after, 42, "02")
    assert not comfort_command_matches(after, command)
