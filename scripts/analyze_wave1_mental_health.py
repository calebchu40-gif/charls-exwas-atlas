#!/usr/bin/env python3
"""Household exposures and mental health in the 2011 wave.

Three outcomes outside the blood panel:

* depressive symptoms, the ten CES-D items ``dc009``–``dc018`` scored 0–3 with the
  two positively worded items reversed, giving 0–30;
* serial-7 score, the number of correct subtractions from 100 down to 65 (0–5);
* self-rated memory (``dc004``), 1 poor to 5 excellent.

Seven household exposures, one at a time, with the pilot covariates. Twenty-one
tests form one exploratory family.
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
NEGATIVE_ITEMS = ["dc009", "dc010", "dc011", "dc012", "dc014", "dc015", "dc017", "dc018"]
POSITIVE_ITEMS = ["dc013", "dc016"]
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_mental_health_exposures_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "mental_health_v1.json"


def add_outcomes(frame: pl.DataFrame) -> pl.DataFrame:
    import pyreadstat
    table = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
    raw, _ = pyreadstat.read_dta(str(table), usecols=["ID", *NEGATIVE_ITEMS, *POSITIVE_ITEMS,
                                                     "dc019", "dc020", "dc021", "dc022", "dc023",
                                                     "dc004"], output_format="polars")
    num = lambda name: pl.col(name).cast(pl.Float64, strict=False)  # noqa: E731
    negative = sum(pl.when(num(item).is_between(1, 4)).then(num(item) - 1.0).otherwise(None)
                   for item in NEGATIVE_ITEMS)
    positive = sum(pl.when(num(item).is_between(1, 4)).then(4.0 - num(item)).otherwise(None)
                   for item in POSITIVE_ITEMS)
    answered = sum(pl.when(num(item).is_between(1, 4)).then(1.0).otherwise(0.0)
                   for item in NEGATIVE_ITEMS + POSITIVE_ITEMS)
    serial = sum((num(name) == value).cast(pl.Float64) for name, value in
                 zip(("dc019", "dc020", "dc021", "dc022", "dc023"), (93.0, 86.0, 79.0, 72.0, 65.0)))
    raw = raw.with_columns([
        pl.when(answered >= 8).then(negative + positive).otherwise(None).alias("cesd"),
        pl.when(num("dc019").is_not_null() & num("dc023").is_not_null()).then(serial)
          .otherwise(None).alias("serial7"),
        pl.when(num("dc004").is_between(1, 5)).then(6.0 - num("dc004")).otherwise(None)
          .alias("memory"),
    ])
    return frame.join(raw.select(["ID", "cesd", "serial7", "memory"]), on="ID", how="left")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = add_outcomes(pilot.load_private_frame())
    rows = []
    for outcome in ("cesd", "serial7", "memory"):
        for exposure in EXPOSURES:
            data = frame.select([exposure, outcome, "bloodweight", "communityID", "age_lower",
                                 *pilot.M1]).drop_nulls()
            data = data.filter((pl.col("age_lower") >= 45) & (pl.col("bloodweight") > 0))
            if data.height < 500:
                continue
            weights = data["bloodweight"].to_numpy().astype(float)
            values = data[outcome].to_numpy().astype(float)
            mean = np.average(values, weights=weights)
            sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
            if not sd > 0:
                continue
            data = data.with_columns([
                ((pl.col(outcome) - mean) / sd).alias("y_std"),
                pl.col("bloodweight").alias("_w"),
                pl.col("communityID").cast(pl.String).alias("_psu"),
            ])
            try:
                result = svy.Sample(data=data, design=svy.Design(psu="_psu", wgt="_w", wr=True)) \
                    .glm.fit(y="y_std", x=[exposure] + pilot.M1, family="gaussian",
                             drop_nulls=True, alpha=0.05).to_polars()
            except Exception:
                continue
            cell = {row["term"]: row for row in result.to_dicts()}.get(exposure)
            if not cell:
                continue
            rows.append({
                "outcome": outcome,
                "exposure": exposure,
                "estimate": float(cell["estimate"]),
                "standard_error": float(cell["std_err"]),
                "ci_lower": float(cell["conf_low"]),
                "ci_upper": float(cell["conf_high"]),
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
    fields = ["outcome", "exposure", "estimate", "standard_error", "ci_lower", "ci_upper",
              "p_value", "q_value_by", "n_model"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        row.setdefault("q_value_by", 1.0)
    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "outcomes": {"cesd": "ten CES-D items, 0-30", "serial7": "correct subtractions 0-5",
                     "memory": "self-rated memory, 1-5 inverted to 5 best"},
        "results": sorted(rows, key=lambda item: item["p_value"]),
        "summary": {"tests": len(rows), "q_lt_05": sum(1 for row in rows if row["q_value_by"] < 0.05)},
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_mental_health_exposures_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
