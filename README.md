# ir-adapter

Turn IR sources into a **common `Signal`** that drives both **ESPHome** firmware
and a **Home Assistant IR-proxy** custom component — one representation, two
transmit paths. The signal/protocol sibling to
[`ir-canonical`](https://github.com/HomeOps/ir-canonical) (which owns the *name*).

```bash
pip install homeops-ir-adapter
```

## Use it

```python
from ir_adapter import flipper, ha, Signal

signals = flipper.from_file("TVs/Sony/Sony_Bravia.ir")   # a Flipper-IRDB .ir path
signals = ha.from_codeset("vizio/tv")                    # an infrared-protocols code set

s = signals[0]
s.name           # "Power"
s.carrier_hz     # 38000
s.timings        # (9000, -4500, 560, -560, ...)  signed: + mark, - space
s.protocol       # "NEC" (None for raw captures)
s.address, s.command
s.repeat         # transmit-layer repeats (parsed frames need ~3)
```

A `Signal` carries both forms so either consumer uses what it needs:

| Consumer | Uses |
|----------|------|
| **ESPHome YAML** (esphome-ir-codegen) | `carrier_hz` + `timings` → `remote_transmitter.transmit_raw` (or `protocol`/`address`/`command` → `transmit_nec`/…) |
| **HA IR-proxy** custom component (concerto) | `protocol`/`address`/`command` → the proxy, with raw `timings` as fallback |

## Adapters

| Adapter | Input | Call |
|---------|-------|------|
| **flipper** | a Flipper-IRDB `.ir` file path | `flipper.from_file(path)` / `flipper.from_text(text)` |
| **ha** | an infrared-protocols code set (`<brand>/<type>`) | `ha.from_codeset("vizio/tv")` / `ha.codesets()` |

Parsed protocols (NEC/NECext, Sony SIRC/15/20, Samsung32, RC5/RC5X, Sharp) are
encoded to timings by
[infrared-protocols](https://github.com/home-assistant-libs/infrared-protocols) —
the same encoder HA's IR proxy uses, so codes are protocol-correct by
construction. A Flipper `type: raw` capture passes through as-is.

> Requires **Python ≥ 3.14** (the infrared-protocols dependency). Parsing of `.ir`
> text works without it; encoding parsed protocols needs it.

## Develop

```bash
python -m build --wheel --no-isolation
pip install dist/*.whl && pytest -q
```

Releases: [release-please](https://github.com/googleapis/release-please) cuts a
release PR; merging it tags + publishes to **PyPI** via trusted publishing
(`publish.yaml`, environment `pypi`).
