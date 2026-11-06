#!/usr/bin/env python3
"""Weighted exposure-exposure correlation network for the 2011 wave.

Builds the "interaction network" module promised on the public site: pairwise
weighted Spearman correlations among household-environment and behavioural
exposures, with Benjamini-Hochberg correction across pairs.

Only aggregate statistics leave the server: nodes (labels) and edges
(correlation, q). No respondent row is exported.
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

PREPARED = WAVE_DATA_DIR / "CHARLS_wave2011_person_analytic.dta"
OUTPUT = PRIVATE_ROOT / "results" / "wave1_exposure_network_v1.json"
SITE_COPY = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "exposure_network_v1.json"

NODES = [
    ("water", "i017", "自来水", "住房"),
    ("electricity", "i016", "通电", "住房"),
    ("piped_gas", "i019", "管道燃气", "住房"),
    ("heating", "i020", "有供暖", "住房"),
    ("fuel_coal", "i022", "炊事：煤", "燃料"),
    ("fuel_gas", "i022", "炊事：天然气", "燃料"),
    ("fuel_marsh", "i022", "炊事：沼气", "燃料"),
    ("fuel_lpg", "i022", "炊事：液化气", "燃料"),
    ("fuel_wood", "i022", "炊事：秸秆/木柴", "燃料"),
    ("urban", "urban_nbs", "城镇", "社区"),
    ("education", "bd001", "教育年限组", "社会经济"),
    ("smoker", "da059", "吸烟", "行为"),
    ("drinker", "da067", "饮酒", "行为"),
]
MIN_ABS_R = 0.15
ALPHA = 0.05


def build_frame() -> pd.DataFrame:
    import pyreadstat
    cols = ["ID", "bloodweight"] + sorted({field for _, field, _, _ in NODES})
    frame, _ = pyreadstat.read_dta(str(PREPARED), usecols=cols)
    ages, _ = pyreadstat.read_dta(str(PRIVATE_ROOT / "age_inputs_2011" / "wave1_age_interval_candidate.dta"),
                                  usecols=["ID", "age_at_interview_lower"])
    frame = frame.merge(ages, on="ID", how="left")
    num = lambda name: pd.to_numeric(frame[name], errors="coerce")  # noqa: E731
    out = pd.DataFrame(index=frame.index)
    out["water"] = np.where(num("i017") == 1, 1.0, np.where(num("i017") == 2, 0.0, np.nan))
    out["electricity"] = np.where(num("i016") == 1, 1.0, np.where(num("i016") == 2, 0.0, np.nan))
    out["piped_gas"] = np.where(num("i019") == 1, 1.0, np.where(num("i019") == 2, 0.0, np.nan))
    out["heating"] = np.where(num("i020") == 1, 1.0, np.where(num("i020") == 2, 0.0, np.nan))
    fuel = num("i022")
    for key, code in (("fuel_coal", 1), ("fuel_gas", 2), ("fuel_marsh", 3),
                      ("fuel_lpg", 4), ("fuel_wood", 6)):
        out[key] = np.where(fuel == code, 1.0, np.where(fuel.isin([1, 2, 3, 4, 5, 6, 7]), 0.0, np.nan))
    out["urban"] = np.where(num("urban_nbs") == 1, 1.0, np.where(num("urban_nbs") == 0, 0.0, np.nan))
    out["education"] = num("bd001")
    out["smoker"] = np.where(num("da059") == 1, 1.0, np.where(num("da059") == 2, 0.0, np.nan))
    out["drinker"] = np.where(num("da067") == 1, 1.0, np.where(num("da067") == 3, 0.0, np.nan))
    age = num("age_at_interview_lower")
    weight = num("bloodweight")
    keep = (weight > 0) & (age >= 45)
    out = out[keep].reset_index(drop=True)
    out["__weight"] = weight[keep].reset_index(drop=True)
    return out


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
    parser.add_argument("--run", action="store_true", help="read the protected Wave 1 table")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected Wave 1 table")

    frame = build_frame()
    keys = [key for key, _, _, _ in NODES]
    edges = []
    pvalues = []
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
            clipped = max(min(rho, 0.999999), -0.999999)
            z = math.atanh(clipped) * math.sqrt(max(n - 3, 1))
            p = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))
            edges.append({"source": keys[i], "target": keys[j], "rho": round(rho, 4),
                          "n": int(n), "p": p})
            pvalues.append(p)
    adjusted = bh([edge["p"] for edge in edges])
    for edge, q in zip(edges, adjusted):
        edge["q"] = float(f"{q:.6g}")
    kept = [edge for edge in edges if abs(edge["rho"]) >= MIN_ABS_R and edge["q"] < ALPHA]
    payload = {
        "schema_version": 1,
        "wave": "2011",
        "method": "weighted Spearman on ranks; BH across pairs",
        "min_abs_r": MIN_ABS_R,
        "alpha": ALPHA,
        "n_rows": int(len(frame)),
        "nodes": [{"id": key, "label": label, "group": group, "field": field}
                  for key, field, label, group in NODES],
        "edges": kept,
    }
    out = require_private_path(OUTPUT)
    if not out.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"output must stay under {PRIVATE_ROOT}")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    SITE_COPY.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    print(json.dumps({"nodes": len(NODES), "pairs": len(edges), "kept": len(kept),
                      "n_rows": payload["n_rows"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
