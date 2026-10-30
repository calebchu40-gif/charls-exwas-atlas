#!/usr/bin/env python3
"""Write protected, aggregate-only Wave 1 pilot pair availability QA.

The audit does not estimate an exposure association. It reconciles the frozen
105 pilot coefficients against the protected blood target, provisional age
intervals, positive bloodweight, observed outcome availability, and released
parent-community keys. Outcome nonmissingness is not treated as outcome
validity; survey-design and methods approval remain separate gates.
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path
from prepare_charls_wave_tables import sha256_file
from require_verified_wave1_frame import require_verified_wave1_frame


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "audit" / "wave1_household_environment_hypothesis_register_v0.csv"
BIOMARKER_CROSSWALK = ROOT / "audit" / "blood_biomarker_crosswalk_v1.csv"
DEFAULT_DATA = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2011_official"
AGE_DATA = PRIVATE_ROOT / "age_inputs_2011" / "wave1_age_interval_candidate.dta"
AGE_QA = PRIVATE_ROOT / "qa_outputs" / "wave1_age_interval_candidate_qa.json"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_pilot_pair_eligibility_private.json"


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("All participant inputs and detailed QA must remain in the protected private root")
    return resolved


def normalized_id(values: pd.Series) -> pd.Series:
    result = values.astype("string").str.strip()
    result = result.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return result.str.replace(r"\.0+$", "", regex=True)


def load_biomarkers() -> list[dict[str, str]]:
    with BIOMARKER_CROSSWALK.open(newline="", encoding="utf-8-sig") as stream:
        rows = [r for r in csv.DictReader(stream) if r["wave"] == "2011" and r["concept_id"] not in {
            "blood_cystatin_c", "blood_collection_metadata"
        }]
    if len(rows) != 15 or len({r["variable"] for r in rows}) != 15:
        raise ValueError("The reviewed Wave 1 conventional-biomarker crosswalk must contain 15 unique outcomes")
    return rows


def load_pilot_coefficients(biomarkers: list[dict[str, str]]) -> list[dict[str, Any]]:
    with REGISTER.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    outcome_keys = {r["variable"] for r in biomarkers}
    selected = [
        r for r in rows
        if r["family_id"] == "wave1_household_environment_K150"
        and r["exposure_field_candidate"] in {"i017", "i022"}
    ]
    expected = 105
    if len(selected) != expected or len({r["hypothesis_id"] for r in selected}) != expected:
        raise ValueError("The registered i017/i022 pilot tranche must have 105 unique coefficient IDs")
    if {r["phenotype_field_candidate"] for r in selected} != outcome_keys:
        raise ValueError("Pilot registry phenotype fields do not match the 15-outcome crosswalk")
    return [{
        "hypothesis_id": r["hypothesis_id"],
        "exposure_field": r["exposure_field_candidate"],
        "exposure_code": float(r["exposure_code_candidate"]),
        "reference_code": float(r["reference_code_candidate"]),
        "phenotype_concept_id": r["phenotype_concept_id"],
        "phenotype_field": r["phenotype_field_candidate"],
        "contrast_id": r["contrast_id"],
    } for r in selected]


def run(data_path: Path, intake: Path, output: Path) -> dict[str, Any]:
    data_path, intake, output = private(data_path), private(intake), private(output)
    blood_path = private(intake / "Blood_20140429.dta")
    age_path, age_qa_path = private(AGE_DATA), private(AGE_QA)
    for required in (data_path, blood_path, age_path, age_qa_path):
        if not required.is_file():
            raise FileNotFoundError(f"Required protected Wave 1 input is missing: {required.name}")

    provenance = require_verified_wave1_frame(data_path=data_path)
    age_qa = json.loads(age_qa_path.read_text(encoding="utf-8"))
    age_hash = sha256_file(age_path)
    if age_qa.get("source_manifest_id") != provenance["source_manifest_id"]:
        raise ValueError("Age candidate is not bound to the verified source manifest")
    if age_qa.get("person_level_output_sha256") != age_hash:
        raise ValueError("Age candidate output hash does not match its protected QA record")
    if age_qa.get("age_derivation_method_reviewed") is not False:
        raise ValueError("This audit accepts only a clearly marked provisional age candidate")

    biomarkers = load_biomarkers()
    coefficients = load_pilot_coefficients(biomarkers)
    exposure_fields = sorted({r["exposure_field"] for r in coefficients})
    outcome_fields = [r["variable"] for r in biomarkers]
    people, _ = pyreadstat.read_dta(
        str(data_path), usecols=["ID", "communityID", "householdID", *exposure_fields]
    )
    blood, _ = pyreadstat.read_dta(
        str(blood_path), usecols=["ID", "bloodweight", *outcome_fields]
    )
    age, _ = pyreadstat.read_dta(
        str(age_path), usecols=["ID", "age_at_interview_lower", "age_at_interview_upper"]
    )
    for frame, name in ((people, "prepared person table"), (blood, "Blood source"), (age, "age candidate")):
        frame["_id"] = normalized_id(frame["ID"])
        if frame["_id"].isna().any() or frame["_id"].duplicated().any():
            raise ValueError(f"{name} IDs must be nonmissing and unique")
    joined = blood.merge(
        people[["_id", "communityID", "householdID", *exposure_fields]],
        on="_id", how="left", validate="1:1", indicator="_person_link",
    )
    if not joined["_person_link"].eq("both").all():
        raise ValueError("Official Blood records do not all map to the prepared person table")
    joined = joined.drop(columns="_person_link").merge(
        age[["_id", "age_at_interview_lower", "age_at_interview_upper"]],
        on="_id", how="left", validate="1:1", indicator="_age_link",
    )
    if not joined["_age_link"].eq("both").all():
        raise ValueError("Official Blood records do not all map to the protected age candidate")
    joined = joined.drop(columns="_age_link")

    weight = pd.to_numeric(joined["bloodweight"], errors="coerce")
    lower = pd.to_numeric(joined["age_at_interview_lower"], errors="coerce")
    upper = pd.to_numeric(joined["age_at_interview_upper"], errors="coerce")
    community = joined["communityID"].astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA})
    bases = {
        "blood_target": weight.gt(0),
        "primary_age_lower_bound_45plus": weight.gt(0) & lower.ge(45),
        "age_upper_bound_45plus_sensitivity": weight.gt(0) & upper.ge(45),
    }
    rows: list[dict[str, Any]] = []
    for spec in coefficients:
        exposure = pd.to_numeric(joined[spec["exposure_field"]], errors="coerce")
        outcome = pd.to_numeric(joined[spec["phenotype_field"]], errors="coerce")
        contrast = exposure.isin([spec["exposure_code"], spec["reference_code"]])
        nonmissing_outcome = outcome.notna()
        analyte_fast_sensitive = spec["phenotype_concept_id"] == "blood_glucose"
        for domain_name, base in bases.items():
            mask = base & contrast
            complete = mask & nonmissing_outcome
            rows.append({
                "hypothesis_id": spec["hypothesis_id"],
                "exposure_field": spec["exposure_field"],
                "exposure_code": spec["exposure_code"],
                "reference_code": spec["reference_code"],
                "phenotype_concept_id": spec["phenotype_concept_id"],
                "phenotype_field": spec["phenotype_field"],
                "domain": domain_name,
                "positive_bloodweight_pair_domain_records": int(mask.sum()),
                "exposure_records": int((mask & exposure.eq(spec["exposure_code"])).sum()),
                "reference_records": int((mask & exposure.eq(spec["reference_code"])).sum()),
                "nonmissing_outcome_pair_records_availability_only": int(complete.sum()),
                "outcome_missing_pair_records": int((mask & ~nonmissing_outcome).sum()),
                "outcome_nonmissing_values_excluded_by_validity_rules": None,
                "distinct_parent_community_keys_in_pair_domain": int(community.loc[complete].nunique(dropna=True)),
                "positive_weight_rows_missing_parent_community": int((complete & community.isna()).sum()),
                "fasting_mapping_status": (
                    "unresolved_blocked_for_primary_handling" if analyte_fast_sensitive
                    else "candidate_all_samples_pending_methods_review" if spec["phenotype_concept_id"] == "blood_triglycerides"
                    else "not_flagged_as_fasting_dependent_by_current_plan"
                ),
                "estimability_status": "availability_only_not_model_estimability",
            })

    report = {
        "status": "protected_aggregate_only_pair_availability_audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": provenance["source_manifest_id"],
        "source_identity_status": provenance["source_identity_status"],
        "prepared_person_table_sha256": provenance["prepared_output_sha256"],
        "blood_source_sha256": sha256_file(blood_path),
        "age_candidate_sha256": age_hash,
        "registry_sha256": sha256_file(REGISTER),
        "biomarker_crosswalk_sha256": sha256_file(BIOMARKER_CROSSWALK),
        "scope": {
            "registered_pilot_coefficients": len(coefficients),
            "domains": list(bases),
            "participant_ids_written": False,
            "participant_ids_logged": False,
            "outcome_value_summaries_written": False,
            "association_models_fitted": False,
            "outcome_validity_rules_applied": False,
            "age_method_approved": False,
            "survey_design_approved": False,
        },
        "pair_rows_private": rows,
        "limitations": [
            "Pair counts describe data availability only; they are not final analytic N.",
            "Nonmissing outcome values are not assumed clinically valid; no distribution-derived rule or assay range was used as an exclusion cutoff.",
            "Positive bloodweight and released parent-community keys do not approve a variance estimator or resolve split sub-PSUs.",
            "The age lower/upper domain masks use an unreviewed provisional candidate and are diagnostic only.",
            "Wave 1 fasting status numeric mapping remains unresolved; glucose is blocked and triglycerides remain an all-sample candidate pending methods review.",
        ],
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
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.data, args.intake, args.output)
    print(json.dumps({
        "status": result["status"],
        "coefficient_rows": result["scope"]["registered_pilot_coefficients"],
        "domains": result["scope"]["domains"],
        "private_output_written": True,
        "association_models_fitted": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
