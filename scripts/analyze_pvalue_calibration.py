#!/usr/bin/env python3
"""p-value calibration for the published association families.

Computes, per family, the genomic-control-style inflation factor
``lambda = median(chi-square) / 0.4549`` (chi-square with one degree of
freedom), the observed share of p<0.05 against the 5% expectation, and the share
of q<0.05. A lambda near one means no systematic shift of the test statistics.

Only the public aggregate payload is used.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "site-prototype" / "dist" / "association_results_v1.json"
PUBLIC_OUT = ROOT / "site-prototype" / "dist" / "pvalue_calibration_v1.json"
CHI2_MEDIAN = 0.4549364231195727
NORMAL = statistics.NormalDist()


def lambda_from(pvalues):
    z = [NORMAL.inv_cdf(1 - value / 2) for value in pvalues]
    chi2 = [value * value for value in z]
    return statistics.median(chi2) / CHI2_MEDIAN


def main() -> int:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    groups = {}
    for family in payload["families"]:
        for row in family["rows"]:
            if row.get("fit_status") != "success":
                continue
            try:
                p = float(row["p_value"])
            except (TypeError, ValueError, KeyError):
                continue
            if not 0 < p <= 1:
                continue
            key = (family["family_id"], row.get("model_id") or "")
            groups.setdefault(key, []).append(row)

    results = []
    for (family_id, model_id), rows in groups.items():
        pvalues = [float(row["p_value"]) for row in rows]
        qvalues = []
        for row in rows:
            try:
                qvalues.append(float(row["q_value_by"]))
            except (TypeError, ValueError, KeyError):
                pass
        results.append({
            "family_id": family_id,
            "model_id": model_id,
            "tests": len(pvalues),
            "lambda": round(lambda_from(pvalues), 3),
            "share_p_lt_05": round(sum(1 for value in pvalues if value < 0.05) / len(pvalues), 3),
            "share_q_lt_05": round(sum(1 for value in qvalues if value < 0.05) / len(qvalues), 3)
            if qvalues else None,
            "median_p": round(statistics.median(pvalues), 4),
            "min_p": min(pvalues),
        })
    results.sort(key=lambda item: -item["tests"])

    overall = {}
    for label, prefix in (("all", ""), ("pilot105", "charls_2011_household_environment_pilot105")):
        pvalues = [float(row["p_value"]) for key, rows in groups.items() for row in rows
                   if not prefix or str(key[0]).startswith(prefix)]
        if pvalues:
            overall[label] = {
                "tests": len(pvalues),
                "lambda": round(lambda_from(pvalues), 3),
                "share_p_lt_05": round(sum(1 for value in pvalues if value < 0.05) / len(pvalues), 3),
            }

    payload_out = {
        "schema_version": 1,
        "method": "lambda = median(chi-square(1)) / 0.4549 on two-sided p-values",
        "interpretation": (
            "lambda is well above one in every family. Correlated outcomes and a shared "
            "household-socioeconomic factor can lift lambda without any computational error, "
            "and these families are curated rather than random, so the atlas is exploratory: "
            "q-values hold only inside the declared family and nothing here is confirmatory."),
        "families": results,
        "overall": overall,
    }
    PUBLIC_OUT.write_text(json.dumps(payload_out, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    print(json.dumps({"families": len(results), "overall": overall}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
