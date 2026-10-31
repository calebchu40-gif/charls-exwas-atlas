#!/usr/bin/env python3
"""Specification curve for the two pilot-105 associations that survived clustering.

The exploratory pilot left two uric-acid associations standing when the PSU was
coarsened from community to county: running water (positive) and coal versus
electricity (negative). This script asks whether those two survive a
NHANES-style ladder of nine model specifications, under both PSU definitions.

Specifications
--------------
M0 unadjusted; M1 age/age^2; M2 +sex; M3 +education; M4 +urban; M5 +smoking;
M6 +drinking; M7 +BMI (the full set).

Everything stays exploratory and PI-delegated: results are written to the
protected workspace only, and no coefficient is published from here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exwas_engine as engine  # noqa: E402
import run_wave1_pilot105_exploratory as drv  # noqa: E402
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path  # noqa: E402

MODELS = {
    "M0": [],
    "M1": ["age_c", "age_c2"],
    "M2": ["age_c", "age_c2", "female"],
    "M3": ["age_c", "age_c2", "female", "edu_2", "edu_3", "edu_4", "edu_5"],
    "M4": ["age_c", "age_c2", "female", "edu_2", "edu_3", "edu_4", "edu_5", "urban"],
    "M5": ["age_c", "age_c2", "female", "edu_2", "edu_3", "edu_4", "edu_5", "urban", "smoker"],
    "M6": ["age_c", "age_c2", "female", "edu_2", "edu_3", "edu_4", "edu_5", "urban", "smoker", "drinker"],
    "M7": ["age_c", "age_c2", "female", "edu_2", "edu_3", "edu_4", "edu_5", "urban", "smoker", "drinker", "bmi"],
}
EXPOSURES = ("running_water_at_residence", "cooking_fuel_coal")
PHENOTYPE = "blood_uric_acid"
OUTPUT = PRIVATE_ROOT / "results" / "wave1_uric_acid_specification_curve_v1.csv"


def load_frame() -> pl.DataFrame:
    import pyreadstat
    frame = drv.load_private_frame()
    prepared = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
    extra, _ = pyreadstat.read_dta(str(prepared), usecols=["ID", "qi002", "ql002", "da059", "da067"],
                                   output_format="polars")
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    height = num("qi002")
    height = pl.when(height < 3.0).then(height * 100.0).otherwise(height)
    weight = num("ql002")
    bmi = pl.when((height >= 100) & (height <= 250) & (weight >= 20) & (weight <= 300)) \
        .then(weight / (height / 100.0) ** 2).otherwise(None)
    extra = extra.with_columns([
        bmi.alias("bmi"),
        pl.when(num("da059") == 1).then(1.0).when(num("da059") == 2).then(0.0)
          .otherwise(None).alias("smoker"),
        pl.when(num("da067") == 1).then(1.0).when(num("da067") == 3).then(0.0)
          .otherwise(None).alias("drinker"),
    ])
    return frame.join(extra.select(["ID", "bmi", "smoker", "drinker"]), on="ID", how="left")


def registry() -> list[engine.VariableSpec]:
    exposures = [
        engine.VariableSpec("running_water_at_residence", "E", "Running water: Yes vs No",
                            drv.WAVE, "water_yes", "binary"),
        engine.VariableSpec("cooking_fuel_coal", "E", "coal vs electricity",
                            drv.WAVE, "fuel_coal", "binary"),
    ]
    phenotype = engine.VariableSpec(PHENOTYPE, "P", PHENOTYPE, drv.WAVE,
                                    f"out_{PHENOTYPE}", "continuous",
                                    unit=drv.OUTCOMES[PHENOTYPE][1])
    return exposures + [phenotype]


def design(psu: str) -> engine.DesignSpec:
    return engine.DesignSpec(
        weight="bloodweight", psu=psu, strata=None,
        age_field="age_lower", age_min=45,
        covariate_sets={name: list(covs) for name, covs in MODELS.items()},
        scale_outcome=True,
        variance_limitations=("released clustering only; no official CHARLS strata or replicate "
                              "weights; with-replacement Taylor approximation"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = load_frame()
    rows: list[dict] = []
    for psu in ("communityID", "psu_county"):
        result = engine.scan(frame, registry(), design(psu), wave=drv.WAVE,
                             models=list(MODELS), family_prefix=f"uric_curve_{psu}")
        for row in result:
            row["psu_definition"] = psu
            rows.append(row)
    out = require_private_path(OUTPUT)
    if not out.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"output must stay under {PRIVATE_ROOT}")
    engine.write_rows(rows, out)

    summary = []
    for row in rows:
        summary.append({
            "psu": row["psu_definition"], "exposure": row["exposure_concept_id"],
            "model": row["model_id"], "estimate": row["estimate"],
            "se": row["standard_error"], "p": row["p_value"],
            "n_model": row["n_model"], "status": row["fit_status"],
        })
    report = {"rows": len(rows), "output": str(out), "curve": summary}
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_uric_acid_specification_curve_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
