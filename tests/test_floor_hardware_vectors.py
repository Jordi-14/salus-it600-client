"""Regression vectors confirmed by 75 real, independently audited writes."""

import json
from pathlib import Path

import pytest

from salus_it600.comfort_warm_floor import build_comfort_warm_floor_command
from salus_it600.exceptions import IT600ValidationError

EVIDENCE = json.loads(
    (Path(__file__).parent / "fixtures" / "comfort_warm_floor_75.json").read_text(encoding="utf-8")
)


def snapshot(vector, *, after=False):
    schedule = vector["after" if after else "before"]
    recorded = vector["afterRecordedCommand" if after else "beforeRecordedCommand"]
    return {
        "status": "success",
        "data": {"UniID": vector["group"], "Endpoint": 9, "DeviceType": 100},
        "DeviceL": {"ModelIdentifier_i": EVIDENCE["model"]},
        "sZDO": {"FirmwareVersion": EVIDENCE["firmware"]},
        "sIT600TH": {
            "Schedule": schedule, "Status_2_d": schedule,
            "PairedTRVShortID": "F" * 24, "PairedWCNumber": 1, "SystemMode": 4,
        },
        "sIT600I": {"CommandResponse_d": recorded},
    }


@pytest.mark.parametrize("vector", EVIDENCE["vectors"], ids=lambda v: f"{v['group']}-{v['step']:02d}")
def test_exact_hardware_command_and_readback(vector):
    command = build_comfort_warm_floor_command(snapshot(vector), vector["targetLevel"])
    assert command == vector["command"]
    before = bytes.fromhex(vector["before"])
    body = bytes.fromhex(command)[3:]
    predicted_after = bytes([0x72]) + body[1:] + before[60:]
    assert predicted_after.hex() == vector["after"]
    assert vector["afterRecordedCommand"] == command + "00"
    assert all(before[i] == predicted_after[i] for i in range(77) if i not in (1, 39, 40, 41))


def test_no_extrapolation_past_last_hardware_verified_counter():
    last = max(EVIDENCE["vectors"], key=lambda v: bytes.fromhex(v["after"])[1])
    assert bytes.fromhex(last["after"])[1] == 34
    with pytest.raises(IT600ValidationError, match="counter"):
        build_comfort_warm_floor_command(snapshot(last, after=True), 1)
