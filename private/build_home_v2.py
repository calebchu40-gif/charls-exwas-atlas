"""Build the homepage overview v2 from the full-scan results."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
RES = BASE / "private/results"
OUT = BASE / "code" / "site-prototype" / "dist" / "home_overview_v2.json"
CJK = re.compile(r"[\u4e00-\u9fff]")

pairs = pd.read_csv(RES / "pair_term_results_v1.csv", low_memory=False)
pairs = pairs[pd.to_numeric(pairs["n_model_min"], errors="coerce") >= 100].copy()

labels = {}
for wave in ("2011", "2013", "2015", "2018", "2020"):
    reg = pd.read_csv(BASE / "private/derived_wave_tables" / f"registry_{wave}_full.csv")
    for cid, label in zip(reg["concept_id"], reg["label"]):
        labels.setdefault(cid, str(label))
index = json.loads((BASE / "private/results/public_full_scan_v3/index.json").read_text(encoding="utf-8"))
for item in index["exposures"] + index["outcomes"]:
    labels[item["id"]] = item["label"]

def top(counter: Counter, n: int = 9):
    out = []
    for cid, value in counter.most_common(n):
        out.append({"id": cid, "label": str(labels.get(cid, cid))[:40], "n": int(value)})
    return out

significant = int((pairs["q_value"] < 0.05).sum())
total = int(len(pairs))

wave_counts = []
for wave in ("2011", "2013", "2015", "2018", "2020"):
    csv = RES / f"scan_{wave}_full_v1.csv"
    fits = 0
    if csv.exists():
        df = pd.read_csv(csv, usecols=["fit_status", "model_id"], low_memory=False)
        fits = int(len(df))
    wave_counts.append({"wave": wave, "fits": fits})

flow = json.loads((BASE / "code" / "site-prototype" / "dist" / "home_overview_v1.json").read_text(encoding="utf-8")).get("module_flow", [])

payload = {
    "stats": {
        "results": total,
        "exposures": int(pairs["exposure_concept_id"].nunique()),
        "outcomes": int(pairs["phenotype_concept_id"].nunique()),
        "fits": int(sum(w["fits"] for w in wave_counts)),
        "waves": 5,
    },
    "mix": [
        {"label": "q < 0.05", "value": significant, "color": "#2f7d5d"},
        {"label": "不显著（同样保留）", "value": total - significant, "color": "#9fb3c0"},
    ],
    "waves": wave_counts,
    "top_exposures": top(Counter(pairs["exposure_concept_id"])),
    "top_outcomes": top(Counter(pairs["phenotype_concept_id"])),
    "flow": flow,
}

OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(json.dumps({"bytes": OUT.stat().st_size, "stats": payload["stats"], "mix": payload["mix"],
                  "top_exposure": payload["top_exposures"][0]}, ensure_ascii=False))
