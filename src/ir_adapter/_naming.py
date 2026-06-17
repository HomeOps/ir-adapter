"""Resolve a raw button name to a canonical control id (homeops-ir-canonical).

Kept here so every adapter labels its Signals the same way: a curated lookup
first, then the broad rule engine, else None (unmapped).
"""

from ir_canonical import canonical as _canonical
from ir_canonical import resolve as _resolve


def control_of(name):
    """Canonical control id for a button name, or None if unmapped."""
    return _resolve(name) or _canonical(name)
