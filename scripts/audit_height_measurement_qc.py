"""Aggregate-only CHARLS measured-height special-code and compliance audit."""
from pathlib import Path
from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR

import pandas as pd
import pyreadstat


DATA = WAVE_DATA_DIR
OUT = QA_OUTPUT_DIR / "height_measurement_qc_aggregate_v1.csv"
WAVES = ["2011", "2013", "2015"]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for wave in WAVES:
        path = DATA / f"CHARLS_wave{wave}_person_analytic.dta"
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        cols = set(meta.column_names)
        data, _ = pyreadstat.read_dta(str(path), usecols=[c for c in ["qi002", "qi003"] if c in cols])
        height = pd.to_numeric(data["qi002"], errors="coerce")
        compliance = data["qi003"].astype(str).str.strip()
        buckets = {
            "height_official_range_0_210_cm": int(height.between(0, 210, inclusive="both").sum()),
            "height_993_unable": int(height.eq(993).sum()),
            "height_999_refused": int(height.eq(999).sum()),
            "height_other_numeric_code_or_out_of_range": int((height.notna() & ~height.between(0, 210, inclusive="both") & ~height.isin([993, 999])).sum()),
            "height_missing": int(height.isna().sum()),
        }
        for bucket, count in buckets.items():
            rows.append({"wave": wave, "field": "qi002", "category": bucket, "n": count,
                         "interpretation": "Official questionnaire range/special codes; no distribution-based trimming."})
        vc = compliance.value_counts(dropna=False)
        for category, count in vc.items():
            label = "blank_or_missing" if category in ["", "nan", "None"] else str(category)
            rows.append({"wave": wave, "field": "qi003", "category": label, "n": int(count),
                         "interpretation": "Compliance response category retained as released; not used as an exclusion rule."})
    pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8-sig")
    summary = pd.DataFrame(rows)
    print(summary[summary.field == "qi002"].pivot(index="wave", columns="category", values="n").to_string())
    print(f"wrote {len(rows)} aggregate rows to {OUT}")


if __name__ == "__main__":
    main()
