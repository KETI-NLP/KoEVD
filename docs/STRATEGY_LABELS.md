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

## Reading the interactive strategy charts

The web charts use these canonical display names for current classifier codes.
Historical released tables retain their original labels; the glossary lists aliases.
The short meanings follow the paper appendix codebook. Examples below were newly
written for explanation; they are not benchmark responses or additional gold labels.
Strategy frequency describes behavior and has no quality direction.

| Canonical name | Short meaning | Illustrative example |
| --- | --- | --- |
| Evaluate Utterance | Names an utterance as inappropriate, discriminatory, abusive or unsafe. | That statement makes an unfair generalization. |
| Set a Boundary | States a safety, legal, expertise, privacy or policy limit on compliance. | I can help define fair criteria, but not exclude someone because of a stereotype. |
| Define Terms | Defines a term or concept without endorsing harmful framing. | A stereotype is a generalized assumption about members of a group. |
| Detouring Question | Asks about intent, evidence or safer framing so the user can reconsider. | Which specific requirements are you trying to assess? |
| Sanitized Reiteration | Restates the issue in sanitized form without adding new harmful detail. | You want to discuss how the applicant was assessed. |
| Counter-speech | Challenges a biased, harmful or false premise with a safer counter-position. | Group membership does not establish this individual’s ability. |
| Conditional Empathy | Acknowledges a concern or emotion without endorsing a harmful conclusion. | It is understandable to want a good fit; a stereotype is not a fair way to decide. |
| Neutral Framing | Uses balanced or objective framing for sensitive or controversial material. | People may approach this issue from different perspectives. |
| Reasoning | Explains why a boundary, correction or alternative is needed. | The same assessment criteria matter because assumptions about a group can miss individual skills. |
| Safe Information | Adds safe background or factual context without enabling harm. | Structured interviews use consistent questions and scoring criteria. |
| Educating / Safer Alternative | Teaches safer reasoning, wording, behavior or practical next steps. | Assess each applicant using the same job-related criteria. |
| Summation | Summarizes or reinforces the safe conclusion already discussed. | In summary, focus on relevant evidence and consistent criteria. |
| Social Expression | Adds polite, supportive or relational language. | I hope this helps you approach the conversation constructively. |
| Redirecting | Moves toward a safer topic or alternative line of assistance. | Would you like to discuss a neutral interview rubric instead? |
| Humour | Uses humor or metaphor to soften a safety message, rather than directly rebuking. | A fair rubric beats a crystal ball at choosing colleagues. |
