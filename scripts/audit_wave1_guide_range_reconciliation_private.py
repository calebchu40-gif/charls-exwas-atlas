#!/usr/bin/env python3
"""Reconcile CHARLS Wave 1 published Blood Guide ranges inside protected storage.

This is a source-consistency QA only. It reads biomarker outcomes and bloodweight,
never IDs; it does not fit models, validate clinical limits, or exclude observations.
All exact ranges and counts are written only under CHARLS_EXWAS_PRIVATE_ROOT.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyreadstat

from prepare_charls_wave_tables import sha256_file
from project_paths import PRIVATE_ROOT, require_private_path
from require_verified_wave1_frame import require_verified_wave1_frame

OUTCOMES = (
    "qc1_vb002", "qc1_vb004", "qc1_vb005", "qc1_vb006", "qc1_vb009",
    "newcho", "newhdl", "newldl", "newtg", "newglu", "newhba1c",
    "newcrp", "newbun", "newcrea", "newua",
)
# Official Blood Users' Guide Table 4/5 descriptive ranges (printed pages 13-14).
# These are comparison references only, not validity bounds or trimming rules.
GUIDE_RANGES = {
    "qc1_vb002": (1.14, 110.80), "qc1_vb004": (5.44, 27.88),
    "qc1_vb005": (14.10, 78.40), "qc1_vb006": (20.70, 132.90),
    "qc1_vb009": (10.0, 1990.0), "newcrp": (0.01, 178.10),
    "newhba1c": (3.5, 14.5), "newcho": (23.97, 627.07),
    "newhdl": (3.09, 158.89), "newldl": (0.39, 385.83),
    "newtg": (2.66, 1904.52), "newbun": (3.75, 89.32),
    "newcrea": (0.18, 11.55), "newglu": (18.0, 722.7),
    "newua": (0.26, 13.31),
}
# The guide labels the Table 4/5 descriptive statistics as weighted while its
# N column is explicitly unweighted. Reconcile the N column separately.
GUIDE_UNWEIGHTED_N = {
    "qc1_vb002": 11528, "qc1_vb004": 11530, "qc1_vb005": 11839,
    "qc1_vb006": 11532, "qc1_vb009": 11531, "newcho": 11655,
    "newhdl": 11663, "newldl": 11642, "newtg": 11656,
    "newglu": 11636, "newhba1c": 11706, "newcrp": 11664,
    "newbun": 11662, "newcrea": 11634, "newua": 11664,
}
DEFAULT_BLOOD = PRIVATE_ROOT / "incoming_2011_official" / "Blood_20140429.dta"
DEFAULT_PERSON = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_guide_range_reconciliation_private.json"


def private(path: Path) -> Path:
    result = require_private_path(path)
    if not result.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("All inputs and outputs must remain inside the protected private root")
    return result


def rounded_range(values: np.ndarray) -> list[float] | None:
    if not values.size:
        return None
    return [round(float(np.min(values)), 2), round(float(np.max(values)), 2)]


def run(blood_path: Path, person_path: Path, output_path: Path) -> dict[str, Any]:
    blood_path, person_path, output_path = map(private, (blood_path, person_path, output_path))
    if not blood_path.is_file() or not person_path.is_file():
        raise FileNotFoundError("Protected official Blood input or source-bound person table is missing")
    source = require_verified_wave1_frame(data_path=person_path)
    columns = [*OUTCOMES, "bloodweight"]
    frame, _ = pyreadstat.read_dta(str(blood_path), usecols=columns)
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Required Blood columns are missing: {missing}")

    weight = pd.to_numeric(frame["bloodweight"], errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
    positive_weight = np.isfinite(weight) & (weight > 0)
    rows: list[dict[str, Any]] = []
    for field in OUTCOMES:
        values = pd.to_numeric(frame[field], errors="coerce").to_numpy(dtype="float64", na_value=np.nan)
        finite = np.isfinite(values)
        all_values = values[finite]
        weighted_frame_values = values[finite & positive_weight]
        guide = [round(float(x), 2) for x in GUIDE_RANGES[field]]
        all_range = rounded_range(all_values)
        positive_weight_range = rounded_range(weighted_frame_values)
        rows.append({
            "field": field,
            "guide_table_unweighted_n": GUIDE_UNWEIGHTED_N[field],
            "all_finite_n_matches_guide": int(all_values.size) == GUIDE_UNWEIGHTED_N[field],
            "positive_bloodweight_finite_n_matches_guide": int(weighted_frame_values.size) == GUIDE_UNWEIGHTED_N[field],
            "guide_table_range": guide,
            "all_finite_range_unweighted": all_range,
            "positive_bloodweight_finite_range_unweighted": positive_weight_range,
            "all_finite_range_matches_guide_to_2dp": all_range == guide,
            "positive_bloodweight_range_matches_guide_to_2dp": positive_weight_range == guide,
            "n_finite_all": int(all_values.size),
            "n_finite_positive_bloodweight": int(weighted_frame_values.size),
            "n_finite_nonpositive_or_missing_bloodweight": int((finite & ~positive_weight).sum()),
            "n_negative_all": int((all_values < 0).sum()),
            "n_zero_all": int((all_values == 0).sum()),
            "rule": "diagnostic_source_reconciliation_only_never_an_exclusion_rule",
        })

    report = {
        "status": "source_bound_guide_range_reconciliation_complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": source["source_manifest_id"],
        "source_identity_status": source["source_identity_status"],
        "prepared_person_table_sha256": source["prepared_output_sha256"],
        "blood_source_sha256": sha256_file(blood_path),
        "guide_source": "CHARLS Blood Data Users' Guide Tables 4-5, printed pages 13-14",
        "guide_table_note": "Tables label descriptive statistics as weighted and the N column as unweighted; the range comparison remains descriptive source reconciliation only.",
        "fields_read": list(OUTCOMES) + ["bloodweight"],
        "identifier_fields_read": False,
        "association_models_fitted": False,
        "weighted_statistics_computed": False,
        "interpretation": (
            "Compare published descriptive endpoints across all finite records and the positive-bloodweight frame. "
            "A match does not prove validity or absence of special codes; a mismatch does not authorize exclusion, "
            "recoding, or a cutoff. No values are selected based on these comparisons."
        ),
        "outcomes": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(output_path, 0o600)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blood", type=Path, default=DEFAULT_BLOOD)
    parser.add_argument("--person", type=Path, default=DEFAULT_PERSON)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.blood, args.person, args.output)
    print(json.dumps({
        "status": report["status"],
        "outcomes_profiled": len(report["outcomes"]),
        "source_identity_status": report["source_identity_status"],
        "identifiers_read": False,
        "association_models_fitted": False,
        "output_private": True,
    }))


if __name__ == "__main__":
    main()
