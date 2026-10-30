#!/usr/bin/env python3
"""Read only the protected Wave 1 Blood Stata header for planned outcomes.

This records variable labels and attached value-label sets without loading any
respondent values. It is a metadata check, not proof of numeric validity rules.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from prepare_charls_wave_tables import sha256_file
from require_verified_wave1_frame import require_verified_wave1_frame


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_BLOOD = PRIVATE_ROOT / "incoming_2011_official" / "Blood_20140429.dta"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_blood_outcome_header_metadata_private.json"
OUTCOME_FIELDS = (
    "qc1_vb002", "qc1_vb004", "qc1_vb005", "qc1_vb006", "qc1_vb009",
    "newtg", "newcrea", "newbun", "newhdl", "newldl", "newcho", "newglu",
    "newua", "newcrp", "newhba1c", "qc1_va003",
)


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Blood metadata input and output must remain inside the private root")
    return resolved


def run(data_path: Path, blood_path: Path, output: Path) -> dict[str, Any]:
    data_path, blood_path, output = map(private, (data_path, blood_path, output))
    if not data_path.is_file() or not blood_path.is_file():
        raise FileNotFoundError("Protected Wave 1 prepared table or official Blood file is missing")
    source = require_verified_wave1_frame(data_path=data_path)
    _, meta = pyreadstat.read_dta(str(blood_path), metadataonly=True)
    names = list(meta.column_names)
    absent = sorted(set(OUTCOME_FIELDS) - set(names))
    if absent:
        raise ValueError(f"Planned outcome metadata fields are absent from the Blood header: {absent}")
    labels = list(meta.column_labels or [""] * len(names))
    column_label_by_name = dict(zip(names, labels, strict=True))
    variable_to_label = dict(meta.variable_to_label or {})
    value_labels = dict(meta.value_labels or {})
    storage_types = dict(getattr(meta, "readstat_variable_types", {}) or {})
    original_formats = dict(getattr(meta, "original_variable_types", {}) or {})
    tagged_missing = dict(getattr(meta, "missing_user_values", {}) or {})
    fields: list[dict[str, Any]] = []
    for field in OUTCOME_FIELDS:
        label_set_name = variable_to_label.get(field)
        label_set = value_labels.get(label_set_name, {}) if label_set_name else {}
        fields.append({
            "field": field,
            "variable_label": column_label_by_name.get(field, ""),
            "storage_type": storage_types.get(field),
            "original_format": original_formats.get(field),
            "value_label_set_name": label_set_name,
            "value_label_entries": len(label_set),
            "value_labels_present": bool(label_set),
            "tagged_missing_values_declared": list(tagged_missing.get(field, []) or []),
        })
    report = {
        "status": "metadata_only_blood_header_review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": source["source_manifest_id"],
        "source_identity_status": source["source_identity_status"],
        "prepared_person_table_sha256": source["prepared_output_sha256"],
        "blood_source_sha256": sha256_file(blood_path),
        "metadata_only": True,
        "respondent_values_read": False,
        "outcome_fields_reviewed": fields,
        "interpretation": "Header variable labels, storage types, original formats, value-label attachments, and declared Stata tagged-missing metadata only; numeric sentinel codes and analytic validity are not inferred from this report.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(output, 0o600)
    return report


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--blood", type=Path, default=DEFAULT_BLOOD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.data, args.blood, args.output)
    print(json.dumps({
        "status": report["status"],
        "planned_fields_reviewed": len(report["outcome_fields_reviewed"]),
        "value_label_fields": sum(item["value_labels_present"] for item in report["outcome_fields_reviewed"]),
        "tagged_missing_metadata_fields": sum(bool(item["tagged_missing_values_declared"]) for item in report["outcome_fields_reviewed"]),
        "respondent_values_read": False,
        "private_output_written": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
