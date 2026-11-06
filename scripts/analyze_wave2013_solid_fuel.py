#!/usr/bin/env python3
"""2013 replication of the solid-fuel contrast on anthropometry.

The 2015 wave already reproduces the fuel-uric-acid direction. This extends the
same harmonised exposure to Wave 2, whose outcomes are measured anthropometry:
standing height, weight and derived BMI.

Covariates: age and age squared, interviewer-recorded gender (``ba000_w2_3``),
education groups and urbanicity. Weight: ``Biomarker_weight``.
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
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path  # noqa: E402

TABLE = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2013_person_analytic.dta"
AGES = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2013_age_interval_candidate.dta"
SOLID = (1, 6, 7)
CLEAN = (2, 4, 5)
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave2013_solid_fuel_anthropometry_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "wave2013_solid_fuel_v1.json"


def load_frame() -> pl.DataFrame:
    import pyreadstat
    table, _ = pyreadstat.read_dta(
        str(TABLE), usecols=["ID", "i022", "qi002", "ql002", "ba000_w2_3", "urban_nbs",
                             "bd001", "Biomarker_weight"], output_format="polars")
    ages, _ = pyreadstat.read_dta(str(AGES), usecols=["ID", "age_at_interview_lower"],
                                  output_format="polars")
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    height = num("qi002")
    height = pl.when(height < 3.0).then(height * 100.0).otherwise(height)
    weight = num("ql002")
    bmi = pl.when((height >= 100) & (height <= 250) & (weight >= 20) & (weight <= 300)) \
        .then(weight / (height / 100.0) ** 2).otherwise(None)
    frame = table.join(ages, on="ID", how="left").with_columns([
        pl.col("i022").cast(pl.Float64, strict=False).alias("fuel"),
        pl.when(height.is_between(100, 250)).then(height).otherwise(None).alias("height"),
        pl.when(weight.is_between(20, 300)).then(weight).otherwise(None).alias("weight"),
        bmi.alias("bmi"),
        num("age_at_interview_lower").alias("age"),
        pl.when(num("ba000_w2_3") == 2).then(1.0)
          .when(num("ba000_w2_3") == 1).then(0.0).otherwise(None).alias("female"),
        pl.when(num("urban_nbs") == 1).then(1.0)
          .when(num("urban_nbs") == 0).then(0.0).otherwise(None).alias("urban"),
        num("bd001").alias("edu"),
        num("Biomarker_weight").alias("wgt"),
    ]).with_columns([
        pl.when(pl.col("fuel").is_in([float(v) for v in SOLID])).then(1.0)
          .when(pl.col("fuel").is_in([float(v) for v in CLEAN])).then(0.0)
          .otherwise(None).alias("solid_fuel"),
    ])
    return frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 2 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 2 table")

    frame = load_frame().filter((pl.col("age") >= 45) & (pl.col("wgt") > 0))
    frame = frame.with_columns([
        (pl.col("age") - 60).alias("age_c"),
        ((pl.col("age") - 60) ** 2).alias("age_c2"),
        pl.when(pl.col("edu") <= 3).then(0.0)
          .when(pl.col("edu") == 4).then(1.0)
          .when(pl.col("edu") == 5).then(2.0)
          .when(pl.col("edu").is_in([6.0, 7.0])).then(3.0)
          .when(pl.col("edu").is_in([8.0, 9.0, 10.0, 11.0])).then(4.0)
          .otherwise(None).alias("edu_group"),
    ]).with_columns([
        (pl.col("edu_group") == 1).cast(pl.Float64).alias("edu_2"),
        (pl.col("edu_group") == 2).cast(pl.Float64).alias("edu_3"),
        (pl.col("edu_group") == 3).cast(pl.Float64).alias("edu_4"),
        (pl.col("edu_group") == 4).cast(pl.Float64).alias("edu_5"),
    ])

    covariates = ["age_c", "age_c2", "female", "urban"]  # 2013 education (bd001) is almost entirely missing
    rows = []
    for outcome in ("height", "weight", "bmi"):
        data = frame.with_columns(pl.col("ID").cast(pl.String).str.slice(0, 6).alias("psu")) \
            .select(["solid_fuel", outcome, "wgt", "psu", *covariates]).drop_nulls()
        data = data.rename({"wgt": "_w"})
        if data.height < 200:
            continue
        weights = data["_w"].to_numpy().astype(float)
        values = data[outcome].to_numpy().astype(float)
        mean = np.average(values, weights=weights)
        sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
        if not sd > 0:
            continue
        data = data.with_columns(((pl.col(outcome) - mean) / sd).alias("y_std"))
        try:
            result = svy.Sample(data=data, design=svy.Design(psu="psu", wgt="_w", wr=True)) \
                .glm.fit(y="y_std", x=["solid_fuel"] + covariates, family="gaussian",
                         drop_nulls=True, alpha=0.05).to_polars()
        except Exception as error:
            rows.append({"outcome": outcome, "fit_status": f"error: {error}"[:160]})
            continue
        cell = {row["term"]: row for row in result.to_dicts()}.get("solid_fuel")
        if not cell:
            rows.append({"outcome": outcome, "fit_status": "term_missing"})
            continue
        rows.append({
            "outcome": outcome,
            "estimate": float(cell["estimate"]),
            "standard_error": float(cell["std_err"]),
            "ci_lower": float(cell["conf_low"]),
            "ci_upper": float(cell["conf_high"]),
            "p_value": float(cell["p_value"]),
            "n_model": data.height,
            "fit_status": "success",
        })

    import csv
    out = require_private_path(PRIVATE_OUT)
    fields = ["outcome", "estimate", "standard_error", "ci_lower", "ci_upper", "p_value",
              "n_model", "fit_status"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})

    ok = [row for row in rows if row.get("fit_status") == "success"]
    payload = {
        "schema_version": 1,
        "wave": "2013",
        "exposure": "solid fuel (coal / crop residue / wood / other) vs clean (gas / LPG / electricity)",
        "outcomes": ["standing height", "weight", "BMI"],
        "results": ok,
        "summary": {"outcomes": len(ok), "p_lt_05": sum(1 for row in ok if row["p_value"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave2013_solid_fuel_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
