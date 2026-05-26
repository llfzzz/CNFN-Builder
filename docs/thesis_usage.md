# Thesis Usage

## Recommended Description

Use conservative wording:

> This study builds a small, auditable image-text dataset for Chinese-topic
> fake/misleading news classification. Samples are collected from public social
> media pages, while labels are grounded in public rumor-refutation,
> fact-checking, or authoritative sources.

## Dataset Construction Paragraph

The dataset construction process can be described as:

1. Collect verified claims from rumor-refutation or fact-checking sources.
2. Assign each claim to one of four Chinese-topic categories.
3. Search public social media pages for image-text posts or video thumbnails
   that match the claim.
4. Store local text and visual assets for thesis experiments.
5. Export only public-safe manifests for reproducibility.

## Experimental Input

The model consumes:

- text: post text, title, description, hashtags, or OCR text
- image: attached image, video thumbnail, or screenshot
- label: `false_misleading` or `true_verified`

## Claims Not To Make

Do not claim:

- the dataset covers all China-related misinformation
- the model detects hidden or unverifiable misinformation
- the tool enables platform governance
- the public repository redistributes raw platform datasets

Use:

- "small-scale"
- "auditable"
- "publicly source-grounded"
- "for thesis experiments"
