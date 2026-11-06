#!/usr/bin/env python3
"""Replication scorecard: the 2011 pilot grid against the 2015 wave.

For every pilot-105 hypothesis, look up the identical exposure, phenotype and
contrast in the 2015 wave of the published payload. Report how many pairs are
available in 2015, how often the sign agrees, the correlation of effect sizes,
and how many are significant in both waves.

Uses only the public aggregate payload.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "site-prototype" / "dist" / "association_results_v1.json"
PUBLIC_OUT = ROOT / "site-prototype" / "dist" / "replication_v1.json"
PRIVATE_OUT = ROOT / "site-prototype" / "dist" / "replication_pairs_private.csv"


def number(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    rows = [row for family in payload["families"] for row in family["rows"]]
    pilot = [row for row in rows
             if str(row.get("model_id", "")).startswith("Pilot105") and row["wave"] == "2011"]
    later = [row for row in rows if row["wave"] == "2015" and row.get("fit_status") == "success"]

    def normalise(row):
        exposure = str(row.get("exposure_concept_id", ""))
        contrast = str(row.get("contrast", "")).lower()
        if exposure.startswith("cooking_fuel"):
            level = exposure.replace("cooking_fuel_", "") if exposure != "cooking_fuel_main" else ""
            if not level:
                for word, label in (("coal", "coal"), ("natural gas", "natural_gas"),
                                    ("marsh", "marsh_gas"), ("lpg", "LPG"),
                                    ("crop", "crop_residue_or_wood"), ("wood", "crop_residue_or_wood"),
                                    ("other", "other")):
                    if word in contrast:
                        level = label
                        break
            return ("cooking_fuel", level, row["phenotype_concept_id"])
        if "water" in exposure:
            return ("running_water", "", row["phenotype_concept_id"])
        return (exposure, "", row["phenotype_concept_id"])

    def key(row):
        return normalise(row)

    index = {}
    for row in later:
        index.setdefault(key(row), row)

    pairs = []
    for row in pilot:
        if row.get("fit_status") != "success":
            continue
        match = index.get(key(row))
        if not match:
            continue
        first = number(row.get("estimate"))
        second = number(match.get("estimate"))
        if first is None or second is None:
            continue
        pairs.append({
            "exposure_concept_id": row["exposure_concept_id"],
            "phenotype_concept_id": row["phenotype_concept_id"],
            "contrast": row.get("contrast", ""),
            "beta_2011": first,
            "beta_2015": second,
            "p_2011": number(row.get("p_value")),
            "p_2015": number(match.get("p_value")),
            "q_2011": number(row.get("q_value_by")),
            "q_2015": number(match.get("q_value_by")),
            "same_sign": (first > 0) == (second > 0),
        })
    n = len(pairs)
    same = sum(1 for pair in pairs if pair["same_sign"])
    xs = [pair["beta_2011"] for pair in pairs]
    ys = [pair["beta_2015"] for pair in pairs]
    if n > 1:
        mx, my = sum(xs) / n, sum(ys) / n
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        sy = math.sqrt(sum((y - my) ** 2 for y in ys))
        corr = cov / (sx * sy) if sx > 0 and sy > 0 else 0.0
    else:
        corr = 0.0

    payload_out = {
        "schema_version": 1,
        "source": "public aggregate payload",
        "description": "2011 pilot-105 hypotheses matched to the identical 2015 estimate",
        "pairs_available": n,
        "same_sign": same,
        "same_sign_fraction": round(same / n, 3) if n else 0,
        "pearson_r": round(corr, 3),
        "q_both_below_05": sum(1 for pair in pairs
                               if (pair["q_2011"] or 1) < 0.05 and (pair["q_2015"] or 1) < 0.05),
        "pairs": pairs,
    }
    PUBLIC_OUT.write_text(json.dumps(payload_out, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    import csv
    with PRIVATE_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pairs[0].keys()) if pairs else ["empty"])
        writer.writeheader()
        writer.writerows(pairs)
    print(json.dumps({k: payload_out[k] for k in
                      ("pairs_available", "same_sign", "pearson_r", "q_both_below_05")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
