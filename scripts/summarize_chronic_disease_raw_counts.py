#!/usr/bin/env python3
"""Write aggregate-only yes/no/missing counts for selected raw CHARLS diseases."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pyreadstat


DISEASE_INDEX = {
    "hypertension_diagnosis": {2011: 1, 2013: 1, 2015: 1, 2018: 1, 2020: 1},
    "dyslipidemia_diagnosis": {2011: 2, 2013: 2, 2015: 2, 2018: 2, 2020: 2},
    "diabetes_diagnosis": {2011: 3, 2013: 3, 2015: 3, 2018: 3, 2020: 3},
    "chronic_lung_disease_diagnosis": {2011: 5, 2013: 5, 2015: 5, 2018: 5, 2020: 5},
    "heart_disease_diagnosis": {2011: 7, 2013: 7, 2015: 7, 2018: 7, 2020: 7},
    "stroke_diagnosis": {2011: 8, 2013: 8, 2015: 8, 2018: 8, 2020: 8},
    "kidney_disease_diagnosis": {2011: 9, 2013: 9, 2015: 9, 2018: 9, 2020: 9},
    "arthritis_diagnosis": {2011: 13, 2013: 13, 2015: 13, 2018: 13, 2020: 14},
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    output: list[dict[str, object]] = []
    for wave in (2011, 2013, 2015, 2018, 2020):
        file = args.data_dir / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(file), metadataonly=True)
        columns = set(meta.column_names)
        fields = {
            concept: f"da{'003' if wave == 2020 else '007'}_{index}_"
            for concept, indices in DISEASE_INDEX.items()
            for index in [indices[wave]]
        }
        available = [field for field in fields.values() if field in columns]
        data, _ = pyreadstat.read_dta(str(file), usecols=available)

        for concept, field in fields.items():
            if field not in data:
                output.append({
                    "wave": wave,
                    "concept_id": concept,
                    "raw_variable": field,
                    "respondent_rows": len(data),
                    "n_yes_code_1": 0,
                    "n_no_code_2": 0,
                    "n_other_nonmissing": 0,
                    "n_missing": len(data),
                    "status": "field_not_found",
                })
                continue
            values = pd.to_numeric(data[field], errors="coerce")
            output.append({
                "wave": wave,
                "concept_id": concept,
                "raw_variable": field,
                "respondent_rows": len(data),
                "n_yes_code_1": int((values == 1).sum()),
                "n_no_code_2": int((values == 2).sum()),
                "n_other_nonmissing": int((values.notna() & ~values.isin([1, 2])).sum()),
                "n_missing": int(values.isna().sum()),
                "status": "raw_response_counts_only_routing_not_resolved",
            })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(output).to_csv(args.out, index=False)


if __name__ == "__main__":
    main()
