#!/usr/bin/env python3
"""Create protected Wave 4/5 cumulative doctor-diagnosis outcome tables.

Only documented positive carry-forward values and routed current yes/no answers
are used. Ambiguous routes remain missing or are tagged as conflicts. The
input prepared-table hash must match its protected manifest; outputs remain
under CHARLS_EXWAS_PRIVATE_ROOT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyreadstat

from project_paths import PRIVATE_ROOT, require_private_path


PRIVATE = PRIVATE_ROOT.resolve()
TABLE_DIR = PRIVATE / "derived_wave_tables_2018_2020_sample_info_spine_20261030"
BASE_COLUMNS = ("ID", "crosssection", "INDV_weight_ad2", "communityID")
DISEASES: dict[str, tuple[tuple[str, str, int], ...]] = {
    "2018": (
        ("hypertension_diagnosis", "Hypertension", 1),
        ("dyslipidemia_diagnosis", "Dyslipidemia", 2),
        ("diabetes_high_blood_sugar_diagnosis", "Diabetes or high blood sugar", 3),
        ("cancer_diagnosis", "Cancer or malignant tumor", 4),
        ("chronic_lung_disease_diagnosis", "Chronic lung diseases", 5),
        ("liver_disease_diagnosis", "Liver disease", 6),
        ("heart_disease_diagnosis", "Heart disease", 7),
        ("stroke_diagnosis", "Stroke", 8),
        ("kidney_disease_diagnosis", "Kidney disease", 9),
        ("digestive_disease_diagnosis", "Stomach or digestive disease", 10),
        ("emotional_psychiatric_diagnosis", "Emotional or psychiatric problems", 11),
        ("memory_related_disease_diagnosis", "Memory-related disease", 12),
        ("arthritis_rheumatism_diagnosis", "Arthritis or rheumatism", 13),
        ("asthma_diagnosis", "Asthma", 14),
    ),
    "2020": (
        ("hypertension_diagnosis", "Hypertension", 1),
        ("dyslipidemia_diagnosis", "Dyslipidemia", 2),
        ("diabetes_high_blood_sugar_diagnosis", "Diabetes or high blood sugar", 3),
        ("cancer_diagnosis", "Cancer or malignant tumor", 4),
        ("chronic_lung_disease_diagnosis", "Chronic lung diseases", 5),
        ("liver_disease_diagnosis", "Liver disease", 6),
        ("heart_disease_diagnosis", "Heart disease", 7),
        ("stroke_diagnosis", "Stroke", 8),
        ("kidney_disease_diagnosis", "Kidney disease", 9),
        ("digestive_disease_diagnosis", "Stomach or digestive disease", 10),
        ("emotional_psychiatric_diagnosis", "Emotional or psychiatric problems", 11),
        ("memory_related_disease_diagnosis", "Memory-related disease", 12),
        ("parkinsons_diagnosis", "Parkinson's disease", 13),
        ("arthritis_rheumatism_diagnosis", "Arthritis or rheumatism", 14),
        ("asthma_diagnosis", "Asthma", 15),
    ),
}


def private_path(path: Path) -> Path:
    resolved = require_private_path(path)
    if not resolved.is_relative_to(PRIVATE):
        raise ValueError(f"CHARLS input/output path escaped protected storage: {resolved}")
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def diagnosis_state(wave: str, prior: Any, current: Any,
                    comparison: Any = None) -> tuple[float, str]:
    """Return 1/0/NaN plus a route state; never infer No from a blank."""
    p, c, comp = _number(prior), _number(current), _number(comparison)
    if wave == "2018":
        if p == 1.0:
            return (1.0, "prior_positive") if c is None else (math.nan, "route_conflict")
        if p is not None:
            return math.nan, "unsupported_prior_code"
        if c == 1.0:
            return 1.0, "current_yes"
        if c == 2.0:
            return 0.0, "current_no"
        return (math.nan, "missing_or_not_routed") if c is None else (math.nan, "unsupported_current_code")

    if wave != "2020":
        raise ValueError(f"Unsupported wave: {wave}")
    if p == 1.0:
        if c is not None:
            return math.nan, "route_conflict"
        if comp == 99.0:
            return math.nan, "route_conflict"
        if comp is None or comp in (1.0, 2.0, 3.0):
            return 1.0, "prior_positive"
        return math.nan, "unsupported_comparison_code"
    if p is not None:
        return math.nan, "unsupported_prior_code"
    if comp is not None:
        return math.nan, "route_conflict"
    if c == 1.0:
        return 1.0, "current_yes"
    if c == 2.0:
        return 0.0, "current_no"
    return (math.nan, "missing_or_not_routed") if c is None else (math.nan, "unsupported_current_code")


def _find_column(columns: list[str], wanted: str) -> str:
    matches = [column for column in columns if column.casefold() == wanted.casefold()]
    if len(matches) != 1:
        raise ValueError(f"Required source field missing or ambiguous: {wanted}")
    return matches[0]


def _manifest_binding(wave: str, manifest_path: Path, data_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = [entry for entry in manifest.get("waves", []) if str(entry.get("wave")) == wave]
    if len(records) != 1:
        raise ValueError(f"Protected prepared-data manifest has no unique Wave {wave} record")
    output = records[0].get("prepared_output", {})
    if output.get("filename") != data_path.name or output.get("sha256") != sha256(data_path):
        raise ValueError(f"Wave {wave} input does not match its protected prepared-table manifest")
    return {
        "prepared_manifest_sha256_private": sha256(manifest_path),
        "prepared_table_sha256_private": sha256(data_path),
        "source_archive_record": records[0].get("source_archive"),
        "source_inputs_record": records[0].get("source_inputs"),
    }


def derive(wave: str, code_commit: str, table_dir: Path | None = None) -> dict[str, Any]:
    if wave not in DISEASES:
        raise ValueError("Wave must be 2018 or 2020")
    if len(code_commit) not in range(7, 41) or any(ch not in "0123456789abcdef" for ch in code_commit):
        raise ValueError("Pass the public analysis-code commit SHA")

    # The active protected builder writes all waves to derived_wave_tables.
    # Keep the older dated directory only as a caller override for archived runs.
    selected_table_dir = private_path(table_dir) if table_dir is not None else private_path(PRIVATE / "derived_wave_tables")
    data_path = private_path(selected_table_dir / f"CHARLS_wave{wave}_person_analytic.dta")
    manifest_path = private_path(selected_table_dir / "prepared_data_manifest.json")
    if not data_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("Protected Wave 4/5 prepared table or manifest is absent")
    binding = _manifest_binding(wave, manifest_path, data_path)
    _, metadata = pyreadstat.read_dta(str(data_path), metadataonly=True)
    columns = list(metadata.column_names)
    id_field, frame_field, weight_field, psu_field = [
        _find_column(columns, name) for name in BASE_COLUMNS
    ]

    routes: list[tuple[str, str, str, str | None, int, str]] = []
    usecols = [id_field, frame_field, weight_field, psu_field]
    for concept, label, index in DISEASES[wave]:
        if wave == "2018":
            current_name, prior_name, comparison_name = f"da007_{index}_", f"zdiagnosed_{index}_", None
        else:
            current_name, prior_name, comparison_name = f"da003_{index}_", f"zdisease_{index}_", f"da002_{index}_"
        current_field, prior_field = _find_column(columns, current_name), _find_column(columns, prior_name)
        comparison_field = _find_column(columns, comparison_name) if comparison_name else None
        routes.append((concept, label, current_field, prior_field, index, comparison_field or ""))
        usecols.extend(field for field in (current_field, prior_field, comparison_field) if field)

    data, _ = pyreadstat.read_dta(str(data_path), usecols=list(dict.fromkeys(usecols)))
    if data[id_field].isna().any() or data[id_field].duplicated().any():
        raise ValueError("Prepared respondent table contains missing or duplicate IDs")
    frame_values = pd.to_numeric(data[frame_field], errors="coerce")
    if frame_values.isna().any() or (set(frame_values.unique()) - {0, 1}):
        raise ValueError("crosssection contains codes outside the documented 0/1 domain")

    state_counts: dict[str, dict[str, int]] = {}
    for concept, label, current_field, prior_field, index, comparison_field in routes:
        outcomes, states = [], []
        for record in data[[prior_field, current_field, comparison_field]].itertuples(index=False, name=None) if comparison_field else data[[prior_field, current_field]].itertuples(index=False, name=None):
            prior = record[0]
            current = record[1]
            comparison = record[2] if comparison_field else None
            value, state = diagnosis_state(wave, prior, current, comparison)
            outcomes.append(value)
            states.append(state)
        data[f"{concept}_ever_doctor_diagnosed"] = outcomes
        data[f"{concept}_source_route_state"] = states
        state_counts[concept] = dict(sorted(Counter(states).items()))

    outcols = [id_field, frame_field, weight_field, psu_field]
    for concept, _, *_ in routes:
        outcols.extend([f"{concept}_ever_doctor_diagnosed", f"{concept}_source_route_state"])
    output_data = data[outcols]
    result_path = private_path(PRIVATE / "derived_wave_tables" / f"CHARLS_wave{wave}_doctor_diagnosis_outcomes_route_derived.dta")
    qa_path = private_path(PRIVATE / "qa_outputs" / f"wave{wave}_doctor_diagnosis_outcome_routes_private.json")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(result_path.parent, 0o700)
        os.chmod(qa_path.parent, 0o700)
    temp_result = private_path(result_path.with_name(result_path.stem + ".tmp.dta"))
    temp_qa = private_path(qa_path.with_name(qa_path.stem + ".tmp.json"))
    if any(path.exists() for path in (result_path, qa_path, temp_result, temp_qa)):
        raise FileExistsError("Protected outcome derivation artifacts already exist; refusing overwrite")
    pyreadstat.write_dta(output_data, str(temp_result), version=15)
    if os.name == "posix":
        os.chmod(temp_result, 0o600)
    summary = {
        "scope": "protected Wave 4/5 cumulative doctor-diagnosis outcome derivation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "wave": wave,
        "outcome_definition": "prior-wave doctor-diagnosed positive or current routed doctor-diagnosis yes; explicit current no only when on the no-prior route; unresolved routes remain missing",
        "source_rule_version": "wave4_wave5_chronic_disease_outcome_routes_2026-11-01",
        "disease_concepts": [{"concept_id": concept, "label": label, "source_index": index,
                              "current_field": current, "prior_field": prior, "comparison_field": comparison or None}
                             for concept, label, current, prior, index, comparison in routes],
        "row_count_private": int(len(output_data)),
        "state_counts_private": state_counts,
        "input_bindings_private": binding,
        "result_file_private": result_path.name,
        "result_sha256_private": sha256(temp_result),
        "code_commit": code_commit,
        "publication": "not a public result; participant-level derivation and exact QA remain private",
    }
    temp_qa.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        os.chmod(temp_qa, 0o600)
    os.replace(temp_result, result_path)
    os.replace(temp_qa, qa_path)
    return {"status": "private_outcome_derivation_complete", "wave": wave,
            "concepts": len(routes), "output": result_path.name}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=("2018", "2020"), required=True)
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--data-dir", type=Path, help="Optional protected prepared-table directory; defaults to private/derived_wave_tables")
    args = parser.parse_args()
    print(json.dumps(derive(args.wave, args.code_commit, args.data_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
