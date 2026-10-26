#!/usr/bin/env python3
"""Reject common respondent-data formats and symlinks from the Git repository.

This is a filename/type guard over Git-indexed paths, not a content scanner.
In particular, CSV files can contain either metadata or respondent records and
must be reviewed under the project's separate publication/disclosure process.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_DATA_ALLOWLIST = ROOT / "audit" / "repository_text_data_path_allowlist_v1.txt"
BLOCKED_SUFFIXES = {
    ".accdb", ".dbf", ".dta", ".feather", ".mdb", ".parquet", ".por",
    ".rda", ".rdata", ".rar", ".rds", ".sas7bdat", ".sav", ".sqlite",
    ".sqlite3", ".xpt", ".zip", ".7z",
}


def main() -> int:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        print("Repository data-boundary check could not inspect the Git index.", file=sys.stderr)
        return 2

    if not TEXT_DATA_ALLOWLIST.is_file():
        print("Repository delimited-text path allowlist is missing.", file=sys.stderr)
        return 2
    approved_text_data = {
        line.strip().replace("\\", "/")
        for line in TEXT_DATA_ALLOWLIST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    blocked_count = 0
    symlink_count = 0
    delimited_paths: set[str] = set()
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = ROOT / Path(raw_path.decode("utf-8", errors="surrogateescape"))
        if path.is_symlink():
            symlink_count += 1
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            blocked_count += 1
        if path.suffix.lower() in {".csv", ".tsv"}:
            delimited_paths.add(raw_path.decode("utf-8", errors="surrogateescape").replace("\\", "/"))

    unreviewed_text_count = len(delimited_paths - approved_text_data)
    stale_allowlist_count = len(approved_text_data - delimited_paths)

    if blocked_count or symlink_count or unreviewed_text_count or stale_allowlist_count:
        print(
            "Repository data-boundary check failed: "
            f"{blocked_count} blocked data/archive file(s), "
            f"{symlink_count} symbolic link(s), "
            f"{unreviewed_text_count} unreviewed CSV/TSV path(s), "
            f"{stale_allowlist_count} stale CSV/TSV allowlist entry(ies).",
            file=sys.stderr,
        )
        return 1

    tracked_count = sum(bool(item) for item in result.stdout.split(b"\0"))
    print(
        f"Repository data-boundary check passed ({tracked_count} tracked paths; "
        f"{len(delimited_paths)} reviewed CSV/TSV paths)."
    )
    print("This check does not inspect file contents; CSV/TSV entries require separate review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
