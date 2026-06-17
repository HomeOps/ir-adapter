"""Flipper adapter: a Flipper-IRDB `.ir` file → list[Signal].

`type: raw` signals pass through as timings; `type: parsed` (NEC/NECext, SIRC/15/20,
Samsung32, RC5/RC5X, Sharp) are encoded to timings by infrared-protocols and keep
their protocol/address/command so a consumer can also transmit them natively.
"""

from . import encode
from .signal import Signal


def parse_ir(text):
    """Parse a Flipper .ir file into a list of signal dicts (split on '#')."""
    entries, cur = [], {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("Filetype", "Version")):
            continue
        if line == "#":
            if cur:
                entries.append(cur)
                cur = {}
            continue
        key, sep, val = line.partition(":")
        if sep:
            cur[key.strip()] = val.strip()
    if cur:
        entries.append(cur)
    return entries


def _le(field):
    """'04 03 00 00' -> integer 0x0304 (little-endian)."""
    out = 0
    for i, byte in enumerate(field.split()):
        out |= int(byte, 16) << (8 * i)
    return out


def _signal(entry):
    """One Flipper entry -> Signal, or None if the protocol isn't encodable."""
    name = entry.get("name", "unnamed")
    if entry.get("type") == "raw":
        carrier = int(entry.get("frequency", "38000"))
        nums = [int(x) for x in entry["data"].split()]
        timings = tuple(n if i % 2 == 0 else -n for i, n in enumerate(nums))
        return Signal(name=name, carrier_hz=carrier, timings=timings, repeat=1)

    protocol = entry.get("protocol", "")
    address = _le(entry["address"])
    command = _le(entry["command"])
    cmd = encode.command_for(protocol, address, command)
    if cmd is None:
        return None
    carrier, timings = encode.raw_timings(cmd)
    return Signal(
        name=name, carrier_hz=carrier, timings=timings, protocol=protocol,
        address=address & 0xFFFF, command=command & 0xFF, repeat=encode.PARSED_REPEAT,
    )


def from_text(text, *, skip_unsupported=True):
    """Parse Flipper `.ir` text into Signals.

    Unsupported protocols and bad fields are skipped by default (set
    skip_unsupported=False to raise instead). ImportError (infrared-protocols not
    installed) is also skipped under the default, so raw captures still come through.
    """
    out = []
    for entry in parse_ir(text):
        try:
            signal = _signal(entry)
        except (KeyError, ValueError, ImportError):
            if skip_unsupported:
                continue
            raise
        if signal is None:
            if skip_unsupported:
                continue
            raise ValueError(f"unsupported protocol for {entry.get('name')!r}")
        out.append(signal)
    return out


def from_file(path, **kwargs):
    """Parse a Flipper `.ir` file path into Signals."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return from_text(fh.read(), **kwargs)
