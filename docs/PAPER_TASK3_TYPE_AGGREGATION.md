# Original paper models: Task 3 type analysis

The 12 paper models now support the same safe/unsafe type explorer as registered
models. Open the initial **Paper experiment · 12 models** leaderboard → a model's
**Details → Task 3**. Below the overall chart, use **Safe and unsafe responses by
user-input type**. Select a type, inspect Topic/Input severity/Explicitness, or
choose **Compare selected type with another model**. The comparison preserves
the selected type, safety view, rate/count mode, search and breakdown axis.

This corrects the earlier statement that paper-model type analysis was
unavailable: the initial public app contained summary tables only, but the
archived original predictions and input metadata were present in the project.

## What the numbers represent

Each model has the original 13,552 Task 3 sources: 162,624 model/source records
across 12 models. Counts were reaggregated from the archived classification
outputs, without generating responses or running a classifier again. Each
model's total/classified/unsafe counts match the existing paper summary exactly.
No earlier Task 1–5 model values or published percentages were replaced.

- Unsafe rate = unsafe / classified responses; safe rate = safe / classified.
  Safe count = classified minus unsafe. These two rates total 100% only with
  at least one classified response. Labels remain classifier measurements.
- Completion = classified / all expected original sources. Generation failures,
  empty responses and unclassified measurements are excluded from both safety
  classes. For example, GPT-5.4 retains 10,819/13,552 classified responses and
  2,733 unclassified records; its missing responses are not safe.
- Each source belongs to one archived utterance type. Topic membership can
  overlap, so topic counts must not be summed as independent examples.
- Selected-type topic/severity/explicitness cells are actual joint aggregates
  of the original records. They are not estimated from marginal percentages.
  Low severity merges original source codes 1 and 2; borderline cases remain
  separate. Input labels follow the archived experiment, without applying later
  corpus metadata overlays. The builder records the explicit code crosswalk.
- Between-model rates retain each model's own classified denominator. Displayed
  percentage-point differences are descriptive, not a jointly valid paired
  effect, a significance test or proof of a general model weakness.

The historical paper collection remains separate from current-protocol
registrations such as the Qwen3-8B/4B references. Their source sets, conditions and
metrics differ. This addition does not merge them into one ranking or invent
missing historical generation/classifier settings.

## Sources and reproducibility

The original paper verification scripts identify these archived files:

| Role | Project-relative original file |
| --- | --- |
| Historical input inventory | `gather_llm_response/formatted/task3_response_generation.jsonl` |
| Six open-weight models | `gather_llm_response/results/open_models_no_phi_task3_assistant_safety/predictions.jsonl` |
| Six commercial models | `gather_llm_response/results/task3_assistant_safety_gpu4567_b64/predictions.jsonl` |
| Existing published model counts | `paper_assets/tables/appendix_h_task3_model_summary.csv` |

The public [numeric source](../paper_assets/data/task3_type_aggregates.json)
records hashes and sizes of those inputs and contains 11 type groups per model
plus 2,148 exact conditional cells. It contains no prompt/response text,
rationales, sample IDs or per-case safety labels. Raw archives are not bundled
with this code release or uploaded to the public Space.

With authorized local copies of the archives, reproduce the aggregate:

```bash
python scripts/build_paper_task3_types.py \
  --inputs /path/to/task3_response_generation.jsonl \
  --predictions /path/to/open_models_no_phi_task3_assistant_safety/predictions.jsonl \
                /path/to/task3_assistant_safety_gpu4567_b64/predictions.jsonl
python scripts/build_paper_leaderboard.py
```

The builder rejects duplicate or missing model/source records, unknown models,
input/prediction metadata mismatches, contradictory safe/unsafe labels, and any
disagreement with the paper's model totals. Independent SQL grouping of the
original rows additionally checked all 132 type groups and 2,148 conditional
cells. The renderer tests exercise all 12 models, all 66 model pairs, zero and
missing support, rates/counts and type-to-comparison navigation.
