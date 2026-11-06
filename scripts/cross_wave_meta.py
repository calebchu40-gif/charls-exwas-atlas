#!/usr/bin/env python3
"""Cross-wave random-effects meta-analysis for repeated exposure-phenotype pairs.

Reads the published aggregate payload (the same file the website serves), groups
rows by exposure x phenotype, and pools estimates from different waves with a
DerSimonian-Laird random-effects model. Only pairs observed in two or more waves
are kept.

Output is an aggregate JSON used by the site's cross-wave view: pooled estimate,
CI, I^2, k, and the per-wave inputs. No respondent data is involved.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "site-prototype" / "dist" / "association_results_v1.json"
OUTPUT = ROOT / "site-prototype" / "dist" / "cross_wave_meta_v1.json"
PRIVATE_OUTPUT = None  # set from the environment when running on the server


def read_rows(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for family in payload["families"]:
        rows.extend(family["rows"])
    return rows


def number(value):
    if value in ("", None):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def der_simonian_laird(estimates: list[float], errors: list[float]) -> dict:
    k = len(estimates)
    weights = [1.0 / (se * se) for se in errors]
    fixed = sum(w * y for w, y in zip(weights, estimates)) / sum(weights)
    q = sum(w * (y - fixed) ** 2 for w, y in zip(weights, estimates))
    df = k - 1
    c = sum(weights) - sum(w * w for w in weights) / sum(weights)
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    random_weights = [1.0 / (se * se + tau2) for se in errors]
    pooled = sum(w * y for w, y in zip(random_weights, estimates)) / sum(random_weights)
    se = math.sqrt(1.0 / sum(random_weights))
    z = pooled / se if se > 0 else 0.0
    p = math.erfc(abs(z) / math.sqrt(2.0))
    i2 = max(0.0, (q - df) / q) * 100 if q > 0 else 0.0
    return {
        "k": k,
        "pooled": pooled,
        "se": se,
        "ci_lower": pooled - 1.96 * se,
        "ci_upper": pooled + 1.96 * se,
        "p": p,
        "q": q,
        "tau2": tau2,
        "i2": i2,
    }


def build(rows: list[dict]) -> dict:
    """Pool exact exposure x phenotype x contrast groups, one primary row per wave.

    Concept ids and contrast strings are compared exactly: no cross-wave
    harmonisation is assumed. Groups contributing more than one row in the same
    wave are dropped rather than treated as independent studies.
    """
    groups: dict[tuple[str, str, str], dict[str, dict]] = {}
    for row in rows:
        if row.get("fit_status") != "success":
            continue
        estimate = number(row.get("estimate"))
        error = number(row.get("standard_error"))
        if estimate is None or error is None or error <= 0:
            continue
        key = (row["exposure_concept_id"], row["phenotype_concept_id"], row.get("contrast", ""))
        wave = row["wave"]
        bucket = groups.setdefault(key, {})
        if wave in bucket:
            bucket[wave] = None  # ambiguous: more than one row for this wave
            continue
        is_or = "odds_ratio" in str(row.get("estimate_type", "")).lower()
        if is_or:
            if estimate <= 0:
                continue
            # the payload stores OR-scale standard errors: convert to the log scale
            analysis_estimate = math.log(estimate)
            analysis_error = error / estimate
        else:
            analysis_estimate = estimate
            analysis_error = error
        bucket[wave] = {
            "wave": wave,
            "model_id": row.get("model_id", ""),
            "estimate": estimate,
            "standard_error": error,
            "ci_lower": number(row.get("ci_lower")),
            "ci_upper": number(row.get("ci_upper")),
            "n_model": row.get("n_model", ""),
            "y": analysis_estimate,
            "se": analysis_error,
            "metric": "OR" if is_or else "beta",
        }
    pairs = []
    dropped_ambiguous = 0
    for (exposure, phenotype, contrast), bucket in groups.items():
        if any(item is None for item in bucket.values()):
            dropped_ambiguous += 1
            continue
        items = sorted(bucket.values(), key=lambda item: item["wave"])
        if len(items) < 2:
            continue
        metrics = {item["metric"] for item in items}
        if len(metrics) != 1:
            continue
        metric = metrics.pop()
        result = der_simonian_laird([item["y"] for item in items], [item["se"] for item in items])
        if metric == "OR":
            result["pooled"], result["ci_lower"], result["ci_upper"] = (
                math.exp(result["pooled"]), math.exp(result["ci_lower"]), math.exp(result["ci_upper"]))
            result["se"] = None
        result["metric"] = metric
        signs = {1 if item["y"] > 0 else -1 for item in items}
        result.update({
            "exposure_concept_id": exposure,
            "phenotype_concept_id": phenotype,
            "contrast": contrast,
            "waves": [item["wave"] for item in items],
            "sign_consistent": len(signs) == 1,
            "inputs": items,
        })
        pairs.append(result)
    pairs.sort(key=lambda item: item["p"])
    return {
        "schema_version": 1,
        "method": ("DerSimonian-Laird random effects over waves; exact exposure/phenotype/"
                   "contrast match; one primary row per wave; groups with duplicate rows in a "
                   "wave are dropped"),
        "pairs": pairs,
        "summary": {
            "pairs": len(pairs),
            "k2": sum(1 for item in pairs if item["k"] == 2),
            "k3plus": sum(1 for item in pairs if item["k"] >= 3),
            "sign_consistent": sum(1 for item in pairs if item["sign_consistent"]),
            "pooled_p_lt_05": sum(1 for item in pairs if item["p"] < 0.05),
            "dropped_ambiguous_groups": dropped_ambiguous,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--payload", type=Path, default=PAYLOAD)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    rows = read_rows(args.payload)
    result = build(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
                        encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
