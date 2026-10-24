"""Hardware-backed floor-comfort vectors, with all device identity removed."""

import copy
from dataclasses import replace
from unittest.mock import AsyncMock

import pytest
from aiohttp.client_exceptions import ServerDisconnectedError

from salus_it600.comfort_warm_floor import (
    build_comfort_warm_floor_command,
    supports_comfort_warm_floor_write,
)
from salus_it600.exceptions import (
    IT600CommandError,
    IT600ConnectionError,
    IT600ValidationError,
)
from salus_it600.parsers.climate import parse_climate_device
from tests.test_gateway_request import FakeSession, make_climate_device, make_gateway

# Observed app Off(counter 7) -> computer level 3(counter 8), confirmed in
# gateway configuration and vendor app on SQ610RFNH firmware 00000054.
OFF = "720701000001050040000000000104002700100006003500050040000500010000000101800000000dfe010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000"
LEVEL_3_COMMAND = "423131730801000001050040000000000104002700100006003500050040000500010000000101800000030ffd010000000100ffffffffffffffffffffffff"


def status_fixture():
    return {
        "status": "success",
        "data": {"UniID": "device-1", "Endpoint": 9, "DeviceType": 100},
        "DeviceL": {"ModelIdentifier_i": "SQ610RFNH"},
        "sZDO": {"FirmwareVersion": "00000054"},
        "sZDOInfo": {"OnlineStatus_i": 1},
        "sIT600TH": {
            "Schedule": OFF, "Status_2_d": OFF,
            "PairedTRVShortID": "F" * 24, "HoldType": 2,
            "HeatingSetpoint_x100": 2100, "SystemMode": 4, "PairedWCNumber": 1,
        },
        "sIT600I": {"CommandResponse_d": "42313173" + OFF[2:120] + "00"},
    }


def replace_blob(status, offset, value):
    blob = status["sIT600TH"]["Schedule"]
    blob = blob[:2 * offset] + value + blob[2 * offset + len(value):]
    status["sIT600TH"]["Schedule"] = blob
    status["sIT600TH"]["Status_2_d"] = blob
    status["sIT600I"]["CommandResponse_d"] = "42313173" + blob[2:120] + "00"


def test_hardware_vector_preserves_danish_language_and_every_other_byte():
    status = status_fixture()
    original = copy.deepcopy(status)
    assert build_comfort_warm_floor_command(status, 3) == LEVEL_3_COMMAND
    before = bytes.fromhex(OFF)
    body = bytes.fromhex(LEVEL_3_COMMAND)[3:]
    assert len(body) == 60
    assert [i for i in range(60) if before[i] != body[i]] == [0, 1, 39, 40, 41]
    assert body[42:48].hex() == "010000000100"
    assert status == original


@pytest.mark.parametrize("level", [0, 1, 2, 3])
def test_all_levels_and_noop(level):
    command = build_comfort_warm_floor_command(status_fixture(), level)
    if level == 0:
        assert command is None
    else:
        assert bytes.fromhex(command)[3 + 39] == level


@pytest.mark.parametrize("level", [-1, 4, True, "3", 1.5])
def test_invalid_levels_never_encode(level):
    with pytest.raises((TypeError, IT600ValidationError)):
        build_comfort_warm_floor_command(status_fixture(), level)


@pytest.mark.parametrize("offset,value", [(1, "09"), (1, "ff"), (39, "04"), (40, "ee"), (43, "01"), (60, "00")])
def test_unverified_counter_pin_and_level_are_rejected(offset, value):
    status = status_fixture()
    replace_blob(status, offset, value)
    assert not supports_comfort_warm_floor_write(status)
    with pytest.raises(IT600ValidationError):
        build_comfort_warm_floor_command(status, 3)


@pytest.mark.parametrize("section,field,value", [
    ("data", "Endpoint", 8),
    ("data", "DeviceType", 200),
    ("DeviceL", "ModelIdentifier_i", "SQ610RF"),
    ("sZDO", "FirmwareVersion", "00000055"),
    ("sIT600TH", "Schedule", "72"),
    ("sIT600TH", "Status_2_d", ""),
    ("sIT600TH", "PairedTRVShortID", "1234"),
    ("sIT600TH", "PairedWCNumber", 0),
    ("sIT600TH", "SystemMode", 3),
    ("sIT600I", "CommandResponse_d", LEVEL_3_COMMAND + "00"),
])
def test_unknown_profiles_layouts_and_pending_commands_rejected(section, field, value):
    status = status_fixture()
    status[section][field] = value
    assert not supports_comfort_warm_floor_write(status)
    with pytest.raises(IT600ValidationError):
        build_comfort_warm_floor_command(status, 3)


def test_parser_exposes_normalized_capability_and_level():
    device = parse_climate_device(status_fixture())
    assert device.supports_comfort_warm_floor
    assert device.advanced_settings.comfort_warm_floor == 0


def setup_gateway():
    gateway = make_gateway(FakeSession())
    status = status_fixture()
    gateway._climate_devices["device-1"] = replace(
        make_climate_device("device-1"), data=status["data"],
        model="SQ610RFNH", sw_version="00000054",
    )
    return gateway, status


async def test_gateway_uses_fresh_settings_and_disables_write_retry():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(side_effect=[
        {"status": "success", "id": [status]},
        {"status": "success", "id": [{"status": "success", "data": status["data"]}]},
    ])
    await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    calls = gateway._make_encrypted_request.call_args_list
    assert calls[0].args[0] == "read"
    assert calls[1].args[1]["id"][0]["sIT600I"]["SetCommand_d"] == LEVEL_3_COMMAND
    assert calls[1].kwargs == {"retry_disconnect": False}
    # Acceptance never changes the cached, reported state optimistically.
    assert gateway.get_climate_device("device-1").advanced_settings is None


async def test_gateway_noop_only_reads():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value={"status": "success", "id": [status]})
    await gateway.set_climate_device_comfort_warm_floor("device-1", 0)
    assert gateway._make_encrypted_request.call_count == 1


async def test_gateway_rejects_wrong_endpoint_before_write():
    gateway, status = setup_gateway()
    status["data"] = {**status["data"], "Endpoint": 8}
    gateway._make_encrypted_request = AsyncMock(return_value={"status": "success", "id": [status]})
    with pytest.raises(IT600CommandError):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    assert gateway._make_encrypted_request.call_count == 1


async def test_nonreplayable_request_is_not_resent_after_disconnect():
    session = FakeSession(error=ServerDisconnectedError())
    gateway = make_gateway(session)
    with pytest.raises(IT600ConnectionError):
        await gateway._make_encrypted_request("write", {"requestAttr": "write"}, retry_disconnect=False)
    assert len(session.post_calls) == 1


@pytest.mark.parametrize("section", ["data", "DeviceL", "sZDO", "sIT600TH", "sIT600I"])
def test_partial_response_has_validation_error(section):
    status = status_fixture()
    status[section] = None
    assert not supports_comfort_warm_floor_write(status)
    with pytest.raises(IT600ValidationError):
        build_comfort_warm_floor_command(status, 1)


async def test_gateway_rejects_pending_settings_without_another_write():
    gateway, status = setup_gateway()
    status["sIT600I"]["CommandResponse_d"] = LEVEL_3_COMMAND + "00"
    gateway._make_encrypted_request = AsyncMock(return_value={"status": "success", "id": [status]})
    with pytest.raises(IT600ValidationError, match="pending"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 1)
    assert gateway._make_encrypted_request.call_count == 1


async def test_gateway_rejects_acknowledgement_for_wrong_device():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(side_effect=[
        {"status": "success", "id": [status]},
        {"status": "success", "id": [{"status": "success", "data": {"UniID": "other", "Endpoint": 9}}]},
    ])
    with pytest.raises(IT600CommandError, match="acknowledge"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    assert gateway._make_encrypted_request.call_count == 2


async def test_fresh_offline_status_never_writes():
    gateway, status = setup_gateway()
    status["sZDOInfo"]["OnlineStatus_i"] = 0
    gateway._make_encrypted_request = AsyncMock(return_value={"status": "success", "id": [status]})
    with pytest.raises(IT600ValidationError, match="offline"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    assert gateway._make_encrypted_request.call_count == 1


async def test_cached_offline_status_never_requests():
    gateway, _ = setup_gateway()
    gateway._climate_devices["device-1"] = replace(gateway._climate_devices["device-1"], available=False)
    gateway._make_encrypted_request = AsyncMock()
    with pytest.raises(IT600ValidationError, match="offline"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    gateway._make_encrypted_request.assert_not_called()


async def test_commands_are_serialized_and_second_pending_change_is_rejected():
    import asyncio

    gateway, status = setup_gateway()
    write_started = asyncio.Event()
    finish_write = asyncio.Event()
    recorded = copy.deepcopy(status)
    calls = []

    async def request(command, body, **kwargs):
        calls.append(command)
        if command == "read":
            return {"status": "success", "id": [copy.deepcopy(recorded)]}
        write_started.set()
        await finish_write.wait()
        recorded["sIT600I"]["CommandResponse_d"] = LEVEL_3_COMMAND + "00"
        return {"status": "success", "id": [{"status": "success", "data": status["data"]}]}

    gateway._make_encrypted_request = request
    first = asyncio.create_task(gateway.set_climate_device_comfort_warm_floor("device-1", 3))
    await write_started.wait()
    second = asyncio.create_task(gateway.set_climate_device_comfort_warm_floor("device-1", 1))
    await asyncio.sleep(0)
    assert calls == ["read", "write"]
    finish_write.set()
    await first
    with pytest.raises(IT600ValidationError, match="pending"):
        await second
    assert calls == ["read", "write", "read"]
