"""Propagate reviewed food/housing source status into the final source index."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def sync_food_crosswalk_index(root: Path, keys: set[tuple[str, str, str]]) -> int:
    source_path = root / "audit/food_environment_crosswalk_v1.csv"
    index_path = root / "audit/ep_concept_source_crosswalk_v1.csv"
    source = pd.read_csv(source_path, dtype=str, encoding="utf-8-sig").fillna("")
    source = source[source.apply(
        lambda r: (str(r["wave"]), str(r["code"]).lower(), str(r["concept_id"])) in keys,
        axis=1,
    )]
    values = {
        (str(r["wave"]), str(r["code"]).lower(), str(r["concept_id"])):
        (str(r["mapping_status"]), str(r["caveat"]))
        for _, r in source.iterrows()
    }
    if set(values) != keys:
        raise ValueError(f"Food source crosswalk mismatch: missing={sorted(keys-set(values))}, unexpected={sorted(set(values)-keys)}")
    index = pd.read_csv(index_path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = index["Source.File"].str.contains("audit/food_environment_crosswalk_v1.csv", regex=False) & index.apply(
        lambda r: any((str(r["Wave"]), str(r["Source.Code"]).lower(), concept.strip()) in keys
                      for concept in str(r["Source.Concept.ID"]).split(" | ")),
        axis=1,
    )
    found = {
        (str(r["Wave"]), str(r["Source.Code"]).lower(), concept.strip())
        for _, r in index[selected].iterrows()
        for concept in str(r["Source.Concept.ID"]).split(" | ")
        if (str(r["Wave"]), str(r["Source.Code"]).lower(), concept.strip()) in keys
    }
    if found != keys:
        raise ValueError(f"Final source index mismatch: missing={sorted(keys-found)}, unexpected={sorted(found-keys)}")
    for row_index in index.index[selected]:
        keys_here = [
            (str(index.at[row_index, "Wave"]), str(index.at[row_index, "Source.Code"]).lower(), concept.strip())
            for concept in str(index.at[row_index, "Source.Concept.ID"]).split(" | ")
            if (str(index.at[row_index, "Wave"]), str(index.at[row_index, "Source.Code"]).lower(), concept.strip()) in keys
        ]
        key = keys_here[0]
        index.at[row_index, "Mapping.Status"], index.at[row_index, "Caveat"] = values[key]
    index.to_csv(index_path, index=False, encoding="utf-8-sig")
    return int(selected.sum())
