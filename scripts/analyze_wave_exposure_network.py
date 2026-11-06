#!/usr/bin/env python3
"""Weighted exposure-exposure correlation network for a CHARLS wave.

Generalises the Wave 1 network to the waves whose prepared tables are available.
Node availability differs by wave (for example 2015 drops electricity, urbanicity
and education); the script keeps only the nodes whose fields exist and records
the dropped ones in the output.

Only aggregate statistics leave the server.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from project_paths import PRIVATE_ROOT, WAVE_DATA_DIR, require_private_path  # noqa: E402

MIN_ABS_R = 0.15
ALPHA = 0.05

NODES = [
    ("water", "i017", "自来水", "住房", {1.0: 1.0, 2.0: 0.0}),
    ("electricity", "i016", "通电", "住房", {1.0: 1.0, 2.0: 0.0}),
    ("piped_gas", "i019", "管道燃气", "住房", {1.0: 1.0, 2.0: 0.0}),
    ("heating", "i020", "有供暖", "住房", {1.0: 1.0, 2.0: 0.0}),
    ("urban", "urban_nbs", "城镇", "社区", {1.0: 1.0, 0.0: 0.0}),
    ("education", "bd001", "教育年限组", "社会经济", None),
    ("smoker", "da059", "吸烟", "行为", {1.0: 1.0, 2.0: 0.0}),
    ("drinker", "da067", "饮酒", "行为", {1.0: 1.0, 3.0: 0.0}),
]
FUEL_NODES = [
    ("fuel_coal", 1, "炊事：煤"),
    ("fuel_gas", 2, "炊事：天然气"),
    ("fuel_marsh", 3, "炊事：沼气"),
    ("fuel_lpg", 4, "炊事：液化气"),
    ("fuel_wood", 6, "炊事：秸秆/木柴"),
]

WAVES = {
    "2011": {"table": "derived_wave_tables_2011_official_rebuild_20261029/CHARLS_wave2011_person_analytic.dta",
             "weight": "bloodweight",
             "age": "age_inputs_2011/wave1_age_interval_candidate.dta"},
    "2013": {"table": "derived_wave_tables/CHARLS_wave2013_person_analytic.dta",
             "weight": "Biomarker_weight",
             "age": "derived_wave_tables/CHARLS_wave2013_age_interval_candidate.dta"},
    "2015": {"table": "derived_wave_tables/CHARLS_wave2015_person_analytic.dta",
             "weight": "Biomarker_weight",
             "age": None},
}


def load(wave: str) -> tuple[pd.DataFrame, list[str], list[str]]:
    import pyreadstat
    spec = WAVES[wave]
    table = PRIVATE_ROOT / spec["table"]
    frame, meta = pyreadstat.read_dta(str(table))
    available = set(frame.columns)
    missing = [key for key, field, _, _, _ in NODES if field not in available]
    kept = [item for item in NODES if item[1] in available]
    num = lambda name: pd.to_numeric(frame[name], errors="coerce")  # noqa: E731
    out = pd.DataFrame(index=frame.index)
    for key, field, _label, _group, mapping in kept:
        values = num(field)
        if mapping is None:
            out[key] = values
        else:
            out[key] = np.select(
                [values == code for code in mapping],
                [value for value in mapping.values()],
                default=np.nan)
    if "i022" in available:
        fuel = num("i022")
        for key, code, _label in FUEL_NODES:
            out[key] = np.where(fuel == code, 1.0,
                                np.where(fuel.isin([1, 2, 3, 4, 5, 6, 7]), 0.0, np.nan))
    weight = num(spec["weight"])
    ages = None
    if spec["age"]:
        ages, *_ = pyreadstat.read_dta(str(PRIVATE_ROOT / spec["age"]),
                                       usecols=["ID", "age_at_interview_lower"])
        ages = pd.to_numeric(ages["age_at_interview_lower"], errors="coerce")
        frame = frame.reset_index(drop=True)
        out = out.reset_index(drop=True)
        weight = weight.reset_index(drop=True)
        ages = ages.reset_index(drop=True)
    keep = weight > 0
    if ages is not None:
        keep = keep & (ages >= 45)
    out = out[keep].reset_index(drop=True)
    out["__weight"] = weight[keep].reset_index(drop=True)
    return out, [key for key, _, _, _, _ in kept] + [key for key, _, _ in FUEL_NODES if key in out], missing


def weighted_rank_corr(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    rx = pd.Series(x).rank().to_numpy()
    ry = pd.Series(y).rank().to_numpy()
    mx = np.average(rx, weights=w)
    my = np.average(ry, weights=w)
    cov = np.average((rx - mx) * (ry - my), weights=w)
    vx = np.average((rx - mx) ** 2, weights=w)
    vy = np.average((ry - my) ** 2, weights=w)
    if vx <= 0 or vy <= 0:
        return float("nan")
    return float(cov / np.sqrt(vx * vy))


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
    parser.add_argument("--run", action="store_true", help="read the protected wave table")
    parser.add_argument("--wave", required=True, choices=sorted(WAVES))
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected wave table")

    frame, keys, missing = load(args.wave)
    edges, pvalues = [], []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            subset = frame[[keys[i], keys[j], "__weight"]].dropna()
            if len(subset) < 500:
                continue
            rho = weighted_rank_corr(subset[keys[i]].to_numpy(), subset[keys[j]].to_numpy(),
                                     subset["__weight"].to_numpy())
            if not np.isfinite(rho):
                continue
            n = len(subset)
            z = math.atanh(max(min(rho, 0.999999), -0.999999)) * math.sqrt(max(n - 3, 1))
            p = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))
            edges.append({"source": keys[i], "target": keys[j], "rho": round(rho, 4),
                          "n": int(n), "p": p})
            pvalues.append(p)
    adjusted = bh([edge["p"] for edge in edges])
    for edge, q in zip(edges, adjusted):
        edge["q"] = float(f"{q:.6g}")
    kept = [edge for edge in edges if abs(edge["rho"]) >= MIN_ABS_R and edge["q"] < ALPHA]

    labels = {key: (label, group) for key, _field, label, group, _m in NODES}
    labels.update({key: (label, "燃料") for key, _code, label in FUEL_NODES})
    payload = {
        "schema_version": 1,
        "wave": args.wave,
        "method": "weighted Spearman on ranks; BH across pairs",
        "min_abs_r": MIN_ABS_R,
        "alpha": ALPHA,
        "n_rows": int(len(frame)),
        "nodes": [{"id": key, "label": labels[key][0], "group": labels[key][1]}
                  for key in keys],
        "edges": kept,
        "dropped_nodes": missing,
    }
    out = require_private_path(PRIVATE_ROOT / "results" / f"{args.wave}_exposure_network_v1.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    site = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / f"exposure_network_{args.wave}_v1.json"
    site.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                    encoding="utf-8")
    print(json.dumps({"wave": args.wave, "nodes": len(keys), "edges": len(kept),
                      "rows": payload["n_rows"], "dropped": missing}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
