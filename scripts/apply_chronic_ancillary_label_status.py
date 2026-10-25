"""Synchronize chronic-disease ancillary labels already transcribed from official sources."""
from pathlib import Path
import csv
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "audit/chronic_disease_ancillary_variable_mapping_v1.csv"
STALE_STATUS = "official variable metadata mapped; item-level value labels/routing review pending"
REVIEWED_STATUS = (
    "official response categories reviewed/transcribed from wave-specific questionnaire/Codebook; "
    "retain source-specific route and time frame; release coding, routed denominator and analysis eligibility require QA"
)


def apply_status(mapping: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    stale = mapping["mapping_status"].eq(STALE_STATUS)
    reviewed_evidence = mapping["value_label_status"].str.contains(
        r"official .*?(?:response labels reviewed|response categories transcribed|response options|selected-option category transcribed)",
        case=False,
        regex=True,
    ) & mapping["value_label_status"].ne(STALE_STATUS)
    target = (stale & reviewed_evidence & mapping["value_labels"].ne("")) | mapping["mapping_status"].eq(REVIEWED_STATUS)
    count = int(target.sum())
    if count != 83:
        raise ValueError(f"Expected 83 stale rows with explicit reviewed labels; found {count}")
    result = mapping.copy()
    result.loc[target, "mapping_status"] = REVIEWED_STATUS
    return result, count


def sync_diagnosis_age_c_metadata() -> int:
    """Give duplicate C-role diagnosis-age rows their reviewed source identity."""
    mapping = pd.read_csv(MAPPING_PATH, dtype=str, encoding="utf-8-sig").fillna("")
    field_path = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
    fields = pd.read_csv(field_path, dtype=str, encoding="utf-8-sig").fillna("")
    source_map = {}
    for row in fields.to_dict("records"):
        key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower(), str(row.get("Data.File.Name", "")).lower())
        if str(row.get("epcf", "")).lower() in {"p", "c"} and row.get("Value.Label.Source"):
            source_map.setdefault(key, row["Value.Label.Source"])
    targets = {}
    for row in mapping.to_dict("records"):
        if row.get("construct") != "reported diagnosis/knowledge time" or row.get("subtype") != "age":
            continue
        key = (str(row["wave"]), str(row["code"]).lower(), str(row["module"]).lower())
        sources = [p.strip() for p in source_map.get(key, "").split(";") if p.strip().startswith("sources_official/")]
        if not sources or any(not (ROOT / source).is_file() for source in sources):
            raise ValueError(f"Missing official source for {row.get('wave')}/{row.get('code')}")
        row["official_sources"] = "; ".join(sources)
        targets[key] = row
    if len(targets) != 56:
        raise ValueError(f"Expected 56 source-reviewed diagnosis-age fields, found {len(targets)}")

    paths = (
        ROOT / "audit/charls_atlas_candidate_fields_v0.csv",
        ROOT / "audit/charls_atlas_candidate_fields_v0.json",
        ROOT / "site-prototype/dist/catalog.json",
        ROOT / "site-prototype/dist/catalog_c.json",
    )
    total = 0
    for path in paths:
        if not path.exists():
            continue
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream)); fields = list(rows[0]) if rows else []
            for item in rows:
                key = (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower(), str(item.get("Data.File.Name", "")).lower())
                if key not in targets or str(item.get("epcf", "")).lower() != "c":
                    continue
                item.update({
                    "category": "source-reviewed chronic-disease timing metadata",
                    "subcategory": "reported diagnosis/knowledge age metadata",
                    "Candidate.Status": "C metadata; age at first reported diagnosis/knowledge is source-mapped to a wave-specific phenotype timing candidate; not biological onset or a default adjustment",
                    "Harmonization.Status": "reported diagnosis/knowledge time is distinct from biological onset; preserve condition index, route, source wave and special values; use the corresponding P candidate when studying this outcome",
                    "Review.Flag": "C metadata only; do not adjust for the same outcome's diagnosis age; disease index and released-file eligibility remain wave-specific",
                    "Value.Labels": "", "Value.Label.Source": targets[key]["official_sources"],
                    "Value.Label.Review": "official question/Codebook field and continuous age unit mapped; no discrete labels or frequencies",
                    "Unit": "age in years",
                })
                total += 1
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
        else:
            rows = json.loads(path.read_text(encoding="utf-8"))
            for item in rows:
                key = (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower(), str(item.get("Data.File.Name", "")).lower())
                if key not in targets or str(item.get("epcf", "")).lower() != "c":
                    continue
                item.update({
                    "category": "source-reviewed chronic-disease timing metadata",
                    "subcategory": "reported diagnosis/knowledge age metadata",
                    "Candidate.Status": "C metadata; age at first reported diagnosis/knowledge is source-mapped to a wave-specific phenotype timing candidate; not biological onset or a default adjustment",
                    "Harmonization.Status": "reported diagnosis/knowledge time is distinct from biological onset; preserve condition index, route, source wave and special values; use the corresponding P candidate when studying this outcome",
                    "Review.Flag": "C metadata only; do not adjust for the same outcome's diagnosis age; disease index and released-file eligibility remain wave-specific",
                    "Value.Labels": "", "Value.Label.Source": targets[key]["official_sources"],
                    "Value.Label.Review": "official question/Codebook field and continuous age unit mapped; no discrete labels or frequencies",
                    "Unit": "age in years",
                })
                total += 1
            path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if total != 224:
        raise ValueError(f"Expected 56 C rows across four catalog representations; updated {total}")
    return total


def main() -> None:
    mapping = pd.read_csv(MAPPING_PATH, dtype=str, encoding="utf-8-sig").fillna("")
    updated, count = apply_status(mapping)
    updated.to_csv(MAPPING_PATH, index=False, encoding="utf-8-sig")
    c_rows = sync_diagnosis_age_c_metadata()
    print(f"Updated response-label status for {count} chronic-disease ancillary fields and source status for {c_rows} diagnosis-age C catalogue rows; release coding/denominator/analysis QA remains pending")


if __name__ == "__main__":
    main()
