#!/usr/bin/env python3
"""Map private Wave 4/5 county-stage scans to the atlas schema after QA."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from engine_to_schema_v3 import build, write_rows
from project_paths import PRIVATE_ROOT, require_private_path
from validate_exwas_result_table import validate_csv

PRIVATE = PRIVATE_ROOT.resolve()
REVIEW = PRIVATE / "analysis_review" / "wave45_environment_disease_v3_county_stage"
RESULTS = PRIVATE / "results"
QA = PRIVATE / "qa_outputs"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE) or not resolved.is_file():
        raise ValueError("Wave 4/5 input is absent or outside protected storage")
    return resolved


def normalize(wave: str, code_commit: str) -> Path:
    source = private(RESULTS / f"wave{wave}_environment_disease_M0_M1_v3_county_stage_private.csv")
    qa_path = private(QA / f"wave{wave}_environment_disease_run_qa_v3_county_stage_private.json")
    freeze_path = private(REVIEW / "wave45_freeze_manifest_v1.json")
    plan_path = private(REVIEW / "wave45_analysis_plan_v1.json")
    register_path = private(REVIEW / "wave45_hypothesis_register_v1.csv")
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    expected_k = int(plan["waves"][wave]["registered_K"])
    if qa.get("wave") != wave or qa.get("registered_K_per_model_private") != expected_k:
        raise ValueError(f"Wave {wave}: QA does not bind the expected complete family")
    if frozen.get("code_commit") != code_commit or qa.get("code_commit") != code_commit:
        raise ValueError(f"Wave {wave}: code commit does not match the frozen execution")
    if frozen.get("plan_sha256") != sha(plan_path) or frozen.get("register_sha256") != sha(register_path):
        raise ValueError(f"Wave {wave}: frozen plan/register hash binding failed")
    with source.open(newline="", encoding="utf-8-sig") as stream:
        import csv
        raw = list(csv.DictReader(stream))
    if len(raw) != expected_k * 2 or len({r.get("analysis_id") for r in raw}) != len(raw):
        raise ValueError(f"Wave {wave}: result table is incomplete or contains duplicate analysis IDs")
    if any(r.get("fit_status") not in {"success", "numerically_unavailable"} for r in raw):
        raise ValueError(f"Wave {wave}: unexpected engine status; retain raw output for repair")
    for row in raw:
        if row.get("fit_status") == "success":
            vals = [float(row[k]) for k in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value")]
            if not all(__import__("math").isfinite(v) for v in vals) or vals[1] <= 0 or vals[2] > vals[3]:
                raise ValueError(f"Wave {wave}: non-finite or invalid successful estimate")
    prepared_hash = frozen["input_bindings_private"][wave]["prepared_table_sha256"]
    source_id = f"charls_wave{wave}_prepared_{prepared_hash[:16]}"
    provenance = {
        "data_release": f"CHARLS {wave} official release",
        "source_identity_status": "verified_official_source",
        "source_hash_status": "private_local_sha256_recorded",
        "source_manifest_id": source_id,
        "target_population": "official cross-sectional respondent/spouse sample with positive INDV_weight_ad2; pairwise complete cases after the model covariates",
        "eligibility_rule": "crosssection=1; finite positive official INDV_weight_ad2; documented householdID county segment verified against communityID; no automatic age cutoff",
        "weight_id": "INDV_weight_ad2", "weight_status": "verified_used",
        "weight_source": f"CHARLS {wave} official Weights release; response-adjusted cross-sectional individual weight",
        "psu_id": "householdID documented county segment, validated against communityID", "psu_status": "verified_used",
        "stratum_id": "", "stratum_status": "not_released",
        "variance_design": "Approximate method: WR Taylor linearization clustered at the documented county stage. Limitation: released implicit-stratum labels and county PPS/FPC are unavailable; community-only results remain sensitivity.",
        "exposure_transform": "Pre-registered wave-specific household-environment contrasts using official questionnaire response codes and routing",
        "phenotype_transform": "Official wave-specific routed cumulative doctor-diagnosed disease history; not incident disease",
        "missingness_rule": "Pairwise complete cases after the registered model covariates; no imputation",
        "comparability_grade": "within_wave_only",
        "estimability_review_status": "reviewed_pass",
        "estimability_review_id": f"w{wave}-county-stage-internal-qa-v1",
        "software_versions": f"Python/pandas/polars/pyreadstat; survey engine; commit: {code_commit}",
    }
    output = RESULTS / f"wave{wave}_environment_disease_M0_M1_v3_county_stage_schema_v3_private.csv"
    output = require_private_path(output)
    if output.exists():
        raise FileExistsError("Refusing to overwrite prior Wave 4/5 normalized output")
    rows = build(raw, provenance)
    output.parent.mkdir(parents=True, exist_ok=True); os.chmod(output.parent, 0o700)
    write_rows(rows, output); os.chmod(output, 0o600)
    errors = validate_csv(output)
    if errors:
        output.unlink(missing_ok=True)
        raise ValueError("Schema-v3 validation failed: " + "; ".join(errors[:8]))
    audit_path = QA / f"wave{wave}_environment_disease_county_stage_normalization_private.json"
    audit_path.write_text(json.dumps({
        "status": "internal_schema_validation_pass", "wave": wave,
        "source_result_sha256": sha(source), "qa_sha256": sha(qa_path),
        "freeze_manifest_sha256": sha(freeze_path), "plan_sha256": sha(plan_path),
        "normalized_result_sha256": sha(output), "row_count_private": len(rows),
        "code_commit": code_commit, "public_release_status": "not_approved",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(audit_path, 0o600)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=("2018", "2020", "both"), default="both")
    parser.add_argument("--code-commit", required=True)
    args = parser.parse_args()
    waves = ("2018", "2020") if args.wave == "both" else (args.wave,)
    for wave in waves:
        out = normalize(wave, args.code_commit)
        print(f"PASS: Wave {wave} county-stage result validated privately as {out.name}")


if __name__ == "__main__":
    main()
