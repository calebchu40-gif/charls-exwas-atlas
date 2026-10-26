#!/usr/bin/env python3
"""Reject respondent-level/tabular data and archives from the public Pages bundle.

This is a file-type release guard only. It does not certify disclosure safety of
JSON/HTML contents; association JSON must still pass the dedicated payload and
disclosure-review validators.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = ROOT / "site-prototype" / "dist"
BLOCKED_SUFFIXES = {
    ".accdb",
    ".csv",
    ".dbf",
    ".dta",
    ".feather",
    ".mdb",
    ".parquet",
    ".por",
    ".rda",
    ".rdata",
    ".rar",
    ".rds",
    ".sav",
    ".sas7bdat",
    ".sqlite",
    ".sqlite3",
    ".tsv",
    ".xls",
    ".xlsx",
    ".xpt",
    ".zip",
    ".7z",
}


def main() -> int:
    site_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SITE_DIR
    site_dir = site_dir.resolve()
    if not site_dir.is_dir():
        print(f"Public site directory does not exist: {site_dir}", file=sys.stderr)
        return 2

    blocked_count = 0
    symlink_count = 0
    file_count = 0
    blocked_suffixes: set[str] = set()
    for path in site_dir.rglob("*"):
        if path.is_symlink():
            symlink_count += 1
            continue
        if not path.is_file():
            continue
        file_count += 1
        suffix = path.suffix.lower()
        if suffix in BLOCKED_SUFFIXES:
            blocked_count += 1
            blocked_suffixes.add(suffix)

    if blocked_count or symlink_count:
        details = []
        if blocked_count:
            details.append(
                f"{blocked_count} blocked tabular/data/archive file(s) "
                f"with suffix(es): {', '.join(sorted(blocked_suffixes))}"
            )
        if symlink_count:
            details.append(f"{symlink_count} symbolic link(s)")
        print("Public site file-boundary check failed: " + "; ".join(details), file=sys.stderr)
        return 1

    print(f"Public site file-boundary check passed ({file_count} static files).")
    print("This check does not replace content-level disclosure review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
