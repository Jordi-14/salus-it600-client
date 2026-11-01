"""Regression vectors confirmed by 75 real, independently audited writes."""

import json
from pathlib import Path

import pytest

from salus_it600.comfort_warm_floor import build_comfort_warm_floor_command

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
def test_historical_settings_preserved_by_comfort_only_encoding(vector):
    command = build_comfort_warm_floor_command(snapshot(vector), vector["targetLevel"])
    before = bytes.fromhex(vector["before"])
    body = bytes.fromhex(command)[3:]
    assert [i for i in range(60) if before[i] != body[i]] == [0, 39]
    assert body[39] == vector["targetLevel"]
    # Historical trial used incrementing commands. Keep its observed protected
    # settings as evidence, without pretending it used the new command strategy.
    actual = bytes.fromhex(vector["after"])
    assert all(before[i] == actual[i] for i in range(77) if i not in (1, 39, 40, 41))


def test_counter_255_is_preserved_without_software_overflow():
    last = max(EVIDENCE["vectors"], key=lambda v: bytes.fromhex(v["after"])[1])
    assert bytes.fromhex(last["after"])[1] == 34
    assert bytes.fromhex(build_comfort_warm_floor_command(snapshot(last, after=True), 1))[4] == 34
    status = snapshot(last, after=True)
    data = bytearray.fromhex(status["sIT600TH"]["Schedule"])
    data[1] = 255
    data[40:42] = b'\xfd\xc0'
    status["sIT600TH"]["Schedule"] = status["sIT600TH"]["Status_2_d"] = data.hex()
    status["sIT600I"]["CommandResponse_d"] = "42313173" + data[1:60].hex() + "00"
    command = build_comfort_warm_floor_command(status, 1)
    assert bytes.fromhex(command)[4] == 255
    assert bytes.fromhex(command)[43:45] == b'\xfd\xc0'
