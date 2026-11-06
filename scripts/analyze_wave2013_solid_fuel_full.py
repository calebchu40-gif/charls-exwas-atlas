#!/usr/bin/env python3
"""2013 anthropometry with the 2011 baseline covariates merged in.

Wave 2 has no education and only patchy urbanicity. Both are time-invariant, so
they are merged from the 2011 baseline after mapping the identifier. Comparing
this fit with the earlier covariate-poor one shows how much of the solid-fuel
anthropometry association was socioeconomic confounding.
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
BASE2011 = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave2013_solid_fuel_anthropometry_full_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "wave2013_solid_fuel_full_v1.json"


def main(argv: list[str] | None = None) -> int:
    import pyreadstat
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected wave tables")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected wave tables")

    table, _ = pyreadstat.read_dta(
        str(TABLE), usecols=["ID", "i022", "qi002", "ql002", "ba000_w2_3", "Biomarker_weight"],
        output_format="polars")
    ages, _ = pyreadstat.read_dta(str(AGES), usecols=["ID", "age_at_interview_lower"],
                                  output_format="polars")
    base, _ = pyreadstat.read_dta(str(BASE2011), usecols=["ID", "urban_nbs", "bd001"],
                                  output_format="polars")

    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    table = table.with_columns(pl.col("ID").cast(pl.String).alias("id_str"))
    table = table.with_columns(
        (pl.col("id_str").str.slice(0, 10) + pl.col("id_str").str.slice(11)).alias("id11"))
    base = base.rename({"ID": "id11"})
    table = table.join(base, on="id11", how="left").join(ages, on="ID", how="left")
    height = num("qi002")
    height = pl.when(height < 3.0).then(height * 100.0).otherwise(height)
    weight = num("ql002")
    bmi = pl.when((height >= 100) & (height <= 250) & (weight >= 20) & (weight <= 300)) \
        .then(weight / (height / 100.0) ** 2).otherwise(None)
    table = table.with_columns([
        pl.when(height.is_between(100, 250)).then(height).otherwise(None).alias("height"),
        pl.when(weight.is_between(20, 300)).then(weight).otherwise(None).alias("weight"),
        bmi.alias("bmi"),
        num("age_at_interview_lower").alias("age"),
        pl.when(num("ba000_w2_3") == 2.0).then(1.0)
          .when(num("ba000_w2_3") == 1.0).then(0.0).otherwise(None).alias("female"),
        pl.when(num("urban_nbs") == 1.0).then(1.0)
          .when(num("urban_nbs") == 0.0).then(0.0).otherwise(None).alias("urban"),
        num("bd001").alias("edu"),
        num("Biomarker_weight").alias("wgt"),
        pl.when(num("i022").is_in([1.0, 6.0, 7.0])).then(1.0)
          .when(num("i022").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0)
          .otherwise(None).alias("solid"),
    ]).with_columns([
        (pl.col("age") - 60).alias("age_c"),
        ((pl.col("age") - 60) ** 2).alias("age_c2"),
        pl.when(pl.col("edu").is_in([1.0, 2.0, 3.0])).then(0.0)
          .when(pl.col("edu").is_in([4.0, 5.0])).then(1.0)
          .when(pl.col("edu").is_in([6.0, 7.0, 8.0])).then(2.0)
          .when(pl.col("edu").is_in([9.0, 10.0, 11.0])).then(3.0)
          .otherwise(None).alias("edu_group"),
    ]).with_columns([
        (pl.col("edu_group") == 1).cast(pl.Float64).alias("edu_2"),
        (pl.col("edu_group") == 2).cast(pl.Float64).alias("edu_3"),
        (pl.col("edu_group") == 3).cast(pl.Float64).alias("edu_4"),
    ])
    table = table.with_columns(pl.col("ID").cast(pl.String).str.slice(0, 6).alias("psu"))
    table = table.filter((pl.col("age") >= 45) & (pl.col("wgt") > 0))

    covariates = ["age_c", "age_c2", "female", "urban", "edu_2", "edu_3", "edu_4"]
    rows = []
    for outcome in ("height", "weight", "bmi"):
        data = table.select(["solid", outcome, "wgt", "psu", *covariates]).drop_nulls()
        data = data.rename({"wgt": "_w"})
        if data.height < 200:
            continue
        weights = data["_w"].to_numpy().astype(float)
        values = data[outcome].to_numpy().astype(float)
        mean = np.average(values, weights=weights)
        sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
        data = data.with_columns(((pl.col(outcome) - mean) / sd).alias("y_std"))
        result = svy.Sample(data=data, design=svy.Design(psu="psu", wgt="_w", wr=True)) \
            .glm.fit(y="y_std", x=["solid"] + covariates, family="gaussian",
                     drop_nulls=True, alpha=0.05).to_polars()
        cell = {row["term"]: row for row in result.to_dicts()}["solid"]
        rows.append({
            "outcome": outcome,
            "estimate": float(cell["estimate"]),
            "standard_error": float(cell["std_err"]),
            "ci_lower": float(cell["conf_low"]),
            "ci_upper": float(cell["conf_high"]),
            "p_value": float(cell["p_value"]),
            "n_model": data.height,
        })

    import csv
    out = require_private_path(PRIVATE_OUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "schema_version": 1,
        "wave": "2013",
        "design": "urbanicity and education merged from the 2011 baseline",
        "results": rows,
        "comparison": {"note": "earlier fit without education: height -0.138, weight -0.196, BMI -0.158"},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave2013_solid_fuel_full_v1.json").write_text(
        json.dumps({"models": len(rows)}, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({row["outcome"]: round(row["estimate"], 3) for row in rows}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
