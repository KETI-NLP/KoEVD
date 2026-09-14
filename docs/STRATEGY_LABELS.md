# Strategy output labels

The classifier returns the internal codes below. The dataset exporter explicitly renames those codes to the canonical display labels. This is a naming crosswalk for the existing annotations, not a new taxonomy or a claim about prediction accuracy. The parser and scorer continue to use the original codes.

| Classifier code | Canonical dataset display label |
|---|---|
| `a_evaluation` | Evaluate Utterance |
| `a_boundary setting` | Set a Boundary |
| `a_providing definitions` | Define Terms |
| `a_detouring q` | Detouring Question |
| `a_reiteration` | Sanitized Reiteration |
| `b_counter speech` | Counter-speech |
| `b_agreeing speech` | Conditional Empathy |
| `b_neutral speech` | Neutral Framing |
| `c_reasoning` | Reasoning |
| `c_info providing` | Safe Information |
| `c_educating` | Educating / Safer Alternative |
| `d_summation` | Summation |
| `d_social expressions` | Social Expression |
| `d_redirecting` | Redirecting |
| `e_humour` | Humour |

`unsafe` is a separate response-safety marker and has no mitigation-strategy counterpart. It must not be counted as a sixteenth mitigation strategy. The scorer can report its inclusion separately.

Machine-readable map: [strategy_label_map.json](strategy_label_map.json).

## Provenance

The two original dataset exporters contain identical `STRATEGY_MAP` dictionaries; the canonical labels were checked against the released `schema/LABELS.json`. In particular, `b_agreeing speech` maps to **Conditional Empathy**, and `c_info providing` maps to **Safe Information**. These mappings were recovered from the exporter, not inferred from similar names.

- `rebuild_current_public_release_dataset.py` SHA-256: `d4fdac1bfff51ae587056c75ebc364044de7a67c8152a416439bcb14ce5e06f4`
- `build_public_release.py` SHA-256: `49b8a3f0b79c02f2ec373c5a0689fa5a2fa6fe2c496d07d67703340999c95009`
