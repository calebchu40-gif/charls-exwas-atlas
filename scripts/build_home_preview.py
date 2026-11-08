"""Build the small homepage preview payload.

The homepage shows three miniature figures so a visitor sees what the atlas
contains before opening a full view. They are derived from already published
aggregates only; nothing here reads individual-level data.

Output: site-prototype/dist/home_preview_v1.json
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"

TERM_LABELS = {
    "fuel_coal": "煤",
    "fuel_crop_residue_or_wood": "秸秆木材",
    "fuel_natural_gas": "天然气",
    "fuel_marsh_gas": "沼气",
    "fuel_LPG": "液化气",
    "fuel_other": "其他燃料",
    "water_yes": "自来水",
}


def load(name: str):
    return json.loads((SITE / name).read_text(encoding="utf-8"))


def rows_of(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    for key in ("results", "rows", "entries", "groups"):
        if isinstance(payload.get(key), list):
            return payload[key]
    return []


def main() -> None:
    labels = load("concept_labels_v1.json")
    exposure_labels = labels.get("exposures", {})

    # 1. Household fuel terms for uric acid, most protective first.
    joint = rows_of(load("joint_household_model_v1.json"))
    uric = [row for row in joint if row.get("phenotype_concept_id") == "blood_uric_acid"
            and row.get("fit_status", "success") == "success"]
    fuel = sorted(
        (
            {
                "term": TERM_LABELS.get(row.get("term"), row.get("term")),
                "estimate": round(row["estimate"], 3),
                "ci_lower": round(row["ci_lower"], 3),
                "ci_upper": round(row["ci_upper"], 3),
            }
            for row in uric
        ),
        key=lambda item: item["estimate"],
    )

    # 2. Exposures carrying the most corrected-significant results.
    families = load("association_results_v1.json")["families"]
    results = [row for family in families for row in family["rows"]]
    significant = Counter(
        row["exposure_concept_id"] for row in results
        if row.get("fit_status") == "success" and float(row.get("q_value_by") or 1) < 0.05
    )
    totals = Counter(row["exposure_concept_id"] for row in results)
    top = [
        {
            "concept": concept,
            "label": exposure_labels.get(concept, {}).get("zh", concept),
            "code": exposure_labels.get(concept, {}).get("code", ""),
            "significant": count,
            "tested": totals[concept],
        }
        for concept, count in significant.most_common(6)
    ]
    # Two cooking-fuel concepts share the same reading label; keep the code.
    seen = Counter(item["label"] for item in top)
    for item in top:
        if seen[item["label"]] > 1 and item["code"]:
            item["label"] = f'{item["label"]}（{item["code"]}）'

    # 3. Published results per wave.
    waves = Counter(str(row.get("wave")) for row in results)
    wave_rows = [{"wave": wave, "results": waves[wave]} for wave in sorted(waves)]

    # 4. One cross-wave line.
    pairs = load("cross_wave_meta_v1.json")["pairs"]
    consistent = sum(1 for pair in pairs if pair.get("sign_consistent"))
    all_waves = sum(1 for pair in pairs if len(pair.get("waves", [])) >= 3)

    payload = {
        "generated": date.today().isoformat(),
        "fuel": fuel,
        "exposures": top,
        "waves": wave_rows,
        "crosswave": {"pairs": len(pairs), "consistent": consistent, "three_wave": all_waves},
    }
    out = SITE / "home_preview_v1.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({
        "fuel_terms": len(fuel),
        "top_exposures": len(top),
        "waves": len(wave_rows),
        "pairs": len(pairs),
        "consistent": consistent,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
