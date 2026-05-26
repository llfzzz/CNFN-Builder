# CNFN-Builder

CNFN-Builder is a lightweight, reproducible toolkit for building a small,
auditable Chinese-topic multimodal fake-news dataset for thesis experiments.

The tool is designed for **local dataset construction** and **public manifest
sharing**. It avoids redistributing raw X, TikTok, or YouTube platform content.
Instead, it stores source URLs, content IDs, labels, topic categories, and
fact-checking sources so that samples can be reviewed or rehydrated under the
user's own platform access.

## Scope

Target task:

```text
Chinese-topic image-text fake/misleading news classification
```

Default labels:

- `false_misleading`
- `true_verified`

Default topic categories:

- `policy_politics`
- `livelihood_economy`
- `industry_economy`
- `technology_narrative`

Supported source modes:

- X public posts through official API access or manual import
- YouTube video metadata and thumbnails through YouTube Data API
- TikTok public page records through manual import unless approved Research API access is available
- Fact-check and rumor-refutation sources for labels

## Install

```bash
python -m pip install -e .
```

No runtime dependency beyond the Python standard library is required.

## Quick Start

Initialize the local workspace:

```bash
cnfn-builder init
```

Fill the templates:

```text
data/claim_bank.csv
data/collection_queue.csv
data/sample_manifest.csv
```

Seed the first 50 checked claims and platform-search tasks from 今日辟谣:

```bash
cnfn-builder seed-piyao --limit 50
```

Validate the dataset:

```bash
cnfn-builder validate
```

Show dataset statistics:

```bash
cnfn-builder stats
```

Export a public-safe manifest:

```bash
cnfn-builder export-public --out data/public_manifest.csv
```

## Optional Platform Search

YouTube search, using your own API key:

```bash
export YOUTUBE_API_KEY="..."
cnfn-builder search-youtube \
  --query "中国 芯片 突破" \
  --out data/youtube_candidates.csv
```

X recent search, using your own bearer token:

```bash
export X_BEARER_TOKEN="..."
cnfn-builder search-x \
  --query '"中国经济" has:images -is:retweet' \
  --out data/x_candidates.csv
```

TikTok is intentionally manual-first in this repository. Do not use this tool
to bypass TikTok access controls or scrape at scale.

## Data Policy

Commit to GitHub:

- code
- templates
- claim IDs
- post/video URLs
- platform content IDs
- labels and label-source URLs
- public-safe manifests
- claim banks and collection queues grounded in public label-source URLs

Do not commit:

- API keys
- raw harvested X/TikTok/YouTube text at scale
- downloaded videos
- user profile data
- private or sensitive personal data
- local screenshots/thumbnails unless you have rights and a clear thesis-use reason

See [docs/platform_compliance.md](docs/platform_compliance.md).

## Pilot Collection Loop

Use `data/claim_bank.csv` as the verified-claim layer and
`data/collection_queue.csv` as the platform-search layer. A row should enter
`data/sample_manifest.csv` only after you find a public X, YouTube, or TikTok
post/video page and save a visual asset path for review.

## Thesis Use

The intended thesis wording is conservative:

> This work constructs a small, auditable image-text dataset for Chinese-topic
> fake/misleading news classification. Samples are collected from public social
> media pages, while labels are grounded in public rumor-refutation,
> fact-checking, or authoritative sources.

See [docs/thesis_usage.md](docs/thesis_usage.md).

The first pilot claim-bank run is summarized in
[docs/pilot_claim_bank_report.md](docs/pilot_claim_bank_report.md).
