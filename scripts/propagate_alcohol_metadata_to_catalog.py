"""Propagate reviewed alcohol labels and semantics into the public field catalog."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "audit/behavior_exposure_variable_mapping_v1.csv"
FIELDS_CSV = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
FIELDS_JSON = ROOT / "audit/charls_atlas_candidate_fields_v0.json"
CATALOG = ROOT / "site-prototype/dist/catalog.json"

CAT_TO_MAP = {
    "Value.Labels": "value_labels",
    "Value.Label.Source": "value_label_source",
    "Harmonization.Status": "note",
}


def record_key(row: dict) -> tuple[str, str, str, str]:
    return (
        str(row.get("Begin.Year", row.get("Source.Wave", ""))),
        str(row.get("Variable.Name", "")).lower(),
        str(row.get("Data.File.Name", "")).casefold(),
        str(row.get("Source.Archive", "")).casefold(),
    )


def apply_record(row: dict, by_key: dict) -> bool:
    mapped = by_key.get(record_key(row))
    if not mapped or not mapped["value_labels"]:
        return False
    for target, source_key in CAT_TO_MAP.items():
        value = mapped[source_key]
        if value and target in row:
            row[target] = value
    if "Value.Label.Review" in row:
        row["Value.Label.Review"] = "officially reviewed"
    if "value_labels" in row:
        row["value_labels"] = mapped["value_labels"]
    if "value_label_source" in row:
        row["value_label_source"] = mapped["value_label_source"]
    if "value_label_review" in row:
        row["value_label_review"] = "officially reviewed"
    if mapped["value_semantics"] and "Harmonization.Status" in row:
        current = str(row.get("Harmonization.Status") or "")
        extra = mapped["value_semantics"]
        if extra not in current:
            row["Harmonization.Status"] = f"{current}; {extra}".strip("; ")
        if "harmonization_status" in row:
            row["harmonization_status"] = row["Harmonization.Status"]
    return True


def main() -> None:
    mapping = pd.read_csv(MAP, dtype=str, encoding="utf-8-sig").fillna("")
    by_key = {}
    for row in mapping[mapping.concept_id.str.startswith("alcohol_")].to_dict("records"):
        key = (row["wave"], row["code"].lower(), row["module"].casefold(), row["source_archive"].casefold())
        if key in by_key:
            prior = by_key[key]
            for field in ("value_labels", "value_label_source"):
                if prior[field] and row[field] and prior[field] != row[field]:
                    raise ValueError(f"Conflicting alcohol mapping for {key}: {field}")
            for field, value in row.items():
                if value:
                    prior[field] = value
        else:
            by_key[key] = row

    updated = 0
    frame = pd.read_csv(FIELDS_CSV, dtype=str, encoding="utf-8-sig").fillna("")
    for idx, row in frame.iterrows():
        record = row.to_dict()
        n = apply_record(record, by_key)
        if n:
            for column in ("Value.Labels", "Value.Label.Source", "Value.Label.Review", "Harmonization.Status"):
                if column in frame.columns:
                    frame.at[idx, column] = record[column]
        updated += int(n)
    frame.to_csv(FIELDS_CSV, index=False, encoding="utf-8-sig")
    print(f"{FIELDS_CSV.relative_to(ROOT)}: propagated reviewed alcohol labels to {updated} exact wave/module/archive rows")

    for path in (FIELDS_JSON, CATALOG):
        raw = path.read_text(encoding="utf-8")
        # These generated catalogs are compact JSON. Strip an accidental
        # literal backslash-n suffix if present, while preserving real JSON
        # escapes inside string values.
        if raw.endswith(r"\n"):
            raw = raw[:-2]
        records = json.loads(raw)
        n = sum(apply_record(row, by_key) for row in records)
        path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: propagated reviewed alcohol labels to {n} exact wave/module/archive rows")
        updated += n
    if updated == 0:
        raise ValueError("No reviewed alcohol labels matched the field catalog")


if __name__ == "__main__":
    main()
