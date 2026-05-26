# Annotation Guide

## Workflow

1. Start from a fact-checking or authoritative source.
2. Extract one factual claim.
3. Assign one topic category.
4. Search public social platforms for matching image-text samples.
5. Keep only samples with text plus an image, thumbnail, or screenshot.
6. Validate that the label source supports the assigned label.

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
