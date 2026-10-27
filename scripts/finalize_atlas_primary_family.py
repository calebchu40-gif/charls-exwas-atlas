#!/usr/bin/env python3
"""Recompute final multiplicity over a frozen atlas-wide primary family.

This utility reads schema-level result CSVs only. It never reads respondent
data, fits models, or writes to the public site. All inputs and outputs must
remain under the protected local CHARLS workspace.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from adjust_exwas_pvalues import adjust_pvalues
from validate_exwas_result_table import read_schema, validate_csv


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CHARLS_ExWAS_Atlas"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,63}$")
MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
FINALIZABLE_STATUSES = {"success", "nonconvergence", "inestimable"}
MANIFEST_FIELDS = {
    "analysis_plan_id",
    "atlas_family_id",
    "primary_model_id",
    "expected_primary_analysis_ids",
}
SCOPE_REVIEW_FIELDS = {
    "review_record_id",
    "decision",
    "reviewer_reference",
    "reviewed_at",
    "manifest_sha256",
}


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(path: Path) -> dict[str, object]:
    if not inside(path, PRIVATE):
        raise ValueError("the frozen family manifest must be under the protected local CHARLS workspace")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != MANIFEST_FIELDS:
        raise ValueError("manifest must contain exactly: " + ", ".join(sorted(MANIFEST_FIELDS)))
    for key in ("analysis_plan_id", "atlas_family_id"):
        if not isinstance(raw[key], str) or not ID_RE.fullmatch(raw[key]):
            raise ValueError(f"manifest {key} must be an opaque, nonblank identifier")
    if not isinstance(raw["primary_model_id"], str) or not MODEL_ID_RE.fullmatch(raw["primary_model_id"]):
        raise ValueError("manifest primary_model_id must be a nonblank model identifier")
    expected = raw["expected_primary_analysis_ids"]
    if (not isinstance(expected, list) or not expected
            or any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in expected)
            or len(expected) != len(set(expected))):
        raise ValueError("expected_primary_analysis_ids must be a nonempty list of unique opaque IDs")
    return raw


def read_scope_review(path: Path, manifest_path: Path) -> dict[str, str]:
    if not inside(path, PRIVATE):
        raise ValueError("the scope-review record must be under the protected local CHARLS workspace")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != SCOPE_REVIEW_FIELDS:
        raise ValueError("scope-review record must contain exactly: " + ", ".join(sorted(SCOPE_REVIEW_FIELDS)))
    if raw["decision"] != "approved_frozen_primary_scope":
        raise ValueError("scope review must approve the frozen primary hypothesis scope")
    for key in ("review_record_id", "reviewer_reference"):
        if not isinstance(raw[key], str) or not ID_RE.fullmatch(raw[key]):
            raise ValueError(f"scope-review {key} must be an opaque nonblank identifier")
    try:
        reviewed_at = datetime.fromisoformat(str(raw["reviewed_at"]).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError("scope-review reviewed_at must be ISO-8601") from exc
    if reviewed_at.tzinfo is None:
        raise ValueError("scope-review reviewed_at must include a timezone")
    if not isinstance(raw["manifest_sha256"], str) or raw["manifest_sha256"].lower() != sha256(manifest_path):
        raise ValueError("scope-review record must bind to the exact frozen manifest SHA-256")
    return {key: str(value) for key, value in raw.items()}


def finalize(manifest_path: Path, scope_review_path: Path, batch_paths: list[Path], output_path: Path) -> dict[str, object]:
    if not batch_paths:
        raise ValueError("supply every validated batch CSV in the frozen atlas scope")
    if not inside(output_path, PRIVATE):
        raise ValueError("final output must stay under the protected local CHARLS workspace")
    if output_path.exists():
        raise FileExistsError("refusing to overwrite a prior finalization; choose a new versioned output name")
    for path in batch_paths:
        if not inside(path, PRIVATE):
            raise ValueError("every batch CSV must stay under the protected local CHARLS workspace")
        errors = validate_csv(path)
        if errors:
            raise ValueError(f"batch failed result-schema validation ({path.name}): " + "; ".join(errors[:5]))

    manifest = read_manifest(manifest_path)
    scope_review = read_scope_review(scope_review_path, manifest_path)
    schema_fields, _ = read_schema()
    selected: dict[str, dict[str, str]] = {}
    source_hashes: list[dict[str, str]] = []
    for path in batch_paths:
        source_hashes.append({"sha256": sha256(path)})
        with path.open(newline="", encoding="utf-8-sig") as stream:
            for row in csv.DictReader(stream):
                if row.get("model_id", "").strip() != manifest["primary_model_id"]:
                    continue
                analysis_id = row.get("analysis_id", "").strip()
                if analysis_id in selected:
                    raise ValueError(f"duplicate primary analysis_id across batches: {analysis_id}")
                selected[analysis_id] = {field: row.get(field, "").strip() for field in schema_fields}

    expected_ids = manifest["expected_primary_analysis_ids"]
    observed_ids = set(selected)
    expected_set = set(expected_ids)
    missing = sorted(expected_set - observed_ids)
    extra = sorted(observed_ids - expected_set)
    if missing or extra:
        raise ValueError(
            f"primary family does not match frozen manifest (missing={len(missing)}, extra={len(extra)})"
        )

    ordered_rows = [selected[analysis_id] for analysis_id in expected_ids]
    bad_statuses = sorted({row["fit_status"] for row in ordered_rows} - FINALIZABLE_STATUSES)
    if bad_statuses:
        raise ValueError("family contains unresolved or failed hypotheses; resolve before finalization: " + ", ".join(bad_statuses))
    family_value = f"{manifest['atlas_family_id']};K={len(ordered_rows)}"
    for row in ordered_rows:
        row["multiple_testing_family"] = family_value
    adjusted = adjust_pvalues([
        float(row["p_value"]) if row["fit_status"] == "success" and row["p_value"] else None
        for row in ordered_rows
    ])
    for row, q_value, bonferroni in zip(
        ordered_rows, adjusted["q_value_by"], adjusted["p_bonferroni"], strict=True
    ):
        row["q_value_by"] = "" if q_value is None else format(q_value, ".17g")
        row["p_bonferroni"] = "" if bonferroni is None else format(bonferroni, ".17g")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path_resolved = output_path.resolve()
    manifest_digest = sha256(manifest_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    record_path = output_path.with_suffix(output_path.suffix + ".finalization.json")
    if record_path.exists():
        raise FileExistsError("refusing to overwrite an existing finalization record")
    temp_csv: Path | None = None
    temp_record: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", newline="", encoding="utf-8", delete=False,
            dir=output_path.parent, prefix=f".{output_path.name}.", suffix=".tmp",
        ) as stream:
            writer = csv.DictWriter(stream, fieldnames=schema_fields, extrasaction="raise")
            writer.writeheader()
            writer.writerows(ordered_rows)
            stream.flush()
            os.fsync(stream.fileno())
            temp_csv = Path(stream.name)
        errors = validate_csv(temp_csv)
        if errors:
            raise ValueError("final family failed result-schema validation: " + "; ".join(errors[:5]))
        record = {
            "record_version": 1,
            "analysis_plan_id": manifest["analysis_plan_id"],
            "atlas_family_id": manifest["atlas_family_id"],
            "primary_model_id": manifest["primary_model_id"],
            "family_size": len(ordered_rows),
            "expected_id_list_sha256": hashlib.sha256(
                "\n".join(expected_ids).encode("utf-8")
            ).hexdigest(),
            "manifest_sha256": manifest_digest,
            "scope_review_record_id": scope_review["review_record_id"],
            "scope_review_sha256": sha256(scope_review_path),
            "input_result_sha256": source_hashes,
            "output_result_sha256": sha256(temp_csv),
            "adjustment": "Benjamini-Yekutieli and Bonferroni over all frozen primary hypotheses; non-estimable rows count toward K",
            "created_at": timestamp,
            "output_file_name": output_path_resolved.name,
        }
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", delete=False,
            dir=output_path.parent, prefix=f".{record_path.name}.", suffix=".tmp",
        ) as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            temp_record = Path(stream.name)
        os.replace(temp_csv, output_path)
        temp_csv = None
        os.replace(temp_record, record_path)
        temp_record = None
    finally:
        if temp_csv is not None:
            temp_csv.unlink(missing_ok=True)
        if temp_record is not None:
            temp_record.unlink(missing_ok=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="Frozen primary-family manifest under protected storage")
    parser.add_argument("--scope-review", required=True, type=Path, help="Independent scope-review record bound to the exact manifest hash")
    parser.add_argument("--batches", required=True, nargs="+", type=Path, help="All validated batch result CSVs under protected storage")
    parser.add_argument("--output", required=True, type=Path, help="New private final-family CSV path; existing files are never overwritten")
    args = parser.parse_args()
    try:
        record = finalize(args.manifest, args.scope_review, args.batches, args.output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"FAIL: {exc}\n")
    print(
        f"PASS: finalized {record['family_size']} frozen primary hypotheses; "
        "result and audit record remain in protected local storage"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
