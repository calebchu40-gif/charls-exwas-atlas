#!/usr/bin/env python3
"""Cooking-fuel gradient: ordinal trend test across fuel cleanliness ranks.

Ranks the main cooking fuel from cleanest to dirtiest (electric 0, gas/LPG 1,
marsh gas 2, coal/wood/other 3) and fits the fifteen blood outcomes against the
rank. A monotone gradient supports a dose-response reading of the separate
fuel contrasts; a flat pattern does not.

Design matches the pilot: bloodweight, communityID PSUs, no stratum, WR Taylor,
age/sex/education/urbanicity, fasting restriction for glucose and triglycerides.
One family of fifteen outcomes, BY correction over K=15.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exwas_engine as engine  # noqa: E402
import run_wave1_pilot105_exploratory as pilot  # noqa: E402
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path  # noqa: E402

RANK = {5.0: 0.0, 2.0: 1.0, 4.0: 1.0, 3.0: 2.0, 1.0: 3.0, 6.0: 3.0, 7.0: 3.0}
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_fuel_gradient_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "fuel_gradient_v1.json"


def add_rank(frame: pl.DataFrame) -> pl.DataFrame:
    import pyreadstat
    fuel, _ = pyreadstat.read_dta(str(WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"),
                                  usecols=["ID", "i022"], output_format="polars")
    fuel = fuel.with_columns(pl.col("i022").cast(pl.Float64, strict=False).alias("code"))
    ranked = pl.when(pl.col("code") == 5.0).then(0.0) \
        .when(pl.col("code").is_in([2.0, 4.0])).then(1.0) \
        .when(pl.col("code") == 3.0).then(2.0) \
        .when(pl.col("code").is_in([1.0, 6.0, 7.0])).then(3.0) \
        .otherwise(None)
    fuel = fuel.with_columns(ranked.alias("fuel_rank"))
    return frame.join(fuel.select(["ID", "fuel_rank"]), on="ID", how="left")


def registry(fasting_only: bool) -> list[engine.VariableSpec]:
    exposure = engine.VariableSpec("cooking_fuel_rank", "E", "炊事燃料清洁度（0=电 → 3=煤/木）",
                                   pilot.WAVE, "fuel_rank", "continuous")
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

    frame = add_rank(pilot.load_private_frame())
    design = engine.DesignSpec(
        weight="bloodweight", psu="communityID", strata=None,
        age_field="age_lower", age_min=45,
        covariate_sets={pilot.MODEL_ID: list(pilot.M1)},
        scale_outcome=True,
        variance_limitations="communityID clustering only; no official strata; WR Taylor")
    full = engine.scan(frame, registry(False), design, wave=pilot.WAVE,
                       models=[pilot.MODEL_ID], family_prefix="fuel_gradient")
    fasting = frame.filter(pl.col("fasting_code") == 1.0)
    fast = engine.scan(fasting, registry(True), design, wave=pilot.WAVE,
                       models=[pilot.MODEL_ID], family_prefix="fuel_gradient")
    rows = full + fast
    engine.assign_families(rows, "fuel_gradient")

    out = require_private_path(PRIVATE_OUT)
    engine.write_rows(rows, out)

    results = []
    for row in sorted(rows, key=lambda item: float(item["p_value"] or 1)):
        if row["fit_status"] != "success":
            continue
        results.append({
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
        "exposure": "cooking fuel rank 0 electric, 1 gas/LPG, 2 marsh gas, 3 coal/wood/other",
        "family_size": len(rows),
        "results": results,
        "summary": {
            "outcomes": len(results),
            "q_lt_05": sum(1 for item in results if item["q"] < 0.05),
            "positive": sum(1 for item in results if item["estimate"] > 0),
        },
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_fuel_gradient_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
