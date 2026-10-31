#!/usr/bin/env python3
"""Compare the pilot-105 sensitivity variants against the main run.

Reads the private result tables written by
:mod:`run_wave1_pilot105_exploratory` and reports, per coefficient:

* sign agreement with ``main``;
* absolute change in the standardized estimate;
* whether the 95% CI still excludes the null;
* whether the by-family q-value still clears 0.05;
* a coarse robustness label (``stable``/``attenuated``/``sign_flip``/``imprecise``).

Only aggregates are printed. The per-coefficient comparison stays in the
protected workspace.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path  # noqa: E402

RESULT_DIR = PRIVATE_ROOT / "results"
MAIN = "wave1_pilot105_main_v1.csv"
VARIANTS = {
    "county_psu": "wave1_pilot105_county_psu_v1.csv",
    "no_urban": "wave1_pilot105_no_urban_v1.csv",
    "age_sex": "wave1_pilot105_age_sex_v1.csv",
    "drop_small": "wave1_pilot105_drop_small_v1.csv",
    "fasting_adjust": "wave1_pilot105_fasting_adjust_v1.csv",
}
FLOAT = ("estimate", "standard_error", "ci_lower", "ci_upper", "p_value", "q_value_by")


def read(path: Path) -> pl.DataFrame:
    frame = pl.read_csv(path, infer_schema_length=10000)
    return frame.with_columns([pl.col(c).cast(pl.Float64, strict=False) for c in FLOAT])


def label(row: dict) -> str:
    if row.get("main_estimate") is None or row.get("variant_estimate") is None:
        return "not_comparable"
    main_sign = 1 if row["main_estimate"] > 0 else -1
    var_sign = 1 if row["variant_estimate"] > 0 else -1
    if main_sign != var_sign:
        return "sign_flip"
    delta = abs(row["variant_estimate"] - row["main_estimate"])
    main_half = None
    if row.get("main_ci_lower") is not None and row.get("main_ci_upper") is not None:
        main_half = (row["main_ci_upper"] - row["main_ci_lower"]) / 2.0
    if main_half and delta > 0.5 * main_half:
        return "attenuated"
    if row.get("variant_ci_lower") is not None and row.get("variant_ci_upper") is not None:
        if row["variant_ci_lower"] <= 0 <= row["variant_ci_upper"]:
            return "imprecise"
    return "stable"


def compare(main: pl.DataFrame, variant: pl.DataFrame, name: str) -> tuple[pl.DataFrame, dict]:
    joined = main.select([
        "analysis_id", "exposure_concept_id", "phenotype_concept_id",
        pl.col("estimate").alias("main_estimate"),
        pl.col("ci_lower").alias("main_ci_lower"),
        pl.col("ci_upper").alias("main_ci_upper"),
        pl.col("q_value_by").alias("main_q"),
    ]).join(
        variant.select([
            "analysis_id",
            pl.col("estimate").alias("variant_estimate"),
            pl.col("ci_lower").alias("variant_ci_lower"),
            pl.col("ci_upper").alias("variant_ci_upper"),
            pl.col("standard_error").alias("variant_se"),
            pl.col("q_value_by").alias("variant_q"),
            pl.col("n_model").alias("variant_n"),
        ]),
        on="analysis_id", how="inner")
    rows = joined.to_dicts()
    for row in rows:
        row["variant"] = name
        row["robustness"] = label(row)
    detail = pl.DataFrame(rows)
    summary = {
        "variant": name,
        "compared": detail.height,
        "sign_agreement": round(
            sum(1 for row in rows if row["main_estimate"] is not None
                and row["variant_estimate"] is not None
                and (row["main_estimate"] > 0) == (row["variant_estimate"] > 0)) / max(detail.height, 1), 3),
        "by_robustness": {key: sum(1 for row in rows if row["robustness"] == key)
                          for key in sorted({row["robustness"] for row in rows})},
        "q_below_05_main": sum(1 for row in rows if (row["main_q"] or 1) < 0.05),
        "q_below_05_variant": sum(1 for row in rows if (row["variant_q"] or 1) < 0.05),
    }
    return detail, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected result tables")
    parser.add_argument("--out", type=Path,
                        default=RESULT_DIR / "wave1_pilot105_robustness_v1.csv")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected result tables")

    main_table = read(RESULT_DIR / MAIN)
    details = []
    summaries = []
    for name, filename in VARIANTS.items():
        path = RESULT_DIR / filename
        if not path.is_file():
            summaries.append({"variant": name, "compared": 0, "missing": True})
            continue
        detail, summary = compare(main_table, read(path), name)
        details.append(detail)
        summaries.append(summary)
    if details:
        combined = pl.concat(details, how="diagonal_relaxed")
        out = require_private_path(args.out)
        if not out.is_relative_to(PRIVATE_ROOT.resolve()):
            parser.error(f"output must stay under {PRIVATE_ROOT}")
        combined.write_csv(out)
    report = {"variants": summaries, "output": str(args.out)}
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_pilot105_robustness_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
