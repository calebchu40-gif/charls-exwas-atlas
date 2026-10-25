"""Propagate questionnaire-reviewed community labels and continuous-count status."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
REVIEWED_MEASUREMENT_PREFIX = "official questionnaire identifies"


def main():
    labels = pd.read_csv(AUDIT / "community_exposure_value_labels_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    category_labels = labels[labels["value_labels"].str.strip().ne("")]
    reviewed_measurements = labels[labels["value_label_status"].str.startswith(REVIEWED_MEASUREMENT_PREFIX)]
    if category_labels.empty and reviewed_measurements.empty:
        raise SystemExit("No reviewed community labels or measurement semantics found")
    updates = {(str(r.wave), str(r.code).lower()): r for r in reviewed_measurements.itertuples(index=False)}
    category_updates = {(str(r.wave), str(r.code).lower()): r for r in category_labels.itertuples(index=False)}
    updated = 0
    for path in (AUDIT / "charls_atlas_candidate_fields_v0.csv", ROOT / "site-prototype/dist/catalog.json"):
        if path.suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for (wave, code), item in category_updates.items():
                selected = (
                    frame["Source.Wave"].astype(str).eq(wave)
                    & frame["Variable.Name"].str.lower().eq(code)
                    & frame["Data.File.Name"].str.lower().eq("community")
                    & frame["epcf"].str.lower().str.contains("e")
                )
                frame.loc[selected, "Value.Labels"] = item.value_labels
                frame.loc[selected, "Value.Label.Review"] = item.value_label_status
                frame.loc[selected, "Value.Label.Source"] = item.value_label_source
                updated += int(selected.sum())
            for (wave, code), item in updates.items():
                selected = (
                    frame["Source.Wave"].astype(str).eq(wave)
                    & frame["Variable.Name"].str.lower().eq(code)
                    & frame["Data.File.Name"].str.lower().eq("community")
                    & frame["epcf"].str.lower().str.contains("e")
                    & frame["Value.Labels"].eq("")
                    & frame["Value.Label.Review"].str.lower().isin(["", "not yet reviewed"])
                )
                frame.loc[selected, "Value.Label.Review"] = item.value_label_status
                frame.loc[selected, "Value.Label.Source"] = item.value_label_source
                updated += int(selected.sum())
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            rows = json.loads(path.read_text(encoding="utf-8"))
            for row in rows:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
                category_item = category_updates.get(key)
                if category_item and str(row.get("Data.File.Name", "")).lower() == "community" and "e" in str(row.get("epcf", "")).lower():
                    row["Value.Labels"] = category_item.value_labels
                    row["Value.Label.Review"] = category_item.value_label_status
                    row["Value.Label.Source"] = category_item.value_label_source
                    for json_key, value in (("value_labels", category_item.value_labels), ("value_label_review", category_item.value_label_status), ("value_label_source", category_item.value_label_source)):
                        if json_key in row:
                            row[json_key] = value
                    updated += 1
                item = updates.get(key)
                if (
                    item and str(row.get("Data.File.Name", "")).lower() == "community"
                    and "e" in str(row.get("epcf", "")).lower()
                    and not str(row.get("Value.Labels", "")).strip()
                    and str(row.get("Value.Label.Review", "")).lower() in {"", "not yet reviewed"}
                ):
                    row["Value.Label.Review"] = item.value_label_status
                    row["Value.Label.Source"] = item.value_label_source
                    if "value_label_review" in row:
                        row["value_label_review"] = item.value_label_status
                    if "value_label_source" in row:
                        row["value_label_source"] = item.value_label_source
                    updated += 1
            path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if updated < 2:
        raise SystemExit(f"Expected to update the source catalogue and public catalogue; updated {updated} rows")
    print(f"Propagated reviewed community labels/count status to {updated} catalogue rows")


if __name__ == "__main__":
    main()
