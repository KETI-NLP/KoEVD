---
title: KoEVD Explorer · Development
emoji: 📊
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
hf_oauth: true
hf_oauth_expiration_minutes: 60
---

# KoEVD Explorer

Private development Space for KETI-NLP. Analyze your model's KoEVD evaluation
results with charts, response cases and paired comparisons across five tasks.
The app uses the same analysis engine as the local KoEVD report.

**Development status:** saved submissions and analysis sessions can disappear
when this Space restarts or rebuilds. Keep your results JSON locally. This is
not a production leaderboard, durable archive or verified model ranking.

## Use the workspace

1. Evaluate your model on a supported KoEVD input set with the current candidate
   evaluator, then export its portable `koevd-results-v1` results JSON.
2. Open the workspace in a separate tab if the embedded view blocks cookies.
3. Upload your results JSON. The server checks it against independently prepared
   inputs; uploaded scores and gold do not configure the benchmark.
4. Upload a second compatible run to compare identical cases, or analyze one run.
5. Download the HTML report, profile JSON, case JSONL, metrics CSV or Markdown.
6. Sign in with HF to save a private development submission. Uploading or saving
   never automatically publishes your model's responses.

Supported input sets: registered full core (17,670 task records), independently
prepared prefixes of 4 or 96 primary/tool sources. Prefix runs are integration
checks, not representative evaluations or full standard baselines. Other custom
input sets need independent operator configuration and are rejected by default.

Task metrics keep their own denominators. Missing, failed and unclassified
outputs remain visible. There is no aggregate ethics score. Task 4 describes
response strategies; Task 5 measures mock tool choices and never executes tools.
Classifier-safe does not imply universally safe behavior. Unresolved classifier
measurements remain diagnostic and excluded from official ranking.

Actual model references and official ranks are not enabled. Reviewer/admin roles
are initially empty; HF login alone grants no review or publication permission.
This development Space does not call GPU models or send responses to a model API.
HF OAuth only supplies sign-in identity; it does not certify inference or scores.

The server launcher defaults to a confidential HF OAuth app. An operator can
explicitly choose a registered secretless public app with
`KOEVD_OAUTH_CLIENT_TYPE=public` and `OAUTH_CLIENT_ID`; no client secret may be set
in that mode. Both modes use server-side PKCE and the same submission permissions.
This is candidate configuration, not evidence of an actual completed HF login.

## Source and licensing

Code: [KETI-NLP/KoEVD](https://github.com/KETI-NLP/KoEVD).
Dataset: [KETI-NLP/KoEVD](https://huggingface.co/datasets/KETI-NLP/KoEVD).
This private Space contains an unmerged platform candidate; the current public
GitHub release may not include all new export/report/submission features.
`deployment-manifest.json` pins deployed source/input file bytes. The source
revision and runtime build status are distinct from GPU validation.

Software uses LICENSE/NOTICE.md; benchmark inputs and their reformatted indexes
remain subject to [DATA_LICENSE.md](DATA_LICENSE.md), the KoEVD Dataset Research
Use Terms. KoEVD includes harmful and sensitive examples for research and safety
evaluation. Harmful operational use is prohibited; scores do not certify safe
deployment. See LICENSES for the separate classifier-wrapper terms.

Paper: San Kim, Wonjung Kim, Heesoo Kwon and Jae Hee Yang (2026),
*KoEVD: A Korean Benchmark for Metadata-Conditioned Multi-Stage LLM Safety Evaluation*.
