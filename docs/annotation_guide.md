# Annotation Guide

## Workflow

1. Start from a fact-checking or authoritative source.
2. Extract one factual claim.
3. Add the claim to `data/claim_bank.csv`.
4. Add platform-search work to `data/collection_queue.csv`.
5. Search public social platforms or authoritative pages for matching
   image-text samples.
6. Add possible matches to `data/candidate_posts.csv`.
7. Keep only samples with text plus an image, thumbnail, or screenshot.
8. Move the row into `data/sample_manifest.csv` only after URL, asset path,
   label source, and collection date are all reviewable.

## Labels

Use `false_misleading` when the label source clearly refutes the claim or
describes it as false, misleading, fabricated, manipulated, or taken out of
context.

Use `true_verified` when the sample is supported by an authoritative source,
official notice, or fact-checking source.

Do not label uncertain claims. Put them in notes outside the training set.

## Topic Categories

- `policy_politics`: policy, institutions, notices, subsidies, public services.
- `livelihood_economy`: jobs, income, prices, welfare, medical insurance, housing.
- `industry_economy`: state-owned enterprises, finance, real estate, manufacturing.
- `technology_narrative`: domestic technology, chips, AI, aerospace, patriotic narratives.

## Exclusion Rules

Exclude samples that:

- have no checkable source URL
- contain only opinion without a factual claim
- lack any image, thumbnail, or screenshot
- expose private personal information
- cannot be reviewed later from the stored URL and label source

## Queue Status

- `todo`: claim is verified, but no platform sample has been accepted.
- `candidate_found`: a possible platform URL has been found and needs review.
- `accepted`: the platform URL and visual asset are good enough for
  `sample_manifest.csv`.
- `rejected`: the candidate does not match the claim or lacks usable visuals.
- `blocked`: the platform source is inaccessible, deleted, or requires access
  that cannot be obtained compliantly.

## Candidate Status

- `unreviewed`: imported or manually added, but not checked.
- `accepted`: checked and usable for `sample_manifest.csv`.
- `rejected`: content does not match the claim or lacks usable text/visuals.
- `blocked`: inaccessible without non-compliant access, login bypass, or captcha.

## True Verified Pairing

Use `seed-true-queue` to create same-topic true-sample search tasks. These rows
are not training data. A `true_verified` sample is valid only after an actual
authoritative URL, text, image/screenshot, and label-source URL are accepted.
