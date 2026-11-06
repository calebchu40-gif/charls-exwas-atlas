#!/usr/bin/env python3
"""Longitudinal trajectories for self-rated health and self-rated memory.

Uses the same five prepared wave tables, the 2011 baseline age band for
stratification, each wave's individual weight, and within-person change for
respondents observed in adjacent waves. Only weighted means and counts are
exported.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from project_paths import PRIVATE_ROOT, require_private_path  # noqa: E402

WAVES = {
    "2011": ("derived_wave_tables_2011_official_rebuild_20261029/CHARLS_wave2011_person_analytic.dta",
             ("INDV_weight", "bloodweight")),
    "2013": ("derived_wave_tables/CHARLS_wave2013_person_analytic.dta", ("INDV_weight",)),
    "2015": ("derived_wave_tables/CHARLS_wave2015_person_analytic.dta", ("INDV_weight",)),
}
# 2018 has no da001; in 2020 dc004 is a different item ("Checking Day") and da001
# carries special codes, so the comparable series stops at 2015.
BANDS = [(45, 54), (55, 64), (65, 74), (75, 200)]
PUBLIC_OUT = Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "trajectories_v1.json"


def band(age: float) -> str:
    for low, high in BANDS:
        if low <= age <= high:
            return f"{low}–{high if high < 200 else '+'}"
    return "unknown"


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float | None:
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if mask.sum() < 30:
        return None
    return float(np.average(values[mask], weights=weights[mask]))


def main(argv: list[str] | None = None) -> int:
    import pyreadstat
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected wave tables")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected wave tables")

    ages, _ = pyreadstat.read_dta(str(PRIVATE_ROOT / "age_inputs_2011" / "wave1_age_interval_candidate.dta"),
                                  usecols=["ID", "age_at_interview_lower"])
    ages = ages.rename(columns={"age_at_interview_lower": "baseline_age"})
    ages["ID"] = ages["ID"].astype(str)
    ages["band"] = ages["baseline_age"].map(lambda value: band(float(value)) if pd.notna(value) else "unknown")

    frames = {}
    for wave, (relative, candidates) in WAVES.items():
        _, meta = pyreadstat.read_dta(str(PRIVATE_ROOT / relative), metadataonly=True)
        weight_field = next((name for name in candidates if name in meta.column_names), None)
        columns = ["ID", "da001", "dc004"] + ([weight_field] if weight_field else [])
        if {"qi002", "ql002"} <= set(meta.column_names):
            columns += ["qi002", "ql002"]
        frame, _ = pyreadstat.read_dta(str(PRIVATE_ROOT / relative), usecols=columns)
        if weight_field:
            frame = frame.rename(columns={weight_field: "weight"})
        else:
            frame["weight"] = 1.0
        frame["ID"] = frame["ID"].astype(str)
        if wave != "2011":
            # 2013/2015/2020 identifiers carry one extra digit before the person
            # suffix; removing it reproduces the 2011 identifier (85% match).
            frame["ID"] = frame["ID"].str.slice(0, 10) + frame["ID"].str.slice(11)
        frame = frame.merge(ages[["ID", "band"]], on="ID", how="left")
        for column in ("da001", "dc004"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame["srh"] = np.where(frame["da001"].between(1, 5), 6 - frame["da001"], np.nan)
        frame["memory"] = np.where(frame["dc004"].between(1, 5), 6 - frame["dc004"], np.nan)
        if "qi002" in frame.columns and "ql002" in frame.columns:
            height = pd.to_numeric(frame["qi002"], errors="coerce")
            height = np.where(height < 3, height * 100, height)
            weight = pd.to_numeric(frame["ql002"], errors="coerce")
            valid = (height >= 100) & (height <= 250) & (weight >= 20) & (weight <= 300)
            frame["bmi"] = np.where(valid, weight / (height / 100.0) ** 2, np.nan)
        else:
            frame["bmi"] = np.nan
        frames[wave] = frame

    by_wave = []
    for wave, frame in frames.items():
        for label in [f"{low}–{high if high < 200 else '+'}" for low, high in BANDS]:
            subset = frame[frame["band"] == label]
            if subset.empty:
                continue
            by_wave.append({
                "wave": wave,
                "band": label,
                "srh": weighted_mean(subset["srh"].to_numpy(float), subset["weight"].to_numpy(float)),
                "memory": weighted_mean(subset["memory"].to_numpy(float), subset["weight"].to_numpy(float)),
                "bmi": weighted_mean(subset["bmi"].to_numpy(float), subset["weight"].to_numpy(float)),
                "n": int(subset[["srh"]].notna().sum().iloc[0]),
            })

    changes = []
    ordered = list(WAVES)
    for left, right in zip(ordered, ordered[1:]):
        merged = frames[left][["ID", "srh", "memory", "bmi"]].merge(
            frames[right][["ID", "srh", "memory", "bmi"]], on="ID", suffixes=("_left", "_right"))
        merged = merged.merge(frames[right][["ID", "weight"]], on="ID", how="left")
        if merged.empty:
            continue
        for field in ("srh", "memory", "bmi"):
            delta = (merged[f"{field}_right"] - merged[f"{field}_left"]).to_numpy(float)
            changes.append({
                "from": left,
                "to": right,
                "field": field,
                "mean_change": weighted_mean(delta, merged["weight"].to_numpy(float)),
                "n": int(np.isfinite(delta).sum()),
            })

    payload = {
        "schema_version": 1,
        "fields": {"srh": "self-rated health, 1 poor .. 5 excellent",
                   "memory": "self-rated memory, 1 poor .. 5 excellent"},
        "ages": "2011 baseline age band",
        "by_wave": by_wave,
        "changes": changes,
        "waves": ordered,
        "excluded_waves": {"2018": "no da001", "2020": "dc004 field meaning changed; da001 special codes"},
        "id_mapping": "2013/2015/2020 identifiers mapped to 2011 by removing character 11",
    }
    PUBLIC_OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
    print(json.dumps({"waves": ordered, "cells": len(by_wave), "changes": len(changes)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
