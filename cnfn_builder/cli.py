from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .exporters import PUBLIC_FIELDS, public_manifest_rows
from .io_utils import ensure_csv, read_csv, write_csv
from .platform_api import search_x, search_youtube
from .piyao_seed import PIYAO_JRPY_SOURCE, build_seed_rows, fetch_piyao_items
from .schema import CLAIM_FIELDS, DEFAULT_DIRS, QUEUE_FIELDS, SAMPLE_FIELDS
from .stats import counter_by, print_counter
from .validators import validate_claim, validate_queue, validate_sample


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cnfn-builder")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create local workspace directories and CSV templates.")

    validate_parser = subparsers.add_parser("validate", help="Validate claim and sample CSV files.")
    validate_parser.add_argument("--claims", default="data/claim_bank.csv")
    validate_parser.add_argument("--samples", default="data/sample_manifest.csv")
    validate_parser.add_argument("--queue", default="data/collection_queue.csv")
    validate_parser.add_argument("--check-assets", action="store_true")

    stats_parser = subparsers.add_parser("stats", help="Print dataset label/topic/platform counts.")
    stats_parser.add_argument("--claims", default="data/claim_bank.csv")
    stats_parser.add_argument("--samples", default="data/sample_manifest.csv")
    stats_parser.add_argument("--queue", default="data/collection_queue.csv")

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

    args = parser.parse_args(argv)
    if args.command == "init":
        return _init()
    if args.command == "validate":
        return _validate(args.claims, args.samples, args.queue, args.check_assets)
    if args.command == "stats":
        return _stats(args.claims, args.samples, args.queue)
    if args.command == "export-public":
        return _export_public(args.samples, args.out)
    if args.command == "search-youtube":
        return _search_youtube(args.query, args.out, args.max_results, args.api_key_env)
    if args.command == "search-x":
        return _search_x(args.query, args.out, args.max_results, args.bearer_env)
    if args.command == "seed-piyao":
        return _seed_piyao(args.source_url, args.limit, args.claims_out, args.queue_out)
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
        ]
        if ensure_csv(path, fields)
    ]
    for path in created:
        print(f"created {path}")
    if not created:
        print("workspace already initialized")
    return 0


def _validate(claims_path: str, samples_path: str, queue_path: str, check_assets: bool) -> int:
    errors: list[str] = []
    for index, row in enumerate(read_csv(claims_path), start=2):
        errors.extend(validate_claim(row, index))
    for index, row in enumerate(read_csv(samples_path), start=2):
        errors.extend(validate_sample(row, index, check_assets))
    for index, row in enumerate(read_csv(queue_path), start=2):
        errors.extend(validate_queue(row, index))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("validation passed")
    return 0


def _stats(claims_path: str, samples_path: str, queue_path: str) -> int:
    claims = read_csv(claims_path)
    rows = read_csv(samples_path)
    queue = read_csv(queue_path)
    print(f"claims: {len(claims)}")
    print_counter("claim labels", counter_by(claims, "label"))
    print_counter("claim topics", counter_by(claims, "topic_category"))
    print(f"queue: {len(queue)}")
    print_counter("queue status", counter_by(queue, "status"))
    print_counter("queue topics", counter_by(queue, "topic_category"))
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


if __name__ == "__main__":
    raise SystemExit(main())
