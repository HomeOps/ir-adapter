"""Tests for the flipper adapter. Encoding tests require infrared-protocols (3.14)."""

import pytest

from ir_adapter import Signal, flipper

RAW = (
    "Filetype: IR signals file\nVersion: 1\n#\n"
    "name: Power\ntype: raw\nfrequency: 38000\ndata: 100 200 300 400\n"
)
NEC = (
    "Filetype: IR signals file\nVersion: 1\n#\n"
    "name: On\ntype: parsed\nprotocol: NEC\naddress: 04 00 00 00\ncommand: 08 00 00 00\n"
)


def test_parse_ir_splits_on_hash():
    entries = flipper.parse_ir(RAW + "#\n" + "name: B\ntype: raw\nfrequency: 38000\ndata: 1 2\n")
    assert [e["name"] for e in entries] == ["Power", "B"]


def test_raw_signal_has_signed_timings_and_no_protocol():
    (sig,) = flipper.from_text(RAW)
    assert isinstance(sig, Signal)
    assert sig.name == "Power"
    assert sig.carrier_hz == 38000
    assert sig.timings == (100, -200, 300, -400)
    assert sig.protocol is None and sig.is_parsed is False
    assert sig.repeat == 1
    assert sig.canonical == "power_toggle"      # name "Power" -> canonical control


def test_unmapped_name_has_no_canonical():
    text = ("Filetype: IR signals file\nVersion: 1\n#\n"
            "name: Whatchamacallit\ntype: raw\nfrequency: 38000\ndata: 1 2\n")
    (sig,) = flipper.from_text(text)
    assert sig.canonical is None


def test_le_decode():
    assert flipper._le("04 03 00 00") == 0x0304


def test_unsupported_protocol_skipped_by_default():
    text = ("Filetype: IR signals file\nVersion: 1\n#\n"
            "name: X\ntype: parsed\nprotocol: RC6\naddress: 00 00 00 00\ncommand: 00 00 00 00\n")
    assert flipper.from_text(text) == []


def test_parsed_nec_signal_carries_protocol_and_timings():
    pytest.importorskip("infrared_protocols")     # encoding needs the library (3.14)
    (sig,) = flipper.from_text(NEC)
    assert sig.protocol == "NEC"
    assert sig.address == 0x04 and sig.command == 0x08
    assert sig.carrier_hz == 38000
    assert sig.timings[:2] == (9000, -4500)     # NEC leader from the library
    assert sig.repeat == 3
    assert sig.canonical == "power_on"          # name "On" -> canonical control
