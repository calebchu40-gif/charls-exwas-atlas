#!/usr/bin/env python3
"""Create a hash-bound internal QA packet for the private Wave 1 rerun.

This record is for internal consistency and normalization only. It is not an
external methods review and does not approve public release.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path

from project_paths import PRIVATE_ROOT, require_private_path

PRIVATE = PRIVATE_ROOT.resolve()
RAW = PRIVATE / "results" / "wave1_county_stage_20261101" / "wave1_household_environment_scaleup_results_private.csv"
PAIR_QA = PRIVATE / "results" / "wave1_county_stage_20261101" / "wave1_household_environment_scaleup_pair_qa_private.csv"
RUN = PRIVATE / "results" / "wave1_county_stage_20261101" / "wave1_household_environment_scaleup_manifest_private.json"
CONFIG = PRIVATE / "analysis_review" / "wave1_household_environment_scaleup_model_config.json"
SCOPE = PRIVATE / "analysis_review" / "wave1_county_stage_scope_manifest_private.json"
REVIEW = PRIVATE / "analysis_review" / "wave1_county_stage_pair_review_private.json"
INTERNAL_REVIEW_ID = "w1-county-stage-internal-qa-20261101-v1"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE) or not resolved.is_file():
        raise ValueError("Wave 1 QA input is absent or outside protected storage")
    return resolved


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def aid(plan_id: str, model: str, hypothesis: str, commit: str) -> str:
    material = "|".join((plan_id, model, hypothesis, commit)).encode("utf-8")
    return "charls-w1-" + hashlib.sha256(material).hexdigest()[:32]


def main() -> None:
    raw_path, qa_path, run_path, config_path = map(private, (RAW, PAIR_QA, RUN, CONFIG))
    raw, qa = read_csv(raw_path), read_csv(qa_path)
    run, config = json.loads(run_path.read_text(encoding="utf-8")), json.loads(config_path.read_text(encoding="utf-8"))
    if run.get("execution_batch") != "full240" or len(raw) != 240 or len({x.get("hypothesis_id") for x in raw}) != 240:
        raise ValueError("Wave 1 run is not the complete unique registered K=240 family")
    if config.get("design", {}).get("psu_field") != "psu_county" or config.get("design", {}).get("weight_field") != "bloodweight":
        raise ValueError("Wave 1 run does not bind the county-stage design and official blood weight")
    if config.get("status") != "user_authorized_internal_analysis" or run.get("public_release_status") != "not_approved":
        raise ValueError("Wave 1 run is not the authorized private-only run")
    commit = str(run.get("code_commit", ""))
    if not commit or config.get("model", {}).get("primary_model_id") != run.get("primary_model_id"):
        raise ValueError("Wave 1 model/run binding is incomplete")
    qa_keys = [(x.get("family_id"), x.get("exposure_concept_id"), x.get("exposure_field_candidate"), x.get("phenotype_concept_id")) for x in qa]
    if len(qa_keys) != len(set(qa_keys)) or not qa:
        raise ValueError("Wave 1 pair QA group keys are blank or duplicated")
    qa_by_key = {tuple(x.get(k, "") for k in ("family_id", "exposure_concept_id", "exposure_field_candidate", "phenotype_concept_id")): x for x in qa}
    decisions = []
    expected_ids = []
    allowed = {"success", "nonconvergence", "inestimable", "blocked_measurement_rule"}
    for row in raw:
        status = row.get("fit_status", "")
        if status == "blocked_by_unresolved_measurement_rule":
            status = "blocked_measurement_rule"
        elif status in {"not_estimable", "insufficient_support", "numerically_unavailable"}:
            status = "inestimable"
        if status not in allowed:
            raise ValueError(f"Unsupported Wave 1 status in private result: {status}")
        key = tuple(row.get(k, "") for k in ("family_id", "exposure_concept_id", "exposure_variable_candidate", "phenotype_concept_id"))
        pair = qa_by_key.get(key)
        if not pair:
            raise ValueError("Wave 1 hypothesis has no matching pair-QA group")
        if row.get("fit_status") == "success":
            nums = [float(row[k]) for k in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value", "n_complete_private", "n_psu_private")]
            if not all(math.isfinite(v) for v in nums) or nums[1] <= 0 or nums[5] < 1 or nums[6] < 2 or nums[2] > nums[3]:
                raise ValueError("Wave 1 successful row has invalid estimate or support metadata")
            if pair.get("status") != "fit_complete" or int(float(pair.get("n_complete", "0"))) != int(nums[5]):
                raise ValueError("Wave 1 pair support does not reconcile with the successful fit")
            est_status, review_id = "reviewed_pass", INTERNAL_REVIEW_ID
        else:
            est_status, review_id = "unresolved", ""
        decisions.append({"hypothesis_id": row["hypothesis_id"], "fit_status": status,
                          "estimability_review_status": est_status, "estimability_review_id": review_id,
                          "fit_message": ""})
        expected_ids.append(aid(config["plan_id"], config["model"]["primary_model_id"], row["hypothesis_id"], commit))
    if len(set(expected_ids)) != 240:
        raise ValueError("Wave 1 generated analysis IDs are not unique")
    scope = {"analysis_plan_id": config["plan_id"], "atlas_family_id": "charls_wave1_county_stage_primary",
             "primary_model_id": config["model"]["primary_model_id"], "expected_primary_analysis_ids": expected_ids}
    for path, obj in ((SCOPE, scope),):
        if path.exists():
            raise FileExistsError("Refusing to overwrite an existing hash-bound scope file")
        path.parent.mkdir(parents=True, exist_ok=True); os.chmod(path.parent, 0o700)
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); os.chmod(path, 0o600)
    review = {"status": "approved_for_private_normalization", "reviewer_reference": "codex-internal-qa-wave1-county",
              "reviewed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "run_manifest_sha256": sha(run_path),
              "runner_results_sha256": sha(raw_path), "pair_qa_sha256": sha(qa_path),
              "configuration_sha256": sha(config_path), "scope_manifest_sha256": sha(SCOPE), "decisions": decisions}
    if REVIEW.exists():
        raise FileExistsError("Refusing to overwrite an existing pair-review record")
    REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); os.chmod(REVIEW, 0o600)
    print("PASS: Wave 1 county-stage K=240 internal QA and normalization records are hash-bound; no public release approved")


if __name__ == "__main__":
    main()
