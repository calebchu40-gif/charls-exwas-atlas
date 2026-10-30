"""Fail-closed provenance check before any Wave 1 association model is run.

This verifies that the prepared respondent table was built from the same four
human-reviewed official release files currently staged in protected storage.
It does not certify survey-design or estimand validity.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from audit_2011_pilot_intake_metadata import (
    audit_archive,
    audit_stata_header,
    evaluate_source_manifest,
)
from project_paths import PRIVATE_ROOT, require_private_path
from prepare_charls_wave_tables import sha256_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]


ROLE_SOURCE_KEYS = {
    "wave1_all_data": "all_data_archive",
    "psu": "psu",
    "weight": "weight",
    "blood": "blood",
}
REQUIRED_ANALYSIS_GATES = (
    "official_source_identity",
    "sample_frame_and_denominators",
    "target_population_age_domain",
    "official_age_source_and_derivation",
    "weight_and_nonresponse_eligibility",
    "final_psu_mapping",
    "variance_method_review",
    "frozen_analysis_plan",
)
ANALYSIS_PLANS = {
    "water_biomarker_pilot": {
        "filename": "wave1_water_biomarker_pilot.json",
        "plan_id": "pilot_2011_water_biomarker_plan_and_gates_2026-10-26",
        "plan_files": (
            "audit/pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md",
            "audit/pilot_followup_execution_plan_2026-10-26.md",
            "audit/pilot_success_criteria_and_scale_up_2026-10-26.md",
            "audit/multiplicity_primary_family_reconciliation_2026-10-27.md",
            "audit/pilot_autonomous_execution_decision_2026-10-27.md",
            "audit/templates/wave1_analysis_readiness.template.json",
        ),
        "additional_gates": (),
    },
    "household_environment_extension": {
        "filename": "wave1_household_environment_extension.json",
        "plan_id": "pilot_2011_water_biomarker_plan_and_gates_2026-10-26#household-environment-K105",
        "plan_files": (
            "audit/pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md",
            "audit/pilot_followup_execution_plan_2026-10-26.md",
            "audit/pilot_success_criteria_and_scale_up_2026-10-26.md",
            "audit/multiplicity_primary_family_reconciliation_2026-10-27.md",
            "audit/pilot_autonomous_execution_decision_2026-10-27.md",
            "audit/wave1_household_environment_covariate_dag_review_2026-10-27.md",
            "audit/templates/wave1_analysis_readiness.template.json",
        ),
        "additional_gates": ("pilot_success_and_reproducibility_review",),
    },
    "household_environment_pilot": {
        "filename": "wave1_household_environment_pilot.json",
        "plan_id": "charls_2011_household_environment_pilot_v1_K105",
        "plan_files": (
            "audit/执行计划_授权确认后_2026-10-30.md",
            "audit/wave1_household_environment_pilot_execution_design_2026-10-30.md",
            "audit/wave1_fasting_status_source_reconciliation_2026-10-30.md",
            "audit/wave1_outcome_rule_cards_source_review_2026-10-30.md",
            "audit/wave1_design_cluster_support_diagnostic_2026-10-30.md",
            "audit/wave1_household_environment_hypothesis_register_v0.csv",
            "audit/wave1_variance_review_recommendation_2026-10-30.md",
            "audit/wave1_pilot_pair_eligibility_review_2026-10-30.md",
            "scripts/audit_wave1_design_cluster_support.py",
            "scripts/audit_wave1_pilot_pair_eligibility.py",
            "audit/templates/wave1_household_environment_pilot_readiness.template.json",
            "audit/templates/wave1_household_environment_pilot_model_config.template.json",
            "scripts/derive_wave1_age_intervals.py",
            "scripts/verify_official_lunar_table_parity.py",
            "scripts/audit_2011_pilot_design_frame.py",
            "scripts/audit_wave1_weight_only_module_presence_private.py",
            "scripts/require_verified_wave1_frame.py",
            "scripts/run_2011_household_environment_scaleup.py",
        ),
        "additional_gates": ("frozen_pilot_configuration",),
        "config_filename": "wave1_household_environment_pilot_model_config.json",
        "config_gate": "frozen_pilot_configuration",
    },
    "household_environment_scaleup": {
        "filename": "wave1_household_environment_scaleup_K150_K90.json",
        "plan_id": "charls_2011_household_environment_scaleup_v1_K150_K90",
        "plan_files": (
            "audit/pilot_2011_water_biomarker_plan_and_gates_2026-10-26.md",
            "audit/pilot_followup_execution_plan_2026-10-26.md",
            "audit/pilot_success_criteria_and_scale_up_2026-10-26.md",
            "audit/multiplicity_primary_family_reconciliation_2026-10-27.md",
            "audit/pilot_autonomous_execution_decision_2026-10-27.md",
            "audit/wave1_household_environment_covariate_dag_review_2026-10-27.md",
            "audit/wave1_household_environment_hypothesis_register_v0.csv",
            "audit/wave1_scaleup_runner_gap_2026-10-27.md",
            "audit/templates/wave1_household_environment_scaleup_readiness.template.json",
            "audit/templates/wave1_household_environment_scaleup_model_config.template.json",
            "scripts/audit_wave1_scaleup_metadata_readiness.py",
            "scripts/run_2011_household_environment_scaleup.py",
        ),
        "additional_gates": (
            "pilot_success_and_reproducibility_review",
            "frozen_scaleup_configuration",
        ),
        "config_filename": "wave1_household_environment_scaleup_model_config.json",
        "config_gate": "frozen_scaleup_configuration",
    },
}


def analysis_plan_fingerprint(plan_key: str) -> str:
    """Hash the exact set and bytes of the tracked documents defining a plan."""
    plan = ANALYSIS_PLANS.get(plan_key)
    if plan is None:
        raise ValueError(f"Unknown Wave 1 analysis plan {plan_key!r}")
    entries = []
    for relative in plan["plan_files"]:
        path = PROJECT_ROOT / relative
        if not path.is_file():
            raise ValueError(f"Wave 1 analysis plan source is missing: {relative}")
        entries.append(f"{relative}\0{sha256_file(path)}")
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


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
    age_path: Path | None = None,
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
    # Bind provenance to the same immutable/versioned directory as an
    # explicitly supplied prepared table. This allows a protected rebuild to
    # be audited without replacing the legacy/default Wave 1 table.
    prepared_dir = (
        root / "derived_wave_tables"
        if data_path is None
        else require_private_path(data_path).parent
    )
    if not prepared_dir.is_relative_to(root):
        raise ValueError("Wave 1 analysis gate: prepared manifest is outside protected storage")
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

    provenance = {
        "source_manifest_id": manifest_id,
        "source_identity_status": current_review["source_identity_status"],
        "prepared_output_sha256": str(output["sha256"]),
        "survey_design_status": "still_requires_independent_review",
    }
    if age_path is not None:
        age_table = require_private_path(age_path)
        if not age_table.is_relative_to(root) or not age_table.is_file():
            raise ValueError("Wave 1 analysis gate: official age-interval candidate is outside protected storage or missing")
        age_input_qa_path = require_private_path(root / "qa_outputs" / "wave1_official_age_inputs_qa.json")
        age_interval_qa_path = require_private_path(root / "qa_outputs" / "wave1_age_interval_candidate_qa.json")
        age_input_path = require_private_path(root / "age_inputs_2011" / "wave1_official_age_inputs.dta")
        age_input_qa = _load_json(age_input_qa_path, "official age-input provenance QA")
        age_interval_qa = _load_json(age_interval_qa_path, "age-interval derivation QA")
        age_digest = sha256_file(age_table)
        age_input_digest = sha256_file(age_input_path)
        if age_interval_qa.get("source_manifest_id") != manifest_id:
            raise ValueError("Wave 1 analysis gate: age-interval candidate belongs to a different source manifest")
        if age_interval_qa.get("person_level_output_sha256") != age_digest:
            raise ValueError("Wave 1 analysis gate: age-interval candidate differs from its private derivation QA hash")
        if age_input_qa.get("source_manifest_id") != manifest_id:
            raise ValueError("Wave 1 analysis gate: official age-input QA belongs to a different source manifest")
        if age_input_qa.get("age_input_sha256") != age_input_digest:
            raise ValueError("Wave 1 analysis gate: official age-input file differs from its private QA hash")
        if age_interval_qa.get("age_input_sha256") != age_input_digest:
            raise ValueError("Wave 1 analysis gate: age-interval candidate is not bound to the current official age inputs")
        if age_input_qa.get("person_source_sha256") != str(output["sha256"]):
            raise ValueError("Wave 1 analysis gate: age-input derivation used a different prepared person table")
        if age_input_qa.get("weight_source_sha256") != prepared_sources["weight"].get("sha256"):
            raise ValueError("Wave 1 analysis gate: age-input derivation used a different Weight source")
        provenance["age_candidate_sha256"] = age_digest
    return provenance


def require_wave1_analysis_readiness(
    private_root: Path,
    source_provenance: dict[str, str],
    analysis_plan: str,
) -> dict[str, str]:
    """Require a review record bound to the exact frame before analysis fitting.

    This gate approves only an internal exploratory pilot. Public release is
    always controlled by the separate disclosure-review workflow.
    """
    root = require_private_path(private_root)
    if not root.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 1 readiness gate: root is outside protected storage")
    plan = ANALYSIS_PLANS.get(analysis_plan)
    if plan is None:
        raise ValueError(f"Wave 1 readiness gate: unknown analysis plan {analysis_plan!r}")
    path = root / "analysis_review" / plan["filename"]
    review = _load_json(path, "Wave 1 analysis readiness review")
    if review.get("status") != "approved_for_exploratory_pilot":
        raise ValueError("Wave 1 readiness gate: no approval for internal exploratory pilot")
    if review.get("source_manifest_id") != source_provenance.get("source_manifest_id"):
        raise ValueError("Wave 1 readiness gate: source manifest binding does not match current frame")
    if review.get("prepared_output_sha256") != source_provenance.get("prepared_output_sha256"):
        raise ValueError("Wave 1 readiness gate: prepared-frame hash binding does not match current frame")
    if review.get("analysis_plan_id") != plan["plan_id"]:
        raise ValueError("Wave 1 readiness gate: approval is not bound to the registered analysis plan")
    expected_plan_hash = analysis_plan_fingerprint(analysis_plan)
    if str(review.get("analysis_plan_sha256", "")).lower() != expected_plan_hash:
        raise ValueError("Wave 1 readiness gate: approval is not bound to the exact registered plan documents")
    if review.get("public_release_status") != "not_approved":
        raise ValueError("Wave 1 readiness gate: pilot approval cannot authorize public release")
    if not str(review.get("reviewer", "")).strip() or not str(review.get("reviewed_at", "")).strip():
        raise ValueError("Wave 1 readiness gate: reviewer and review date are required")
    gates = review.get("gates")
    if not isinstance(gates, dict):
        raise ValueError("Wave 1 readiness gate: required gate decisions are missing")
    for gate in (*REQUIRED_ANALYSIS_GATES, *plan["additional_gates"]):
        decision = gates.get(gate)
        if not isinstance(decision, dict) or decision.get("status") != "passed":
            raise ValueError(f"Wave 1 readiness gate: {gate} has not passed")
        if not str(decision.get("evidence", "")).strip():
            raise ValueError(f"Wave 1 readiness gate: {gate} has no evidence citation")
    age_gate = gates["official_age_source_and_derivation"]
    for field in ("field", "derivation_method", "source_anchor", "validation_evidence"):
        if not str(age_gate.get(field, "")).strip():
            raise ValueError(f"Wave 1 readiness gate: official age source/derivation lacks {field}")
    if age_gate.get("source_tier") != "official_charls":
        raise ValueError("Wave 1 readiness gate: age must come from an official CHARLS release or maintained algorithm")
    variance = gates["variance_method_review"]
    if not str(variance.get("method", "")).strip() or not str(variance.get("limitations", "")).strip():
        raise ValueError("Wave 1 readiness gate: variance method and limitations must be explicit")
    result = {
        "status": review["status"],
        "reviewer": review["reviewer"],
        "reviewed_at": review["reviewed_at"],
        "analysis_plan_id": review["analysis_plan_id"],
        "analysis_plan_sha256": expected_plan_hash,
        "public_release_status": "not_approved",
    }
    if plan.get("config_filename"):
        config_path = root / "analysis_review" / str(plan["config_filename"])
        config = _load_json(config_path, "frozen household-environment analysis configuration")
        config_gate = gates[str(plan["config_gate"])]
        config_digest = sha256_file(config_path)
        if str(config_gate.get("sha256", "")).lower() != config_digest:
            raise ValueError("Wave 1 readiness gate: analysis configuration hash is not approved")
        for key, expected in {
            "plan_id": plan["plan_id"],
            "analysis_plan_sha256": expected_plan_hash,
            "source_manifest_id": source_provenance.get("source_manifest_id"),
            "prepared_output_sha256": source_provenance.get("prepared_output_sha256"),
        }.items():
            if config.get(key) != expected:
                raise ValueError(f"Wave 1 readiness gate: frozen scale-up configuration {key} binding differs")
        if "age_candidate_sha256" in source_provenance:
            if config.get("age_candidate_sha256") != source_provenance["age_candidate_sha256"]:
                raise ValueError("Wave 1 readiness gate: frozen configuration is not bound to the reviewed age-interval candidate")
        if config.get("status") != "frozen":
            raise ValueError("Wave 1 readiness gate: model configuration is not frozen")
        if not str(config.get("reviewer", "")).strip() or not str(config.get("reviewed_at", "")).strip():
            raise ValueError("Wave 1 readiness gate: frozen model configuration lacks reviewer/date")
        for section in ("target", "frame", "design", "model", "outcome_transformations", "outcome_validity_rules"):
            if not isinstance(config.get(section), dict) or not config[section]:
                raise ValueError(f"Wave 1 readiness gate: frozen analysis configuration section {section!r} is missing")
        design = config["design"]
        for field in (
            "weight_field", "psu_field", "variance_method", "variance_limitations",
            "singleton_psu_method", "domain_singleton_method", "on_domain_singletons",
        ):
            if not str(design.get(field, "")).strip():
                raise ValueError(f"Wave 1 readiness gate: frozen analysis design lacks {field}")
        strata = design.get("stratum_fields")
        if not isinstance(strata, list) or any(not str(item).strip() for item in strata):
            raise ValueError("Wave 1 readiness gate: stratum_fields must be an explicit list (possibly empty)")
        model = config["model"]
        if model.get("family") != "gaussian" or not str(model.get("primary_model_id", "")).strip():
            raise ValueError("Wave 1 readiness gate: frozen primary model must declare its ID and Gaussian family")
        for key in ("continuous_covariates", "binary_covariates", "categorical_covariates"):
            if not isinstance(model.get(key), (list, dict)):
                raise ValueError(f"Wave 1 readiness gate: frozen model lacks {key}")
        transforms = config["outcome_transformations"]
        if len(transforms) != 15 or any(
            not isinstance(value, str) or value not in {"identity", "log"}
            for value in transforms.values()
        ):
            raise ValueError("Wave 1 readiness gate: all 15 outcome transformations must be frozen as identity or log")
        validity = config["outcome_validity_rules"]
        if set(validity) != set(transforms):
            raise ValueError("Wave 1 readiness gate: all 15 outcomes need an approved source-bound validity rule")
        required_validity_fields = (
            "review_status", "reviewer", "reviewed_at", "source_anchor", "unit",
            "valid_domain_rule", "valid_min", "valid_max", "invalid_codes",
            "lod_censoring_rule", "topcode_rule", "fasting_rule",
        )
        for concept, rule in validity.items():
            if not isinstance(rule, dict) or any(key not in rule for key in required_validity_fields):
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} is incomplete")
            if rule.get("review_status") != "approved":
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} is not approved")
            for key in ("reviewer", "reviewed_at", "source_anchor", "unit", "valid_domain_rule"):
                if not str(rule.get(key, "")).strip():
                    raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} lacks {key}")
            if rule.get("lod_censoring_rule") not in {"none_reported", "handled_by_invalid_codes_or_bounds"}:
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has unsupported LOD handling")
            if rule.get("topcode_rule") not in {"none_reported", "handled_by_invalid_codes_or_bounds"}:
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has unsupported top-code handling")
            fasting = rule.get("fasting_rule")
            if not isinstance(fasting, dict) or fasting.get("mode") not in {"not_applicable", "retain_all", "restrict", "blocked"}:
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has unsupported fasting handling")
            if fasting["mode"] == "restrict":
                if not str(fasting.get("field", "")).strip() or not isinstance(fasting.get("eligible_codes"), list) or not fasting["eligible_codes"]:
                    raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has incomplete fasting restriction")
            elif fasting["mode"] == "blocked":
                if not str(fasting.get("block_reason", "")).strip():
                    raise ValueError(f"Wave 1 readiness gate: blocked fasting rule for {concept} lacks a reason")
                if fasting.get("field") not in (None, "") or fasting.get("eligible_codes", []) not in (None, []):
                    raise ValueError(f"Wave 1 readiness gate: blocked fasting rule for {concept} cannot declare guessed codes")
            elif fasting.get("field") not in (None, "") or fasting.get("eligible_codes", []) not in (None, []):
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has unsupported fasting fields")
            if not isinstance(rule.get("invalid_codes"), list):
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} must list invalid_codes")
            for code in rule["invalid_codes"]:
                if isinstance(code, bool) or not isinstance(code, (int, float)) or not math.isfinite(float(code)):
                    raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has invalid special codes")
            lower, upper = rule.get("valid_min"), rule.get("valid_max")
            if lower is not None and (isinstance(lower, bool) or not isinstance(lower, (int, float)) or not math.isfinite(float(lower))):
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has invalid valid_min")
            if upper is not None and (isinstance(upper, bool) or not isinstance(upper, (int, float)) or not math.isfinite(float(upper))):
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has invalid valid_max")
            if lower is not None and upper is not None and lower > upper:
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} has reversed bounds")
            if (
                rule["lod_censoring_rule"] == "handled_by_invalid_codes_or_bounds"
                or rule["topcode_rule"] == "handled_by_invalid_codes_or_bounds"
            ) and not rule["invalid_codes"] and lower is None and upper is None:
                raise ValueError(f"Wave 1 readiness gate: validity rule for {concept} claims handled censoring without executable codes/bounds")
        result[f"{plan['config_gate']}_sha256"] = config_digest
    return result
