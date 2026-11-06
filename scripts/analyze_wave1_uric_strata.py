#!/usr/bin/env python3
"""Stratified robustness for the solid-fuel / uric-acid association.

Two strata sets, chosen because they are the main competing explanations:

* body-mass index (<24, 24–27.9, >=28), from measured height and weight;
* kidney function, CKD-EPI eGFR (<60 vs >=60).

Within each stratum the solid-fuel contrast is refitted with the pilot
covariates. If the association persists across strata it is less likely to be an
artefact of adiposity or impaired renal clearance alone.
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

PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_solid_fuel_uric_strata_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "uric_strata_v1.json"


def add_measures(frame: pl.DataFrame) -> pl.DataFrame:
    import pyreadstat
    table = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
    raw, _ = pyreadstat.read_dta(str(table), usecols=["ID", "qi002", "ql002", "newcrea", "i022"],
                                  output_format="polars")
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    height = num("qi002")
    height = pl.when(height < 3.0).then(height * 100.0).otherwise(height)
    weight = num("ql002")
    bmi = pl.when((height >= 100) & (height <= 250) & (weight >= 20) & (weight <= 300)) \
        .then(weight / (height / 100.0) ** 2).otherwise(None)
    raw = raw.with_columns([bmi.alias("bmi"),
                            num("newcrea").alias("crea"),
                            num("i022").alias("fuel")])
    raw = raw.with_columns(
        pl.when(pl.col("fuel").is_in([1.0, 6.0, 7.0])).then(1.0)
          .when(pl.col("fuel").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0)
          .otherwise(None).alias("solid"))
    return frame.join(raw.select(["ID", "bmi", "crea", "solid"]), on="ID", how="left")


def egfr(crea: pl.Expr, age: pl.Expr, female: pl.Expr) -> pl.Expr:
    kappa = pl.when(female == 1.0).then(0.7).otherwise(0.9)
    alpha = pl.when(female == 1.0).then(-0.329).otherwise(-0.411)
    ratio = crea / kappa
    value = (141.0
             * pl.min_horizontal(ratio, pl.lit(1.0)).pow(alpha)
             * pl.max_horizontal(ratio, pl.lit(1.0)).pow(-1.209)
             * (0.993 ** age)
             * pl.when(female == 1.0).then(1.018).otherwise(1.0))
    return pl.when((crea > 0) & (crea < 20)).then(value.clip(1.0, 200.0)).otherwise(None)


def fit(frame: pl.DataFrame, label: str, group: str) -> dict | None:
    data = frame.select(["solid", "out_blood_uric_acid", "bloodweight", "communityID",
                         "age_lower", *pilot.M1]).drop_nulls()
    data = data.filter((pl.col("age_lower") >= 45) & (pl.col("bloodweight") > 0))
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
            .glm.fit(y="y_std", x=["solid"] + pilot.M1, family="gaussian",
                     drop_nulls=True, alpha=0.05).to_polars()
    except Exception:
        return None
    cell = {row["term"]: row for row in result.to_dicts()}.get("solid")
    if not cell:
        return None
    return {
        "stratum_set": group,
        "stratum": label,
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

    frame = add_measures(pilot.load_private_frame())
    frame = frame.with_columns([egfr(pl.col("crea"), pl.col("age_mid"), pl.col("female")).alias("egfr")])
    rows: list[dict] = []
    for label, condition in (
        ("BMI <24", (pl.col("bmi") < 24)),
        ("BMI 24–27.9", (pl.col("bmi") >= 24) & (pl.col("bmi") < 28)),
        ("BMI ≥28", (pl.col("bmi") >= 28)),
    ):
        subset = frame.filter(condition)
        result = fit(subset, label, "BMI")
        if result:
            rows.append(result)
    for label, condition in (("eGFR <60", pl.col("egfr") < 60),
                             ("eGFR ≥60", pl.col("egfr") >= 60)):
        subset = frame.filter(condition)
        result = fit(subset, label, "eGFR")
        if result:
            rows.append(result)

    import csv
    out = require_private_path(PRIVATE_OUT)
    fields = ["stratum_set", "stratum", "estimate", "standard_error", "ci_lower", "ci_upper",
              "p_value", "n_model"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "outcome": "blood_uric_acid",
        "exposure": "solid fuel vs clean fuel",
        "results": rows,
        "summary": {"strata": len(rows),
                    "p_lt_05": sum(1 for row in rows if row["p_value"] < 0.05),
                    "sign_consistent": len({1 if row["estimate"] > 0 else -1 for row in rows}) == 1},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_solid_fuel_uric_strata_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
