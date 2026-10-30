"""A truncated preferred alias must not hide a complete legacy settings blob."""
import pytest

from salus_it600.parsers.advanced_settings import parse_advanced_settings

BLOB = '720701000001050040000000000104002700100006003500050040000500010000000101800000000dfe010000000100ffffffffffffffffffffffffffffffffffffffffffffffffffffff0000'


@pytest.mark.parametrize('preferred', ['', '72', '72'+'00'*100, 42, None])
def test_complete_schedule_alias_is_decoded_when_preferred_alias_is_incomplete(preferred):
    expected = parse_advanced_settings({'Schedule': BLOB})
    assert expected is not None
    assert parse_advanced_settings({'Status_2_d': preferred, 'Schedule': BLOB}) == expected
