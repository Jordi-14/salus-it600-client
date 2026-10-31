"""App command readiness must not hide a readable floor-comfort entity."""
import copy
from unittest.mock import AsyncMock

import pytest

from salus_it600.comfort_warm_floor import (
    build_comfort_warm_floor_command,
    supports_comfort_warm_floor_profile,
    supports_comfort_warm_floor_write,
)
from salus_it600.exceptions import IT600ValidationError
from salus_it600.parsers.climate import parse_climate_device
from tests.test_comfort_warm_floor import replace_blob, setup_gateway, status_fixture
from tests.test_floor_command_lifecycle import confirmed, envelope


async def test_app_change_stays_readable_while_pending_and_never_allows_second_write():
    gateway, before = setup_gateway()
    # An actual level 1 before a vendor-app Off command, using synthetic identity.
    replace_blob(before, 39, '01')
    command = build_comfort_warm_floor_command(before, 0)
    pending = copy.deepcopy(before)
    pending['sIT600I']['CommandResponse_d'] = command + '00'
    after = confirmed(before, command)
    parsed = [parse_climate_device(status) for status in (before, pending, after)]
    assert [d.advanced_settings.comfort_warm_floor for d in parsed] == [1, 1, 0]
    assert all(d.supports_comfort_warm_floor for d in parsed)
    assert not supports_comfort_warm_floor_write(pending)
    gateway._make_encrypted_request = AsyncMock(return_value=envelope(pending))
    with pytest.raises(IT600ValidationError, match='pending'):
        await gateway.set_climate_device_comfort_warm_floor('device-1', 3)
    assert [call.args[0] for call in gateway._make_encrypted_request.call_args_list] == ['read']


@pytest.mark.parametrize('echo', [None, '', 'bad', '4231317300' + '00' * 58])
def test_missing_or_unknown_echo_cannot_hide_known_reported_setting(echo):
    status = status_fixture()
    status['sIT600I']['CommandResponse_d'] = echo
    assert supports_comfort_warm_floor_profile(status)
    assert parse_climate_device(status).advanced_settings.comfort_warm_floor == 0
    assert not supports_comfort_warm_floor_write(status)
    with pytest.raises(IT600ValidationError):
        build_comfort_warm_floor_command(status, 1)


def test_missing_command_section_remains_readable_but_not_writable():
    status = status_fixture()
    del status['sIT600I']
    assert supports_comfort_warm_floor_profile(status)
    assert not supports_comfort_warm_floor_write(status)


@pytest.mark.parametrize('section,key,value', [
    ('DeviceL','ModelIdentifier_i','SQ610RF'),
    ('sZDO','FirmwareVersion','00000055'),
    ('sIT600TH','Status_2_d','72'),
    ('sIT600TH','SystemMode',3),
])
def test_unsupported_profile_still_unavailable(section,key,value):
    status = status_fixture()
    status[section][key] = value
    assert not supports_comfort_warm_floor_profile(status)
    assert not supports_comfort_warm_floor_write(status)
