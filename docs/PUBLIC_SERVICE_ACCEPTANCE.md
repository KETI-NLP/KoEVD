# Public service acceptance: analysis clarity and display evidence

Updated 2026-10-21. **[v0.3.0-rc.23](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.23)**
clarifies per-model rates, source support and Task 3/4/5 exploration in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).

The release attachment [chart_clarity_acceptance_20261021.json](https://github.com/KETI-NLP/KoEVD/releases/download/v0.3.0-rc.23/chart_clarity_acceptance_20261021.json)
records the exact application and Space revisions, final CI, installation and
public-browser acceptance. See the [task analysis guide](TASK_ANALYSIS_GUIDE.md)
and [first-user guide](GETTING_STARTED.md).

## Interpretation and behavior

- Observed task charts use each model's own valid-output denominator; the separate
  matched-input statistics use jointly valid measurements. They are named separately.
- Unique input inventories, valid measurements and conditional row support have
  explicit labels. Strategy co-inclusion includes full-input completion.
- Task 3 support/completion thresholds filter display groups and mask cross cells;
  cohort totals, mathematical denominators and contrast screening stay unchanged.
  Every compared model must meet thresholds. Hidden counts and recovery are explicit.
- Live numerical matrices retain both axes while scrolling, use clearer text, and
  preserve keyboard selection, pinned evidence, numerical export and SVG export.
  The fifteen-strategy comparison uses compact paired dots with both fractions.
- Task 5's denominator switch is beside the affected response-group bars. The
  seven-outcome and correspondence matrices always include invalid observations.
  Framing marks offer explicit detail navigation and condition/framing undo.
- Optional controls/context are collapsed initially; active input requirements
  remain visible. Empty input conditions provide filter-removal/undo guidance.

## Numerical and operational scope

No classifier, generation or parsing inference is rerun. Original results, all
twelve historical numerical assets, published revisions and matched statistics
remain unchanged. Historical and current-protocol collections remain separate.
No combined ethics score, official rank or causal/significance claim is introduced.

The release receipt lists regression, fresh-install and actual browser checks.
The service remains public CPU Basic with one replica. Existing operator inputs,
LFS rules, state/secret settings and resource/backup policy are preserved. No
raw-result uploads or new private transmissions are part of this update.

[Previous rc22 acceptance](audit/public_service_acceptance_rc22_20261021.md)
preserves the archived-source reconciliation and prior numerical evidence.
