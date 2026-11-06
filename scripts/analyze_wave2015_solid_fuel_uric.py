#!/usr/bin/env python3
"""2015 replication of the solid-fuel / uric-acid contrast with full covariates.

The 2015 analytic table carries the blood panel, the household items, the
biomarker weight and interviewer-recorded sex, but no age, urbanicity or
education. Age is derived from the recorded birth year and the time-invariant
covariates are merged from the 2011 baseline after mapping the identifier.
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

TABLE = PRIVATE_ROOT / "derived_wave_tables" / "CHARLS_wave2015_person_analytic_with_official_blood.dta"
BASE2011 = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave2015_solid_fuel_uric_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "wave2015_solid_fuel_v1.json"


def main(argv: list[str] | None = None) -> int:
    import pyreadstat
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected wave tables")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected wave tables")

    frame, _ = pyreadstat.read_dta(
        str(TABLE), usecols=["ID", "i022", "bl_ua", "Biomarker_weight", "ba000_w2_3",
                            "ba002_1", "communityID"], output_format="polars")
    base, _ = pyreadstat.read_dta(
        str(BASE2011), usecols=["ID", "urban_nbs", "bd001"], output_format="polars")
    base = base.rename({"ID": "id11"})

    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    frame = frame.with_columns(pl.col("ID").cast(pl.String).alias("id_str"))
    frame = frame.with_columns(
        (pl.col("id_str").str.slice(0, 10) + pl.col("id_str").str.slice(11)).alias("id11"))
    frame = frame.join(base, on="id11", how="left")
    frame = frame.with_columns([
        pl.when(num("ba002_1").is_between(1900, 2000)).then(2015.0 - num("ba002_1"))
          .otherwise(None).alias("age"),
        pl.when(num("ba000_w2_3") == 2.0).then(1.0)
          .when(num("ba000_w2_3") == 1.0).then(0.0).otherwise(None).alias("female"),
        pl.when(num("urban_nbs") == 1.0).then(1.0)
          .when(num("urban_nbs") == 0.0).then(0.0).otherwise(None).alias("urban"),
        pl.when(num("i022").is_in([1.0, 6.0, 7.0])).then(1.0)
          .when(num("i022").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0)
          .otherwise(None).alias("solid"),
        num("bl_ua").alias("ua"),
        num("Biomarker_weight").alias("wgt"),
        num("bd001").alias("edu"),
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
    frame = frame.filter((pl.col("age") >= 45) & (pl.col("wgt") > 0) & (pl.col("ua") > 0))

    covariates = ["age_c", "age_c2", "female", "urban", "edu_2", "edu_3", "edu_4"]
    data = frame.select(["solid", "ua", "wgt", "communityID", *covariates]).drop_nulls()
    data = data.rename({"communityID": "psu", "wgt": "_w"})
    weights = data["_w"].to_numpy().astype(float)
    values = data["ua"].to_numpy().astype(float)
    mean = np.average(values, weights=weights)
    sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
    data = data.with_columns(((pl.col("ua") - mean) / sd).alias("y_std"))
    result = svy.Sample(data=data, design=svy.Design(psu="psu", wgt="_w", wr=True)) \
        .glm.fit(y="y_std", x=["solid"] + covariates, family="gaussian",
                 drop_nulls=True, alpha=0.05).to_polars()
    cell = {row["term"]: row for row in result.to_dicts()}["solid"]
    row = {
        "wave": "2015",
        "exposure": "solid fuel vs clean fuel",
        "outcome": "blood_uric_acid",
        "estimate": float(cell["estimate"]),
        "standard_error": float(cell["std_err"]),
        "ci_lower": float(cell["conf_low"]),
        "ci_upper": float(cell["conf_high"]),
        "p_value": float(cell["p_value"]),
        "n_model": data.height,
    }
    import csv
    out = require_private_path(PRIVATE_OUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    payload = {
        "schema_version": 1,
        "wave": "2015",
        "design": "age from recorded birth year; sex recorded in 2015; urbanicity and education from the 2011 baseline",
        "results": [row],
        "summary": {"estimate": row["estimate"], "p_value": row["p_value"], "n": row["n_model"]},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave2015_solid_fuel_uric_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
