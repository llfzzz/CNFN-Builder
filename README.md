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
data/candidate_posts.csv
data/sample_manifest.csv
```

Seed the first 50 checked claims and platform-search tasks from 今日辟谣:

```bash
cnfn-builder seed-piyao --limit 50
```

Seed same-topic `true_verified` search tasks:

```bash
cnfn-builder seed-true-queue --limit 50
```

Add a manually found candidate:

```bash
cnfn-builder add-candidate \
  --queue-id QUEUE_000001 \
  --claim-id CLAIM_000001 \
  --platform youtube \
  --url "https://www.youtube.com/watch?v=..." \
  --text "title description hashtags"
```

Capture a public-page screenshot, if Playwright is installed:

```bash
python -m pip install ".[capture]"
python -m playwright install chromium
cnfn-builder capture-url --candidate-id CAND_000001
```

Accept a reviewed item into the training manifest:

```bash
cnfn-builder accept-sample \
  --candidate-id CAND_000001 \
  --thumbnail-or-screenshot-path assets_local/screenshots/CAND_000001.png \
  --label-source "中国互联网联合辟谣平台 / 今日辟谣" \
  --label-source-url "https://www.piyao.org.cn/..." \
  --collection-date 2026-05-26
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

Export CLIP-readable experiment input:

```bash
cnfn-builder export-clip
```

Write a thesis audit report:

```bash
cnfn-builder audit --out reports/dataset_audit.md
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
`data/collection_queue.csv` as the search-task layer. Use
`data/candidate_posts.csv` for raw candidate URLs and
`data/sample_manifest.csv` only for accepted, reviewable image-text samples.

Minimum thesis data flow:

```text
claim -> queue -> candidate -> screenshot/asset -> accepted sample -> audit -> CLIP export
```

## Thesis Use

The intended thesis wording is conservative:

> This work constructs a small, auditable image-text dataset for Chinese-topic
> fake/misleading news classification. Samples are collected from public social
> media pages, while labels are grounded in public rumor-refutation,
> fact-checking, or authoritative sources.

See [docs/thesis_usage.md](docs/thesis_usage.md).

The first pilot claim-bank run is summarized in
[docs/pilot_claim_bank_report.md](docs/pilot_claim_bank_report.md).
