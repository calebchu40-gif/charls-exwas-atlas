"""Build the public full-scan aggregate (n>=100) with exposure/outcome indexes.

Outputs (private/results/public_full_scan/):
    index.json          — exposures, outcomes, counts, version
    edges_0..7.json     — compact result rows sharded by pair id hash
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

BASE = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas")
RES = BASE / "private/results"
OUT = RES / "public_full_scan"
MIN_N = 100
SHARDS = 8

pairs = pd.read_csv(RES / "pair_term_results_v1.csv", low_memory=False)
pairs = pairs[pd.to_numeric(pairs["n_model_min"], errors="coerce") >= MIN_N].copy()
print("rows kept:", len(pairs))

# label map from every wave registry (longest label wins)
labels = {}
kinds = {}
for wave in ("2011", "2013", "2015", "2018", "2020"):
    reg = pd.read_csv(BASE / "private/derived_wave_tables" / f"registry_{wave}_full.csv")
    for _, row in reg.iterrows():
        cid = row["concept_id"]
        label = str(row["label"]).strip()
        if cid not in labels or len(label) > len(labels[cid]):
            labels[cid] = label
        kinds.setdefault(cid, str(row["kind"]))

exposures = sorted(pairs["exposure_concept_id"].unique())
outcomes = sorted(pairs["phenotype_concept_id"].unique())

def label_for(cid: str) -> str:
    return labels.get(cid) or cid

def spread(cid: str, column: str) -> dict:
    sub = pairs[pairs[column] == cid]
    return {
        "n_results": int(len(sub)),
        "n_significant": int((sub["q_value"] < 0.05).sum()),
        "n_partners": int(sub["phenotype_concept_id" if column == "exposure_concept_id" else "exposure_concept_id"].nunique()),
    }

index = {
    "version": "v1",
    "min_n": MIN_N,
    "n_results": int(len(pairs)),
    "exposures": [
        {"id": cid, "label": label_for(cid), "kind": kinds.get(cid, ""), **spread(cid, "exposure_concept_id")}
        for cid in exposures
    ],
    "outcomes": [
        {"id": cid, "label": label_for(cid), "kind": kinds.get(cid, ""), **spread(cid, "phenotype_concept_id")}
        for cid in outcomes
    ],
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("index bytes:", (OUT / "index.json").stat().st_size, "exposures", len(exposures), "outcomes", len(outcomes))

shards = [[] for _ in range(SHARDS)]
for row in pairs.itertuples(index=False):
    key = f"{row.exposure_concept_id}|{row.phenotype_concept_id}|{row.exposure_term}"
    bucket = int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16) % SHARDS
    shards[bucket].append([
        row.exposure_concept_id,
        row.phenotype_concept_id,
        row.exposure_term,
        round(float(row.estimate), 4),
        round(float(row.standard_error), 4),
        round(float(row.ci_lower), 4),
        round(float(row.ci_upper), 4),
        round(float(row.p_value), 6),
        round(float(row.q_value), 6) if pd.notna(row.q_value) else None,
        int(row.n_model_min),
        1 if row.estimate > 0 else 0,
    ])

for i, rows in enumerate(shards):
    path = OUT / f"edges_{i}.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"edges_{i}: {len(rows)} rows, {path.stat().st_size} bytes")

total = sum(len(rows) for rows in shards)
print("total shard rows:", total)
