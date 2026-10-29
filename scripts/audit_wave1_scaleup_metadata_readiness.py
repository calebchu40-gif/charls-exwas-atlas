#!/usr/bin/env python3
"""Cross-check the planned Wave 1 K150/K90 registry against public metadata.

This audit reads only the tracked official Codebook extraction, the reviewed
questionnaire-routing note, and the candidate hypothesis register/crosswalk.
It never reads CHARLS respondent records and cannot approve an analysis plan.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "audit" / "wave1_household_environment_hypothesis_register_v0.csv"
CROSSWALK = ROOT / "audit" / "blood_biomarker_crosswalk_v1.csv"
CODEBOOK = ROOT / "audit" / "CHARLS_2011_Codebook_extracted.txt"
ROUTE_REVIEW = ROOT / "audit" / "housing_fuel_source_review_2026-10-24.md"

EXPECTED_CONTRASTS = {
    ("running_water_at_residence", "i017", "yes_vs_no", "1", "Yes", "2", "No"),
    ("electricity_access", "i016", "yes_vs_no", "1", "Yes", "2", "No"),
    ("piped_gas_access", "i019", "yes_vs_no", "1", "Yes", "2", "No"),
    ("residential_heating", "i020", "yes_vs_no", "1", "Yes", "2", "No"),
}
EXPECTED_CONTRASTS |= {
    ("cooking_fuel_main", "i022", f"code_{code}_vs_5", str(code), label, "5", "Electric")
    for code, label in {
        1: "Coal", 2: "Natural gas", 3: "Marsh gas", 4: "LPG",
        6: "Crop residue/Wood", 7: "Other",
    }.items()
}
EXPECTED_CONTRASTS |= {
    ("heating_energy", "i021", f"code_{code}_vs_5", str(code), label, "5", "Electric")
    for code, label in {
        1: "Solar", 2: "Coal", 3: "Natural gas", 4: "LPG",
        6: "Crop residue/Wood", 7: "Other",
    }.items()
}
FAMILY_SIZES = {
    "wave1_household_environment_K150": 150,
    "wave1_heating_route_K90": 90,
}
ROUTED_FAMILY = "wave1_heating_route_K90"
K90_ROUTE = (
    "I020=2 (No) routes to I021; I020=1 (Yes) skips to I022; "
    "K90 is limited to the routed No domain."
)
K150_ROUTE_BY_FIELD = {
    "i017": "all eligible valid respondents",
    "i022": (
        "Main cooking-fuel item; 2011 has no explicit no-cooking response. "
        "Do not infer a category from blank; verify release eligibility and missingness."
    ),
    "i016": "all eligible valid respondents",
    "i019": "all eligible valid respondents",
    "i020": "all eligible valid respondents",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def audit() -> dict[str, object]:
    errors: list[str] = []
    register = read_csv(REGISTER)
    crosswalk = read_csv(CROSSWALK)
    codebook = CODEBOOK.read_text(encoding="utf-8", errors="replace").casefold()
    route_review = ROUTE_REVIEW.read_text(encoding="utf-8", errors="replace").casefold()

    analytes = {
        row["concept_id"]: (row["variable"], row["unit"])
        for row in crosswalk
        if row.get("wave") == "2011"
        and row.get("concept_id") not in {"blood_cystatin_c", "blood_collection_metadata"}
    }
    if len(analytes) != 15:
        errors.append(f"expected 15 eligible 2011 biomarker metadata rows, found {len(analytes)}")

    observed_contrasts = {
        (row.get("exposure_concept_id", ""), row.get("exposure_field_candidate", ""),
         row.get("contrast_id", ""), row.get("exposure_code_candidate", ""),
         row.get("exposure_label_candidate", ""), row.get("reference_code_candidate", ""),
         row.get("reference_label_candidate", ""))
        for row in register
    }
    if observed_contrasts != EXPECTED_CONTRASTS:
        errors.append("registered Wave 1 exposure contrasts/codes/labels differ from the reviewed metadata specification")

    for family, size in FAMILY_SIZES.items():
        rows = [row for row in register if row.get("family_id") == family]
        if len(rows) != size:
            errors.append(f"{family}: expected {size} planned cells, found {len(rows)}")
        for row in rows:
            concept = row.get("phenotype_concept_id", "")
            expected = analytes.get(concept)
            if expected is None:
                errors.append(f"{family}: phenotype {concept!r} is absent from the 2011 biomarker crosswalk")
            elif (row.get("phenotype_field_candidate"), row.get("phenotype_unit_candidate")) != expected:
                errors.append(f"{family}: phenotype field/unit mismatch for {concept}")
            if row.get("primary_model_id") != "not_frozen":
                errors.append(f"{family}: primary model must remain not_frozen before official-source review")
            if row.get("analysis_status") != "planned_not_approved" or row.get("public_release_status") != "not_approved":
                errors.append(f"{family}: hypothesis/release status must remain unapproved")
            route = row.get("route_candidate", "")
            expected_route = K90_ROUTE if family == ROUTED_FAMILY else K150_ROUTE_BY_FIELD.get(
                row.get("exposure_field_candidate", "")
            )
            if route != expected_route:
                errors.append(
                    f"{family}: route rule does not match exposure field "
                    f"{row.get('exposure_field_candidate', '')!r}"
                )

    for code in ("i016", "i017", "i019", "i020", "i021", "i022"):
        if code not in codebook:
            errors.append(f"official 2011 Codebook extraction is missing item {code}")
    if "yes skips the heating-source item to `i022`; no proceeds to `i021`" not in route_review:
        errors.append("reviewed 2011 heating-source route was not found in the cross-wave housing review")

    return {
        "audit_type": "public_metadata_crosswalk_for_planned_wave1_scaleup",
        "participant_data_read": False,
        "planned_hypotheses": len(register),
        "phenotype_metadata_rows": len(analytes),
        "exposure_contrast_specs": len(EXPECTED_CONTRASTS),
        "families": FAMILY_SIZES,
        "route_constraint": "i020 == 2 (No) for i021 heating-energy contrasts",
        "source_reviewed_for_candidate_fields": not errors,
        "analysis_model_approved": False,
        "association_results_created": False,
        "status": "passed_metadata_crosswalk_only" if not errors else "failed",
        "errors": errors,
    }


def main() -> None:
    report = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "passed_metadata_crosswalk_only":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
