"""Regressions for shared responses, uncertain sends, and inherited input checks."""

import copy
from unittest.mock import AsyncMock

import pytest

from salus_it600.comfort_warm_floor import (
    NON_SETTINGS_RESPONSE,
    build_comfort_warm_floor_command,
)
from salus_it600.exceptions import (
    IT600ConnectionError,
    IT600ValidationError,
)
from salus_it600.gateway import _validate_positive_number, _validate_setpoint
from salus_it600.parsers.advanced_settings import parse_advanced_settings
from salus_it600.parsers.common import _numeric_value
from tests.test_comfort_warm_floor import replace_blob, setup_gateway, status_fixture
from tests.test_floor_beta import confirmed, envelope


async def test_observed_other_command_echo_requires_stable_read_and_preserves_write_guards(
    monkeypatch,
):
    gateway, status = setup_gateway()
    status["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    command = build_comfort_warm_floor_command(status, 3)
    after = confirmed(status, command)
    # The shared echo may be replaced by B34L after the setting was applied.
    after["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    gateway._make_encrypted_request = AsyncMock(
        side_effect=[
            envelope(status),
            envelope(status),
            envelope(status),
            envelope(after),
        ]
    )
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    await gateway.set_climate_device_comfort_warm_floor(
        "device-1", 3, confirmation_timeout=1
    )
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == [
        "read",
        "read",
        "write",
        "read",
    ]
    assert not gateway._pending_floor_commands


async def test_shared_echo_does_not_allow_overwriting_a_changing_snapshot(monkeypatch):
    gateway, status = setup_gateway()
    status["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    changed = copy.deepcopy(status)
    replace_blob(changed, 39, "01")
    changed["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    gateway._make_encrypted_request = AsyncMock(
        side_effect=[envelope(status), envelope(changed)]
    )
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    with pytest.raises(IT600ValidationError, match="changed during"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    assert [c.args[0] for c in gateway._make_encrypted_request.call_args_list] == [
        "read",
        "read",
    ]


async def test_unknown_send_remains_blocked_even_if_shared_echo_is_overwritten(
    monkeypatch,
):
    gateway, status = setup_gateway()
    gateway._make_encrypted_request = AsyncMock(
        side_effect=[envelope(status), IT600ConnectionError("lost")]
    )
    with pytest.raises(IT600ConnectionError):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    assert gateway._pending_floor_commands
    status["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(status))
    with pytest.raises(IT600ValidationError, match="pending or uncertain"):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 1)
    assert gateway._make_encrypted_request.call_count == 1


@pytest.mark.parametrize("echo", ["4233344d", "", None, "00", "42313173" + "zz" * 60])
def test_no_general_allowance_for_unknown_or_malformed_echo(echo):
    status = status_fixture()
    status["sIT600I"]["CommandResponse_d"] = echo
    with pytest.raises(IT600ValidationError):
        build_comfort_warm_floor_command(status, 1)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_inherited_numeric_validation_rejects_non_finite_inputs(value):
    assert _numeric_value(value) is None
    with pytest.raises(IT600ValidationError):
        _validate_positive_number(value, "timeout")
    with pytest.raises(IT600ValidationError):
        _validate_setpoint(value, 5, 35)
    with pytest.raises(IT600ValidationError):
        _validate_setpoint(20, value, 35)


@pytest.mark.parametrize("preferred", ["", "72", "72" + "00" * 100, 42, None])
def test_inherited_decoder_falls_back_to_complete_legacy_alias(preferred):
    base = status_fixture()["sIT600TH"]["Schedule"]
    assert parse_advanced_settings(
        {"Status_2_d": preferred, "Schedule": base}
    ) == parse_advanced_settings({"Schedule": base})


def test_equivalent_hex_alias_case_does_not_change_command():
    status = status_fixture()
    expected = build_comfort_warm_floor_command(status, 1)
    status["sIT600TH"]["Status_2_d"] = status["sIT600TH"]["Schedule"].upper()
    assert build_comfort_warm_floor_command(status, 1) == expected


async def test_applied_unknown_command_is_resolved_with_fresh_state_and_new_counter(
    monkeypatch,
):
    gateway, status = setup_gateway()
    first = build_comfort_warm_floor_command(status, 3)
    gateway._make_encrypted_request = AsyncMock(
        side_effect=[envelope(status), IT600ConnectionError("lost")]
    )
    with pytest.raises(IT600ConnectionError):
        await gateway.set_climate_device_comfort_warm_floor("device-1", 3)
    applied = confirmed(status, first)
    applied["sIT600I"]["CommandResponse_d"] = NON_SETTINGS_RESPONSE
    next_command = build_comfort_warm_floor_command(applied, 1)
    final = confirmed(applied, next_command)
    gateway._make_encrypted_request = AsyncMock(
        side_effect=[
            envelope(applied),
            envelope(applied),
            envelope(applied),
            envelope(final),
        ]
    )
    monkeypatch.setattr("salus_it600.gateway.asyncio.sleep", AsyncMock())
    await gateway.set_climate_device_comfort_warm_floor(
        "device-1", 1, confirmation_timeout=1
    )
    write = gateway._make_encrypted_request.call_args_list[2]
    assert write.args[0] == "write"
    assert write.args[1]["id"][0]["sIT600I"]["SetCommand_d"] == next_command
    assert bytes.fromhex(next_command)[4] == bytes.fromhex(first)[4] + 1
