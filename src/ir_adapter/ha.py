"""HA adapter: infrared-protocols' own curated code sets → list[Signal].

Each brand/type code set (e.g. 'vizio/tv') exposes Enums whose members have a
`.to_command()`; we encode each to timings. (These are HA's curated codes — the
same library the IR proxy uses — so they're protocol-correct by construction.)
"""

from . import encode
from .signal import Signal


def codesets():
    """Yield (relpath, list[Signal]) for every infrared-protocols code set.

    The library's brand dirs (codes/vizio/…) are namespace packages with no
    __init__.py, which pkgutil won't descend into — so we walk the package on disk
    and import each module by name.
    """
    import enum
    import importlib
    import os

    import infrared_protocols.codes as codes_pkg
    from infrared_protocols.commands import Command

    base = codes_pkg.__name__
    for root in list(codes_pkg.__path__):
        for dirpath, _dirs, files in os.walk(root):
            for filename in sorted(files):
                if not filename.endswith(".py") or filename == "__init__.py":
                    continue
                relmod = os.path.relpath(os.path.join(dirpath, filename), root)[:-3]
                relmod = relmod.replace(os.sep, ".")
                modname = f"{base}.{relmod}"
                try:
                    mod = importlib.import_module(modname)
                except Exception:
                    continue
                signals, seen = [], set()
                for attr in vars(mod).values():
                    if not (isinstance(attr, type) and issubclass(attr, enum.Enum)):
                        continue
                    if attr.__module__ != modname or not hasattr(attr, "to_command"):
                        continue
                    for member in attr:
                        if member.name in seen:
                            continue
                        try:
                            command = member.to_command()
                        except Exception:
                            continue
                        if not isinstance(command, Command):
                            continue
                        seen.add(member.name)
                        carrier, timings = encode.raw_timings(command)
                        signals.append(Signal(name=member.name, carrier_hz=carrier,
                                              timings=timings, repeat=encode.PARSED_REPEAT))
                if signals:
                    yield relmod.replace(".", "/"), signals


def from_codeset(name):
    """Signals for one code set path, e.g. 'vizio/tv'; [] if unknown."""
    for rel, signals in codesets():
        if rel == name:
            return signals
    return []
