"""Aggregate-only audit of the protected CHARLS 2011 pilot design frame.

This audit reads respondent records locally but emits aggregate counts only.
Its output must stay under the protected private root. It does not authenticate
the release, certify national representativeness, or estimate associations.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl
import pyreadstat

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path


DATA = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2011_person_analytic.dta"
AGE = PRIVATE_ROOT / "age_candidates" / "age_candidate_2011.dta"
PSU_MAP = PRIVATE_ROOT / "raw_extract_2011_community" / "psu.dta"
DEFAULT_REPORT = QA_OUTPUT_DIR / "charls_2011_pilot_design_frame_aggregate.json"
# These are different documented quantities. The National Baseline and Blood
# guides report 17,708 interviews/target blood sample, while the official
# Codebook lists 17,705 observations for the person ID field and 17,708 for
# individual-weight fields. Do not collapse these into one expected table size.
OFFICIAL_BLOOD_TARGET_N = 17_708
OFFICIAL_CODEBOOK_PERSON_ID_OBS = 17_705
OFFICIAL_CODEBOOK_INDIVIDUAL_WEIGHT_OBS = 17_708


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError(f"Output must remain inside protected storage: {resolved}")
    return resolved


def read_table(path: Path, columns: list[str]) -> pl.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required protected input is missing: {path.name}")
    frame, _ = pyreadstat.read_dta(str(path), usecols=columns, output_format="polars")
    return frame


def count(frame: pl.DataFrame, expression: pl.Expr) -> int:
    return int(frame.select(expression.sum()).item() or 0)


def audit(data_path: Path = DATA, age_path: Path = AGE,
          psu_path: Path = PSU_MAP) -> dict[str, Any]:
    person = read_table(data_path, ["ID", "communityID", "bloodweight", "i017"])
    age = read_table(age_path, ["ID", "age_years_candidate"])
    psu = read_table(psu_path, ["communityID"])

    person_ids_ok = (person["ID"].null_count() == 0
                     and person["ID"].n_unique() == person.height)
    age_ids_ok = (age["ID"].null_count() == 0
                  and age["ID"].n_unique() == age.height)
    joined = person.join(age, on="ID", how="left", validate="1:1")
    psu_ids_ok = (psu["communityID"].null_count() == 0
                  and psu["communityID"].n_unique() == psu.height)
    unmatched_psu = joined.join(
        psu.select("communityID").unique(), on="communityID", how="anti"
    ).height

    age_value = pl.col("age_years_candidate").cast(pl.Float64, strict=False)
    weight = pl.col("bloodweight").cast(pl.Float64, strict=False)
    exposure = pl.col("i017").cast(pl.Float64, strict=False)
    age_missing = age_value.is_null() | ~age_value.is_finite()
    weight_valid = weight.is_not_null() & weight.is_finite() & (weight > 0)
    output = joined.with_columns(
        age_value.alias("_age"), weight.alias("_weight"), exposure.alias("_exposure")
    )
    domain45 = pl.col("_age") >= 45
    blood_frame_n = int(output.height)
    result: dict[str, Any] = {
        "wave": "2011 baseline",
        "audit_utc": datetime.now(timezone.utc).isoformat(),
        "audit_type": "aggregate-only protected design-frame preflight",
        "respondent_level_rows_written": False,
        "associations_estimated": False,
        "official_release_authenticated": False,
        "published_denominator_references": {
            "national_baseline_interviews": {
                "observations": OFFICIAL_BLOOD_TARGET_N,
                "source": "CHARLS National Baseline User Guide",
            },
            "blood_collection_target": {
                "observations": OFFICIAL_BLOOD_TARGET_N,
                "source": "CHARLS 2011 Blood Data User Guide, Sampling and Sample Weights",
            },
            "codebook_person_id_field": {
                "observations": OFFICIAL_CODEBOOK_PERSON_ID_OBS,
                "source": "CHARLS 2011 Codebook, Demographic Background: ID OBS",
            },
            "codebook_individual_weight_fields": {
                "observations": OFFICIAL_CODEBOOK_INDIVIDUAL_WEIGHT_OBS,
                "source": "CHARLS 2011 Codebook, Weight: ind weight ad2 OBS",
            },
        },
        "official_target_source": "https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf",
        "local_prepared_frame_n": blood_frame_n,
        "difference_from_blood_guide_target_n": blood_frame_n - OFFICIAL_BLOOD_TARGET_N,
        "difference_from_codebook_person_id_obs_n": blood_frame_n - OFFICIAL_CODEBOOK_PERSON_ID_OBS,
        "person_id_unique_complete": bool(person_ids_ok),
        "age_candidate_id_unique_complete": bool(age_ids_ok),
        "age_candidate_rows": int(age.height),
        "age_domain": {
            "age_missing_or_nonfinite_n": count(output, age_missing),
            "age_under_45_n": count(output, pl.col("_age").is_not_null() & (pl.col("_age") < 45)),
            "age_45_plus_n": count(output, domain45),
            "age_45_plus_with_positive_bloodweight_n": count(output, domain45 & weight_valid),
            "age_45_plus_with_valid_water_code_n": count(
                output, domain45 & pl.col("_exposure").is_in([1.0, 2.0])
            ),
        },
        "bloodweight": {
            "positive_finite_n": count(output, weight_valid),
            "missing_or_nonfinite_n": count(
                output, weight.is_null() | ~weight.is_finite()
            ),
            "nonpositive_n": count(output, weight.is_finite() & (weight <= 0)),
        },
        "psu": {
            "map_rows": int(psu.height),
            "map_key_unique_complete": bool(psu_ids_ok),
            "respondent_rows_unmatched_to_map_n": int(unmatched_psu),
            "unique_respondent_psu_count": int(joined["communityID"].n_unique()),
            "variance_stratum_status": "unresolved; do not infer from geography/context fields",
        },
        "gates": {
            # A count comparison alone is not a reconciliation. This script
            # reads a legacy derived frame, not the authorized source files
            # needed to explain the published file-specific counts.
            "frame_denominator_reconciled": False,
            "age_domain_source_verified": False,
            "bloodweight_source_and_eligibility_verified": False,
            "final_psu_and_variance_design_verified": False,
            "formal_model_gate": "not_passed",
        },
        "limitations": [
            "Official documentation reports different file/field denominators: 17,708 interviews and blood-target members, 17,705 Codebook observations for person ID, and 17,708 observations for individual-weight fields.",
            "Comparisons between the local prepared table and published counts are diagnostics only; the derived table is not release-authenticated and this aggregate audit cannot reconcile source records or missing keys.",
            "Reconcile person, weight, PSU, and blood files by documented IDs and eligibility using the authorized release before analysis.",
            "Age candidate, bloodweight, and PSU source identity/coverage remain unverified against the authorized release.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--age", type=Path, default=AGE)
    parser.add_argument("--psu-map", type=Path, default=PSU_MAP)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    result = audit(args.data, args.age, args.psu_map)
    output = private_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"prepared rows: {result['local_prepared_frame_n']}")
    print(f"difference from Blood Guide target (diagnostic only): {result['difference_from_blood_guide_target_n']}")
    print(f"difference from Codebook person-ID observations (diagnostic only): {result['difference_from_codebook_person_id_obs_n']}")
    print(f"age 45+ domain rows: {result['age_domain']['age_45_plus_n']}")
    print(f"positive bloodweight rows: {result['bloodweight']['positive_finite_n']}")
    print(f"respondent PSU rows unmatched: {result['psu']['respondent_rows_unmatched_to_map_n']}")
    print(f"formal model gate: {result['gates']['formal_model_gate']}")
    print(f"aggregate report saved privately: {output}")


if __name__ == "__main__":
    main()
