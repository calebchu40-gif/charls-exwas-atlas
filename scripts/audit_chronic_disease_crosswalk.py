#!/usr/bin/env python3
"""Aggregate-only QA of raw-wave self-reported diseases vs Harmonized CHARLS D.

The script reads respondent IDs and selected disease fields locally, performs an
ID join in memory, and writes only wave/concept-level counts (never IDs/rows).
It is a crosswalk QA, not an implementation of an official CHARLS derived
outcome. Harmonized CHARLS D is a third-party reference and must be reviewed.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import pandas as pd
import pyreadstat
from project_paths import require_private_path


DISEASES = {
    "hypertension_diagnosis": ("hibpe", 1),
    "dyslipidemia_diagnosis": ("dyslipe", 2),
    "diabetes_diagnosis": ("diabe", 3),
    "chronic_lung_disease_diagnosis": ("lunge", 5),
    "heart_disease_diagnosis": ("hearte", 7),
    "stroke_diagnosis": ("stroke", 8),
    "kidney_disease_diagnosis": ("kidneye", 9),
    "arthritis_diagnosis": ("arthre", 13),
}

WAVES = (2011, 2013, 2015, 2018)


def normalize_id(value: object) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    result = str(value).strip()
    if result.endswith(".0") and result[:-2].isdigit():
        result = result[:-2]
    return result or None


def align_wave_id(value: object, wave: int) -> str | None:
    """Align baseline respondent ID to Wave 2 format per CHARLS release note."""
    result = normalize_id(value)
    if wave == 2011 and result and len(result) == 11 and result.isdigit():
        # The official 2013 release note says to add the household split digit
        # "0" after the 9-digit baseline household ID and retain the final two
        # individual-within-household digits.
        return result[:9] + "0" + result[9:]
    return result


def valid_binary(value: object) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number in (0.0, 1.0)


def numeric_binary(value: object) -> int | None:
    return int(float(value)) if valid_binary(value) else None


def valid_raw_yes_no(value: object) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number in (1.0, 2.0)


def raw_as_binary(value: object) -> int | None:
    if not valid_raw_yes_no(value):
        return None
    return 1 if float(value) == 1.0 else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--derived-dir", type=Path, required=True)
    parser.add_argument("--harmonized-dta", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.derived_dir = require_private_path(args.derived_dir)
    args.harmonized_dta = require_private_path(args.harmonized_dta)
    args.out = require_private_path(args.out)

    _, hmeta = pyreadstat.read_dta(str(args.harmonized_dta), metadataonly=True)
    available = set(hmeta.column_names)
    id_column = "ID" if "ID" in available else next(
        (name for name in available if name.lower() == "id"), None
    )
    if id_column is None:
        raise ValueError("Harmonized CHARLS D has no ID column")

    hcols = [id_column]
    for wave in range(1, 5):
        for suffix, _ in DISEASES.values():
            name = f"r{wave}{suffix}"
            if name in available:
                hcols.append(name)
    harm, _ = pyreadstat.read_dta(str(args.harmonized_dta), usecols=hcols)
    harm["_join_id"] = harm[id_column].map(normalize_id)
    harm = harm.dropna(subset=["_join_id"]).drop_duplicates("_join_id")

    output: list[dict[str, object]] = []
    for wave in WAVES:
        number = WAVES.index(wave) + 1
        raw_path = args.derived_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        _, rmeta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        raw_available = set(rmeta.column_names)
        needed_raw = ["ID"] + [f"da007_{index}_" for _, index in DISEASES.values()]
        raw, _ = pyreadstat.read_dta(
            str(raw_path), usecols=[name for name in needed_raw if name in raw_available]
        )
        raw["_join_id"] = raw["ID"].map(lambda value: align_wave_id(value, wave))
        joined = raw.merge(harm, on="_join_id", how="left", suffixes=("", "_harm"))
        joined["_harm_id_match"] = joined["_join_id"].isin(harm["_join_id"])

        for concept, (suffix, raw_index) in DISEASES.items():
            raw_name = f"da007_{raw_index}_"
            harm_name = f"r{number}{suffix}"
            raw_values = joined[raw_name] if raw_name in joined else pd.Series([None] * len(joined))
            harm_values = joined[harm_name] if harm_name in joined else pd.Series([None] * len(joined))
            raw_valid = raw_values.map(valid_raw_yes_no)
            harm_valid = harm_values.map(valid_binary)
            overlap = raw_valid & harm_valid
            concordant = sum(
                raw_as_binary(left) == numeric_binary(right)
                for left, right in zip(raw_values[overlap], harm_values[overlap])
            )
            n_overlap = int(overlap.sum())
            output.append(
                {
                    "wave": wave,
                    "concept_id": concept,
                    "respondent_rows": len(raw),
                    "harmonized_id_match_rows": int(joined["_harm_id_match"].sum()),
                    "raw_valid_yes_no_1_2_n": int(raw_valid.sum()),
                    "harmonized_valid_0_1_n": int(harm_valid.sum()),
                    "raw_harmonized_valid_overlap_n": n_overlap,
                    "raw_harmonized_concordant_n": concordant,
                    "raw_harmonized_discordant_n": n_overlap - concordant,
                    "crosswalk_status": "aggregate_qa_only_review_required",
                    "qa_note": (
                        "2011 baseline ID adjusted to Wave 2 format per official release note before comparison"
                        if wave == 2011
                        else "Direct raw item vs harmonized ever-status comparison; discrepancies require wave routing and code review"
                    ),
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(output).to_csv(args.out, index=False)


if __name__ == "__main__":
    main()
