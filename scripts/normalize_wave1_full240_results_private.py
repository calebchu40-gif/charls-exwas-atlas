#!/usr/bin/env python3
"""Normalize a reviewed CHARLS Wave 1 full240 run into private schema-v3 rows.

This adapter intentionally rejects pilot105 tranches. It reads only the
runner's private result/QA CSVs and metadata manifests; it never reads CHARLS
respondent files, fits a model, or writes to the public site. All paths must
resolve inside PRIVATE_ROOT. The required review record binds the exact input
hashes and supplies one estimability decision for every registered hypothesis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from adjust_exwas_pvalues import adjust_pvalues
from project_paths import PRIVATE_ROOT
from validate_exwas_result_table import read_schema, validate_csv


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "audit" / "wave1_household_environment_hypothesis_register_v0.csv"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,63}$")
SCOPE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,63}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
FINAL_STATUSES = {"success", "nonconvergence", "inestimable", "blocked_measurement_rule"}
REVIEW_DECISION_FIELDS = {
    "hypothesis_id", "fit_status", "estimability_review_status",
    "estimability_review_id", "fit_message",
}
REVIEW_FIELDS = {
    "status", "reviewer_reference", "reviewed_at", "run_manifest_sha256",
    "runner_results_sha256", "pair_qa_sha256", "configuration_sha256",
    "scope_manifest_sha256", "decisions",
}
SCOPE_FIELDS = {
    "analysis_plan_id", "atlas_family_id", "primary_model_id",
    "expected_primary_analysis_ids",
}


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _private_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not _inside(resolved, PRIVATE_ROOT):
        raise ValueError(f"{label} must stay under the protected private root")
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} does not exist: {resolved.name}")
    return resolved


def _private_output(path: Path) -> Path:
    resolved = path.resolve()
    if not _inside(resolved, PRIVATE_ROOT):
        raise ValueError("output must stay under the protected private root")
    if resolved.exists():
        raise FileExistsError("refusing to overwrite an existing canonical result table")
    return resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _read_csv(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        if not fields or len(fields) != len(set(fields)):
            raise ValueError(f"{label} must have a unique, nonempty header")
        return fields, [dict(row) for row in reader]


def _iso_datetime(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be timezone-aware ISO-8601")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be timezone-aware ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return parsed.isoformat()


def _finite(raw: object, label: str) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"successful row lacks numeric {label}") from exc
    if not math.isfinite(value):
        raise ValueError(f"successful row has non-finite {label}")
    return value


def _analysis_id(plan_id: str, model_id: str, hypothesis_id: str, commit: str) -> str:
    material = "|".join((plan_id, model_id, hypothesis_id, commit)).encode("utf-8")
    return "charls-w1-" + hashlib.sha256(material).hexdigest()[:32]


def normalize(
    raw_results_path: Path,
    pair_qa_path: Path,
    run_manifest_path: Path,
    intake_manifest_path: Path,
    config_path: Path,
    scope_manifest_path: Path,
    review_path: Path,
    output_path: Path,
) -> dict[str, object]:
    raw_results_path = _private_file(raw_results_path, "runner results")
    pair_qa_path = _private_file(pair_qa_path, "pair QA")
    run_manifest_path = _private_file(run_manifest_path, "run manifest")
    intake_manifest_path = _private_file(intake_manifest_path, "official intake manifest")
    config_path = _private_file(config_path, "frozen full240 configuration")
    scope_manifest_path = _private_file(scope_manifest_path, "frozen scope manifest")
    review_path = _private_file(review_path, "pair-level review")
    output_path = _private_output(output_path)

    run = _read_json(run_manifest_path, "run manifest")
    intake = _read_json(intake_manifest_path, "official intake manifest")
    config = _read_json(config_path, "frozen configuration")
    scope = _read_json(scope_manifest_path, "scope manifest")
    review = _read_json(review_path, "pair-level review")
    if run.get("execution_batch") != "full240":
        raise ValueError("only the complete full240 execution can be normalized")
    if run.get("participant_data_release") is not False or run.get("public_release_status") != "not_approved":
        raise ValueError("run manifest must confirm private-only, unapproved output")
    configuration_status = config.get("status")
    if configuration_status not in {"frozen", "user_authorized_internal_analysis"}:
        raise ValueError("full240 model configuration is neither frozen nor user-authorized for this run")
    if run.get("analysis_id") != config.get("plan_id") or scope.get("analysis_plan_id") != config.get("plan_id"):
        raise ValueError("run, configuration, and scope manifest plan IDs differ")
    model_id = config.get("model", {}).get("primary_model_id")
    if not isinstance(model_id, str) or run.get("primary_model_id") != model_id or scope.get("primary_model_id") != model_id:
        raise ValueError("primary model IDs do not match across run, config, and scope")
    commit = str(run.get("code_commit", ""))
    if not COMMIT_RE.fullmatch(commit):
        raise ValueError("run manifest has no valid code commit")
    if not HASH_RE.fullmatch(str(run.get("model_configuration_sha256", ""))) or _sha256(config_path) != run["model_configuration_sha256"]:
        raise ValueError("frozen configuration hash does not match the run manifest")
    if not HASH_RE.fullmatch(str(run.get("prepared_frame_sha256", ""))):
        raise ValueError("run manifest lacks a prepared-frame hash")
    if not isinstance(run.get("source_manifest_id"), str) or not ID_RE.fullmatch(run["source_manifest_id"]):
        raise ValueError("run manifest lacks an opaque official-source manifest ID")
    prepared_hash = str(run.get("prepared_frame_sha256", "")).lower()
    if not HASH_RE.fullmatch(prepared_hash):
        raise ValueError("run manifest lacks a valid prepared-frame hash")
    if config.get("source_manifest_id") != run["source_manifest_id"]:
        raise ValueError("frozen configuration is not bound to the run's official-source manifest")
    if (intake.get("source_manifest_id") != run["source_manifest_id"]
            or intake.get("source_identity_review", {}).get("status") != "verified_official_source"):
        raise ValueError("official intake manifest is not verified or does not match the run")
    source_roles = {
        item.get("role"): item for item in intake.get("required_files", [])
        if isinstance(item, dict)
    }
    for role in ("wave1_all_data", "psu", "weight", "blood"):
        entry = source_roles.get(role)
        if (not isinstance(entry, dict)
                or entry.get("identity_review_status") != "verified_official_source"
                or not HASH_RE.fullmatch(str(entry.get("reviewed_local_sha256", "")).lower())):
            raise ValueError(f"official intake manifest lacks a reviewed local hash for {role}")
    if (not HASH_RE.fullmatch(str(config.get("analysis_plan_sha256", "")))
            or config.get("analysis_plan_sha256") != run.get("analysis_plan_sha256")):
        raise ValueError("run manifest and frozen configuration do not share the same plan fingerprint")

    if set(scope) != SCOPE_FIELDS:
        raise ValueError("scope manifest must have exactly the finalizer's four fields")
    family_id = scope.get("atlas_family_id")
    if not isinstance(family_id, str) or not SCOPE_ID_RE.fullmatch(family_id):
        raise ValueError("scope manifest has an invalid atlas_family_id")
    expected_ids = scope.get("expected_primary_analysis_ids")
    if (not isinstance(expected_ids, list) or len(expected_ids) != 240
            or any(not isinstance(item, str) or not SCOPE_ID_RE.fullmatch(item) for item in expected_ids)
            or len(expected_ids) != len(set(expected_ids))):
        raise ValueError("frozen scope must contain exactly 240 unique primary analysis IDs")

    if set(review) != REVIEW_FIELDS or review.get("status") != "approved_for_private_normalization":
        raise ValueError("pair-level review is missing or not approved for private normalization")
    _iso_datetime(review.get("reviewed_at"), "reviewed_at")
    if not isinstance(review.get("reviewer_reference"), str) or not ID_RE.fullmatch(review["reviewer_reference"]):
        raise ValueError("reviewer_reference must be an opaque identifier")
    hash_bindings = {
        "run_manifest_sha256": run_manifest_path,
        "runner_results_sha256": raw_results_path,
        "pair_qa_sha256": pair_qa_path,
        "configuration_sha256": config_path,
        "scope_manifest_sha256": scope_manifest_path,
    }
    for field, path in hash_bindings.items():
        if review.get(field) != _sha256(path):
            raise ValueError(f"pair-level review does not bind the exact {field.removesuffix('_sha256')}")

    raw_fields, raw_rows = _read_csv(raw_results_path, "runner results")
    qa_fields, qa_rows = _read_csv(pair_qa_path, "pair QA")
    required_raw = {
        "hypothesis_id", "family_id", "wave", "exposure_concept_id",
        "exposure_variable_candidate", "contrast_id", "exposure_label",
        "reference_label", "phenotype_concept_id", "phenotype_variable_candidate",
        "phenotype_unit", "outcome_transform", "model_id", "fit_status",
        "estimate", "standard_error", "ci_lower", "ci_upper", "p_value",
        "n_complete_private", "release_status",
    }
    if not required_raw.issubset(raw_fields):
        raise ValueError("runner results are missing required private contract columns")
    if any(row.get("release_status") != "not_approved" for row in raw_rows):
        raise ValueError("runner results must remain explicitly unapproved for public release")
    raw_by_id: dict[str, dict[str, str]] = {}
    for row in raw_rows:
        hypothesis_id = row.get("hypothesis_id", "")
        if not hypothesis_id or hypothesis_id in raw_by_id:
            raise ValueError("runner results contain blank or duplicate hypothesis IDs")
        raw_by_id[hypothesis_id] = row

    _, register_rows = _read_csv(REGISTER, "public hypothesis register")
    expected_register = [row for row in register_rows if row.get("family_id") in {
        "wave1_household_environment_K150", "wave1_heating_route_K90"
    }]
    if len(expected_register) != 240:
        raise ValueError("public register does not contain exactly the frozen K150+K90 scope")
    register_by_id = {row["hypothesis_id"]: row for row in expected_register}
    if len(register_by_id) != 240 or set(raw_by_id) != set(register_by_id):
        raise ValueError("full240 runner IDs do not exactly match the public 240-hypothesis register")
    qa_key_fields = {"family_id", "exposure_concept_id", "exposure_field_candidate", "phenotype_concept_id"}
    if not qa_key_fields.issubset(qa_fields):
        raise ValueError("pair QA is missing the registered family/exposure/phenotype keys")
    expected_qa_keys = {
        (row["family_id"], row["exposure_concept_id"], row["exposure_field_candidate"], row["phenotype_concept_id"])
        for row in expected_register
    }
    actual_qa_keys: set[tuple[str, str, str, str]] = set()
    for row in qa_rows:
        key = tuple(row.get(field, "") for field in (
            "family_id", "exposure_concept_id", "exposure_field_candidate", "phenotype_concept_id"
        ))
        if any(not value for value in key) or key in actual_qa_keys:
            raise ValueError("pair QA contains blank or duplicate group keys")
        actual_qa_keys.add(key)
    if actual_qa_keys != expected_qa_keys:
        raise ValueError("pair QA groups do not exactly cover the full240 registry")
    qa_by_key = {
        tuple(row[field] for field in (
            "family_id", "exposure_concept_id", "exposure_field_candidate", "phenotype_concept_id"
        )): row
        for row in qa_rows
    }

    decisions = review.get("decisions")
    if not isinstance(decisions, list) or len(decisions) != 240:
        raise ValueError("pair-level review must contain exactly 240 decisions")
    decision_by_id: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict) or set(decision) != REVIEW_DECISION_FIELDS:
            raise ValueError("each pair decision must have the exact allowlisted fields")
        hypothesis_id = decision.get("hypothesis_id")
        if not isinstance(hypothesis_id, str) or hypothesis_id in decision_by_id:
            raise ValueError("pair review contains blank or duplicate hypothesis IDs")
        if decision.get("fit_status") not in FINAL_STATUSES:
            raise ValueError("pair review contains a non-finalizable fit status")
        status = decision.get("estimability_review_status")
        if status not in {"reviewed_pass", "blocked_support", "blocked_separation", "blocked_design", "unresolved"}:
            raise ValueError("pair review contains an unsupported estimability status")
        review_id = decision.get("estimability_review_id", "")
        if decision["fit_status"] == "success":
            if status != "reviewed_pass" or not isinstance(review_id, str) or not ID_RE.fullmatch(review_id):
                raise ValueError("success requires reviewed_pass and an opaque estimability review ID")
        elif status == "reviewed_pass" or review_id:
            raise ValueError("non-success decisions cannot claim reviewed_pass")
        if decision["fit_status"] == "blocked_measurement_rule":
            if status != "unresolved" or review_id:
                raise ValueError("blocked_measurement_rule requires unresolved status and no pair-review ID")
        decision_by_id[hypothesis_id] = decision
    if set(decision_by_id) != set(register_by_id):
        raise ValueError("pair-level review IDs do not exactly match all 240 registered hypotheses")

    analysis_ids = {
        hypothesis_id: _analysis_id(config["plan_id"], model_id, hypothesis_id, commit)
        for hypothesis_id in register_by_id
    }
    if set(analysis_ids.values()) != set(expected_ids):
        raise ValueError("generated analysis IDs do not match the frozen scope manifest")

    manifest_fields, _ = read_schema()
    family_value = f"{family_id};K=240"
    target = str(config.get("target", {}).get("population_description", "")).strip()
    if not target:
        raise ValueError("frozen configuration lacks an explicit target population")
    design = config.get("design", {})
    if (design.get("weight_field") != "bloodweight" or design.get("psu_field") != "communityID"
            or design.get("stratum_fields") != [] or design.get("with_replacement") is not True):
        raise ValueError("frozen configuration does not match the reviewed Wave 1 approximate design")
    variance = (
        "Approximate method: unstratified with-replacement Taylor linearization, "
        f"clustered by {design['psu_field']}. Limitation: released CHARLS implicit strata, "
        "PPS size measures, and the final split-community PSU map are not reproduced."
    )
    software = f"Python {run.get('python', 'unknown')}; svy {run.get('svy_version', 'unknown')}; commit:{commit}"
    weight_source = "CHARLS Wave 1 official Blood release document 201 (2014-04-29) and Weight document 118; bloodweight"
    rows: list[dict[str, str]] = []
    raw_p_values: list[float | None] = []
    for hypothesis_id in expected_ids:
        reg = register_by_id[hypothesis_id]
        raw = raw_by_id[hypothesis_id]
        decision = decision_by_id[hypothesis_id]
        if raw.get("model_id") != model_id or raw.get("wave") != "2011":
            raise ValueError("raw result model or wave does not match frozen configuration")
        raw_registry_bindings = {
            "family_id": "family_id",
            "exposure_concept_id": "exposure_concept_id",
            "exposure_variable_candidate": "exposure_field_candidate",
            "contrast_id": "contrast_id",
            "exposure_label": "exposure_label_candidate",
            "reference_label": "reference_label_candidate",
            "phenotype_concept_id": "phenotype_concept_id",
            "phenotype_variable_candidate": "phenotype_field_candidate",
            "phenotype_unit": "phenotype_unit_candidate",
        }
        if any(raw.get(raw_field) != reg.get(register_field)
               for raw_field, register_field in raw_registry_bindings.items()):
            raise ValueError(f"raw result metadata does not match the frozen register for {hypothesis_id}")
        final_status = decision["fit_status"]
        if final_status == "blocked_measurement_rule" and raw.get("fit_status") != "blocked_by_unresolved_measurement_rule":
            raise ValueError("measurement-rule block must match the runner's unresolved measurement status")
        if final_status == "success" and raw.get("fit_status") != "success":
            raise ValueError("pair review cannot promote a runner failure to successful fit")
        if final_status == "success":
            qa_key = (
                reg["family_id"], reg["exposure_concept_id"],
                reg["exposure_field_candidate"], reg["phenotype_concept_id"],
            )
            pair_qa = qa_by_key[qa_key]
            if pair_qa.get("status") != "fit_complete":
                raise ValueError("pair review cannot mark a result successful when pair QA did not complete")
            n_complete_qa = _finite(pair_qa.get("n_complete"), "pair QA n_complete")
            if n_complete_qa < 1 or not n_complete_qa.is_integer():
                raise ValueError("successful result requires a positive integer pair-complete QA count")
        row = {field: "" for field in manifest_fields}
        row.update({
            "analysis_id": analysis_ids[hypothesis_id],
            "data_release": "CHARLS 2011 Wave 1 baseline; Blood release 2014-04-29",
            "source_identity_status": "verified_official_source",
            "source_hash_status": "private_local_sha256_recorded",
            "source_manifest_id": str(run["source_manifest_id"]),
            "wave": "2011",
            "target_population": target,
            "exposure_concept_id": str(reg["exposure_concept_id"]),
            "exposure_variable": str(raw["exposure_variable_candidate"]),
            "phenotype_concept_id": str(reg["phenotype_concept_id"]),
            "phenotype_variable": str(raw["phenotype_variable_candidate"]),
            "eligibility_rule": str(config["frame"].get("analysis_sample_rule", "")) + "; " + str(config["target"].get("age_domain_method", "")),
            "model_id": model_id,
            "estimate_type": "Survey-weighted Gaussian association; registered contrast; weighted-SD outcome scale; approximate Taylor SE and 95% CI",
            "multiple_testing_family": family_value,
            "weight_status": "verified_used",
            "weight_id": "bloodweight",
            "weight_source": weight_source,
            "psu_status": "verified_used",
            "psu_id": str(design["psu_field"]),
            "stratum_status": "not_released",
            "variance_design": variance,
            "exposure_transform": f"Raw registered contrast: {raw['exposure_label']} vs {raw['reference_label']}; field {raw['exposure_variable_candidate']}",
            "phenotype_transform": f"{raw['outcome_transform']}; original unit {raw['phenotype_unit']}; standardized outcome scale",
            "missingness_rule": str(config["model"].get("missing_data_rule", "")),
            "comparability_grade": "within_wave_only",
            "estimability_review_status": str(decision["estimability_review_status"]),
            "estimability_review_id": str(decision.get("estimability_review_id", "")),
            "fit_status": final_status,
            "fit_message": str(decision.get("fit_message", "")),
            "software_versions": software,
        })
        p_value: float | None = None
        if final_status == "success":
            for field in ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value"):
                row[field] = format(_finite(raw.get(field), field), ".17g")
            if float(row["standard_error"]) <= 0 or float(row["ci_lower"]) > float(row["ci_upper"]):
                raise ValueError("successful raw estimate has invalid SE or CI")
            p_value = float(row["p_value"])
            n_model = _finite(raw.get("n_complete_private"), "n_complete_private")
            if n_model < 1 or not n_model.is_integer():
                raise ValueError("successful result requires a positive integer private model N")
            if n_model > n_complete_qa:
                raise ValueError("successful model N exceeds its pair-complete QA count")
            row["n_model"] = str(int(n_model))
        raw_p_values.append(p_value)
        rows.append(row)

    adjusted = adjust_pvalues(raw_p_values)
    for row, q_value, bonf in zip(rows, adjusted["q_value_by"], adjusted["p_bonferroni"], strict=True):
        if row["fit_status"] == "success":
            if q_value is None or bonf is None:
                raise ValueError("full-family adjustment unexpectedly omitted a successful hypothesis")
            row["q_value_by"] = format(q_value, ".17g")
            row["p_bonferroni"] = format(bonf, ".17g")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    errors = validate_csv_from_rows(rows, manifest_fields)
    if errors:
        raise ValueError("normalized schema-v3 table failed validation: " + "; ".join(errors[:8]))
    descriptor, temporary_name = tempfile.mkstemp(prefix=".full240-normalize-", suffix=".csv", dir=output_path.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with temporary.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=manifest_fields)
            writer.writeheader()
            writer.writerows(rows)
        os.chmod(temporary, 0o600)
        temporary.replace(output_path)
        os.chmod(output_path, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {
        "status": "private_full240_normalization_complete",
        "rows": len(rows),
        "successful_rows": sum(row["fit_status"] == "success" for row in rows),
        "non_success_rows": sum(row["fit_status"] != "success" for row in rows),
        "family": family_value,
        "configuration_status": configuration_status,
        "output_mode": "0600",
        "public_release": False,
    }


def validate_csv_from_rows(rows: list[dict[str, str]], fields: list[str]) -> list[str]:
    """Validate in memory through a private temporary table, then remove it."""
    PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".full240-schema-check-", suffix=".csv", dir=PRIVATE_ROOT)
    os.chmod(name, 0o600)
    temporary = Path(name)
    try:
        stream = os.fdopen(descriptor, "w", newline="", encoding="utf-8-sig")
        with stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    try:
        return validate_csv(temporary)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize a reviewed full240 CHARLS result run inside private storage.")
    parser.add_argument("--raw-results", type=Path, required=True)
    parser.add_argument("--pair-qa", type=Path, required=True)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--intake-manifest", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--scope-manifest", type=Path, required=True)
    parser.add_argument("--pair-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(normalize(
        args.raw_results, args.pair_qa, args.run_manifest, args.intake_manifest, args.config,
        args.scope_manifest, args.pair_review, args.output,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
