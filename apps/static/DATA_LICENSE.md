# KoEVD Dataset Research Use Terms v1.0

Effective Date: [2026-05-26]

These KoEVD Dataset Research Use Terms ("Terms") govern access to and use of the KoEVD dataset ("Dataset"). By downloading, accessing, copying, using, modifying, or redistributing any part of the Dataset, you agree to these Terms.

These Terms apply to the KoEVD benchmark data, including Korean user utterances, assistant response candidates, labels, metadata, task views, official splits, documentation, and any other data files distributed as part of the KoEVD dataset package. These Terms do not apply to separately released source code, which may be distributed under the Apache License 2.0 or another stated software license.

## 1. Definitions

"Dataset" means the KoEVD dataset and associated data files released under these Terms.

"Licensor" means the authors, institution, or organization releasing the Dataset.

"User" means any individual or organization that accesses, uses, copies, modifies, redistributes, or creates derivatives from the Dataset.

"Derivative Dataset" means any modified, transformed, filtered, translated, reformatted, annotated, sampled, or combined version of the Dataset, including task-specific subsets or conversions.

"Model Artifact" means any model, classifier, adapter, checkpoint, embedding index, synthetic data generator, evaluation system, or other machine-learning artifact trained, fine-tuned, evaluated, calibrated, or otherwise developed using the Dataset.

"Prohibited Use" means any use described in Section 5.

## 2. License Grant

Subject to these Terms, the Licensor grants the User a limited, worldwide, royalty-free, non-exclusive, non-transferable license to use, copy, modify, and create derivative works from the Dataset for research, evaluation, education, auditing, benchmarking, and safety-analysis purposes.

The Dataset may be used to evaluate, audit, compare, or improve the safety behavior of language models and related AI systems, provided that such use complies with these Terms.

## 3. Attribution

Users must provide appropriate attribution when using the Dataset or any Derivative Dataset in publications, reports, model cards, dataset cards, repositories, or other public materials.

Attribution must include:

- The dataset name: KoEVD
- The associated paper citation, if available
- A link or reference to the official Dataset repository or release page, if available
- A statement that the Dataset contains harmful, offensive, illegal, privacy-sensitive, discriminatory, or otherwise sensitive content for safety-evaluation purposes

Suggested attribution:

> This work uses KoEVD, a Korean benchmark for metadata-conditioned multi-stage LLM safety evaluation. KoEVD contains harmful and sensitive examples for research and safety-evaluation purposes only.

## 4. Permitted Uses

Subject to the restrictions in Section 5, Users may use the Dataset for:

1. Academic, nonprofit, or industry research on language-model safety, alignment, risk evaluation, refusal behavior, harmfulness detection, response strategy analysis, and tool/action-choice safety.
2. Benchmarking and evaluating language models, classifiers, moderation systems, or AI assistants.
3. Developing or validating safety classifiers, evaluation metrics, auditing pipelines, or red-teaming analysis tools.
4. Creating aggregate statistics, figures, tables, or research analyses.
5. Creating Derivative Datasets for internal research or evaluation, provided that the Derivative Dataset remains subject to these Terms.
6. Sharing limited excerpts in research papers, presentations, or documentation, provided that such excerpts are sanitized or paraphrased when necessary to avoid operationally harmful detail, personal identifiers, or executable tool arguments.

## 5. Prohibited Uses

Users may not use the Dataset, Derivative Datasets, or Model Artifacts derived from the Dataset for any of the following purposes:

1. Harmful, illegal, violent, abusive, exploitative, discriminatory, privacy-invasive, cyber-abusive, or physically dangerous activity.
2. Training, fine-tuning, optimizing, prompting, evaluating, or deploying systems to generate, improve, operationalize, or automate harmful instructions, illegal activity, cyber abuse, privacy invasion, harassment, discrimination, self-harm facilitation, or physical-world harm.
3. Developing or improving tools, agents, workflows, or services that enable real-world execution of harmful actions, including but not limited to cyber attacks, fraud, doxxing, surveillance, stalking, weaponization, illegal procurement, or physical harm.
4. Using rejected or strongly rejected responses as positive training targets for harmful behavior generation.
5. Reconstructing, extracting, identifying, or attempting to identify any real person, private individual, annotator, internal worker, source, organization, account, address, contact information, or workflow identity.
6. Publishing raw harmful examples in a way that provides procedural, actionable, executable, or operationally useful instructions for harm.
7. Deploying the Dataset or any Model Artifact as a general-purpose production safety filter, legal/medical/financial advice system, automated moderation authority, or compliance certification system without additional validation and appropriate safeguards.
8. Misrepresenting Dataset scores as proof that a model or system is safe for deployment.
9. Removing or obscuring content warnings, provenance information, attribution, or use restrictions when redistributing permitted subsets or derivatives.
10. Using the Dataset in violation of applicable laws, regulations, institutional policies, or third-party terms.

## 6. Redistribution

Users may redistribute the Dataset or Derivative Datasets only if all of the following conditions are met:

1. The redistribution preserves these Terms or applies terms no less restrictive than these Terms.
2. The redistribution includes attribution to KoEVD and the associated paper or official release.
3. The redistribution includes clear content warnings and prohibited-use restrictions.
4. The redistribution does not include added personal identifiers, workflow metadata, internal usernames, timestamps, file paths, or other identifying information.
5. The redistribution does not make harmful content more actionable than in the original Dataset.
6. The redistribution does not imply endorsement by the Licensor.

The Licensor may request removal or correction of redistributed copies that violate these Terms.

## 7. Derivative Datasets and Model Artifacts

Derivative Datasets must remain subject to these Terms or terms no less restrictive than these Terms.

Users are responsible for ensuring that Model Artifacts trained, fine-tuned, calibrated, evaluated, or otherwise developed using the Dataset are not used for Prohibited Uses.

If a Model Artifact is released publicly and the Dataset materially contributed to its training, fine-tuning, calibration, evaluation, or safety analysis, the User should disclose the Dataset use in the relevant model card, dataset card, technical report, or documentation, subject to applicable confidentiality and safety considerations.

## 8. Sensitive Content and Safety Handling

The Dataset intentionally contains harmful, offensive, illegal, privacy-sensitive, discriminatory, or otherwise sensitive scenarios for safety-evaluation purposes.

Users must handle the Dataset with appropriate care, including:

1. Limiting access to people with a legitimate research, evaluation, or safety-auditing purpose.
2. Avoiding unnecessary exposure of annotators, students, workers, or users to harmful content.
3. Using sanitized or paraphrased examples in public-facing materials when raw examples would increase misuse risk.
4. Avoiding publication of operationally actionable harmful detail, executable tool arguments, or personal identifiers.
5. Complying with applicable institutional review, data protection, cybersecurity, and research ethics requirements.

## 9. No Personal Data Warranty

The Dataset was constructed from curated safety scenarios rather than personal user submissions or real-world user logs. The Licensor has taken steps to avoid inclusion of real personal identifiers and workflow metadata. However, the Dataset is provided "as is," and Users are responsible for conducting any additional review required for their own use case, jurisdiction, institution, or release context.

Users must report any suspected personal identifier, privacy issue, or sensitive workflow metadata discovered in the Dataset to the Licensor through the official contact channel, if available.

## 10. No Warranty

The Dataset is provided "as is," without warranties or representations of any kind, express or implied, including but not limited to warranties of accuracy, completeness, fitness for a particular purpose, non-infringement, safety, or suitability for deployment.

The Licensor does not warrant that the Dataset is free from errors, bias, offensive content, harmful content, or other sensitive material.

## 11. Limitation of Liability

To the maximum extent permitted by applicable law, the Licensor shall not be liable for any direct, indirect, incidental, consequential, special, exemplary, or punitive damages arising from or related to access to or use of the Dataset, Derivative Datasets, or Model Artifacts.

Users are solely responsible for their use of the Dataset and for compliance with applicable laws, regulations, institutional policies, and third-party terms.

## 12. Termination

If a User violates these Terms, the license granted under these Terms terminates automatically. Upon termination, the User must stop using the Dataset and make reasonable efforts to delete or disable access to copies of the Dataset and Derivative Datasets under their control, except where retention is required by law, institutional policy, or archival obligations.

Sections concerning attribution, prohibited uses, redistribution restrictions, derivative obligations, no warranty, limitation of liability, and termination survive termination.

## 13. Updates

The Licensor may update these Terms for future releases of the Dataset. Continued use of a future release is governed by the Terms distributed with that release.

## 14. Contact

Questions, suspected privacy issues, or misuse reports should be directed to:

[Insert official contact email or repository issue tracker]