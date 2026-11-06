#!/usr/bin/env python3
"""Exploratory CHARLS 2011 health index and its household-exposure associations.

Five components, each oriented so that higher is healthier:

* systolic blood pressure (mean of the three readings, inverted);
* body mass index (valid 10-60, inverted);
* serial-7 score (number of correct subtractions from 100 down to 65);
* self-rated health (``da001``, 1=excellent .. 5=poor, inverted);
* self-rated memory (``dc004``, same direction, inverted).

Each component is z-scored with survey weights inside the analysis sample, the
index is the mean of the available z-scores (at least three required), and the
result is mapped to 0-100 as 50 + 10 z, clipped. The index is then regressed on
the seven household exposures and the pilot covariates.

Exploratory only: the weighting of components is a documented convention, not a
validated instrument.
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

PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_health_index_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "health_index_v1.json"
TERMS = ["water_yes", "fuel_coal", "fuel_natural_gas", "fuel_marsh_gas",
         "fuel_LPG", "fuel_crop_residue_or_wood", "fuel_other"]
CORRECT = (93.0, 86.0, 79.0, 72.0, 65.0)


def build_index() -> pl.DataFrame:
    import pyreadstat
    table = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
    columns = ["ID", "bloodweight", "qa003", "qa007", "qa011", "qi002", "ql002",
               "dc019", "dc020", "dc021", "dc022", "dc023", "da001", "dc004"]
    raw, _ = pyreadstat.read_dta(str(table), usecols=columns, output_format="polars")
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    systolic = (num("qa003") + num("qa007") + num("qa011")) / 3.0
    height = num("qi002")
    height = pl.when(height < 3.0).then(height * 100.0).otherwise(height)
    weight = num("ql002")
    bmi = pl.when((height >= 100) & (height <= 250) & (weight >= 20) & (weight <= 300)) \
        .then(weight / (height / 100.0) ** 2).otherwise(None)
    serial = sum((num(name) == value).cast(pl.Float64) for name, value in
                 zip(("dc019", "dc020", "dc021", "dc022", "dc023"), CORRECT))
    frame = raw.with_columns([
        pl.when(systolic.is_between(60, 260)).then(-systolic).otherwise(None).alias("c_sbp"),
        pl.when(bmi.is_between(10, 60)).then(-bmi).otherwise(None).alias("c_bmi"),
        serial.alias("c_serial7"),
        pl.when(num("da001").is_between(1, 5)).then(6.0 - num("da001")).otherwise(None).alias("c_srh"),
        pl.when(num("dc004").is_between(1, 5)).then(6.0 - num("dc004")).otherwise(None).alias("c_memory"),
    ])
    return frame


def zscore(series: pl.Series, weights: pl.Series) -> pl.Series:
    values = series.to_numpy().astype(float)
    w = weights.to_numpy().astype(float)
    mask = np.isfinite(values) & np.isfinite(w) & (w > 0)
    if mask.sum() < 100:
        return pl.Series([None] * len(series))
    mean = np.average(values[mask], weights=w[mask])
    sd = math.sqrt(np.average((values[mask] - mean) ** 2, weights=w[mask]))
    out = np.full(len(values), np.nan)
    out[mask] = (values[mask] - mean) / sd if sd > 0 else np.nan
    return pl.Series(out).fill_nan(None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = build_index()
    weight = frame["bloodweight"].cast(pl.Float64, strict=False)
    components = ["c_sbp", "c_bmi", "c_serial7", "c_srh", "c_memory"]
    for component in components:
        frame = frame.with_columns(zscore(frame[component], weight).alias(f"z_{component}"))
    zcols = [f"z_{component}" for component in components]
    frame = frame.with_columns(
        pl.concat_list([pl.col(c) for c in zcols]).list.drop_nulls().alias("_zv"))
    frame = frame.with_columns([
        pl.col("_zv").list.len().alias("n_components"),
        pl.col("_zv").list.mean().alias("_z"),
    ])
    frame = frame.with_columns(
        (50.0 + 10.0 * pl.col("_z")).clip(0.0, 100.0).alias("health_index"))
    frame = frame.filter(pl.col("n_components") >= 3)

    design_frame = pilot.load_private_frame().join(
        frame.select(["ID", "health_index", "n_components"]), on="ID", how="inner")
    design_frame = design_frame.filter(
        (pl.col("age_lower") >= 45) & (pl.col("bloodweight") > 0)
        & pl.col("health_index").is_not_null())
    for term in TERMS + pilot.M1:
        design_frame = design_frame.filter(pl.col(term).is_not_null())

    weights = design_frame["bloodweight"].to_numpy().astype(float)
    values = design_frame["health_index"].to_numpy().astype(float)
    mean = np.average(values, weights=weights)
    sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
    design_frame = design_frame.with_columns([
        ((pl.col("health_index") - mean) / sd).alias("y_std"),
        pl.col("bloodweight").alias("_w"),
        pl.col("communityID").cast(pl.String).alias("_psu"),
    ])
    result = svy.Sample(
        data=design_frame,
        design=svy.Design(psu="_psu", wgt="_w", wr=True),
    ).glm.fit(y="y_std", x=TERMS + pilot.M1, family="gaussian",
              where=pl.col("age_lower") >= 45, drop_nulls=True, alpha=0.05).to_polars()
    table = {row["term"]: row for row in result.to_dicts()}
    rows = []
    for term in TERMS:
        cell = table.get(term)
        if not cell:
            continue
        rows.append({
            "term": term,
            "estimate": float(cell["estimate"]),
            "standard_error": float(cell["std_err"]),
            "ci_lower": float(cell["conf_low"]),
            "ci_upper": float(cell["conf_high"]),
            "p": float(cell["p_value"]),
        })
    import csv
    out = require_private_path(PRIVATE_OUT)
    fields = ["term", "estimate", "standard_error", "ci_lower", "ci_upper", "p"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})

    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "components": ["systolic BP", "BMI", "serial-7", "self-rated health", "self-rated memory"],
        "index": {"mean": mean, "sd": sd, "n": int(design_frame.height)},
        "associations": rows,
        "summary": {"n": int(design_frame.height),
                    "terms": len(rows),
                    "p_lt_05": sum(1 for row in rows if row["p"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_health_index_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
