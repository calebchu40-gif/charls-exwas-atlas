#!/usr/bin/env python3
"""Create a restricted, aggregate-only QA profile for prespecified Wave 1 biomarkers.

This reads outcome columns from the authorized Blood file but never reads or
exports identifiers. The profile is diagnostic only: observed distributions
must not be used to invent validity cutoffs, decode fasting, or select models.
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
    "newtg", "newcrea", "newbun", "newhdl", "newldl", "newcho", "newglu",
    "newua", "newcrp", "newhba1c",
)
QUANTILES = (0.001, 0.01, 0.5, 0.99, 0.999)
# Ranges transcribed from the CHARLS Blood Users' Guide assay-method table.
# They describe assay method metadata only, never analytic validity cutoffs.
GUIDE_ASSAY_RANGES = {
    "newtg": (4.0, 1000.0), "newcrea": (0.1, 25.0), "newbun": (5.0, 100.0),
    "newhdl": (3.0, 120.0), "newldl": (3.0, 400.0), "newcho": (3.0, 800.0),
    "newglu": (2.0, 450.0), "newua": (None, 20.0), "newcrp": (0.1, 20.0),
    "newhba1c": (0.0, 40.0),
}
DEFAULT_BLOOD = PRIVATE_ROOT / "incoming_2011_official" / "Blood_20140429.dta"
DEFAULT_PERSON = PRIVATE_ROOT / "derived_wave_tables_2011_official_rebuild_20261029" / "CHARLS_wave2011_person_analytic.dta"
DEFAULT_OUTPUT = PRIVATE_ROOT / "qa_outputs" / "wave1_biomarker_value_profile_private.json"


def private(path: Path) -> Path:
    result = require_private_path(path)
    if not result.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ValueError("All inputs and outputs must remain inside the protected private root")
    return result


def run(blood_path: Path, person_path: Path, output_path: Path) -> dict[str, Any]:
    blood_path, person_path, output_path = map(private, (blood_path, person_path, output_path))
    if not blood_path.is_file() or not person_path.is_file():
        raise FileNotFoundError("Protected official Blood input or source-bound person table is missing")
    source = require_verified_wave1_frame(data_path=person_path)
    frame, meta = pyreadstat.read_dta(str(blood_path), usecols=list(OUTCOMES))
    missing = sorted(set(OUTCOMES) - set(frame.columns))
    if missing:
        raise ValueError(f"Expected outcome columns missing from official Blood file: {missing}")
    frame = frame.loc[:, list(OUTCOMES)]

    fields: list[dict[str, Any]] = []
    for name in OUTCOMES:
        raw = frame[name]
        values = pd.to_numeric(raw, errors="coerce")
        array = values.to_numpy(dtype="float64", na_value=np.nan)
        finite = array[np.isfinite(array)]
        source_present = raw.notna().to_numpy()
        parsed_missing = values.isna().to_numpy()
        nonfinite_nonmissing = int((values.notna().to_numpy() & ~np.isfinite(array)).sum())
        summary: dict[str, Any] = {
            "field": name,
            "n_rows": int(len(array)),
            "n_source_missing_or_stata_missing": int(raw.isna().sum()),
            "n_numeric_parse_failures": int((source_present & parsed_missing).sum()),
            "n_nonfinite_nonmissing": nonfinite_nonmissing,
            "n_finite": int(finite.size),
            "n_negative": int((finite < 0).sum()),
            "n_zero": int((finite == 0).sum()),
            "n_positive": int((finite > 0).sum()),
            "quantiles_unweighted_diagnostic_only": {},
            "outside_guide_assay_range_diagnostic_only": None,
        }
        if finite.size:
            quant = np.quantile(finite, QUANTILES)
            summary["min_diagnostic_only"] = float(np.min(finite))
            summary["max_diagnostic_only"] = float(np.max(finite))
            summary["quantiles_unweighted_diagnostic_only"] = {
                f"p{q * 100:g}": float(value) for q, value in zip(QUANTILES, quant, strict=True)
            }
            bounds = GUIDE_ASSAY_RANGES.get(name)
            if bounds is not None:
                lower, upper = bounds
                summary["outside_guide_assay_range_diagnostic_only"] = bool(
                    (lower is not None and np.min(finite) < lower)
                    or (upper is not None and np.max(finite) > upper)
                )
        fields.append(summary)

    report = {
        "status": "restricted_aggregate_value_profile_complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_id": source["source_manifest_id"],
        "source_identity_status": source["source_identity_status"],
        "prepared_person_table_sha256": source["prepared_output_sha256"],
        "blood_source_sha256": sha256_file(blood_path),
        "fields_read": list(OUTCOMES),
        "identifiers_read": False,
        "association_models_fitted": False,
        "weights_used": False,
        "statistics_are_unweighted_diagnostics_only": True,
        "rule": "Do not infer fasting codes, special missing codes, or validity cutoffs from these distributions. Guide assay-range comparisons are diagnostic only and never imply exclusion. Any exclusions require authoritative source documentation and pre-model review.",
        "outcomes": fields,
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
        "association_models_fitted": False,
        "identifiers_read": False,
        "output_private": True,
    }))


if __name__ == "__main__":
    main()
