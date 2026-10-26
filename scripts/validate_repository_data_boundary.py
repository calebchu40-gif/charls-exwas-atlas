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

    blocked_count = 0
    symlink_count = 0
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = ROOT / Path(raw_path.decode("utf-8", errors="surrogateescape"))
        if path.is_symlink():
            symlink_count += 1
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            blocked_count += 1

    if blocked_count or symlink_count:
        print(
            "Repository data-boundary check failed: "
            f"{blocked_count} blocked data/archive file(s), "
            f"{symlink_count} symbolic link(s).",
            file=sys.stderr,
        )
        return 1

    tracked_count = sum(bool(item) for item in result.stdout.split(b"\0"))
    print(f"Repository data-boundary check passed ({tracked_count} tracked paths).")
    print("This check does not inspect file contents or classify CSV records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
