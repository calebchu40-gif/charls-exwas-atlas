"""Fail-closed provenance check before any Wave 1 association model is run.

This verifies that the prepared respondent table was built from the same four
human-reviewed official release files currently staged in protected storage.
It does not certify survey-design or estimand validity.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from audit_2011_pilot_intake_metadata import (
    audit_archive,
    audit_stata_header,
    evaluate_source_manifest,
)
from project_paths import PRIVATE_ROOT, require_private_path
from prepare_charls_wave_tables import sha256_file


ROLE_SOURCE_KEYS = {
    "wave1_all_data": "all_data_archive",
    "psu": "psu",
    "weight": "weight",
    "blood": "blood",
}


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Wave 1 analysis gate: {label} is missing")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Wave 1 analysis gate: {label} is unreadable") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Wave 1 analysis gate: {label} must be a JSON object")
    return value


def require_verified_wave1_frame(
    private_root: Path = PRIVATE_ROOT,
    data_path: Path | None = None,
) -> dict[str, str]:
    """Check current source identity, prepared-table provenance, and output hash.

    All source and derived files must be in the configured private CHARLS root.
    The function reads only archive inventories, Stata headers, JSON manifests,
    and file hashes; it does not read respondent-level values.
    """
    root = require_private_path(private_root)
    if not root.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError(f"Wave 1 analysis gate: root is outside protected storage: {root}")
    intake_dir = root / "incoming_2011_official"
    intake_manifest = _load_json(intake_dir / "intake_manifest.json", "intake manifest")
    prepared_dir = root / "derived_wave_tables"
    prepared_manifest = _load_json(prepared_dir / "prepared_data_manifest.json", "prepared-data manifest")

    wave = next((item for item in prepared_manifest.get("waves", [])
                 if isinstance(item, dict) and str(item.get("wave")) == "2011"), None)
    if wave is None:
        raise ValueError("Wave 1 analysis gate: prepared-data manifest has no 2011 entry")
    source_review = wave.get("source_review")
    if not isinstance(source_review, dict):
        raise ValueError("Wave 1 analysis gate: prepared 2011 table predates source-review provenance")
    if source_review.get("source_identity_status") != "verified_official_source":
        raise ValueError("Wave 1 analysis gate: prepared 2011 table has no verified source identity")
    manifest_id = str(intake_manifest.get("source_manifest_id", ""))
    if not manifest_id or source_review.get("source_manifest_id") != manifest_id:
        raise ValueError("Wave 1 analysis gate: prepared table and current intake manifest IDs differ")

    prepared_sources = wave.get("source_inputs")
    if not isinstance(prepared_sources, dict):
        raise ValueError("Wave 1 analysis gate: prepared table source inputs are missing")
    role_results: dict[str, dict[str, Any]] = {}
    for role, source_key in ROLE_SOURCE_KEYS.items():
        stored = prepared_sources.get(source_key)
        if not isinstance(stored, dict):
            raise ValueError(f"Wave 1 analysis gate: prepared table is missing {role} provenance")
        filename = str(stored.get("filename", ""))
        digest = str(stored.get("sha256", "")).lower()
        if not filename or Path(filename).name != filename or len(digest) != 64:
            raise ValueError(f"Wave 1 analysis gate: invalid prepared {role} provenance")
        source_path = require_private_path(intake_dir / filename)
        if not source_path.is_relative_to(intake_dir):
            raise ValueError(f"Wave 1 analysis gate: unsafe staged {role} filename")
        if not source_path.is_file():
            raise ValueError(f"Wave 1 analysis gate: reviewed {role} file is no longer staged")
        if role == "wave1_all_data":
            observed = audit_archive(source_path)
        else:
            observed = audit_stata_header(source_path, role)
        if observed.get("local_sha256") != digest:
            raise ValueError(f"Wave 1 analysis gate: staged {role} bytes differ from prepared source")
        role_results[role] = {
            "status": "metadata_read",
            "file_name": observed.get("file_name"),
            "local_sha256": observed.get("local_sha256"),
        }

    current_review = evaluate_source_manifest(intake_manifest, role_results)
    if current_review.get("source_identity_status") != "verified_official_source":
        errors = "; ".join(current_review.get("source_identity_review_errors", []))
        raise ValueError(f"Wave 1 analysis gate: current source review is not valid: {errors}")
    if current_review.get("source_manifest_id") != source_review.get("source_manifest_id"):
        raise ValueError("Wave 1 analysis gate: current and prepared source-review IDs differ")

    output = wave.get("prepared_output")
    if not isinstance(output, dict):
        raise ValueError("Wave 1 analysis gate: prepared output hash is missing")
    output_filename = str(output.get("filename", ""))
    if not output_filename or Path(output_filename).name != output_filename:
        raise ValueError("Wave 1 analysis gate: unsafe prepared output filename")
    table = require_private_path(data_path or prepared_dir / output_filename)
    if not table.is_relative_to(root):
        raise ValueError("Wave 1 analysis gate: prepared respondent table is outside protected storage")
    if not table.is_file():
        raise ValueError("Wave 1 analysis gate: prepared respondent table is missing")
    if table.name != output.get("filename") or sha256_file(table) != output.get("sha256"):
        raise ValueError("Wave 1 analysis gate: prepared respondent table differs from manifest hash")

    return {
        "source_manifest_id": manifest_id,
        "source_identity_status": current_review["source_identity_status"],
        "prepared_output_sha256": str(output["sha256"]),
        "survey_design_status": "still_requires_independent_review",
    }
