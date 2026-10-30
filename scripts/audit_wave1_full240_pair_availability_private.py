#!/usr/bin/env python3
"""Write owner-only Wave 1 K=240 pair-availability diagnostics.

This is not an association runner. It reports only aggregate pair availability
and community support for the frozen candidate register, using finite-value
availability masks without applying any unresolved outcome-validity rules.
The 90-coefficient heating-route family is restricted to the documented
I020=2 route into I021. Exact counts are written only below PRIVATE_ROOT.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
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
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_full240_pair_availability_private.json"

FAMILY_SIZES = {
    "wave1_household_environment_K150": 150,
    "wave1_heating_route_K90": 90,
}
I021_ROUTE = "I020=2 (No) routes to I021; I020=1 (Yes) skips to I022; K90 is limited to the routed No domain."


def private(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("All participant inputs and detailed QA must remain in protected PRIVATE_ROOT")
    return resolved


def normalized_id(values: pd.Series) -> pd.Series:
    result = values.astype("string").str.strip()
    result = result.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return result.str.replace(r"\.0+$", "", regex=True)


def read_registry() -> list[dict[str, Any]]:
    with REGISTER.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    rows = [row for row in rows if row["family_id"] in FAMILY_SIZES]
    for family, expected in FAMILY_SIZES.items():
        family_rows = [row for row in rows if row["family_id"] == family]
        if len(family_rows) != expected or len({row["hypothesis_id"] for row in family_rows}) != expected:
            raise ValueError(f"Candidate register must have {expected} unique hypotheses for {family}")
    if len(rows) != 240 or len({row["hypothesis_id"] for row in rows}) != 240:
        raise ValueError("The two registered Wave 1 families must contain exactly 240 unique hypotheses")

    specs: list[dict[str, Any]] = []
    for row in rows:
        field = row["exposure_field_candidate"]
        family = row["family_id"]
        route = row["route_candidate"].strip()
        if family == "wave1_heating_route_K90":
            if field != "i021" or route != I021_ROUTE:
                raise ValueError("K90 must use the exact reviewed I020=2 route into I021")
            route_rule = "i020_eq_2"
        elif route == "all eligible valid respondents":
            route_rule = "none"
        elif route.startswith("Main cooking-fuel item; 2011 has no explicit no-cooking response."):
            if field != "i022":
                raise ValueError("The no-explicit-no-cooking route note is expected only for I022")
            route_rule = "i022_documented_route_caveat_no_extra_filter"
        else:
            raise ValueError(f"Unreviewed route rule in registry for {field}: {route}")
        specs.append({
            "hypothesis_id": row["hypothesis_id"],
            "family_id": family,
            "exposure_field": field,
            "exposure_code": float(row["exposure_code_candidate"]),
            "reference_code": float(row["reference_code_candidate"]),
            "phenotype_concept_id": row["phenotype_concept_id"],
            "phenotype_field": row["phenotype_field_candidate"],
            "contrast_id": row["contrast_id"],
            "route_candidate": route,
            "route_rule": route_rule,
        })
    return specs


def finite_numeric(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    return values.notna() & np.isfinite(values)


def run(data_path: Path, intake: Path, output: Path) -> dict[str, Any]:
    data_path, intake, output = private(data_path), private(intake), private(output)
    blood_path = private(intake / "Blood_20140429.dta")
    age_path, age_qa_path = private(AGE_DATA), private(AGE_QA)
    for required in (data_path, blood_path, age_path, age_qa_path):
        if not required.is_file():
            raise FileNotFoundError(f"Required protected input is missing: {required.name}")

    provenance = require_verified_wave1_frame(data_path=data_path)
    age_qa = json.loads(age_qa_path.read_text(encoding="utf-8"))
    age_hash = sha256_file(age_path)
    if age_qa.get("source_manifest_id") != provenance["source_manifest_id"]:
        raise ValueError("Age candidate is not bound to the verified Wave 1 source manifest")
    if age_qa.get("person_level_output_sha256") != age_hash:
        raise ValueError("Age candidate output hash does not match its protected QA record")
    if age_qa.get("age_derivation_method_reviewed") is not False:
        raise ValueError("This availability audit accepts only the explicitly provisional age candidate")

    specs = read_registry()
    exposure_fields = sorted({spec["exposure_field"] for spec in specs})
    outcome_fields = sorted({spec["phenotype_field"] for spec in specs})
    if len(outcome_fields) != 15:
        raise ValueError("The candidate register must map to 15 conventional Wave 1 Blood outcomes")
    people, _ = pyreadstat.read_dta(
        str(data_path), usecols=["ID", "communityID", *exposure_fields]
    )
    blood, _ = pyreadstat.read_dta(
        str(blood_path), usecols=["ID", "bloodweight", *outcome_fields]
    )
    age, _ = pyreadstat.read_dta(
        str(age_path), usecols=["ID", "age_at_interview_lower", "age_at_interview_upper"]
    )
    for frame, label in ((people, "prepared person table"), (blood, "Blood source"), (age, "age candidate")):
        frame["_id"] = normalized_id(frame["ID"])
        if frame["_id"].isna().any() or frame["_id"].duplicated().any():
            raise ValueError(f"{label} IDs must be nonmissing and unique")

    joined = blood.merge(
        people[["_id", "communityID", *exposure_fields]],
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
    valid_weight = weight.notna() & np.isfinite(weight) & weight.gt(0)
    valid_age_interval = lower.notna() & np.isfinite(lower) & upper.notna() & np.isfinite(upper) & lower.le(upper)
    domains = {
        "blood_target_positive_bloodweight": valid_weight,
        "lower_age_bound_45plus_provisional_domain": valid_weight & valid_age_interval & lower.ge(45),
        "upper_age_bound_45plus_provisional_sensitivity": valid_weight & valid_age_interval & upper.ge(45),
    }
    community = joined["communityID"].astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA})
    rows_out: list[dict[str, Any]] = []
    for spec in specs:
        exposure = pd.to_numeric(joined[spec["exposure_field"]], errors="coerce")
        outcome = pd.to_numeric(joined[spec["phenotype_field"]], errors="coerce")
        if spec["route_rule"] == "i020_eq_2":
            routed = pd.to_numeric(joined["i020"], errors="coerce").eq(2)
        else:
            routed = pd.Series(True, index=joined.index)
        contrast = exposure.isin([spec["exposure_code"], spec["reference_code"]])
        outcome_available = finite_numeric(outcome)
        for domain_name, base in domains.items():
            domain = base & routed
            candidate_rows = domain & contrast
            complete = candidate_rows & outcome_available
            exp_arm = exposure.eq(spec["exposure_code"])
            ref_arm = exposure.eq(spec["reference_code"])
            exp_communities = set(community.loc[complete & exp_arm].dropna().tolist())
            ref_communities = set(community.loc[complete & ref_arm].dropna().tolist())
            sizes = community.loc[complete].dropna().value_counts()
            rows_out.append({
                "hypothesis_id": spec["hypothesis_id"],
                "family_id": spec["family_id"],
                "exposure_field": spec["exposure_field"],
                "phenotype_field": spec["phenotype_field"],
                "contrast_id": spec["contrast_id"],
                "route_rule": spec["route_rule"],
                "domain": domain_name,
                "positive_weight_domain_rows": int(domain.sum()),
                "routed_rows_in_domain": int((base & routed).sum()),
                "registered_contrast_rows": int(candidate_rows.sum()),
                "exposure_arm_rows": int((candidate_rows & exp_arm).sum()),
                "reference_arm_rows": int((candidate_rows & ref_arm).sum()),
                "finite_outcome_available_rows_only": int(complete.sum()),
                "outcome_unavailable_rows": int((candidate_rows & ~outcome_available).sum()),
                "community_keys_in_complete_availability_mask": int(community.loc[complete].nunique(dropna=True)),
                "communities_exposure_arm_availability_only": len(exp_communities),
                "communities_reference_arm_availability_only": len(ref_communities),
                "communities_both_arms_availability_only": len(exp_communities & ref_communities),
                "single_record_communities_availability_only": int((sizes == 1).sum()),
                "multiple_record_communities_availability_only": int((sizes > 1).sum()),
                "availability_rows_missing_community_key": int((complete & community.isna()).sum()),
                "model_estimability": "not_assessed_by_availability_audit",
            })

    report = {
        "status": "protected_aggregate_only_full240_pair_availability_audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": provenance["source_manifest_id"],
        "source_identity_status": provenance["source_identity_status"],
        "prepared_person_table_sha256": provenance["prepared_output_sha256"],
        "blood_source_sha256": sha256_file(blood_path),
        "age_candidate_sha256": age_hash,
        "registry_sha256": sha256_file(REGISTER),
        "biomarker_crosswalk_sha256": sha256_file(BIOMARKER_CROSSWALK),
        "scope": {
            "registered_coefficients": len(specs),
            "family_sizes": FAMILY_SIZES,
            "domains": list(domains),
            "participant_ids_written": False,
            "participant_ids_logged": False,
            "outcome_value_summaries_written": False,
            "association_models_fitted": False,
            "outcome_validity_rules_applied": False,
            "age_derivation_approved": False,
            "survey_design_approved": False,
            "model_estimability_assessed": False,
            "exact_rows_are_final_model_n": False,
        },
        "pair_rows_private": rows_out,
        "limitations": [
            "All row-level inputs and exact pair/domain counts remain in owner-only PRIVATE_ROOT; no IDs are emitted.",
            "Finite nonmissing outcome values indicate availability only; no finite sentinel or outcome-validity rules were applied.",
            "Assay ranges, clinical cutoffs, and sample distributions were not used to filter or classify values.",
            "K90 uses only the documented I020=2 route into I021; no outcome models or formal estimability decisions were made.",
            "The 45+ age interval candidate is provisional; age-domain rows are diagnostic and are not final model N.",
            "Community support counts describe availability only and do not validate the communityID WR Taylor approximation.",
            "The 14 glucose/TG coefficients remain blocked for fasting estimand and bloodweight applicability review.",
            "This audit does not open the independent-methods or disclosure gate and cannot authorize analysis or release.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(output, 0o600)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.data, args.intake, args.output)
    print(json.dumps({
        "status": report["status"],
        "registered_coefficients": report["scope"]["registered_coefficients"],
        "family_sizes": report["scope"]["family_sizes"],
        "domains": report["scope"]["domains"],
        "private_output_written": True,
        "association_models_fitted": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
