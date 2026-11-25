"""SQ610 display resolution writes, with all device identity removed."""

import asyncio
import copy
from dataclasses import replace
from unittest.mock import AsyncMock

import pytest

from salus_it600.display_resolution import (
    DISPLAY_RESOLUTION_PENDING_SECONDS,
    build_display_resolution_command,
    display_resolution_applied,
    supports_display_resolution,
)
from salus_it600.exceptions import (
    IT600CommandError,
    IT600ConnectionError,
    IT600ValidationError,
)
from salus_it600.parsers.climate import parse_climate_device
from tests.test_gateway_request import FakeSession, make_climate_device, make_gateway

# Anonymized settings read-back reporting 0.5 °C (byte 11 = 00).
SETTINGS = "720701000001050040000000000104002700100006003500050040000500010000000101800000000dfe010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000"
RESOLUTION_01_COMMAND = "423131730701000001050040000001000104002700100006003500050040000500010000000101800000000dfe010000000100ffffffffffffffffffffffff"
NON_SETTINGS_RESPONSE = "4233344c"
ACK = {"status": "success", "id": [{"status": "success", "data": {"UniID": "device-1", "Endpoint": 9}}]}


def status_fixture():
    """Return an online SQ610RFNH/00000054 read with a recorded applied command."""
    return {
        "status": "success",
        "data": {"UniID": "device-1", "Endpoint": 9, "DeviceType": 100},
        "DeviceL": {"ModelIdentifier_i": "SQ610RFNH"},
        "sZDO": {"FirmwareVersion": "00000054"},
        "sZDOInfo": {"OnlineStatus_i": 1},
        "sIT600TH": {
            "Schedule": SETTINGS, "Status_2_d": SETTINGS,
            "HoldType": 2,
        },
        "sIT600I": {"CommandResponse_d": "42313173" + SETTINGS[2:120] + "00"},
    }


def replace_blob(status, offset, value):
    """Change reported settings bytes as an applied command would."""
    blob = status["sIT600TH"]["Schedule"]
    blob = blob[:2 * offset] + value + blob[2 * offset + len(value):]
    status["sIT600TH"]["Schedule"] = status["sIT600TH"]["Status_2_d"] = blob
    status["sIT600I"]["CommandResponse_d"] = "42313173" + blob[2:120] + "00"


def in_flight_echo(status, offset, value):
    """Record a same-counter settings command the device has not applied."""
    body = bytearray.fromhex(status["sIT600TH"]["Schedule"][2:120])
    body[offset - 1] = value
    return "42313173" + body.hex() + "00"


def applied(status, command):
    """Return the read-back after the device applies a command."""
    after = copy.deepcopy(status)
    blob = bytearray.fromhex("72" + command[8:] + status["sIT600TH"]["Schedule"][120:])
    blob[1] = (blob[1] + 1) % 256
    blob[40:42] = b"\xa5\x5a"  # Opaque simulated device metadata.
    after["sIT600TH"]["Schedule"] = after["sIT600TH"]["Status_2_d"] = blob.hex()
    after["sIT600I"]["CommandResponse_d"] = command + "00"
    return after


def envelope(status):
    """Wrap one device status as a gateway read response."""
    return {"status": "success", "id": [status]}


def setup_gateway():
    """Return a gateway with one cached SQ610 and its matching read status."""
    gateway = make_gateway(FakeSession())
    status = status_fixture()
    gateway._climate_devices["device-1"] = replace(
        make_climate_device("device-1"), data=status["data"],
        model="SQ610RFNH", sw_version="00000054",
    )
    return gateway, status


def written_body(call):
    """Return the 60-byte settings body of a recorded write call."""
    return bytes.fromhex(call.args[1]["id"][0]["sIT600I"]["SetCommand_d"])[3:]


def test_change_preserves_every_other_byte():
    status = status_fixture()
    original = copy.deepcopy(status)
    command = build_display_resolution_command(status, 1)
    assert command == RESOLUTION_01_COMMAND
    body = bytes.fromhex(command)[3:]
    assert len(body) == 60
    assert [i for i in range(60) if bytes.fromhex(SETTINGS)[i] != body[i]] == [0, 11]
    assert status == original


@pytest.mark.parametrize("counter", range(256))
def test_all_counter_values_are_copied_unchanged(counter):
    status = status_fixture()
    replace_blob(status, 1, bytes([counter]).hex())
    replace_blob(status, 40, "a55a")
    body = bytes.fromhex(build_display_resolution_command(status, 1))[3:]
    original = bytes.fromhex(status["sIT600TH"]["Schedule"])
    assert [i for i in range(60) if body[i] != original[i]] == [0, 11]


def test_reported_resolution_is_a_noop():
    assert build_display_resolution_command(status_fixture(), 0) is None
    status = status_fixture()
    replace_blob(status, 11, "01")
    assert build_display_resolution_command(status, 1) is None
    assert bytes.fromhex(build_display_resolution_command(status, 0))[3 + 11] == 0


@pytest.mark.parametrize("resolution", [True, "1", 0.5, None])
def test_non_integer_resolutions_are_type_errors(resolution):
    with pytest.raises(TypeError, match="must be an integer"):
        build_display_resolution_command(status_fixture(), resolution)


@pytest.mark.parametrize("resolution", [-1, 2, 5])
def test_unknown_resolution_codes_are_rejected(resolution):
    with pytest.raises(IT600ValidationError, match="must be 0 or 1"):
        build_display_resolution_command(status_fixture(), resolution)


def test_unknown_reported_resolution_is_rejected():
    status = status_fixture()
    replace_blob(status, 11, "02")
    with pytest.raises(IT600ValidationError, match="Unsupported display resolution"):
        build_display_resolution_command(status, 1)
    assert not supports_display_resolution(status)


@pytest.mark.parametrize("section,field,value,message", [
    ("sZDO", "FirmwareVersion", "00000055", "not verified"),
    ("DeviceL", "ModelIdentifier_i", "SQ610RF", "not verified"),
    ("data", "Endpoint", 1, "endpoint"),
    ("sIT600TH", "Schedule", "72" + "00" * 75, "layout"),
    ("sIT600TH", "Status_2_d", "72" + "00" * 76, "aliases"),
])
def test_unverified_profile_or_layout_is_rejected(section, field, value, message):
    status = status_fixture()
    status[section][field] = value
    with pytest.raises(IT600ValidationError, match=message):
        build_display_resolution_command(status, 1)
    assert not supports_display_resolution(status)
    assert not parse_climate_device(status).supports_display_resolution


def test_unverified_tail_is_rejected():
    status = status_fixture()
    replace_blob(status, 50, "00")
    with pytest.raises(IT600ValidationError, match="tail"):
        build_display_resolution_command(status, 1)


def test_pin_protected_settings_are_rejected():
    status = status_fixture()
    replace_blob(status, 43, "01")
    with pytest.raises(IT600ValidationError, match="PIN"):
        build_display_resolution_command(status, 1)
    # The reported resolution stays readable; only writing is refused.
    assert supports_display_resolution(status)



def test_in_flight_settings_echo_blocks_encoding_but_not_support():
    status = status_fixture()
    status["sIT600I"]["CommandResponse_d"] = in_flight_echo(status, 2, 0)
    with pytest.raises(IT600ValidationError, match="Settings command is pending"):
        build_display_resolution_command(status, 1)
    assert supports_display_resolution(status)


def test_missing_command_section_blocks_encoding():
    status = status_fixture()
    del status["sIT600I"]
    with pytest.raises(IT600ValidationError, match="Incomplete"):
        build_display_resolution_command(status, 1)
    assert supports_display_resolution(status)


@pytest.mark.parametrize("recorded", ["", "42313173", None])
def test_unrecognized_command_echo_blocks_encoding(recorded):
    status = status_fixture()
    status["sIT600I"]["CommandResponse_d"] = recorded
    with pytest.raises(IT600ValidationError, match="recorded layout is unverified"):
        build_display_resolution_command(status, 1)


def test_non_settings_echo_allows_encoding():
    status = status_fixture()
    status["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE.upper()
    assert build_display_resolution_command(status, 1) == RESOLUTION_01_COMMAND


def test_parser_exposes_capability_and_reported_resolution():
    device = parse_climate_device(status_fixture())
    assert device.supports_display_resolution
    assert device.advanced_settings.display_resolution == 0


def test_applied_check_compares_resolution_only():
    status = status_fixture()
    after = applied(status, RESOLUTION_01_COMMAND)
    assert display_resolution_applied(after, RESOLUTION_01_COMMAND)
    replace_blob(after, 2, "00")
    assert display_resolution_applied(after, RESOLUTION_01_COMMAND)
    assert not display_resolution_applied(status, RESOLUTION_01_COMMAND)
    assert not display_resolution_applied(after, "not hex")
    assert not display_resolution_applied(after, RESOLUTION_01_COMMAND[:-2])


async def test_gateway_uses_fresh_settings_and_disables_write_retry():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), ACK])
    await gateway.set_climate_device_display_resolution("device-1", 1)
    calls = gateway._make_encrypted_request.call_args_list
    assert calls[0].args[0] == "read"
    assert calls[1].args[1]["id"][0]["sIT600I"]["SetCommand_d"] == RESOLUTION_01_COMMAND
    assert calls[1].kwargs == {"retry_disconnect": False}


async def test_gateway_noop_never_writes():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    await gateway.set_climate_device_display_resolution("device-1", 0)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == ["read"]


@pytest.mark.parametrize("resolution,error", [
    (True, TypeError),
    (-1, IT600ValidationError),
    (2, IT600ValidationError),
])
async def test_gateway_rejects_invalid_resolution_before_reading(resolution, error):
    gateway, _ = setup_gateway()
    gateway._make_encrypted_request = AsyncMock()
    with pytest.raises(error):
        await gateway.set_climate_device_display_resolution("device-1", resolution)
    gateway._make_encrypted_request.assert_not_called()


async def test_cached_offline_status_never_requests():
    gateway, _ = setup_gateway()
    gateway._climate_devices["device-1"] = replace(gateway._climate_devices["device-1"], available=False)
    gateway._make_encrypted_request = AsyncMock()
    with pytest.raises(IT600ValidationError, match="^Cannot change display resolution on an offline device$"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    gateway._make_encrypted_request.assert_not_called()


async def test_fresh_offline_status_never_writes():
    gateway, status = setup_gateway()
    status["sZDOInfo"]["OnlineStatus_i"] = 0
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    with pytest.raises(IT600ValidationError, match="offline"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    assert gateway._make_encrypted_request.call_count == 1


async def test_missing_device_response_never_writes():
    gateway, _ = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value={"status": "success", "id": []})
    with pytest.raises(IT600CommandError, match="display-resolution device response"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    assert gateway._make_encrypted_request.call_count == 1


async def test_gateway_rejects_acknowledgement_for_wrong_device():
    gateway, status = setup_gateway()
    other = {"status": "success", "id": [{"status": "success", "data": {"UniID": "other", "Endpoint": 9}}]}
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), other])
    with pytest.raises(IT600CommandError, match="^Gateway did not acknowledge the display-resolution write$"):
        await gateway.set_climate_device_display_resolution("device-1", 1)


async def test_failed_write_stays_pending_until_expiry(monkeypatch):
    gateway, status = setup_gateway()
    clock = [0]
    monkeypatch.setattr(gateway, "_display_resolution_time", lambda: clock[0])
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), IT600ConnectionError("lost")])
    with pytest.raises(IT600ConnectionError):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    clock[0] = DISPLAY_RESOLUTION_PENDING_SECONDS - 1
    with pytest.raises(IT600ValidationError, match="still pending"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    clock[0] = DISPLAY_RESOLUTION_PENDING_SECONDS
    await gateway.set_climate_device_display_resolution("device-1", 1)
    assert written_body(gateway._make_encrypted_request.call_args_list[-1])[11] == 1



async def test_pending_write_blocks_a_second_write_until_applied():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    await gateway.set_climate_device_display_resolution("device-1", 1)
    with pytest.raises(IT600ValidationError, match="still pending"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(applied(status, RESOLUTION_01_COMMAND)))
    await gateway.set_climate_device_display_resolution("device-1", 0)
    assert written_body(gateway._make_encrypted_request.call_args_list[-1])[11] == 0


async def test_writes_are_serialized_and_see_the_previous_command():
    gateway, status = setup_gateway()
    write_started = asyncio.Event()
    finish_write = asyncio.Event()
    calls = []

    async def request(command, body, **kwargs):
        calls.append(command)
        if command == "read":
            return envelope(copy.deepcopy(status))
        write_started.set()
        await finish_write.wait()
        return ACK

    gateway._make_encrypted_request = request
    first = asyncio.create_task(gateway.set_climate_device_display_resolution("device-1", 1))
    await write_started.wait()
    second = asyncio.create_task(gateway.set_climate_device_display_resolution("device-1", 1))
    await asyncio.sleep(0)
    assert calls == ["read", "write"]
    finish_write.set()
    await first
    with pytest.raises(IT600ValidationError, match="still pending"):
        await second
    assert calls == ["read", "write", "read"]


async def test_app_change_of_another_setting_does_not_release_pending(monkeypatch):
    gateway, status = setup_gateway()
    clock = [0]
    monkeypatch.setattr(gateway, "_display_resolution_time", lambda: clock[0])
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    await gateway.set_climate_device_display_resolution("device-1", 1)
    # The app changes another settings byte; byte 11 stays at 0.
    app = copy.deepcopy(status)
    replace_blob(app, 2, "00")
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(app))
    with pytest.raises(IT600ValidationError, match="still pending"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    clock[0] = DISPLAY_RESOLUTION_PENDING_SECONDS
    await gateway.set_climate_device_display_resolution("device-1", 1)
    body = written_body(gateway._make_encrypted_request.call_args_list[-1])
    assert (body[11], body[2]) == (1, 0)


async def test_applied_write_releases_pending_despite_other_changes():
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    await gateway.set_climate_device_display_resolution("device-1", 1)
    after = applied(status, RESOLUTION_01_COMMAND)
    replace_blob(after, 2, "00")
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(after))
    await gateway.set_climate_device_display_resolution("device-1", 0)
    body = written_body(gateway._make_encrypted_request.call_args_list[-1])
    assert (body[11], body[2]) == (0, 0)


async def test_expired_local_echo_is_rechecked_then_written(monkeypatch):
    gateway, status = setup_gateway()
    clock = [0]
    monkeypatch.setattr(gateway, "_display_resolution_time", lambda: clock[0])
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    await gateway.set_climate_device_display_resolution("device-1", 1)
    # The gateway recorded the command, but the device never applied it.
    status["sIT600I"]["CommandResponse_d"] = RESOLUTION_01_COMMAND + "00"
    clock[0] = DISPLAY_RESOLUTION_PENDING_SECONDS
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    await gateway.set_climate_device_display_resolution("device-1", 1)
    calls = gateway._make_encrypted_request.call_args_list
    assert [c.args[0] for c in calls] == ["read", "read", "write"]
    assert written_body(calls[2])[11] == 1


async def test_non_settings_echo_requires_stable_settings(monkeypatch):
    gateway, status = setup_gateway()
    status["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    changed = copy.deepcopy(status)
    replace_blob(changed, 2, "00")
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), envelope(changed)])
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    with pytest.raises(IT600ValidationError, match="^Display resolution settings changed during stability check$"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == ["read", "read"]


async def test_new_echo_during_stability_check_uses_strict_guard(monkeypatch):
    gateway, status = setup_gateway()
    status["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    stable = copy.deepcopy(status)
    stable["sIT600I"]["CommandResponse_d"] = in_flight_echo(status, 2, 0)
    gateway._make_encrypted_request = AsyncMock(side_effect=[envelope(status), envelope(stable)])
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    with pytest.raises(IT600ValidationError, match="Settings command is pending"):
        await gateway.set_climate_device_display_resolution("device-1", 1)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == ["read", "read"]
