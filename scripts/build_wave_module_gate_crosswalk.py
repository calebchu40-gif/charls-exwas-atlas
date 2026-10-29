#!/usr/bin/env python3
"""Build a public, metadata-only wave/module analysis-gate crosswalk.

Reads only the repository's candidate-field catalog. It never opens CHARLS
microdata or private analysis outputs. Counts refer to unique catalog field
names by candidate E/P/C role, not participants, eligible outcomes, or tests.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "audit" / "charls_atlas_candidate_fields_v0.csv"
OUTPUT = ROOT / "audit" / "wave_module_source_estimand_weight_gate_crosswalk_v1.csv"

WAVE_RULES = {
    "2011": {
        "sample_marker": "Baseline respondent/spouse and module eligibility; confirm interview and route fields",
        "estimand_start": "Wave-specific cross-sectional target; apply age 45+ as a domain only after target and full design frame are approved",
        "weight_candidates": "Individual sampling weight for eligible interview outcomes; bloodweight for the documented blood-response target",
        "weight_gate": "Module-level target/applicability not independently approved",
        "runner": "Historical water/blood exploratory runner only; K150/K90 template is not frozen",
    },
    "2013": {
        "sample_marker": "Weights archive crosssection/longitudinal indicators; module participation and any required baseline-ID transformation must also be checked",
        "estimand_start": "Wave-specific cross-sectional target by default; longitudinal estimand requires a separate risk set and attrition specification",
        "weight_candidates": "INDV_weight_ad2 for eligible cross-sectional interview outcomes; Biomarker_weight for cross-sectional pairs with a measure from the official Biomarker.dta target (verify crosssection and pair-level eligibility); no released longitudinal biomarker weight",
        "weight_gate": "Official weight purpose is documented for the Biomarker module; exact pair eligibility, file linkage, sample flags, age domain, and survey variance remain unapproved",
        "runner": "No Wave 2 association runner or frozen configuration",
    },
    "2015": {
        "sample_marker": "Sample_Infor.crosssection plus module participation; preserve blood collection/fasting metadata for blood outcomes",
        "estimand_start": "Wave-specific cross-sectional target; any age 45+ restriction is a domain of the approved full module frame",
        "weight_candidates": "INDV_weight_ad2 for eligible interview outcomes; Blood_weight for the released cross-sectional blood target",
        "weight_gate": "Module-level target/applicability and blood target linkage not independently approved",
        "runner": "No Wave 3 association runner or frozen configuration",
    },
    "2018": {
        "sample_marker": "Sample_Infor.crosssection plus module participation; HCAP has a separate age-restricted assessment frame",
        "estimand_start": "Wave-specific cross-sectional target by module; do not treat HCAP as a routine outcome for all age-45+ respondents",
        "weight_candidates": "INDV_weight_ad2 for eligible main-respondent/spouse interview outcomes; verify HCAP-specific target separately",
        "weight_gate": "Module-level target/applicability and HCAP frame not independently approved",
        "runner": "No Wave 4 association runner or frozen configuration",
    },
    "2020": {
        "sample_marker": "Sample_Infor.crosssection plus module participation; apply the released proxy/partial-interview eligibility rules",
        "estimand_start": "Wave-specific cross-sectional target by module; COVID-era routing and proxy status require explicit handling",
        "weight_candidates": "INDV_weight_ad2 for eligible representative-sample outcomes, subject to module and proxy/partial-interview rules",
        "weight_gate": "Module-level target/applicability not independently approved",
        "runner": "No Wave 5 association runner or frozen configuration",
    },
}

FIELDS = [
    "wave", "source_module", "source_archive",
    "candidate_unique_fields_E", "candidate_unique_fields_P", "candidate_unique_fields_C",
    "candidate_field_count_note", "sample_eligibility_marker_candidate",
    "estimand_starting_point_candidate", "weight_field_candidates_not_approved",
    "weight_applicability_status", "survey_design_status", "runner_configuration_status",
]


def main() -> None:
    groups: dict[tuple[str, str], dict[str, object]] = {}
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"Source.Wave", "Data.File.Name", "Source.Archive", "Variable.Name", "epcf"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Candidate catalog lacks required metadata columns: {sorted(required)}")
        for row in reader:
            wave = (row.get("Source.Wave") or "").strip()
            if wave not in WAVE_RULES:
                continue
            module = (row.get("Data.File.Name") or row.get("Component") or "").strip()
            variable = (row.get("Variable.Name") or "").strip()
            if not module or not variable:
                continue
            key = (wave, module.casefold())
            group = groups.setdefault(key, {
                "modules": Counter(), "archives": set(), "roles": {r: set() for r in "epc"},
            })
            group["modules"][module] += 1
            archive = (row.get("Source.Archive") or "").strip()
            if archive:
                group["archives"].add(archive)
            roles = {role.strip().casefold() for role in (row.get("epcf") or "").split(",")}
            for role in "epc":
                if role in roles:
                    group["roles"][role].add(variable)

    output_rows = []
    for (wave, _), group in sorted(groups.items(), key=lambda item: (int(item[0][0]), item[0][1])):
        wave_rule = WAVE_RULES[wave]
        module = group["modules"].most_common(1)[0][0]
        module_weight_candidates = wave_rule["weight_candidates"]
        module_weight_gate = wave_rule["weight_gate"]
        if wave == "2013" and "biomarker" in module.casefold():
            module_weight_candidates = (
                "Biomarker_weight for cross-sectional pairs using a measure from the official Biomarker.dta target; "
                "verify crosssection and pair-level eligibility; no released longitudinal biomarker weight"
            )
            module_weight_gate = (
                "Official source documents a cross-sectional response-adjusted biomarker weight; exact pair eligibility, "
                "file linkage, age domain, and survey variance remain unapproved"
            )
        output_rows.append({
            "wave": wave,
            "source_module": module,
            "source_archive": "; ".join(sorted(group["archives"], key=str.casefold)),
            "candidate_unique_fields_E": len(group["roles"]["e"]),
            "candidate_unique_fields_P": len(group["roles"]["p"]),
            "candidate_unique_fields_C": len(group["roles"]["c"]),
            "candidate_field_count_note": "Unique catalog variable names by candidate role; not analyzed pairs, eligible records, or participant N",
            "sample_eligibility_marker_candidate": wave_rule["sample_marker"],
            "estimand_starting_point_candidate": wave_rule["estimand_start"],
            "weight_field_candidates_not_approved": module_weight_candidates,
            "weight_applicability_status": module_weight_gate,
            "survey_design_status": "Open: module-specific PSU/strata/variance and age-domain method require review",
            "runner_configuration_status": wave_rule["runner"],
        })

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Wrote {len(output_rows)} wave/module metadata rows to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
