"""Encode a parsed protocol to raw timings via home-assistant-libs/infrared-protocols.

This library IS the "HA protocol": the same encoder Home Assistant's IR proxy uses,
so codes we emit are protocol-correct by construction for both ESPHome and HA. We
keep no protocol math of our own — `command_for()` builds the library Command and
`raw_timings()` returns the timings it produces. Imports are local so parsing/raw
passthrough work without the library installed.
"""

# Flipper SIRC variants -> SonyCommand address width (command is always 7-bit).
SONY_ADDRESS_BITS = {"SIRC": 5, "SIRC15": 8, "SIRC20": 13}

# The library returns ONE frame per command (repetition is the transmit layer's
# job, as HA's IR proxy does). Sony SIRC and others need ~3 frames before a device
# acts, so parsed signals carry this repeat hint; a raw capture is authoritative.
PARSED_REPEAT = 3


def command_for(protocol, address, command):
    """Build an infrared-protocols Command for a parsed signal, or None if unmapped.

    Field values pass straight through so the library's own range checks reject bad
    data (raising ValueError) rather than us emitting a wrong-but-plausible code.
    """
    if protocol in ("NEC", "NECext"):
        from infrared_protocols.commands.nec import NECCommand

        # NECCommand selects standard (<=0xFF, adds inversion) vs extended (16-bit)
        # from the address width — matching Flipper NEC vs NECext.
        return NECCommand(address=address & 0xFFFF, command=command & 0xFF)
    if protocol in SONY_ADDRESS_BITS:
        from infrared_protocols.commands.sony import SonyCommand

        return SonyCommand(address=address, address_bits=SONY_ADDRESS_BITS[protocol], command=command)
    if protocol == "Samsung32":
        from infrared_protocols.commands.samsung import Samsung32Command

        return Samsung32Command(address=address & 0xFFFF, command=command & 0xFF)
    if protocol in ("RC5", "RC5X"):
        from infrared_protocols.commands.rc5 import RC5Command

        return RC5Command(address=address, command=command)
    if protocol == "Sharp":
        from infrared_protocols.commands.sharp import SharpCommand

        return SharpCommand(address=address, command=command)
    return None


def raw_timings(command):
    """(carrier_hz, signed timings) for a library Command.

    The library already returns ESPHome's signed convention (+ = mark, - = space),
    so we pass it through unchanged. (Flipper `type: raw` data, by contrast, is
    all-positive and is sign-alternated by the flipper adapter.)
    """
    return command.modulation, tuple(command.get_raw_timings())
