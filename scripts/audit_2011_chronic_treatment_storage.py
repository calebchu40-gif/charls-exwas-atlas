"""Aggregate-only QA of 2011 CHARLS disease-treatment option storage.

Reads only the 32 option columns from the protected prepared Wave 1 table.
The output contains field-level pass/fail indicators only, no respondent data,
IDs, response values, or exact counts.
"""
from __future__ import annotations

from pathlib import Path
import argparse

import pandas as pd
import pyreadstat

from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path


DISEASES = {
    "2": "dyslipidemia",
    "5": "chronic_lung_disease",
    "6": "liver_disease",
    "7": "heart_disease",
    "9": "kidney_disease",
    "10": "digestive_disease",
    "12": "memory_related_disease",
    "13": "arthritis_rheumatism",
}
OPTIONS = ("1", "2", "3", "4")


def expected_columns() -> list[str]:
    return [f"da010_{disease}_s{option}" for disease in DISEASES for option in OPTIONS]


def summarize_group(frame: pd.DataFrame, disease: str) -> dict[str, object]:
    columns = [f"da010_{disease}_s{option}" for option in OPTIONS]
    numeric = frame[columns].apply(pd.to_numeric, errors="coerce")
    present = numeric.notna()
    expected = pd.DataFrame(
        {column: option for column, option in zip(columns, (1, 2, 3, 4))},
        index=numeric.index,
    )
    mismatches = present & numeric.ne(expected)
    none_selected = present[columns[-1]]
    any_other_selected = present[columns[:-1]].any(axis=1)
    diagnosis = pd.to_numeric(frame[f"da007_{disease}_"], errors="coerce")
    any_treatment_answer = present.any(axis=1)
    return {
        "wave": "2011",
        "disease_index": disease,
        "field_count": len(columns),
        "all_fields_observed": bool(present.any(axis=0).all()),
        "all_nonmissing_values_match_option_index": not bool(mismatches.any().any()),
        "none_option_never_cooccurs_with_treatment_option": not bool(
            (none_selected & any_other_selected).any()
        ),
        "treatment_observed_when_doctor_diagnosis_response_is_no": bool(
            (any_treatment_answer & diagnosis.eq(2)).any()
        ),
        "interpretation": (
            "aggregate storage-pattern check on local prepared table only; "
            "does not establish source archive identity, response denominator, "
            "sample design, or model eligibility"
        ),
    }


def audit_frame(frame: pd.DataFrame) -> list[dict[str, object]]:
    expected = expected_columns()
    route_columns = [f"da007_{disease}_" for disease in DISEASES]
    missing = sorted((set(expected) | set(route_columns)) - {name.lower() for name in frame.columns})
    if missing:
        raise ValueError(f"Wave 1 prepared table is missing {len(missing)} audit fields")
    normalized = {name.lower(): name for name in frame.columns}
    normalized_frame = frame.rename(columns={value: key for key, value in normalized.items()})
    return [summarize_group(normalized_frame, disease) for disease in DISEASES]


def run(data_dir: Path = WAVE_DATA_DIR, output_dir: Path = QA_OUTPUT_DIR) -> Path:
    data_dir = require_private_path(data_dir)
    output_dir = require_private_path(output_dir)
    table_path = data_dir / "CHARLS_wave2011_person_analytic.dta"
    _, meta = pyreadstat.read_dta(str(table_path), metadataonly=True)
    by_lower = {name.lower(): name for name in meta.column_names}
    missing = sorted(set(expected_columns()) - set(by_lower))
    if missing:
        raise ValueError(f"Wave 1 prepared table is missing {len(missing)} treatment option fields")
    route_columns = [f"da007_{disease}_" for disease in DISEASES]
    frame, _ = pyreadstat.read_dta(
        str(table_path), usecols=[by_lower[name] for name in expected_columns() + route_columns]
    )
    rows = audit_frame(frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "chronic_treatment_storage_2011_aggregate_qa.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=WAVE_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=QA_OUTPUT_DIR)
    args = parser.parse_args()
    output_path = run(args.data_dir, args.output_dir)
    print(f"Wrote eight disease-level storage summaries to protected local output: {output_path}")
    print("No respondent IDs, response values, or exact response counts were exported.")


if __name__ == "__main__":
    main()
