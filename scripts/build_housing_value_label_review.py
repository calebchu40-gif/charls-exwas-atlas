"""Build wave-specific reviewed response labels for common dwelling fields."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
raw = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

LABELS = {
    "i015": ("1=Yes; 2=No", ["2011", "2013", "2015", "2018"]),
    "i016": ("1=Yes; 2=No", ["2011", "2013", "2018"]),
    "i017": ("1=Yes; 2=No", ["2011", "2013", "2015", "2018"]),
    "i018": ("1=Hot water provided; 2=Water heater installed by the household; 3=No", ["2011", "2013", "2015", "2018"]),
    "i019": ("1=Yes; 2=No", ["2011", "2013", "2015", "2018"]),
    "i020": ("1=Yes; 2=No", ["2011", "2013", "2015", "2018"]),
}
rows = []
for code, (labels, waves) in LABELS.items():
    for wave in waves:
        found = raw[(raw.wave == wave) & (raw.variable.str.lower() == code.lower())]
        if found.empty:
            raise SystemExit(f"Official variable catalog has no {wave} {code}; check mapping.")
        rows.append({
            "wave": wave, "code": code, "value_labels": labels,
            "value_label_status": "Official codebook response labels reviewed",
            "value_label_source": f"sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        })
out = pd.DataFrame(rows)
out.to_csv(ROOT / "audit/housing_value_label_review_v1.csv", index=False, encoding="utf-8-sig")
print(f"reviewed housing value labels={len(out)}; distinct fields={out.code.nunique()}; waves={out.wave.nunique()}")
