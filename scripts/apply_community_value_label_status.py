"""Propagate reviewed continuous-count semantics for community metadata fields."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
STATUS_PREFIX = "official questionnaire identifies a continuous household count;"


def main():
    labels = pd.read_csv(AUDIT / "community_exposure_value_labels_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    labels = labels[labels["value_label_status"].str.startswith(STATUS_PREFIX)]
    if labels.empty:
        raise SystemExit("No reviewed community continuous-count labels found")
    updates = {(str(r.wave), str(r.code).lower()): r for r in labels.itertuples(index=False)}
    updated = 0
    for path in (AUDIT / "charls_atlas_candidate_fields_v0.csv", ROOT / "site-prototype/dist/catalog.json"):
        if path.suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
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
            path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    if updated < 2:
        raise SystemExit(f"Expected to update the source catalogue and public catalogue; updated {updated} rows")
    print(f"Propagated reviewed community continuous-count status to {updated} catalogue rows")


if __name__ == "__main__":
    main()
