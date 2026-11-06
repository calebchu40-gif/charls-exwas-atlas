#!/usr/bin/env python3
"""Solid fuel versus clean fuel: a harmonised 2011 blood-panel contrast.

The pilot treats each cooking-fuel code as its own exposure. This script asks the
policy-facing question directly: households burning coal, crop residue or wood
versus households using gas, LPG or electricity.

Design mirrors the pilot: bloodweight, communityID PSUs, no stratum, WR Taylor;
age/age^2, sex, education groups and urbanicity; glucose and triglycerides
restricted to the fasting subsample. Fifteen blood outcomes form one family, so
the BY correction is computed over K=15.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exwas_engine as engine  # noqa: E402
import run_wave1_pilot105_exploratory as pilot  # noqa: E402
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path  # noqa: E402

SOLID_CODES = (1.0, 6.0, 7.0)      # coal, crop residue/wood, other
CLEAN_CODES = (2.0, 4.0, 5.0)      # natural gas, LPG, electricity
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_solid_fuel_blood_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "solid_fuel_blood_v1.json"


def add_solid_fuel(frame: pl.DataFrame) -> pl.DataFrame:
    import pyreadstat
    table = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
    fuel, _ = pyreadstat.read_dta(str(table), usecols=["ID", "i022"], output_format="polars")
    fuel = fuel.with_columns(pl.col("i022").cast(pl.Float64, strict=False).alias("fuel_code"))
    code = pl.col("fuel_code")
    fuel = fuel.with_columns(
        pl.when(code.is_in(SOLID_CODES)).then(1.0)
          .when(code.is_in(CLEAN_CODES)).then(0.0)
          .otherwise(None).alias("solid_fuel"))
    return frame.join(fuel.select(["ID", "solid_fuel"]), on="ID", how="left")


def registry(fasting_only: bool) -> list[engine.VariableSpec]:
    exposure = engine.VariableSpec("solid_fuel_vs_clean", "E", "固体燃料 vs 清洁燃料",
                                   pilot.WAVE, "solid_fuel", "binary")
    concepts = pilot.FASTING_SENSITIVE if fasting_only else tuple(
        c for c in pilot.OUTCOMES if c not in pilot.FASTING_SENSITIVE)
    phenotypes = [engine.VariableSpec(c, "P", c, pilot.WAVE, f"out_{c}", "continuous",
                                      unit=pilot.OUTCOMES[c][1]) for c in concepts]
    return [exposure] + phenotypes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = add_solid_fuel(pilot.load_private_frame())
    design = engine.DesignSpec(
        weight="bloodweight", psu="communityID", strata=None,
        age_field="age_lower", age_min=45,
        covariate_sets={pilot.MODEL_ID: list(pilot.M1)},
        scale_outcome=True,
        variance_limitations="communityID clustering only; no official strata; WR Taylor")
    full = engine.scan(frame, registry(False), design, wave=pilot.WAVE,
                       models=[pilot.MODEL_ID], family_prefix="solid_fuel")
    fasting = frame.filter(pl.col("fasting_code") == 1.0)
    fast = engine.scan(fasting, registry(True), design, wave=pilot.WAVE,
                       models=[pilot.MODEL_ID], family_prefix="solid_fuel")
    rows = full + fast
    engine.assign_families(rows, "solid_fuel")

    out = require_private_path(PRIVATE_OUT)
    engine.write_rows(rows, out)

    public = []
    for row in sorted(rows, key=lambda item: float(item["p_value"] or 1)):
        if row["fit_status"] != "success":
            continue
        public.append({
            "phenotype_concept_id": row["phenotype_concept_id"],
            "estimate": float(row["estimate"]),
            "ci_lower": float(row["ci_lower"]),
            "ci_upper": float(row["ci_upper"]),
            "p": float(row["p_value"]),
            "q": float(row["q_value_by"]),
            "n": row["n_model"],
        })
    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "exposure": "solid fuel (coal / crop residue / wood / other) vs clean (gas / LPG / electricity)",
        "family_size": len(rows),
        "results": public,
        "summary": {
            "outcomes": len(public),
            "q_lt_05": sum(1 for item in public if item["q"] < 0.05),
            "positive": sum(1 for item in public if item["estimate"] > 0),
        },
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_solid_fuel_blood_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
