#!/usr/bin/env python3
"""Turn the exploratory pilot-105 result table into a public browser family.

The public site only serves disclosure-reviewed aggregate rows. This script
maps the private scan output onto the exact row shape used by
``association_results_v1.json`` and writes a single-family JSON fragment that
can be merged into the published payload.

The user (PI) authorised publication of these exploratory aggregates on
2026-11-01. Every row keeps ``disclosure_status = approved_public_aggregate``;
the family id and model id are prefixed so the site can label the block as
exploratory rather than mixing it with the registered K=845 family.

Run only on the protected server:

    python scripts/build_wave1_pilot105_public_family.py --run
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from project_paths import PRIVATE_ROOT, require_private_path  # noqa: E402

RESULTS = PRIVATE_ROOT / "results" / "wave1_pilot105_main_v1.csv"
OUTPUT = PRIVATE_ROOT / "results" / "wave1_pilot105_public_family_v1.json"

FAMILY_ID = "charls_2011_household_environment_pilot105_v1"
MODEL_ID = "Pilot105_M1_age_sex_urban_education"
DATA_RELEASE = "CHARLS 2011 Wave 1 baseline; household-environment pilot (exploratory)"
TARGET = ("Observed Wave 1 Blood-file respondents with finite positive bloodweight and lower-bound "
          "age >= 45; complete cases for exposures, outcomes and covariates; not a causal estimand.")
VARIANCE = ("communityID PSUs, no official stratum, with-replacement Taylor approximation; "
            "official CHARLS strata and replicate weights are not released")
COMPARABILITY = "wave_specific_exploratory_pi_delegated_not_independently_reviewed"

FIELDS = (
    "analysis_id", "data_release", "wave", "exposure_concept_id", "exposure_variable",
    "phenotype_concept_id", "phenotype_variable", "target_population", "model_id",
    "estimate_type", "contrast", "estimate", "standard_error", "ci_lower", "ci_upper",
    "p_value", "q_value_by", "p_bonferroni", "n_model", "fit_status",
    "variance_design", "comparability_grade", "disclosure_status",
)


def number(value: str):
    text = (value or "").strip()
    if text == "":
        return ""
    try:
        return float(text)
    except ValueError:
        return ""


def build(rows: list[dict[str, str]]) -> dict:
    public = []
    for row in rows:
        if row.get("fit_status") != "success":
            continue
        public.append({
            "analysis_id": "w1p105-" + row["analysis_id"],
            "data_release": DATA_RELEASE,
            "wave": row["wave"],
            "exposure_concept_id": row["exposure_concept_id"],
            "exposure_variable": row["exposure_variable"],
            "phenotype_concept_id": row["phenotype_concept_id"],
            "phenotype_variable": row["phenotype_variable"],
            "target_population": TARGET,
            "model_id": MODEL_ID,
            "estimate_type": "standardized_linear_beta",
            "contrast": row.get("exposure_contrast", ""),
            "estimate": number(row.get("estimate")),
            "standard_error": number(row.get("standard_error")),
            "ci_lower": number(row.get("ci_lower")),
            "ci_upper": number(row.get("ci_upper")),
            "p_value": number(row.get("p_value")),
            "q_value_by": number(row.get("q_value_by")),
            "p_bonferroni": number(row.get("p_bonferroni")),
            "n_model": int(float(row["n_model"])) if row.get("n_model") else "",
            "fit_status": "success",
            "variance_design": VARIANCE,
            "comparability_grade": COMPARABILITY,
            "disclosure_status": "approved_public_aggregate",
        })
    return {"family_id": FAMILY_ID, "family_size": len(public), "rows": public}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected result table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected result table")
    with RESULTS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    family = build(rows)
    out = require_private_path(OUTPUT)
    if not out.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"output must stay under {PRIVATE_ROOT}")
    out.write_text(json.dumps(family, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"family_id": family["family_id"], "rows": family["family_size"],
                      "output": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
