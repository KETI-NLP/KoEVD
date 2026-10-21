# Public service acceptance: evidence and cross-task analysis flow

Updated 2026-10-21. **[v0.3.0-rc.24](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.24)**
improves Task 3/4/5 evidence inspection, candidate recovery and explicit
cross-task condition transfer in the [Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).

The release attachment [analysis_flow_acceptance_20261021.json](https://github.com/KETI-NLP/KoEVD/releases/download/v0.3.0-rc.24/analysis_flow_acceptance_20261021.json)
records exact source/Space revisions, CI, fresh installation and public-browser
checks. See the [task analysis guide](TASK_ANALYSIS_GUIDE.md).

- Tooltips use actual dimensions to stay within the viewport. Explicit selection
  reveals full evidence and offers return to the selected mark. Task 4/5 comparison
  evidence retains the corresponding observation for each model.
- Task 5 response-label navigation includes its local denominator controller.
  Outcome composition places model rows together under each framing; all seven
  outcomes, invalid observations and expected-input denominators are preserved.
- Task 3 candidates hidden by display thresholds have explicit keep/clear actions.
  Their independent screening policy and all underlying cohort totals remain intact.
- Opt-in task transfer previews source/target counts and input scope; unsupported
  metadata are disclosed. Ordinary tabs retain independent task memory. Matching
  metadata do not establish identical inputs, execution traces or causal effects.
- Charts offer height expansion, and narrow matrix views reserve more data space.

No inference is rerun. The twelve historical numerical assets, existing registered
profiles, revisions, original scores and matched-input statistics remain unchanged.
Historical and current-protocol collections stay separate; no combined ethics
score or official rank is introduced.

Public CPU Basic, one replica, operator inputs, LFS rules, state/secret settings
and resource/backup policies are preserved. This is a code-only update with no
raw-result uploads or new private-data transmissions.

[Previous rc23 acceptance](audit/public_service_acceptance_rc23_20261021.md)
preserves the preceding denominator, evidence-filter and matrix checks.

## Korean first-user guide

The [Korean walkthrough](USER_GUIDE_KO.md) connects pinned evaluation commands,
recovery, private registration and optional numerical sharing to real Qwen3-8B/4B
Task 3–5 analysis examples. The GitHub README, Space header, standalone submission
introduction and Space card link to it. This documentation/navigation update
retains the rc24 evaluation client and its scoring definitions.
No model results, state configuration, credentials or resource policies change.
