#!/usr/bin/env python3
"""Build a disclosure-reviewed, allowlisted browser payload from protected results.

This command never reads respondent-level data. It requires the private result
table and a separate row-level disclosure decision file to be under the
protected local CHARLS workspace. A whole multiplicity family is withheld if
any of its hypotheses is withheld; partial families are never exported.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from validate_exwas_result_table import validate_csv
from validate_public_site_payload import validate_association_payload


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CHARLS_ExWAS_Atlas"
DEFAULT_OUTPUT = ROOT / "site-prototype" / "dist" / "association_results_v1.json"
FAMILY_RE = re.compile(r"^([A-Za-z0-9_.-]+);K=([1-9][0-9]*)$")
OPAQUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,63}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
REVIEW_FIELDS = {
    "analysis_id", "decision", "review_record_id", "reviewer_reference",
    "reviewed_at", "reviewed_result_sha256",
}
PUBLIC_ROW_FIELDS = (
    "analysis_id", "data_release", "wave", "exposure_concept_id", "exposure_variable",
    "phenotype_concept_id", "phenotype_variable", "target_population", "model_id",
    "estimate_type", "contrast", "estimate", "standard_error", "ci_lower", "ci_upper",
    "p_value", "q_value_by", "p_bonferroni", "n_model", "fit_status",
    "variance_design", "comparability_grade",
)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _read_reviews(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = REVIEW_FIELDS - set(reader.fieldnames or [])
        if missing:
            raise ValueError("review CSV is missing fields: " + ", ".join(sorted(missing)))
        reviews: dict[str, dict[str, str]] = {}
        for line, raw in enumerate(reader, start=2):
            row = {key: str(raw.get(key, "")).strip() for key in REVIEW_FIELDS}
            analysis_id = row["analysis_id"]
            if not analysis_id or analysis_id in reviews:
                raise ValueError(f"review CSV row {line}: blank or duplicate analysis_id")
            if row["decision"] not in {"approved_public_aggregate", "withheld"}:
                raise ValueError(f"review CSV row {line}: unsupported disclosure decision")
            if not OPAQUE_RE.fullmatch(row["review_record_id"]):
                raise ValueError(f"review CSV row {line}: review_record_id must be opaque")
            if not OPAQUE_RE.fullmatch(row["reviewer_reference"]):
                raise ValueError(f"review CSV row {line}: reviewer_reference must be a non-identifying reference")
            try:
                reviewed_at = datetime.fromisoformat(row["reviewed_at"].replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"review CSV row {line}: reviewed_at must be ISO-8601") from exc
            if reviewed_at.tzinfo is None:
                raise ValueError(f"review CSV row {line}: reviewed_at must include a timezone")
            if not SHA256_RE.fullmatch(row["reviewed_result_sha256"]):
                raise ValueError(f"review CSV row {line}: reviewed_result_sha256 must be 64 hexadecimal characters")
            reviews[analysis_id] = row
    return reviews


def build_payload(rows: list[dict[str, str]], reviews: dict[str, dict[str, str]],
                  result_sha256: str, generated_at: str | None = None) -> dict[str, Any]:
    if not SHA256_RE.fullmatch(result_sha256):
        raise ValueError("result_sha256 must identify the exact validated result CSV")
    row_ids = [row.get("analysis_id", "").strip() for row in rows]
    if not row_ids or any(not item for item in row_ids) or len(set(row_ids)) != len(row_ids):
        raise ValueError("result rows must have unique, nonblank analysis_id values")
    if set(reviews) != set(row_ids):
        raise ValueError("disclosure reviews must cover exactly every result row")
    for analysis_id, review in reviews.items():
        if set(review) != REVIEW_FIELDS or review.get("analysis_id") != analysis_id:
            raise ValueError(f"disclosure review is incomplete or mismatched for {analysis_id}")
        if review.get("decision") not in {"approved_public_aggregate", "withheld"}:
            raise ValueError(f"unsupported disclosure decision for {analysis_id}")
        if not OPAQUE_RE.fullmatch(review.get("review_record_id", "")):
            raise ValueError(f"disclosure review lacks an opaque record ID for {analysis_id}")
        if not OPAQUE_RE.fullmatch(review.get("reviewer_reference", "")):
            raise ValueError(f"disclosure review lacks a non-identifying reviewer reference for {analysis_id}")
        if review.get("reviewed_result_sha256", "").lower() != result_sha256.lower():
            raise ValueError(f"disclosure review does not match the exact result file for {analysis_id}")
        try:
            reviewed_at = datetime.fromisoformat(review.get("reviewed_at", "").replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"disclosure review has invalid reviewed_at for {analysis_id}") from exc
        if reviewed_at.tzinfo is None:
            raise ValueError(f"disclosure review reviewed_at requires a timezone for {analysis_id}")

    families: dict[str, list[dict[str, str]]] = {}
    family_sizes: dict[str, int] = {}
    for row in rows:
        family = row.get("multiple_testing_family", "").strip()
        match = FAMILY_RE.fullmatch(family)
        if not match:
            raise ValueError(f"invalid multiple_testing_family for {row['analysis_id']}")
        family_id, k_text = match.groups()
        declared_size = int(k_text)
        if family_id in family_sizes and family_sizes[family_id] != declared_size:
            raise ValueError(f"family {family_id} has inconsistent declared K values")
        family_sizes[family_id] = declared_size
        families.setdefault(family_id, []).append(row)

    public_families: list[dict[str, Any]] = []
    for family_id in sorted(families):
        members = families[family_id]
        if len(members) != family_sizes[family_id]:
            raise ValueError(f"family {family_id} is incomplete; public release requires all K rows")
        # The review is all-or-nothing at family level, preventing a selected
        # subset from misrepresenting the predeclared multiplicity family.
        if not all(reviews[row["analysis_id"]]["decision"] == "approved_public_aggregate" for row in members):
            continue
        public_rows = []
        for row in members:
            public_row = {key: row.get(key, "") for key in PUBLIC_ROW_FIELDS}
            public_row["disclosure_status"] = "approved_public_aggregate"
            if row.get("fit_status") != "success":
                for field in ("estimate", "standard_error", "ci_lower", "ci_upper",
                              "p_value", "q_value_by", "p_bonferroni", "n_model"):
                    public_row[field] = ""
            public_rows.append(public_row)
        public_families.append({
            "family_id": family_id,
            "family_size": family_sizes[family_id],
            "rows": public_rows,
        })
    if not public_families:
        raise ValueError("no complete multiplicity family has explicit approval; no public payload created")
    return {
        "schema_version": 1,
        "release_status": "disclosure_reviewed",
        "generated_at": generated_at or datetime.now().astimezone().isoformat(),
        "families": public_families,
    }


def write_release(results_path: Path, review_path: Path, output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    if not _inside(results_path, PRIVATE) or not _inside(review_path, PRIVATE):
        raise ValueError("result and disclosure-review files must stay under the protected local CHARLS workspace")
    if not _inside(output_path, ROOT / "site-prototype" / "dist"):
        raise ValueError("public output must stay in site-prototype/dist")
    result_sha256 = hashlib.sha256(results_path.read_bytes()).hexdigest()
    errors = validate_csv(results_path)
    if errors:
        raise ValueError("result table failed validation: " + "; ".join(errors[:8]))
    with results_path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if result_sha256 != hashlib.sha256(results_path.read_bytes()).hexdigest():
        raise ValueError("result CSV changed during validation/export; disclosure review must be repeated")
    payload = build_payload(rows, _read_reviews(review_path), result_sha256)
    payload_errors = validate_association_payload(payload)
    if payload_errors:
        raise ValueError("generated public payload failed site validation: " + "; ".join(payload_errors[:8]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", delete=False,
            dir=output_path.parent, prefix=f".{output_path.name}.", suffix=".tmp",
        ) as temporary:
            temporary.write(serialized)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        # The temp file lives in the same directory so replacement is atomic
        # on the target filesystem; readers never see a partially written JSON.
        os.replace(temporary_path, output_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True, help="protected private schema-v3 result CSV")
    parser.add_argument("--review", type=Path, required=True, help="protected private disclosure decision CSV")
    parser.add_argument("--publish", action="store_true", required=True,
                        help="explicitly write an approved aggregate payload into the public site directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        payload = write_release(args.results, args.review, args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({"release_status": payload["release_status"],
                      "families": len(payload["families"]),
                      "rows": sum(len(f["rows"]) for f in payload["families"]),
                      "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
