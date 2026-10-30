"""Metadata-only source check for the optional CHARLS Wave 1 medical questionnaire.

The file is a documentation item, not an analysis input. This utility checks
only its filename, size, and platform-published MD5 plus a local SHA-256. It
does not parse, extract, or publish the document. Keep the input and JSON
report in the configured private root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


EXPECTED_NAME = "Medical-questionnaire-2011.doc"
EXPECTED_MD5 = "d1f9351dff8bdadb0d1f692ff58b75c6"
OFFICIAL_RECORD = "https://opendata.pku.edu.cn/file.xhtml?datasetVersionId=97&fileId=138"
DEFAULT_INPUT = PRIVATE_ROOT / "intake_raw" / "official_docs_wave1" / EXPECTED_NAME
DEFAULT_REPORT = QA_OUTPUT_DIR / "wave1_medical_questionnaire_intake_metadata.json"


def _private_input(path: Path) -> Path:
    resolved = require_private_path(path)
    root = PRIVATE_ROOT.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Questionnaire input must remain inside the configured private root")
    if path.is_symlink():
        raise ValueError("Symlink inputs are not accepted for official source verification")
    return resolved


def _hash(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(path: Path) -> dict[str, Any]:
    source = _private_input(path)
    base = {
        "official_record": OFFICIAL_RECORD,
        "expected_filename": EXPECTED_NAME,
        "platform_md5": EXPECTED_MD5,
        "metadata_only": True,
        "document_content_parsed": False,
        "respondent_values_read": False,
    }
    if not source.exists():
        return {**base, "status": "missing"}
    if not source.is_file():
        return {**base, "status": "not_a_regular_file"}
    md5 = _hash(source, "md5")
    return {
        **base,
        "status": "platform_md5_match" if md5 == EXPECTED_MD5 else "platform_md5_mismatch",
        "file_name": source.name,
        "file_bytes": source.stat().st_size,
        "observed_md5": md5,
        "local_sha256": _hash(source, "sha256"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    report_path = require_private_path(args.output)
    if not report_path.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Report must remain inside the configured private root")
    result = audit(args.input)
    if result["status"] == "missing":
        print("Wave 1 Medical questionnaire: missing; no content inspected")
        return
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(report_path, 0o600)
    except OSError:
        pass
    print(f"Wave 1 Medical questionnaire: {result['status']}; metadata report saved privately")
    if result["status"] != "platform_md5_match":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
