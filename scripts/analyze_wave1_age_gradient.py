#!/usr/bin/env python3
"""Age gradient of the fuel-uric-acid association (2011).

Fits the coal-vs-electric, wood-vs-electric and solid-vs-clean contrasts within
four baseline age bands, keeping the pilot covariates inside each band. The aim
is to see whether the association is concentrated in a particular age group.
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

BANDS = [(45, 54), (55, 64), (65, 74), (75, 200)]
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_fuel_uric_age_gradient_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "age_gradient_v1.json"


def add_exposures(frame: pl.DataFrame) -> pl.DataFrame:
    import pyreadstat
    fuel, _ = pyreadstat.read_dta(str(WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"),
                                  usecols=["ID", "i022"], output_format="polars")
    fuel = fuel.with_columns(pl.col("i022").cast(pl.Float64, strict=False).alias("code"))
    fuel = fuel.with_columns([
        pl.when(pl.col("code") == 1.0).then(1.0)
          .when(pl.col("code").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0).otherwise(None).alias("coal_vs_clean"),
        pl.when(pl.col("code") == 6.0).then(1.0)
          .when(pl.col("code").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0).otherwise(None).alias("wood_vs_clean"),
        pl.when(pl.col("code").is_in([1.0, 6.0, 7.0])).then(1.0)
          .when(pl.col("code").is_in([2.0, 3.0, 4.0, 5.0])).then(0.0).otherwise(None).alias("solid_vs_clean"),
    ])
    return frame.join(fuel.select(["ID", "coal_vs_clean", "wood_vs_clean", "solid_vs_clean"]),
                      on="ID", how="left")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = add_exposures(pilot.load_private_frame())
    rows = []
    for low, high in BANDS:
        band = frame.filter((pl.col("age_mid") >= low) & (pl.col("age_mid") <= high))
        for term in ("coal_vs_clean", "wood_vs_clean", "solid_vs_clean"):
            data = band.select([term, "out_blood_uric_acid", "bloodweight", "communityID",
                                "age_lower", *pilot.M1]).drop_nulls()
            data = data.filter((pl.col("age_lower") >= 45) & (pl.col("bloodweight") > 0))
            if data.height < 200:
                continue
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
            except Exception as error:
                rows.append({"band": f"{low}-{high if high < 200 else '+'}", "term": term,
                             "fit_status": f"error: {error}"[:120]})
                continue
            cell = {row["term"]: row for row in result.to_dicts()}.get(term)
            if not cell:
                continue
            rows.append({
                "band": f"{low}–{high if high < 200 else '+'}",
                "term": term,
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
    fields = ["band", "term", "estimate", "standard_error", "ci_lower", "ci_upper",
              "p_value", "n_model", "fit_status"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})
    ok = [row for row in rows if row.get("fit_status") == "success"]
    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "outcome": "blood_uric_acid",
        "bands": [row["band"] for row in ok],
        "results": ok,
        "summary": {"models": len(ok), "p_lt_05": sum(1 for row in ok if row["p_value"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_fuel_uric_age_gradient_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
