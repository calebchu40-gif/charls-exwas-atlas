"""Local aggregate profile of Wave 5 ages and cross-sectional weights.

This checks data availability by age band; it does not establish that any
subgroup is nationally representative. Output stays under the private QA root.
"""
from pathlib import Path

import pandas as pd
import pyreadstat

from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path


AGE_BANDS = ("under_45", "45_49", "50_54", "55_59", "60_plus", "age_missing")
WEIGHTS = ("INDV_weight", "INDV_weight_ad2")
MIN_CELL_N = 10


def age_band(value):
    age = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(age):
        return "age_missing"
    if age < 45:
        return "under_45"
    if age < 50:
        return "45_49"
    if age < 55:
        return "50_54"
    if age < 60:
        return "55_59"
    return "60_plus"


def summarize_age_weights(frame: pd.DataFrame) -> list[dict[str, object]]:
    crosssection = pd.to_numeric(frame["crosssection"], errors="coerce").eq(1)
    bands = frame["xrage"].map(age_band)
    rows = []
    for weight_name in WEIGHTS:
        weight = pd.to_numeric(frame[weight_name], errors="coerce")
        valid_weight = crosssection & weight.gt(0)
        denominator = float(weight[valid_weight].sum())
        for band in AGE_BANDS:
            mask = crosssection & bands.eq(band)
            weighted_mask = mask & weight.gt(0)
            n = int(mask.sum())
            weighted_n = int(weighted_mask.sum())
            suppressed = weighted_n < MIN_CELL_N
            rows.append({
                "wave": 2020,
                "sample": "official_crosssection_flag_1",
                "age_band": band,
                "weight": weight_name,
                "unweighted_n": n if n >= MIN_CELL_N else None,
                "positive_weight_n": weighted_n if not suppressed else None,
                "weighted_population_sum": round(float(weight[weighted_mask].sum()), 2) if not suppressed else None,
                "weighted_percent_of_positive_weight_total": round(100 * float(weight[weighted_mask].sum()) / denominator, 2) if not suppressed and denominator > 0 else None,
                "cell_suppressed_lt_10": suppressed,
                "interpretation": "age/weight coverage only; does not certify subgroup representativeness or settle the official younger-cohort limitation",
            })
    return rows


def main() -> None:
    data_dir = require_private_path(WAVE_DATA_DIR)
    output_dir = require_private_path(QA_OUTPUT_DIR)
    source = data_dir / "CHARLS_wave2020_person_analytic.dta"
    _, meta = pyreadstat.read_dta(str(source), metadataonly=True)
    required = {"xrage", "crosssection", *WEIGHTS}
    missing = sorted(required - set(meta.column_names))
    if missing:
        raise ValueError(f"Wave 5 prepared table lacks required target-coverage fields: {missing}")
    frame, _ = pyreadstat.read_dta(str(source), usecols=sorted(required))
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "wave5_age_target_coverage_v1.csv"
    pd.DataFrame(summarize_age_weights(frame)).to_csv(out, index=False, encoding="utf-8-sig")
    print("Wave 5 age/weight availability summary written to the private QA directory.")


if __name__ == "__main__":
    main()
