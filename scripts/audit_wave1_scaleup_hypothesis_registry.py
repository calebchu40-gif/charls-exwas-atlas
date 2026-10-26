#!/usr/bin/env python3
"""Metadata-only structural audit for the planned Wave 1 K150/K90 registry.

This checks completeness and status labels in the predeclared hypothesis
register. It does not read CHARLS participant data, validate candidate codes,
approve a model, or produce association results.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "audit" / "wave1_household_environment_hypothesis_register_v0.csv"

EXPECTED = {
    "wave1_household_environment_K150": {
        "size": 150,
        "role": "post_pilot_exploratory_scaleup_block",
        "contrasts": {
            ("running_water_at_residence", "i017", "yes_vs_no"),
            ("cooking_fuel_main", "i022", "code_1_vs_5"),
            ("cooking_fuel_main", "i022", "code_2_vs_5"),
            ("cooking_fuel_main", "i022", "code_3_vs_5"),
            ("cooking_fuel_main", "i022", "code_4_vs_5"),
            ("cooking_fuel_main", "i022", "code_6_vs_5"),
            ("cooking_fuel_main", "i022", "code_7_vs_5"),
            ("electricity_access", "i016", "yes_vs_no"),
            ("piped_gas_access", "i019", "yes_vs_no"),
            ("residential_heating", "i020", "yes_vs_no"),
        },
        "route": "all eligible valid respondents",
    },
    "wave1_heating_route_K90": {
        "size": 90,
        "role": "post_pilot_exploratory_conditional_subdomain",
        "contrasts": {
            ("heating_energy", "i021", f"code_{code}_vs_5")
            for code in (1, 2, 3, 4, 6, 7)
        },
        "route": "i020 == 2 (No); routed heating-energy item",
    },
}


def audit_registry(path: Path = REGISTER) -> dict[str, object]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    errors: list[str] = []
    required = {
        "hypothesis_id", "family_id", "family_size", "family_role", "wave",
        "exposure_concept_id", "exposure_field_candidate", "contrast_id",
        "phenotype_concept_id", "route_candidate", "analysis_status",
        "public_release_status", "prior_pilot_overlap", "multiplicity_scope_candidate",
    }
    if not rows:
        errors.append("registry is empty")
    missing_columns = sorted(required - set(rows[0])) if rows else sorted(required)
    if missing_columns:
        errors.append("missing columns: " + ", ".join(missing_columns))

    ids = [row.get("hypothesis_id", "") for row in rows]
    if any(not item for item in ids):
        errors.append("one or more hypothesis IDs are blank")
    duplicate_ids = sorted(key for key, n in Counter(ids).items() if key and n > 1)
    if duplicate_ids:
        errors.append(f"duplicate hypothesis IDs: {len(duplicate_ids)}")

    observed_families = {row.get("family_id", "") for row in rows}
    if observed_families != set(EXPECTED):
        errors.append(f"unexpected family set: {sorted(observed_families)}")

    phenotype_sets: dict[str, set[str]] = {}
    family_summary: dict[str, object] = {}
    for family_id, spec in EXPECTED.items():
        family_rows = [row for row in rows if row.get("family_id") == family_id]
        phenotypes = {row.get("phenotype_concept_id", "") for row in family_rows}
        phenotype_sets[family_id] = phenotypes
        contrasts = {
            (row.get("exposure_concept_id", ""),
             row.get("exposure_field_candidate", ""),
             row.get("contrast_id", ""))
            for row in family_rows
        }
        if len(phenotypes) != 15 or "" in phenotypes:
            errors.append(f"{family_id}: expected 15 nonblank phenotype concepts")
        if contrasts != spec["contrasts"]:
            errors.append(f"{family_id}: candidate contrast set differs from registered design")
        if len(family_rows) != spec["size"]:
            errors.append(f"{family_id}: expected {spec['size']} rows, found {len(family_rows)}")
        counts = Counter(
            (row.get("exposure_concept_id", ""), row.get("exposure_field_candidate", ""),
             row.get("contrast_id", ""), row.get("phenotype_concept_id", ""))
            for row in family_rows
        )
        if any(n != 1 for n in counts.values()) or len(counts) != spec["size"]:
            errors.append(f"{family_id}: contrast-by-phenotype cells are duplicated or incomplete")
        if any(row.get("family_role") != spec["role"] for row in family_rows):
            errors.append(f"{family_id}: family role label changed")
        if any(row.get("route_candidate") != spec["route"] for row in family_rows):
            errors.append(f"{family_id}: route label changed")
        if any(row.get("analysis_status") != "planned_not_approved" for row in family_rows):
            errors.append(f"{family_id}: planned hypotheses must remain unapproved")
        if any(row.get("public_release_status") != "not_approved" for row in family_rows):
            errors.append(f"{family_id}: public release must remain unapproved")
        family_summary[family_id] = {
            "planned_rows": len(family_rows),
            "distinct_contrasts": len(contrasts),
            "distinct_phenotypes": len(phenotypes),
            "role": spec["role"],
            "route": spec["route"],
            "all_not_approved": all(
                row.get("analysis_status") == "planned_not_approved"
                and row.get("public_release_status") == "not_approved"
                for row in family_rows
            ),
        }
    if phenotype_sets.get("wave1_household_environment_K150") != phenotype_sets.get("wave1_heating_route_K90"):
        errors.append("K150 and K90 do not use the same 15 phenotype concepts")

    return {
        "audit_type": "metadata_only_hypothesis_registry_structure",
        "participant_data_read": False,
        "registry_path": path.relative_to(ROOT).as_posix(),
        "total_planned_rows": len(rows),
        "families": family_summary,
        "status": "passed_structural_checks_only" if not errors else "failed",
        "model_approved": False,
        "association_results_created": False,
        "errors": errors,
    }


def main() -> None:
    report = audit_registry()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "passed_structural_checks_only":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
