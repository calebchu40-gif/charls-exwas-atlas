#!/usr/bin/env python3
"""Household exposures and sleep in the 2011 wave.

Outcomes: usual nightly sleep hours (``da049``), short sleep (<6 h) and long
sleep (>9 h). Seven household exposures are entered one at a time with the pilot
covariates; linear models for hours, logistic for the two binary outcomes.
Twenty-one tests form one exploratory family.
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

EXPOSURES = ["water_yes", "fuel_coal", "fuel_natural_gas", "fuel_marsh_gas", "fuel_LPG",
             "fuel_crop_residue_or_wood", "fuel_other"]
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_sleep_exposures_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "sleep_v1.json"


def add_sleep(frame: pl.DataFrame) -> pl.DataFrame:
    import pyreadstat
    raw, _ = pyreadstat.read_dta(str(WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"),
                                 usecols=["ID", "da049"], output_format="polars")
    hours = pl.col("da049").cast(pl.Float64, strict=False)
    raw = raw.with_columns([
        pl.when(hours.is_between(0, 16)).then(hours).otherwise(None).alias("sleep_hours"),
        pl.when(hours.is_between(0, 16)).then((hours < 6).cast(pl.Float64)).otherwise(None).alias("short_sleep"),
        pl.when(hours.is_between(0, 16)).then((hours > 9).cast(pl.Float64)).otherwise(None).alias("long_sleep"),
    ])
    return frame.join(raw.select(["ID", "sleep_hours", "short_sleep", "long_sleep"]),
                      on="ID", how="left")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = add_sleep(pilot.load_private_frame())
    rows = []
    for outcome, family in (("sleep_hours", "gaussian"), ("short_sleep", "binomial"),
                            ("long_sleep", "binomial")):
        for exposure in EXPOSURES:
            data = frame.select([exposure, outcome, "bloodweight", "communityID", "age_lower",
                                 *pilot.M1]).drop_nulls()
            data = data.filter((pl.col("age_lower") >= 45) & (pl.col("bloodweight") > 0))
            if data.height < 500:
                continue
            if family == "gaussian":
                weights = data["bloodweight"].to_numpy().astype(float)
                values = data[outcome].to_numpy().astype(float)
                mean = np.average(values, weights=weights)
                sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
                data = data.with_columns(((pl.col(outcome) - mean) / sd).alias("y"))
            else:
                data = data.with_columns(pl.col(outcome).alias("y"))
            data = data.with_columns([pl.col("bloodweight").alias("_w"),
                                      pl.col("communityID").cast(pl.String).alias("_psu")])
            try:
                result = svy.Sample(data=data, design=svy.Design(psu="_psu", wgt="_w", wr=True)) \
                    .glm.fit(y="y", x=[exposure] + pilot.M1, family=family,
                             drop_nulls=True, alpha=0.05).to_polars()
            except Exception:
                continue
            cell = {row["term"]: row for row in result.to_dicts()}.get(exposure)
            if not cell:
                continue
            estimate = float(cell["estimate"])
            low, high = float(cell["conf_low"]), float(cell["conf_high"])
            if family == "binomial":
                estimate, low, high = math.exp(estimate), math.exp(low), math.exp(high)
            rows.append({
                "outcome": outcome,
                "exposure": exposure,
                "measure": "OR" if family == "binomial" else "beta",
                "estimate": estimate,
                "ci_lower": low,
                "ci_upper": high,
                "p_value": float(cell["p_value"]),
                "n_model": data.height,
            })

    order = np.argsort([row["p_value"] for row in rows])
    n = len(rows)
    adjusted = np.empty(n)
    running = 1.0
    for rank in range(n - 1, -1, -1):
        index = order[rank]
        running = min(running, rows[index]["p_value"] * n / (rank + 1))
        adjusted[index] = running
    for row, q in zip(rows, adjusted):
        row["q_value_by"] = float(q)

    import csv
    out = require_private_path(PRIVATE_OUT)
    fields = ["outcome", "exposure", "measure", "estimate", "ci_lower", "ci_upper", "p_value",
              "q_value_by", "n_model"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "outcomes": {"sleep_hours": "usual nightly hours", "short_sleep": "<6 h",
                     "long_sleep": ">9 h"},
        "results": sorted(rows, key=lambda item: item["p_value"]),
        "summary": {"tests": len(rows), "q_lt_05": sum(1 for row in rows if row["q_value_by"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_sleep_exposures_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
