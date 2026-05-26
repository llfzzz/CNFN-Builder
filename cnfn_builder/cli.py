from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from .exporters import PUBLIC_FIELDS, public_manifest_rows
from .io_utils import ensure_csv, read_csv, write_csv
from .platform_api import search_x, search_youtube
from .schema import CLAIM_FIELDS, DEFAULT_DIRS, SAMPLE_FIELDS
from .stats import counter_by, print_counter
from .validators import validate_claim, validate_sample


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cnfn-builder")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create local workspace directories and CSV templates.")

    validate_parser = subparsers.add_parser("validate", help="Validate claim and sample CSV files.")
    validate_parser.add_argument("--claims", default="data/claim_bank.csv")
    validate_parser.add_argument("--samples", default="data/sample_manifest.csv")
    validate_parser.add_argument("--check-assets", action="store_true")

    stats_parser = subparsers.add_parser("stats", help="Print dataset label/topic/platform counts.")
    stats_parser.add_argument("--samples", default="data/sample_manifest.csv")

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

    args = parser.parse_args(argv)
    if args.command == "init":
        return _init()
    if args.command == "validate":
        return _validate(args.claims, args.samples, args.check_assets)
    if args.command == "stats":
        return _stats(args.samples)
    if args.command == "export-public":
        return _export_public(args.samples, args.out)
    if args.command == "search-youtube":
        return _search_youtube(args.query, args.out, args.max_results, args.api_key_env)
    if args.command == "search-x":
        return _search_x(args.query, args.out, args.max_results, args.bearer_env)
    return 2


def _init() -> int:
    for directory in DEFAULT_DIRS:
        Path(directory).mkdir(parents=True, exist_ok=True)
    created = [
        path
        for path, fields in [
            ("data/claim_bank.csv", CLAIM_FIELDS),
            ("data/sample_manifest.csv", SAMPLE_FIELDS),
        ]
        if ensure_csv(path, fields)
    ]
    for path in created:
        print(f"created {path}")
    if not created:
        print("workspace already initialized")
    return 0


def _validate(claims_path: str, samples_path: str, check_assets: bool) -> int:
    errors: list[str] = []
    for index, row in enumerate(read_csv(claims_path), start=2):
        errors.extend(validate_claim(row, index))
    for index, row in enumerate(read_csv(samples_path), start=2):
        errors.extend(validate_sample(row, index, check_assets))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("validation passed")
    return 0


def _stats(samples_path: str) -> int:
    rows = read_csv(samples_path)
    print(f"samples: {len(rows)}")
    print_counter("labels", counter_by(rows, "label"))
    print_counter("topics", counter_by(rows, "topic_category"))
    print_counter("platforms", counter_by(rows, "platform"))
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


if __name__ == "__main__":
    raise SystemExit(main())
