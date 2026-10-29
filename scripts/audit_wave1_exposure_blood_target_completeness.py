#!/usr/bin/env python3
"""Protected aggregate-only check of Wave 1 household-exposure coverage.

This checks linkage and candidate contrast-code coverage among records in the
official Blood file with a positive bloodweight. It reads no blood outcomes,
does not fit associations, writes no identifiers, and stores its report only
inside the protected local CHARLS workspace. Counts are diagnostic only: they
are not final model N because age, covariate, outcome-validity, variance, and
independent-review gates remain separate.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
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
DEFAULT_DATA = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_INTAKE = PRIVATE_ROOT / "incoming_2011_official"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_exposure_blood_target_completeness_private.json"
AGE_DATA = PRIVATE_ROOT / "age_inputs_2011" / "wave1_age_interval_candidate.dta"
AGE_QA = PRIVATE_ROOT / "qa_outputs" / "wave1_age_interval_candidate_qa.json"
EXPOSURE_FIELDS = ("i016", "i017", "i019", "i020", "i021", "i022")


def private(path: Path) -> Path:
    path = require_private_path(path)
    if not path.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("Wave 1 exposure completeness inputs/outputs must remain in protected local storage")
    return path


def normalized_id(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    return values.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}).str.replace(r"\.0+$", "", regex=True)


def load_register() -> dict[str, dict[str, Any]]:
    with REGISTER.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    result: dict[str, dict[str, Any]] = {}
    for family in ("wave1_household_environment_K150", "wave1_heating_route_K90"):
        family_rows = [row for row in rows if row["family_id"] == family]
        if not family_rows:
            raise ValueError(f"Missing planned family: {family}")
        for row in family_rows:
            field = row["exposure_field_candidate"]
            if field not in EXPOSURE_FIELDS:
                raise ValueError(f"Unrecognized planned exposure field: {field}")
            entry = result.setdefault(field, {"families": set(), "codes": set(), "contrasts": {}})
            entry["families"].add(family)
            for key in ("exposure_code_candidate", "reference_code_candidate"):
                entry["codes"].add(float(row[key]))
            contrast = row["contrast_id"]
            route = row["route_candidate"].strip()
            prior = entry["contrasts"].get(contrast)
            spec = {
                "exposure_code": float(row["exposure_code_candidate"]),
                "reference_code": float(row["reference_code_candidate"]),
                "route": route,
                "family": family,
            }
            if prior is not None and prior != spec:
                raise ValueError(f"Inconsistent frozen contrast metadata: {field}/{contrast}")
            entry["contrasts"][contrast] = spec
    for field, entry in result.items():
        for contrast, spec in entry["contrasts"].items():
            if field == "i021" and (spec["route"] != "I020=2 (No) routes to I021; I020=1 (Yes) skips to I022; K90 is limited to the routed No domain."):
                raise ValueError(f"Unexpected I021 route metadata for {contrast}")
    return result


def run(data_path: Path, intake: Path, output: Path) -> dict[str, Any]:
    data_path, intake, output = private(data_path), private(intake), private(output)
    if output.exists() and output.is_dir():
        raise ValueError("Output path is a directory")
    blood_path = private(intake / "Blood_20140429.dta")
    age_path, age_qa_path = private(AGE_DATA), private(AGE_QA)
    if not data_path.is_file() or not blood_path.is_file() or not age_path.is_file() or not age_qa_path.is_file():
        raise FileNotFoundError("Official Wave 1 prepared frame, Blood source, or age candidate is missing")

    provenance = require_verified_wave1_frame(data_path=data_path)
    # Read only the planned household exposure fields from the prepared table
    # and the identifier/official weight from the Blood file.
    people, _ = pyreadstat.read_dta(str(data_path), usecols=["ID", "householdID", *EXPOSURE_FIELDS])
    blood, _ = pyreadstat.read_dta(str(blood_path), usecols=["ID", "bloodweight"])
    age_qa = json.loads(age_qa_path.read_text(encoding="utf-8"))
    if age_qa.get("source_manifest_id") != provenance["source_manifest_id"]:
        raise ValueError("Age candidate is not bound to the reviewed Wave 1 source manifest")
    if age_qa.get("age_derivation_method_reviewed") is not False or age_qa.get("survey_design_approved") is not False:
        raise ValueError("Age candidate status changed; inspect its review gate before using it")
    if age_qa.get("person_level_output_path") != age_path.name:
        raise ValueError("Age candidate path does not match its private QA record")
    age_digest = sha256_file(age_path)
    if age_qa.get("person_level_output_sha256") != age_digest:
        raise ValueError("Age candidate output hash does not match its private QA record")
    age, _ = pyreadstat.read_dta(
        str(age_path),
        usecols=["ID", "age_at_interview_lower", "age_at_interview_upper", "age45_domain_status_candidate"],
    )
    people["_id"] = normalized_id(people["ID"])
    blood["_id"] = normalized_id(blood["ID"])
    age["_id"] = normalized_id(age["ID"])
    if people["_id"].isna().any() or people["_id"].duplicated().any():
        raise ValueError("Prepared respondent ID is missing or non-unique")
    if blood["_id"].isna().any() or blood["_id"].duplicated().any():
        raise ValueError("Official Blood-file ID is missing or non-unique")
    if age["_id"].isna().any() or age["_id"].duplicated().any():
        raise ValueError("Age-candidate ID is missing or non-unique")

    joined = blood[["_id", "bloodweight"]].merge(
        people[["_id", "householdID", *EXPOSURE_FIELDS]],
        on="_id", how="left", validate="1:1", indicator=True,
    )
    if (joined["_merge"] != "both").any():
        raise ValueError("Some official Blood-file IDs do not link to the prepared respondent frame")
    joined = joined.drop(columns="_merge").merge(
        age[["_id", "age_at_interview_lower", "age_at_interview_upper", "age45_domain_status_candidate"]],
        on="_id", how="left", validate="1:1", indicator="_age_merge",
    )
    if len(age) != int(age_qa.get("row_count", -1)):
        raise ValueError("Age candidate row count does not match its private QA record")
    joined["age_interval_available"] = (
        pd.to_numeric(joined["age_at_interview_lower"], errors="coerce").notna()
        & pd.to_numeric(joined["age_at_interview_upper"], errors="coerce").notna()
    )
    age_lower = pd.to_numeric(joined["age_at_interview_lower"], errors="coerce")
    age_upper = pd.to_numeric(joined["age_at_interview_upper"], errors="coerce")
    if ((age_lower.notna() & age_upper.notna()) & (age_lower.gt(age_upper) | age_lower.lt(0) | age_upper.gt(120))).any():
        raise ValueError("Age candidate contains an invalid interval")
    weights = pd.to_numeric(joined["bloodweight"], errors="coerce")
    weighted_target = weights.notna() & weights.map(math.isfinite) & weights.gt(0)
    if not weighted_target.any():
        raise ValueError("No positive official bloodweight records found")

    specifications = load_register()
    fields: dict[str, Any] = {}
    for field, spec in specifications.items():
        values = pd.to_numeric(joined[field], errors="coerce")
        in_route = pd.Series(True, index=joined.index)
        route_n = int(weighted_target.sum())
        if field == "i021":
            heating = pd.to_numeric(joined["i020"], errors="coerce")
            in_route = heating.eq(2)
            route_n = int((weighted_target & in_route).sum())
        supported = values.isin(sorted(spec["codes"]))
        eligible = weighted_target & in_route
        result = {
            "planned_families": sorted(spec["families"]),
            "bloodweight_positive_target_records": int(weighted_target.sum()),
            "route_eligible_records": route_n,
            "contrast_code_supported_records": int((eligible & supported).sum()),
            "not_in_registered_contrast_codes_records": int((eligible & ~supported).sum()),
            "household_key_missing_records_in_supported_domain": int((eligible & supported & joined["householdID"].isna()).sum()),
            "contrast_support": {},
            "household_value_consistency": {},
            "age_candidate_coverage": {
                "interval_available_records": int((eligible & supported & joined["age_interval_available"]).sum()),
                "age_interval_missing_or_unresolved_records": int((eligible & supported & ~joined["age_interval_available"]).sum()),
                "age45_domain_status_counts_private": {
                    str(label): int(((eligible & supported) & joined["age45_domain_status_candidate"].eq(label)).sum())
                    for label in sorted(joined["age45_domain_status_candidate"].dropna().astype(str).unique())
                },
                "method_reviewed": False,
                "used_to_filter_records": False,
            },
        }
        for contrast, contrast_spec in sorted(spec["contrasts"].items()):
            e_code, r_code = contrast_spec["exposure_code"], contrast_spec["reference_code"]
            result["contrast_support"][contrast] = {
                "exposure_category_records": int((eligible & values.eq(e_code)).sum()),
                "reference_category_records": int((eligible & values.eq(r_code)).sum()),
            }
        # Check that the person-level prepared table has not propagated
        # conflicting household answers across respondents in a household.
        household_ids = joined.loc[eligible & joined["householdID"].notna(), ["householdID", field]].copy()
        distinct = household_ids.groupby("householdID", dropna=True)[field].nunique(dropna=True)
        result["household_value_consistency"] = {
            "households_with_multiple_nonmissing_values": int(distinct.gt(1).sum()),
            "households_with_any_nonmissing_value": int(distinct.gt(0).sum()),
        }
        fields[field] = result

    report: dict[str, Any] = {
        "status": "aggregate_only_pre_analysis_eligibility_audit",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": provenance["source_manifest_id"],
        "source_identity_status": provenance["source_identity_status"],
        "prepared_data_sha256": provenance["prepared_output_sha256"],
        "blood_source_sha256": sha256_file(blood_path),
        "age_candidate_sha256": age_digest,
        "age_candidate_derivation_reviewed": False,
        "scope": {
            "population": "official Wave 1 Blood-file records with positive bloodweight",
            "fields_read_from_prepared_table": list(EXPOSURE_FIELDS),
            "phenotype_values_read": False,
            "provisional_age_interval_candidate_read": True,
            "age_candidate_values_used_to_filter": False,
            "association_models_fitted": False,
            "counts_are_final_model_n": False,
        },
        "blood_frame": {
            "blood_source_rows": int(len(blood)),
            "positive_bloodweight_records": int(weighted_target.sum()),
            "missing_or_nonpositive_bloodweight_records": int((~weighted_target).sum()),
            "prepared_person_matches": int(len(joined)),
        },
        "exposures": fields,
        "interpretation": "Private aggregate coverage diagnostics only. Does not resolve age, PSU/variance, covariate, outcome-validity, fasting, independent review, or final analysis N.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        output.chmod(0o600)
    except OSError:
        pass
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
        "source_identity_status": report["source_identity_status"],
        "fields_audited": sorted(report["exposures"]),
        "report_saved_under_protected_root": str(private(args.output).parent == PRIVATE_ROOT or private(args.output).is_relative_to(PRIVATE_ROOT)),
        "association_models_fitted": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
