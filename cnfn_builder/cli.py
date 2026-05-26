from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .audit import audit_rows
from .candidates import add_candidate, import_candidate_rows, review_candidate
from .capture import capture_url
from .clip_export import clip_rows, split_rows, write_jsonl
from .exporters import PUBLIC_FIELDS, public_manifest_rows
from .io_utils import ensure_csv, read_csv, write_csv
from .platform_api import search_x, search_youtube
from .piyao_seed import PIYAO_JRPY_SOURCE, build_seed_rows, fetch_piyao_items
from .samples import accept_sample
from .schema import CANDIDATE_FIELDS, CLAIM_FIELDS, DEFAULT_DIRS, QUEUE_FIELDS, SAMPLE_FIELDS
from .stats import counter_by, print_counter
from .true_queue import build_true_queue_rows
from .validators import validate_candidate, validate_claim, validate_queue, validate_sample


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cnfn-builder")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create local workspace directories and CSV templates.")

    validate_parser = subparsers.add_parser("validate", help="Validate claim and sample CSV files.")
    validate_parser.add_argument("--claims", default="data/claim_bank.csv")
    validate_parser.add_argument("--samples", default="data/sample_manifest.csv")
    validate_parser.add_argument("--queue", default="data/collection_queue.csv")
    validate_parser.add_argument("--candidates", default="data/candidate_posts.csv")
    validate_parser.add_argument("--check-assets", action="store_true")

    stats_parser = subparsers.add_parser("stats", help="Print dataset label/topic/platform counts.")
    stats_parser.add_argument("--claims", default="data/claim_bank.csv")
    stats_parser.add_argument("--samples", default="data/sample_manifest.csv")
    stats_parser.add_argument("--queue", default="data/collection_queue.csv")
    stats_parser.add_argument("--candidates", default="data/candidate_posts.csv")

    export_parser = subparsers.add_parser("export-public", help="Export public-safe manifest.")
    export_parser.add_argument("--samples", default="data/sample_manifest.csv")
    export_parser.add_argument("--out", default="data/public_manifest.csv")

    youtube_parser = subparsers.add_parser("search-youtube", help="Search YouTube Data API.")
    youtube_parser.add_argument("--query", required=True)
    youtube_parser.add_argument("--out", default="data/youtube_candidates.csv")
    youtube_parser.add_argument("--max-results", type=int, default=10)
    youtube_parser.add_argument("--api-key-env", default="YOUTUBE_API_KEY")

    x_parser = subparsers.add_parser("search-x", help="Search X recent posts API.")
    x_parser.add_argument("--query", required=True)
    x_parser.add_argument("--out", default="data/x_candidates.csv")
    x_parser.add_argument("--max-results", type=int, default=10)
    x_parser.add_argument("--bearer-env", default="X_BEARER_TOKEN")

    seed_parser = subparsers.add_parser("seed-piyao", help="Seed claim bank and collection queue from 今日辟谣.")
    seed_parser.add_argument("--source-url", default=PIYAO_JRPY_SOURCE)
    seed_parser.add_argument("--limit", type=int, default=50)
    seed_parser.add_argument("--claims-out", default="data/claim_bank.csv")
    seed_parser.add_argument("--queue-out", default="data/collection_queue.csv")

    true_queue_parser = subparsers.add_parser("seed-true-queue", help="Seed true_verified same-topic search tasks.")
    true_queue_parser.add_argument("--claims", default="data/claim_bank.csv")
    true_queue_parser.add_argument("--queue-out", default="data/collection_queue.csv")
    true_queue_parser.add_argument("--limit", type=int, default=50)

    add_candidate_parser = subparsers.add_parser("add-candidate", help="Add one candidate platform item.")
    add_candidate_parser.add_argument("--candidates", default="data/candidate_posts.csv")
    add_candidate_parser.add_argument("--queue-id", default="")
    add_candidate_parser.add_argument("--claim-id", default="")
    add_candidate_parser.add_argument("--platform", required=True)
    add_candidate_parser.add_argument("--url", required=True)
    add_candidate_parser.add_argument("--text", required=True)
    add_candidate_parser.add_argument("--thumbnail-url", default="")
    add_candidate_parser.add_argument("--media-url", default="")
    add_candidate_parser.add_argument("--published-at", default="")
    add_candidate_parser.add_argument("--source-method", default="manual")
    add_candidate_parser.add_argument("--notes", default="")

    import_candidate_parser = subparsers.add_parser("import-candidates", help="Import candidate rows from a CSV file.")
    import_candidate_parser.add_argument("--input", required=True)
    import_candidate_parser.add_argument("--candidates", default="data/candidate_posts.csv")
    import_candidate_parser.add_argument("--queue-id", default="")
    import_candidate_parser.add_argument("--claim-id", default="")
    import_candidate_parser.add_argument("--source-method", default="")

    review_candidate_parser = subparsers.add_parser("review-candidate", help="Update candidate review status.")
    review_candidate_parser.add_argument("--candidates", default="data/candidate_posts.csv")
    review_candidate_parser.add_argument("--candidate-id", required=True)
    review_candidate_parser.add_argument("--status", required=True, choices=["unreviewed", "accepted", "rejected", "blocked"])
    review_candidate_parser.add_argument("--notes", default="")

    accept_parser = subparsers.add_parser("accept-sample", help="Accept a candidate or manual row into sample_manifest.csv.")
    accept_parser.add_argument("--samples", default="data/sample_manifest.csv")
    accept_parser.add_argument("--candidates", default="data/candidate_posts.csv")
    accept_parser.add_argument("--queue", default="data/collection_queue.csv")
    accept_parser.add_argument("--candidate-id", default="")
    accept_parser.add_argument("--platform", default="")
    accept_parser.add_argument("--post-url", default="")
    accept_parser.add_argument("--post-text", default="")
    accept_parser.add_argument("--image-path", default="")
    accept_parser.add_argument("--thumbnail-or-screenshot-path", default="")
    accept_parser.add_argument("--topic-category", default="")
    accept_parser.add_argument("--label", default="")
    accept_parser.add_argument("--label-source", required=True)
    accept_parser.add_argument("--label-source-url", required=True)
    accept_parser.add_argument("--collection-date", required=True)
    accept_parser.add_argument("--notes", default="")

    capture_parser = subparsers.add_parser("capture-url", help="Capture a public URL screenshot with optional Playwright.")
    capture_parser.add_argument("--url", default="")
    capture_parser.add_argument("--out", default="")
    capture_parser.add_argument("--candidate-id", default="")
    capture_parser.add_argument("--candidates", default="data/candidate_posts.csv")
    capture_parser.add_argument("--timeout-ms", type=int, default=15000)

    clip_parser = subparsers.add_parser("export-clip", help="Export CLIP-readable JSONL files.")
    clip_parser.add_argument("--samples", default="data/sample_manifest.csv")
    clip_parser.add_argument("--out", default="data/clip_dataset.jsonl")
    clip_parser.add_argument("--split-dir", default="data/splits")
    clip_parser.add_argument("--seed", type=int, default=42)
    clip_parser.add_argument("--check-assets", action="store_true")

    audit_parser = subparsers.add_parser("audit", help="Write dataset audit report.")
    audit_parser.add_argument("--claims", default="data/claim_bank.csv")
    audit_parser.add_argument("--queue", default="data/collection_queue.csv")
    audit_parser.add_argument("--candidates", default="data/candidate_posts.csv")
    audit_parser.add_argument("--samples", default="data/sample_manifest.csv")
    audit_parser.add_argument("--out", default="reports/dataset_audit.md")

    args = parser.parse_args(argv)
    if args.command == "init":
        return _init()
    if args.command == "validate":
        return _validate(args.claims, args.samples, args.queue, args.candidates, args.check_assets)
    if args.command == "stats":
        return _stats(args.claims, args.samples, args.queue, args.candidates)
    if args.command == "export-public":
        return _export_public(args.samples, args.out)
    if args.command == "search-youtube":
        return _search_youtube(args.query, args.out, args.max_results, args.api_key_env)
    if args.command == "search-x":
        return _search_x(args.query, args.out, args.max_results, args.bearer_env)
    if args.command == "seed-piyao":
        return _seed_piyao(args.source_url, args.limit, args.claims_out, args.queue_out)
    if args.command == "seed-true-queue":
        return _seed_true_queue(args.claims, args.queue_out, args.limit)
    if args.command == "add-candidate":
        return _add_candidate(args)
    if args.command == "import-candidates":
        return _import_candidates(args)
    if args.command == "review-candidate":
        return _review_candidate(args.candidates, args.candidate_id, args.status, args.notes)
    if args.command == "accept-sample":
        return _accept_sample(args)
    if args.command == "capture-url":
        return _capture_url(args)
    if args.command == "export-clip":
        return _export_clip(args.samples, args.out, args.split_dir, args.seed, args.check_assets)
    if args.command == "audit":
        return _audit(args.claims, args.queue, args.candidates, args.samples, args.out)
    return 2


def _init() -> int:
    for directory in DEFAULT_DIRS:
        Path(directory).mkdir(parents=True, exist_ok=True)
    created = [
        path
        for path, fields in [
            ("data/claim_bank.csv", CLAIM_FIELDS),
            ("data/sample_manifest.csv", SAMPLE_FIELDS),
            ("data/collection_queue.csv", QUEUE_FIELDS),
            ("data/candidate_posts.csv", CANDIDATE_FIELDS),
        ]
        if ensure_csv(path, fields)
    ]
    for path in created:
        print(f"created {path}")
    if not created:
        print("workspace already initialized")
    return 0


def _validate(claims_path: str, samples_path: str, queue_path: str, candidates_path: str, check_assets: bool) -> int:
    errors: list[str] = []
    for index, row in enumerate(read_csv(claims_path), start=2):
        errors.extend(validate_claim(row, index))
    samples = read_csv(samples_path)
    for index, row in enumerate(samples, start=2):
        errors.extend(validate_sample(row, index, check_assets))
    for index, row in enumerate(read_csv(queue_path), start=2):
        errors.extend(validate_queue(row, index))
    for index, row in enumerate(read_csv(candidates_path), start=2):
        errors.extend(validate_candidate(row, index))
    errors.extend(_duplicate_sample_url_errors(samples))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("validation passed")
    return 0


def _stats(claims_path: str, samples_path: str, queue_path: str, candidates_path: str) -> int:
    claims = read_csv(claims_path)
    rows = read_csv(samples_path)
    queue = read_csv(queue_path)
    candidates = read_csv(candidates_path)
    print(f"claims: {len(claims)}")
    print_counter("claim labels", counter_by(claims, "label"))
    print_counter("claim topics", counter_by(claims, "topic_category"))
    print(f"queue: {len(queue)}")
    print_counter("queue status", counter_by(queue, "status"))
    print_counter("queue topics", counter_by(queue, "topic_category"))
    print(f"candidates: {len(candidates)}")
    print_counter("candidate status", counter_by(candidates, "match_status"))
    print_counter("candidate platforms", counter_by(candidates, "platform"))
    print(f"samples: {len(rows)}")
    print_counter("sample labels", counter_by(rows, "label"))
    print_counter("sample topics", counter_by(rows, "topic_category"))
    print_counter("sample platforms", counter_by(rows, "platform"))
    return 0


def _export_public(samples_path: str, out_path: str) -> int:
    rows = read_csv(samples_path)
    exported = public_manifest_rows(rows)
    write_csv(out_path, PUBLIC_FIELDS, exported)
    print(f"exported {len(exported)} rows to {out_path}")
    return 0


def _search_youtube(query: str, out_path: str, max_results: int, api_key_env: str) -> int:
    api_key = os.environ.get(api_key_env)
    if not api_key:
        print(f"missing API key env var: {api_key_env}", file=sys.stderr)
        return 1
    rows = search_youtube(api_key, query, max_results)
    fields = ["platform", "content_id", "url", "title", "description", "channel_title", "published_at", "thumbnail_url"]
    write_csv(out_path, fields, rows)
    print(f"wrote {len(rows)} YouTube candidates to {out_path}")
    return 0


def _search_x(query: str, out_path: str, max_results: int, bearer_env: str) -> int:
    bearer_token = os.environ.get(bearer_env)
    if not bearer_token:
        print(f"missing bearer token env var: {bearer_env}", file=sys.stderr)
        return 1
    rows = search_x(bearer_token, query, max_results)
    fields = ["platform", "content_id", "url", "text", "created_at", "author_id", "media_urls"]
    write_csv(out_path, fields, rows)
    print(f"wrote {len(rows)} X candidates to {out_path}")
    return 0


def _seed_piyao(source_url: str, limit: int, claims_out: str, queue_out: str) -> int:
    items = fetch_piyao_items(source_url)
    claims, queue = build_seed_rows(items, limit, source_url)
    write_csv(claims_out, CLAIM_FIELDS, claims)
    write_csv(queue_out, QUEUE_FIELDS, queue)
    print(f"seeded {len(claims)} claims to {claims_out}")
    print(f"seeded {len(queue)} collection tasks to {queue_out}")
    return 0


def _seed_true_queue(claims_path: str, queue_path: str, limit: int) -> int:
    claims = read_csv(claims_path)
    existing = [row for row in read_csv(queue_path) if not row.get("queue_id", "").startswith("TRUE_QUEUE_")]
    rows = build_true_queue_rows(claims, limit)
    write_csv(queue_path, QUEUE_FIELDS, existing + rows)
    print(f"seeded {len(rows)} true_verified search tasks to {queue_path}")
    return 0


def _add_candidate(args: argparse.Namespace) -> int:
    row = add_candidate(
        args.candidates,
        {
            "queue_id": args.queue_id,
            "claim_id": args.claim_id,
            "platform": args.platform,
            "candidate_url": args.url,
            "candidate_text": args.text,
            "thumbnail_url": args.thumbnail_url,
            "media_url": args.media_url,
            "published_at": args.published_at,
            "source_method": args.source_method,
            "notes": args.notes,
        },
    )
    print(f"added candidate {row['candidate_id']} to {args.candidates}")
    return 0


def _import_candidates(args: argparse.Namespace) -> int:
    rows = read_csv(args.input)
    for row in rows:
        if args.queue_id:
            row["queue_id"] = args.queue_id
        if args.claim_id:
            row["claim_id"] = args.claim_id
        if args.source_method:
            row["source_method"] = args.source_method
    created = import_candidate_rows(args.candidates, rows)
    print(f"imported {len(created)} candidates to {args.candidates}")
    return 0


def _review_candidate(candidates_path: str, candidate_id: str, status: str, notes: str) -> int:
    row = review_candidate(candidates_path, candidate_id, status, notes)
    print(f"candidate {row['candidate_id']} status={row['match_status']}")
    return 0


def _accept_sample(args: argparse.Namespace) -> int:
    row = accept_sample(
        samples_path=args.samples,
        candidates_path=args.candidates,
        queue_path=args.queue,
        candidate_id=args.candidate_id,
        platform=args.platform,
        post_url=args.post_url,
        post_text=args.post_text,
        image_path=args.image_path,
        thumbnail_or_screenshot_path=args.thumbnail_or_screenshot_path,
        topic_category=args.topic_category,
        label=args.label,
        label_source=args.label_source,
        label_source_url=args.label_source_url,
        collection_date=args.collection_date,
        notes=args.notes,
    )
    print(f"accepted sample {row['sample_id']} to {args.samples}")
    return 0


def _capture_url(args: argparse.Namespace) -> int:
    url = args.url
    out = args.out
    if args.candidate_id:
        candidates = read_csv(args.candidates)
        candidate = next((row for row in candidates if row.get("candidate_id") == args.candidate_id), None)
        if not candidate:
            print(f"candidate not found: {args.candidate_id}", file=sys.stderr)
            return 1
        url = url or candidate.get("candidate_url", "")
        out = out or f"assets_local/screenshots/{args.candidate_id}.png"
    if not url:
        print("missing --url or --candidate-id with candidate_url", file=sys.stderr)
        return 1
    if not out:
        print("missing --out", file=sys.stderr)
        return 1
    result = capture_url(url, out, args.timeout_ms)
    print(result.message)
    if result.ok:
        print(result.path)
        return 0
    if args.candidate_id:
        review_candidate(args.candidates, args.candidate_id, "blocked", result.message)
    return 1


def _export_clip(samples_path: str, out_path: str, split_dir: str, seed: int, check_assets: bool) -> int:
    rows = clip_rows(read_csv(samples_path), check_assets=check_assets)
    split = split_rows(rows, seed=seed)
    write_jsonl(out_path, split)
    for split_name in ["train", "val", "test"]:
        write_jsonl(Path(split_dir) / f"{split_name}.jsonl", [row for row in split if row.get("split") == split_name])
    print(f"exported {len(split)} CLIP rows to {out_path}")
    return 0


def _audit(claims_path: str, queue_path: str, candidates_path: str, samples_path: str, out_path: str) -> int:
    report = audit_rows(
        claims=read_csv(claims_path),
        queue=read_csv(queue_path),
        candidates=read_csv(candidates_path),
        samples=read_csv(samples_path),
    )
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"wrote audit report to {out_path}")
    return 0


def _duplicate_sample_url_errors(samples: list[dict[str, str]]) -> list[str]:
    seen: dict[str, int] = {}
    errors: list[str] = []
    for index, row in enumerate(samples, start=2):
        url = row.get("post_url", "")
        if not url:
            continue
        if url in seen:
            errors.append(f"row {index}: duplicate post_url also appears on row {seen[url]}")
        else:
            seen[url] = index
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
