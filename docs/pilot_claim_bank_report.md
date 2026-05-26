# Pilot Claim Bank Report

Generated on 2026-05-26 with:

```bash
python -m cnfn_builder.cli seed-piyao --limit 50
python -m cnfn_builder.cli seed-true-queue --limit 50
python -m cnfn_builder.cli validate
python -m cnfn_builder.cli stats
```

## Source

The first pilot claim bank is seeded from 中国互联网联合辟谣平台 / 今日辟谣.

- Source index: https://www.piyao.org.cn/jrpy/index.htm
- Data endpoint used by the page: http://www.piyao.org.cn/jrpy/ds_e0bb8399925745768458fc917f771895.json

## Current Output

Files:

- `data/claim_bank.csv`: 50 checked `false_misleading` claims.
- `data/collection_queue.csv`: 100 search tasks, including 50 false/misleading
  platform-search tasks and 50 same-topic `true_verified` authority-search tasks.
- `data/candidate_posts.csv`: empty candidate pool.
- `data/sample_manifest.csv`: still empty; no training sample is accepted yet.

Topic distribution:

| Topic | Count |
|---|---:|
| `policy_politics` | 12 |
| `livelihood_economy` | 22 |
| `industry_economy` | 9 |
| `technology_narrative` | 7 |

Claim label distribution:

| Label | Count |
|---|---:|
| `false_misleading` | 50 |
| `true_verified` | 0 |

Queue label distribution:

| Label | Count |
|---|---:|
| `false_misleading` | 50 |
| `true_verified` | 50 |

## Interpretation

This is not the final dataset. It is the verified-claim layer for the first
collection loop. A row becomes a training sample only after a public X,
YouTube, or TikTok page is found and a usable image, thumbnail, or screenshot
is saved locally.

The current source naturally over-represents livelihood and incident rumors.
For a thesis dataset, the next supplementation should target:

- technology narratives from 科普中国科学辟谣 or other science fact-checking pages
- industry/economy claims from financial, market, property, and state-owned
  enterprise rumor-refutation sources
- `true_verified` samples from authoritative official or news sources

The `true_verified` queue rows are search tasks only. They are not accepted
samples and do not create labels without a real authoritative URL, text, and
visual asset.

## Next Action

Work through `data/collection_queue.csv` from `QUEUE_000001` onward:

1. Search X, YouTube, and TikTok manually or through official APIs.
2. Save candidate URL in `candidate_post_url`.
3. Add possible matches to `data/candidate_posts.csv`.
4. Save screenshot, thumbnail, or image under `assets_local/`.
5. Mark reviewed candidates as `accepted`, `rejected`, or `blocked`.
6. Move accepted candidates into `data/sample_manifest.csv`.
