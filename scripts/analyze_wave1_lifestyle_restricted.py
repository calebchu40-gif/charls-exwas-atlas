#!/usr/bin/env python3
"""Lifestyle-restricted sensitivity for the fuel-uric-acid association.

Coal, wood and solid fuel are strongly patterned by rurality and socioeconomic
position, and smoking and drinking travel with them. Restricting to respondents
who never smoked and did not drink in the past year removes part of that
lifestyle confounding; if the association survives, it is less likely to be an
artefact of smoking or alcohol alone.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import svy  # noqa: E402
import run_wave1_pilot105_exploratory as pilot  # noqa: E402
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path  # noqa: E402

PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_fuel_uric_lifestyle_restricted_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "lifestyle_restricted_v1.json"


def add_exposures(frame: pl.DataFrame) -> pl.DataFrame:
    import pyreadstat
    fuel, _ = pyreadstat.read_dta(str(WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"),
                                  usecols=["ID", "i022", "da059", "da067"], output_format="polars")
    fuel = fuel.with_columns([
        pl.when(pl.col("da059").cast(pl.Float64, strict=False) == 1.0).then(1.0)
          .when(pl.col("da059").cast(pl.Float64, strict=False) == 2.0).then(0.0)
          .otherwise(None).alias("smoker"),
        pl.when(pl.col("da067").cast(pl.Float64, strict=False) == 1.0).then(1.0)
          .when(pl.col("da067").cast(pl.Float64, strict=False) == 3.0).then(0.0)
          .otherwise(None).alias("drinker"),
    ])
    fuel = fuel.with_columns(pl.col("i022").cast(pl.Float64, strict=False).alias("code"))
    fuel = fuel.with_columns([
        pl.when(pl.col("code") == 1.0).then(1.0)
          .when(pl.col("code").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0).otherwise(None).alias("coal"),
        pl.when(pl.col("code") == 6.0).then(1.0)
          .when(pl.col("code").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0).otherwise(None).alias("wood"),
        pl.when(pl.col("code").is_in([1.0, 6.0, 7.0])).then(1.0)
          .when(pl.col("code").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0).otherwise(None).alias("solid"),
    ])
    return frame.join(fuel.select(["ID", "coal", "wood", "solid", "smoker", "drinker"]),
                      on="ID", how="left")


def fit(frame: pl.DataFrame, term: str) -> dict | None:
    data = frame.select([term, "out_blood_uric_acid", "bloodweight", "communityID",
                         "age_lower", "smoker", "drinker", *pilot.M1]).drop_nulls()
    data = data.filter((pl.col("age_lower") >= 45) & (pl.col("bloodweight") > 0)
                       & (pl.col("smoker") == 0.0) & (pl.col("drinker") == 0.0))
    if data.height < 300:
        return None
    weights = data["bloodweight"].to_numpy().astype(float)
    values = data["out_blood_uric_acid"].to_numpy().astype(float)
    mean = np.average(values, weights=weights)
    sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
    data = data.with_columns([
        ((pl.col("out_blood_uric_acid") - mean) / sd).alias("y_std"),
        pl.col("bloodweight").alias("_w"),
        pl.col("communityID").cast(pl.String).alias("_psu"),
    ])
    try:
        result = svy.Sample(data=data, design=svy.Design(psu="_psu", wgt="_w", wr=True)) \
            .glm.fit(y="y_std", x=[term] + pilot.M1, family="gaussian",
                     drop_nulls=True, alpha=0.05).to_polars()
    except Exception:
        return None
    cell = {row["term"]: row for row in result.to_dicts()}.get(term)
    if not cell:
        return None
    return {
        "term": term,
        "estimate": float(cell["estimate"]),
        "standard_error": float(cell["std_err"]),
        "ci_lower": float(cell["conf_low"]),
        "ci_upper": float(cell["conf_high"]),
        "p_value": float(cell["p_value"]),
        "n_model": data.height,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = add_exposures(pilot.load_private_frame())
    rows = [row for row in (fit(frame, term) for term in ("coal", "wood", "solid")) if row]
    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "restriction": "never smoker and no alcohol in the past year",
        "outcome": "blood_uric_acid",
        "results": rows,
        "summary": {"models": len(rows), "p_lt_05": sum(1 for row in rows if row["p_value"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_fuel_uric_lifestyle_restricted_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
