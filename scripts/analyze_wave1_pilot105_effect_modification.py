#!/usr/bin/env python3
"""Effect modification for the 2011 pilot-105 grid.

Re-runs the pilot within strata of sex, urbanicity, education and age, dropping
the stratifying covariate from the model so the design stays full rank, and then
tests whether the stratum-specific estimates differ (z-test on the difference).

Outputs
-------
* private table: every stratum x hypothesis estimate (protected workspace);
* public JSON: interaction tests plus stratum estimates for the strongest
  modifications only (aggregate statistics, no respondent rows).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exwas_engine as engine  # noqa: E402
import run_wave1_pilot105_exploratory as pilot  # noqa: E402
from project_paths import PRIVATE_ROOT, QA_OUTPUT_DIR, require_private_path  # noqa: E402

STRATA = {
    "sex": ("female", {1.0: "女性", 0.0: "男性"}),
    "urban": ("urban", {1.0: "城镇", 0.0: "农村"}),
    "education": (None, {}),   # derived below
    "age": (None, {}),         # derived below
}
PRIVATE_OUT = PRIVATE_ROOT / "results" / "wave1_pilot105_effect_modification_v1.csv"
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / \
    "effect_modification_v1.json"


def strata_frame(frame: pl.DataFrame, name: str) -> tuple[str, dict[float, str], pl.Expr]:
    if name == "sex":
        return "female", {1.0: "女性", 0.0: "男性"}, pl.col("female")
    if name == "urban":
        return "urban", {1.0: "城镇", 0.0: "农村"}, pl.col("urban")
    if name == "education":
        level = pl.col("edu_2") + pl.col("edu_3") + pl.col("edu_4") + pl.col("edu_5")
        return "edu_high", {1.0: "初中及以上", 0.0: "小学及以下"}, level
    if name == "age":
        return "age65", {1.0: "65 岁及以上", 0.0: "45–64 岁"}, (pl.col("age_mid") >= 65).cast(pl.Float64)
    raise ValueError(name)


def run(frame: pl.DataFrame, name: str) -> list[dict]:
    column, labels, expr = strata_frame(frame, name)
    frame = frame.with_columns(expr.alias(column))
    rows: list[dict] = []
    for value, label in labels.items():
        subset = frame.filter(pl.col(column) == value)
        drop = {
            "sex": {"female"},
            "urban": {"urban"},
            "education": {"edu_2", "edu_3", "edu_4", "edu_5"},
            "age": set(),
        }[name]
        covariates = [c for c in pilot.M1 if c not in drop]
        design = engine.DesignSpec(
            weight="bloodweight", psu="communityID", strata=None,
            age_field="age_lower", age_min=45,
            covariate_sets={pilot.MODEL_ID: covariates},
            scale_outcome=True,
            variance_limitations="communityID clustering only; no official strata; WR Taylor")
        scan = engine.scan(subset, pilot.registry(False, False), design, wave=pilot.WAVE,
                           models=[pilot.MODEL_ID], family_prefix=f"em_{name}")
        fasting = subset.filter(pl.col("fasting_code") == 1.0)
        scan_fast = engine.scan(fasting, pilot.registry(True, False), design, wave=pilot.WAVE,
                                models=[pilot.MODEL_ID], family_prefix=f"em_{name}")
        for row in scan + scan_fast:
            row["stratum"] = column
            row["stratum_value"] = value
            row["stratum_label"] = label
            rows.append(row)
    return rows


def interaction_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], dict[float, dict]] = {}
    for row in rows:
        if row["fit_status"] != "success":
            continue
        key = (row["stratum"], row["analysis_id"])
        grouped.setdefault(key, {})[row["stratum_value"]] = row
    results = []
    for (stratum, key), cells in grouped.items():
        if len(cells) != 2:
            continue
        a, b = cells.get(1.0), cells.get(0.0)
        if not a or not b:
            continue
        est_a, se_a = float(a["estimate"]), float(a["standard_error"])
        est_b, se_b = float(b["estimate"]), float(b["standard_error"])
        diff = est_a - est_b
        se_diff = math.sqrt(se_a * se_a + se_b * se_b)
        z = diff / se_diff if se_diff > 0 else 0.0
        p = math.erfc(abs(z) / math.sqrt(2.0))
        results.append({
            "analysis_id": key,
            "stratum": stratum,
            "exposure_concept_id": a["exposure_concept_id"],
            "phenotype_concept_id": a["phenotype_concept_id"],
            "contrast": a.get("exposure_contrast", ""),
            "label_high": a["stratum_label"],
            "label_low": b["stratum_label"],
            "estimate_high": est_a,
            "estimate_low": est_b,
            "difference": diff,
            "se_difference": se_diff,
            "p_interaction": p,
        })
    results.sort(key=lambda item: item["p_interaction"])
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = pilot.load_private_frame()
    rows: list[dict] = []
    for name in STRATA:
        rows.extend(run(frame, name))
    out = require_private_path(PRIVATE_OUT)
    import csv
    fields = list(engine.RESULT_COLUMNS) + ["p_bonferroni", "q_value_by",
                                            "stratum", "stratum_value", "stratum_label"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})
    interactions = interaction_rows(rows)
    public = {
        "schema_version": 1,
        "wave": pilot.WAVE,
        "method": "stratum-specific weighted models; z-test on the difference between strata",
        "strata": ["sex", "urban", "education", "age"],
        "rows": len(rows),
        "interactions": interactions,
        "summary": {
            "tested": len(interactions),
            "p_lt_05": sum(1 for item in interactions if item["p_interaction"] < 0.05),
            "bonferroni_threshold": round(0.05 / max(len(interactions), 1), 6),
            "bonferroni_hits": sum(1 for item in interactions
                                   if item["p_interaction"] < 0.05 / max(len(interactions), 1)),
        },
    }
    PUBLIC_OUT.write_text(json.dumps(public, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    QA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (QA_OUTPUT_DIR / "wave1_pilot105_effect_modification_v1.json").write_text(
        json.dumps(public["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(public["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
