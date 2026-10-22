"""Aggregate-only audit of CHARLS physical-activity module eligibility."""
from pathlib import Path
from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR

import pandas as pd
import pyreadstat


DATA = WAVE_DATA_DIR
OUT = QA_OUTPUT_DIR / "activity_subsample_aggregate_v1.csv"
WAVES = ["2011", "2013", "2015", "2018", "2020"]


def nonblank(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype(str).str.strip().ne("")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for wave in WAVES:
        path = DATA / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        names = set(meta.column_names)
        activity_prefix = "da032_" if wave == "2020" else "da051_"
        activity_vars = [
            f"{activity_prefix}{i}_" for i in (1, 2, 3)
            if f"{activity_prefix}{i}_" in names
        ]
        assignment = "da051_random" if "da051_random" in names else None
        weight = next((v for v in ["INDV_weight_ad2", "INDV_weight", "ind_weight_ad2", "ind_weight"] if v in names), None)
        usecols = ["ID", *activity_vars]
        if assignment:
            usecols.append(assignment)
        if weight:
            usecols.append(weight)
        data, _ = pyreadstat.read_dta(str(path), usecols=usecols)
        answered = pd.Series(False, index=data.index)
        for var in activity_vars:
            answered |= nonblank(data[var])
        valid_counts = {
            var: int(data[var].astype(str).str.strip().isin(["1", "2", "1.0", "2.0"]).sum())
            for var in activity_vars
        }
        positive_weight_n = None
        if weight:
            positive_weight_n = int(pd.to_numeric(data[weight], errors="coerce").gt(0).sum())

        if assignment:
            assign = data[assignment].astype(str).str.strip()
            groups = sorted(x for x in assign.unique() if x)
            for group in groups:
                in_group = assign.eq(group)
                rows.append({
                    "wave": wave,
                    "record_type": "assignment_group",
                    "activity_assignment_field": assignment,
                    "assignment_code_uninterpreted": group,
                    "n_group": int(in_group.sum()),
                    "n_any_activity_nonblank": int((in_group & answered).sum()),
                    "n_all_activity_blank": int((in_group & ~answered).sum()),
                    "n_positive_individual_weight": int((in_group & pd.to_numeric(data[weight], errors="coerce").gt(0)).sum()) if weight else None,
                    "activity_fields": ";".join(activity_vars),
                    "field_valid_1_or_2_counts": str(valid_counts),
                    "interpretation": "Assignment code retained without semantic recoding; compare assignment and response only.",
                })
            unassigned = assign.eq("")
            rows.append({
                "wave": wave,
                "record_type": "assignment_missing",
                "activity_assignment_field": assignment,
                "assignment_code_uninterpreted": "blank",
                "n_group": int(unassigned.sum()),
                "n_any_activity_nonblank": int((unassigned & answered).sum()),
                "n_all_activity_blank": int((unassigned & ~answered).sum()),
                "n_positive_individual_weight": int((unassigned & pd.to_numeric(data[weight], errors="coerce").gt(0)).sum()) if weight else None,
                "activity_fields": ";".join(activity_vars),
                "field_valid_1_or_2_counts": str(valid_counts),
                "interpretation": "Blank assignment is not recoded as eligible or ineligible.",
            })
        rows.append({
            "wave": wave,
            "record_type": "wave_summary",
            "activity_assignment_field": assignment or "not present in released person table",
            "assignment_code_uninterpreted": "",
            "n_group": len(data),
            "n_any_activity_nonblank": int(answered.sum()),
            "n_all_activity_blank": int((~answered).sum()),
            "n_positive_individual_weight": positive_weight_n,
            "activity_fields": ";".join(activity_vars),
            "field_valid_1_or_2_counts": str(valid_counts),
            "interpretation": "Nonblank/valid response coverage only; blank is not treated as no physical activity.",
        })

    result = pd.DataFrame(rows)
    result.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"wrote {len(result)} aggregate rows to {OUT}")
    print(result[result.record_type == "wave_summary"][[
        "wave", "n_group", "n_any_activity_nonblank", "n_all_activity_blank", "n_positive_individual_weight"
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
