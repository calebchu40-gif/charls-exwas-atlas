#!/usr/bin/env python3
"""Mutually adjusted household-exposure model for the 2011 blood panel.

The pilot fits one exposure at a time. Household exposures are strongly
correlated (see the exposure network), so this script fits all seven at once:
running water plus the six cooking-fuel dummies against each of the fifteen blood
outcomes, with the same survey design and covariates as the pilot.

Outputs a private coefficient table and a public aggregate JSON.
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
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path  # noqa: E402

TERMS = ["water_yes", "fuel_coal", "fuel_natural_gas", "fuel_marsh_gas",
         "fuel_LPG", "fuel_crop_residue_or_wood", "fuel_other"]
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_joint_household_model_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "joint_household_model_v1.json"


def bh(pvalues: list[float]) -> list[float]:
    order = np.argsort(pvalues)
    n = len(pvalues)
    adjusted = np.empty(n)
    running = 1.0
    for rank in range(n - 1, -1, -1):
        index = order[rank]
        running = min(running, pvalues[index] * n / (rank + 1))
        adjusted[index] = running
    return adjusted.tolist()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = pilot.load_private_frame()
    rows: list[dict] = []
    for concept, (_field, _unit) in pilot.OUTCOMES.items():
        column = f"out_{concept}"
        cols = ["bloodweight", "communityID", "age_lower", column, "fasting_code", *TERMS, *pilot.M1]
        data = frame.select(cols).drop_nulls()
        data = data.filter((pl.col("age_lower") >= 45) & (pl.col("bloodweight") > 0))
        if concept in pilot.FASTING_SENSITIVE:
            data = data.filter(pl.col("fasting_code") == 1.0)
        if data.height < 200:
            continue
        weights = data["bloodweight"].to_numpy().astype(float)
        values = data[column].to_numpy().astype(float)
        mean = np.average(values, weights=weights)
        sd = math.sqrt(np.average((values - mean) ** 2, weights=weights))
        if not sd > 0:
            continue
        data = data.with_columns(((pl.col(column) - mean) / sd).alias("y_std"))
        data = data.with_columns([
            pl.col("bloodweight").alias("_w"),
            pl.col("communityID").cast(pl.String).alias("_psu"),
        ])
        try:
            result = svy.Sample(
                data=data,
                design=svy.Design(psu="_psu", wgt="_w", wr=True),
            ).glm.fit(y="y_std", x=TERMS + pilot.M1, family="gaussian",
                      where=pl.col("age_lower") >= 45, drop_nulls=True, alpha=0.05).to_polars()
        except Exception as error:  # rank deficiency or separation
            rows.append({"phenotype_concept_id": concept, "term": "MODEL", "estimate": "",
                         "standard_error": "", "p_value": "", "n_model": data.height,
                         "fit_status": f"error: {error}"[:200]})
            continue
        table = {row["term"]: row for row in result.to_dicts()}
        for term in TERMS:
            cell = table.get(term)
            if not cell:
                continue
            rows.append({
                "phenotype_concept_id": concept,
                "term": term,
                "estimate": float(cell["estimate"]),
                "standard_error": float(cell["std_err"]),
                "ci_lower": float(cell["conf_low"]),
                "ci_upper": float(cell["conf_high"]),
                "p_value": float(cell["p_value"]),
                "n_model": data.height,
                "fit_status": "success",
            })
    pvalues = [row["p_value"] for row in rows if row.get("fit_status") == "success"]
    adjusted = bh(pvalues)
    index = 0
    for row in rows:
        if row.get("fit_status") == "success":
            row["q_value_by"] = adjusted[index]
            index += 1
        else:
            row["q_value_by"] = ""

    out = require_private_path(PRIVATE_OUT)
    import csv
    fields = ["phenotype_concept_id", "term", "estimate", "standard_error", "ci_lower",
              "ci_upper", "p_value", "q_value_by", "n_model", "fit_status"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})

    public = [row for row in rows if row.get("fit_status") == "success"]
    public.sort(key=lambda item: item["p_value"])
    payload = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "method": "one survey-weighted model per outcome with all seven household exposures",
        "terms": TERMS,
        "results": public,
        "summary": {
            "tested": len(public),
            "q_lt_05": sum(1 for item in public if item["q_value_by"] < 0.05),
            "models": len({item["phenotype_concept_id"] for item in public}),
        },
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_joint_household_model_v1.json").write_text(
        json.dumps(payload["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
