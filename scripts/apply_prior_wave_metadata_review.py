"""Record source-checked prior-wave history/routing metadata in the C catalogue."""
import argparse
import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "site-prototype/dist/catalog_c.json"
OUTPUT = ROOT / "audit/prior_wave_metadata_review_v1.csv"
TARGET_FAMILIES = {
    "prior-interview response-history routing flags": 41,
    "prior-wave diagnosis-time answer-history flags": 14,
}

def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())

def propagate() -> None:
    review = pd.read_csv(OUTPUT, dtype=str, encoding="utf-8-sig").fillna("")
    targets = {(str(r.wave), str(r.code).lower()): r for r in review.itertuples(index=False)}
    paths = [
        ROOT / "audit/charls_atlas_candidate_fields_v0.csv",
        ROOT / "audit/charls_atlas_candidate_fields_v0.json",
        ROOT / "site-prototype/dist/catalog.json",
    ]
    for path in paths:
        if path.suffix == ".csv":
            data = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            updated = 0
            for (wave, code), item in targets.items():
                selected = (data["Source.Wave"].astype(str).eq(wave)
                            & data["Variable.Name"].str.lower().eq(code)
                            & data["epcf"].str.lower().eq("c"))
                if selected.any():
                    data.loc[selected, "Value.Label.Review"] = item.review_status
                    data.loc[selected, "Value.Label.Source"] = item.official_source
                    data.loc[selected, "Value.Labels"] = ""
                    data.loc[selected, "Review.Flag"] = item.catalog_note
                    data.loc[selected, "Harmonization.Status"] = item.catalog_note
                    updated += int(selected.sum())
            if updated != len(targets):
                raise SystemExit(f"Expected to propagate {len(targets)} C rows into {path}, updated {updated}")
            data.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            updated = 0
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
                item = targets.get(key)
                if item and str(row.get("epcf", "")).lower() == "c":
                    row["Value.Label.Review"] = item.review_status
                    row["Value.Label.Source"] = item.official_source
                    row["Value.Labels"] = ""
                    row["Review.Flag"] = item.catalog_note
                    row["Harmonization.Status"] = item.catalog_note
                    row["value_label_review"] = item.review_status
                    row["value_label_source"] = item.official_source
                    row["value_labels"] = ""
                    row["harmonization_status"] = item.catalog_note
                    updated += 1
            if updated != len(targets):
                raise SystemExit(f"Expected to propagate {len(targets)} C rows into {path}, updated {updated}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"Propagated {len(targets)} source-checked C metadata rows into {path.relative_to(ROOT)}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--propagate", action="store_true")
    args = parser.parse_args()
    if args.propagate:
        propagate()
        return
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))
    targets = [
        row for row in rows
        if row.get("subcategory") in TARGET_FAMILIES
        and row.get("Value.Label.Review", "").strip().lower() == "not yet reviewed"
    ]
    observed = {family: sum(row["subcategory"] == family for row in targets) for family in TARGET_FAMILIES}
    if observed != TARGET_FAMILIES:
        raise SystemExit(f"Unexpected pending metadata family sizes: {observed}")
    audit = []
    for row in targets:
        wave = str(row["Source.Wave"])
        code = str(row["Variable.Name"])
        source = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        source_path = ROOT / source
        if not source_path.exists():
            raise SystemExit(f"Missing official Codebook source for {wave}/{code}: {source}")
        codebook = compact(source_path.read_text(encoding="utf-8", errors="replace"))
        if compact(code) not in codebook:
            raise SystemExit(f"Official Codebook field not found: {wave}/{code}")
        if row["subcategory"] == "prior-wave diagnosis-time answer-history flags":
            note = "Prior-interview answer-history indicator for the diagnosis/known-time item indexed by disease slot; not diagnosis status or diagnosis time."
        else:
            note = "Prior-interview response-history, preload, or route-validation metadata; not a respondent behavior measure or independent exposure."
        audit.append({
            "wave": wave,
            "code": code,
            "metadata_family": row["subcategory"],
            "official_source": source,
            "source_field_label": row.get("Variable.Description", ""),
            "review_status": "official wave Codebook field located; prior-wave answer-history/routing metadata only; not an exposure/phenotype; no response-value categories assigned",
            "value_labels": "",
            "catalog_note": note,
        })
    pd.DataFrame(audit).sort_values(["wave", "metadata_family", "code"]).to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"Source-checked {len(audit)} prior-wave history/routing metadata fields across {len(set(r['wave'] for r in audit))} waves; no answer categories assigned.")

if __name__ == "__main__":
    main()
