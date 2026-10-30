"""Reject non-finite values and recheck temperature bounds after rounding."""
from dataclasses import replace
from unittest.mock import AsyncMock

import pytest

from salus_it600.exceptions import IT600ValidationError
from salus_it600.gateway import _validate_positive_number, _validate_setpoint
from salus_it600.parsers.common import _numeric_value
from tests.test_gateway_request import FakeSession, make_climate_device, make_gateway


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_numbers_are_rejected(value):
    assert _numeric_value(value) is None
    with pytest.raises(IT600ValidationError):
        _validate_positive_number(value, "timeout")
    with pytest.raises(IT600ValidationError):
        _validate_setpoint(value, 5, 35)
    with pytest.raises(IT600ValidationError):
        _validate_setpoint(20, value, 35)


def test_inverted_bounds_are_invalid():
    with pytest.raises(IT600ValidationError):
        _validate_setpoint(20, 35, 5)


@pytest.mark.parametrize("minimum,maximum,target", [(5.1, 35, 5.1), (5, 34.9, 34.9)])
async def test_rounding_cannot_cross_device_limits(minimum, maximum, target):
    gateway = make_gateway(FakeSession())
    gateway._climate_devices['climate-1'] = replace(make_climate_device(), min_temp=minimum, max_temp=maximum,
        min_heat_temp=minimum, max_heat_temp=maximum, system_mode=4)
    gateway._make_encrypted_request = AsyncMock()
    with pytest.raises(IT600ValidationError):
        await gateway.set_climate_device_temperature('climate-1', target)
    gateway._make_encrypted_request.assert_not_called()
