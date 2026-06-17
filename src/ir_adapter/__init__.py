"""ir-adapter — IR sources → a common Signal for ESPHome and HA's IR proxy.

Adapters normalize different IR sources into `Signal` objects:

    from ir_adapter import flipper, ha, Signal

    signals = flipper.from_file("TVs/Sony/Sony_Bravia.ir")   # a Flipper .ir path
    signals = ha.from_codeset("vizio/tv")                    # an infrared-protocols code set

Each `Signal` carries both the decoded protocol (protocol/address/command, when
available) and the raw `carrier_hz`+`timings`, so the same object drives ESPHome
`transmit_raw`/`transmit_nec` and Home Assistant's IR proxy.
"""

from . import flipper, ha
from .signal import Signal

try:
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("homeops-ir-adapter")
except Exception:                       # not installed (running from source)
    __version__ = "0.0.0"

__all__ = ["Signal", "flipper", "ha", "from_flipper_file", "__version__"]


def from_flipper_file(path, **kwargs):
    """Convenience shortcut for :func:`ir_adapter.flipper.from_file`."""
    return flipper.from_file(path, **kwargs)
