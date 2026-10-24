"""Review exact residential location and migration C fields as metadata only."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ("2011", "bb001_1"), ("2011", "bb001_3"), ("2011", "bb001_4"),
    ("2011", "bc005_1"), ("2011", "bc005_3"), ("2011", "bc005_4"),
    ("2011", "bb012_1"), ("2011", "bb012_3"), ("2011", "bb012_4"), ("2011", "bb011"),
    ("2013", "bc005_2"), ("2013", "bb000_w2_1_1"), ("2013", "bb011"),
    ("2013", "bb012"), ("2013", "bb013_w2_1"), ("2013", "bb012_1"),
    ("2015", "bb000_w3_2"),
}
QUESTIONNAIRES = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt",
}
FAMILY = "residential geography and migration metadata"
STATUS = (
    "official questionnaire and Codebook item identity reviewed; location/migration metadata only; "
    "no place-code values or Codebook sample summaries reproduced"
)
NOTE = (
    "Residential place, settlement, or migration-history descriptor, depending on the source item; "
    "not a measured environmental exposure or ambient-dose estimate. Exact geographic identifiers "
    "and code mappings are not reproduced here. Preserve source wave and conditional route; do not "
    "infer a current exposure location or use as a default adjustment covariate."
)


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def review_records() -> list[dict[str, str]]:
    catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
    result = []
    for wave, code in sorted(TARGETS):
        qrel = QUESTIONNAIRES[wave]
        crel = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        questionnaire = (ROOT / qrel).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        codebook = (ROOT / crel).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        token = compact(code)
        if token not in compact(questionnaire):
            raise SystemExit(f"Questionnaire does not contain {wave}/{code}")
        if token not in compact(codebook):
            raise SystemExit(f"Codebook does not contain {wave}/{code}")
        matches = [r for r in catalog if str(r.get("Source.Wave", "")) == wave and str(r.get("Variable.Name", "")).lower() == code and str(r.get("epcf", "")).lower() == "c"]
        if len(matches) != 1:
            raise SystemExit(f"Expected one C row for {wave}/{code}; found {len(matches)}")
        label = str(matches[0].get("Variable.Description", ""))
        kind = "settlement type" if (wave, code) == ("2015", "bb000_w3_2") else "residential geography or migration history"
        result.append({
            "wave": wave,
            "code": code,
            "metadata_family": FAMILY,
            "source_field_label": label,
            "source_item_type": kind,
            "official_sources": f"{qrel}; {crel}",
            "review_status": STATUS,
            "catalog_note": NOTE,
        })
    return result


def update_row(row: dict[str, object], item: dict[str, str]) -> None:
    row["category"] = "measurement metadata"
    row["subcategory"] = FAMILY
    row["Candidate.Status"] = "official questionnaire and Codebook reviewed; residential context metadata"
    row["Harmonization.Status"] = item["catalog_note"]
    row["Review.Flag"] = "C residential geography/migration metadata; not an exposure dose or selected adjustment covariate"
    row["Value.Labels"] = ""
    row["Value.Label.Source"] = item["official_sources"]
    row["Value.Label.Review"] = STATUS
    row["value_labels"] = ""
    row["value_label_source"] = item["official_sources"]
    row["value_label_review"] = STATUS
    row["harmonization_status"] = item["catalog_note"]


def main() -> None:
    records = review_records()
    pd.DataFrame(records).to_csv(ROOT / "audit/residential_location_metadata_review_v1.csv", index=False, encoding="utf-8-sig")
    target_map = {(r["wave"], r["code"]): r for r in records}
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists():
            continue
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            updated = 0
            for (wave, code), item in target_map.items():
                mask = df["Source.Wave"].eq(wave) & df["Variable.Name"].str.lower().eq(code) & df["epcf"].str.lower().eq("c")
                if int(mask.sum()) != 1:
                    raise SystemExit(f"Expected one C row in {rel}: {wave}/{code}")
                for idx in df.index[mask]:
                    row = df.loc[idx].to_dict()
                    update_row(row, item)
                    for key, value in row.items():
                        if key in df.columns:
                            df.at[idx, key] = value
                    updated += 1
            if updated != len(records):
                raise SystemExit(f"Expected {len(records)} updated rows in {rel}; found {updated}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            updated = 0
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
                if key in target_map and str(row.get("epcf", "")).lower() == "c":
                    update_row(row, target_map[key])
                    updated += 1
            if updated != len(records):
                raise SystemExit(f"Expected {len(records)} updated rows in {rel}; found {updated}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Reviewed {len(records)} residential geography/migration metadata fields; geographic code labels and sample summaries omitted.")


if __name__ == "__main__":
    main()
