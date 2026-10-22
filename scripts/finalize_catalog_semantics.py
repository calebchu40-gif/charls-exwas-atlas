"""Preserve reviewed partial-label and internal-measure notes in site series."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
fields = pd.read_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv", dtype=str, encoding="utf-8-sig").fillna("")
series_path = ROOT / "audit/charls_atlas_candidate_series_v0.csv"
series = pd.read_csv(series_path, dtype=str, encoding="utf-8-sig").fillna("")
if "harmonization_status" not in series:
    series["harmonization_status"] = ""
for idx, item in series.iterrows():
    selected = (
        fields["epcf"].eq(item["epcf"]) & fields["category"].eq(item["category"])
        & fields["subcategory"].eq(item["subcategory"])
        & fields["Variable.Name"].str.lower().eq(str(item["Variable.Name"]).lower())
    )
    rows = fields.loc[selected]
    partial = rows.loc[
        rows["Value.Label.Review"].str.startswith("official Codebook extraction exposes only a partial response-code set"),
        "Value.Label.Review",
    ]
    if not partial.empty:
        series.at[idx, "value_label_review"] = partial.iloc[0]
    numeric = rows.loc[
        rows["Value.Label.Review"].str.startswith(("continuous count measure", "continuous recorded response", "continuous raw subtraction response")),
        "Value.Label.Review",
    ]
    if not numeric.empty:
        series.at[idx, "value_label_review"] = numeric.iloc[0]
    numeric_time = rows.loc[
        rows["Value.Label.Review"].str.startswith("numeric/time unit metadata available"),
        "Value.Label.Review",
    ]
    if not numeric_time.empty:
        series.at[idx, "value_label_review"] = numeric_time.iloc[0]
    numeric_note = rows.loc[
        rows["Harmonization.Status"].str.startswith(("continuous count per source-defined", "raw recorded subtraction response")),
        "Harmonization.Status",
    ]
    if not numeric_note.empty:
        series.at[idx, "harmonization_status"] = numeric_note.iloc[0]
    note = rows.loc[
        rows["Harmonization.Status"].str.startswith("continuous internal biomarker/clinical or physical measure"),
        "Harmonization.Status",
    ]
    if not note.empty:
        series.at[idx, "harmonization_status"] = note.iloc[0]
records = series.to_dict(orient="records")
series.to_csv(series_path, index=False, encoding="utf-8-sig")
payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
(ROOT / "audit/charls_atlas_candidate_series_v0.json").write_text(payload, encoding="utf-8")
partial_count = int(series["value_label_review"].str.startswith("official Codebook extraction exposes only a partial response-code set").sum())
note_count = int(series["harmonization_status"].str.startswith("continuous internal biomarker/clinical or physical measure").sum())
print(f"site series finalized: partial-label notes={partial_count}; internal-measure notes={note_count}")
