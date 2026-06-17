"""The common IR signal representation shared by every consumer.

One `Signal` drives both transmit paths:

  * ESPHome YAML        -> `carrier_hz` + `timings` as remote_transmitter.transmit_raw
                           (or `protocol`/`address`/`command` as transmit_nec/…).
  * HA IR-proxy custom  -> `protocol`/`address`/`command` straight to the proxy,
    component             falling back to raw `timings` for un-parsed captures.

`timings` is ESPHome's signed convention: + = carrier on (mark), - = off (space).
`canonical` is the control this button maps to (homeops-ir-canonical), resolved at
parse time so the Signal is self-describing — `None` when the name has no mapping.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Signal:
    name: str
    carrier_hz: int
    timings: tuple[int, ...] = field(default_factory=tuple)
    protocol: str | None = None     # NEC / NECext / SIRC / Samsung32 / … ; None for raw
    address: int | None = None
    command: int | None = None
    repeat: int = 1                 # transmit-layer repeats (library frames need ~3)
    canonical: str | None = None    # canonical control id (e.g. volume_up); None if unmapped

    @property
    def is_parsed(self) -> bool:
        """True when a decoded protocol/address/command is available (not a raw capture)."""
        return self.protocol is not None
