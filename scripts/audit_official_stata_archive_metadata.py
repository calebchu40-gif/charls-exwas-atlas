#!/usr/bin/env python3
"""Inspect official Stata archive headers without reading respondent values.

Input ZIP files and the JSON report must remain under the protected local
CHARLS workspace. DTA members are staged temporarily in its private staging
directory and read with pyreadstat's metadata-only mode; temporary extracts
are removed before the command exits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

import pyreadstat


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_archive(archive: Path, private_root: Path) -> dict[str, object]:
    if not is_within(archive, private_root):
        raise ValueError(f"archive must be under protected workspace: {archive.name}")
    if archive.suffix.lower() != ".zip":
        raise ValueError(f"only ZIP archives are supported: {archive.name}")
    members_out: list[dict[str, object]] = []
    with zipfile.ZipFile(archive) as zf:
        members = [info for info in zf.infolist() if not info.is_dir()]
        dta_members = [info for info in members if info.filename.lower().endswith(".dta")]
        if not dta_members:
            raise ValueError(f"archive contains no Stata member: {archive.name}")
        staging = private_root / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="header_only_", dir=staging) as temp_dir:
            temp_root = Path(temp_dir)
            for index, info in enumerate(dta_members):
                staged = temp_root / f"member_{index:03d}.dta"
                with zf.open(info) as source, staged.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
                empty_frame, meta = pyreadstat.read_dta(
                    str(staged), metadataonly=True, apply_value_formats=False
                )
                if len(empty_frame.index) != 0:
                    raise RuntimeError("metadata-only reader unexpectedly returned observations")
                members_out.append({
                    "archive_member": info.filename,
                    "row_count_from_header": meta.number_rows,
                    "column_count": meta.number_columns,
                    "variable_names": list(meta.column_names),
                    "variable_labels": list(meta.column_labels),
                    "value_label_sets": getattr(meta, "variable_value_labels", {}) or {},
                    "metadata_only": True,
                    "respondent_values_read": False,
                })
    return {
        "archive_filename": archive.name,
        "archive_size_bytes": archive.stat().st_size,
        "archive_sha256": sha256(archive),
        "zip_members": [info.filename for info in members],
        "stata_members": members_out,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, default=Path(os.environ.get(
        "LOCALAPPDATA", Path.home()
    )) / "CHARLS_ExWAS_Atlas")
    parser.add_argument("--archive", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    private_root = args.private_root.resolve()
    output = args.output.resolve()
    if not is_within(output, private_root / "qa_outputs"):
        raise ValueError("metadata report must be written under protected qa_outputs")
    records = [inspect_archive(path.resolve(), private_root) for path in args.archive]
    report = {
        "report_type": "official_stata_archive_metadata_only",
        "pyreadstat_version": pyreadstat.__version__,
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for record in records:
        for member in record["stata_members"]:
            print(
                f"{record['archive_filename']} :: {member['archive_member']} "
                f"rows={member['row_count_from_header']} columns={member['column_count']} "
                f"metadata_only=True"
            )
    print(f"private_report={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
