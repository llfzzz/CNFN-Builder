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
4. Store candidate URLs in a review queue before accepting samples.
5. Store local text and visual assets for thesis experiments.
6. Pair false/misleading claims with same-topic true/verified samples from
   authoritative sources where possible.
7. Export only public-safe manifests for reproducibility.

## Experimental Input

The model consumes:

- text: post text, title, description, hashtags, or OCR text
- image: attached image, video thumbnail, or screenshot
- label: `false_misleading` or `true_verified`

`cnfn-builder export-clip` writes JSONL rows with:

```text
sample_id, text, image_path, label, label_id, topic_category, split, post_url, label_source_url
```

This is the input boundary for the CLIP feature-extraction and fusion
experiments. Model training code should read this export instead of reading the
raw annotation CSVs directly.

## Data Availability Wording

Use conservative wording:

> The public repository contains the dataset construction code, schemas,
> public source URLs, label-source URLs, and public-safe manifests. Local
> screenshots and platform media assets used for feature extraction are retained
> for thesis review and are not redistributed in bulk because platform content
> is governed by third-party terms.

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
