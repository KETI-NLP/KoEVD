# KoEVD Classifier Research Use Terms v1.0

Effective Date: [2026-05-26]

These terms govern access to and use of the KoEVD classifier artifacts released under `public_release/classifiers`.

## 1. Scope

The classifier package contains adapter-only measurement artifacts for:

- Task 3 assistant-response safety classification;
- Task 4 response-strategy classification.

The package may include LoRA adapter weights, tokenizer files used with the adapters, inference wrappers, local REST wrappers, classifier cards, sanitized validation metrics, manifests, and documentation.

Base model weights are not redistributed in this package. Users must obtain the required base models from their original providers and comply with the corresponding third-party licenses and terms.

## 2. Intended Uses

The classifier artifacts are intended for:

- reproducing KoEVD Task 3 and Task 4 measurement;
- auditing generated assistant responses for research evaluation;
- validating or comparing measurement pipelines;
- academic, nonprofit, or industry research on LLM safety evaluation.

The classifiers are reproducible measurement proxies. They are not human ground truth, deployment-ready moderation systems, or general-purpose safety filters.

## 3. Prohibited Uses

Users must not use the classifier artifacts to:

1. train, fine-tune, optimize, prompt, operationalize, or deploy systems for harmful, illegal, privacy-invasive, cyber-abusive, discriminatory, self-harm-facilitating, or physically harmful behavior;
2. build or certify a production safety filter, legal/medical/financial advice system, automated moderation authority, compliance system, or safety-critical deployment without independent validation and safeguards;
3. identify or attempt to identify any real person, annotator, worker, source, organization, account, address, or workflow identity;
4. remove content warnings, attribution, or prohibited-use restrictions when redistributing permitted copies or derivatives;
5. represent classifier outputs as proof that a model or system is safe for deployment;
6. use classifier outputs to select, optimize, or improve harmful generations or unsafe tool/action behavior.

## 4. Redistribution

Redistribution is allowed only if these terms or terms no less restrictive are preserved. Redistributed copies must include attribution, content warnings, base-model dependency notes, and prohibited-use restrictions.

## 5. No Warranty

The classifier artifacts are provided "as is" for research measurement. The authors do not warrant that classifier predictions are error-free, complete, unbiased, suitable for deployment, or sufficient for any safety-critical decision.

## 6. Relationship to Dataset Terms

The KoEVD dataset is governed by the dataset terms distributed under `dataset/koevd_v1/`. When classifier use involves KoEVD records, both the dataset terms and these classifier terms apply.

