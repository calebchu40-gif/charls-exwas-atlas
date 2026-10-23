"""Apply the source-verified five-wave heating and cooking fuel review."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "audit" / "food_environment_crosswalk_v1.csv"
SITE_PATH = ROOT / "site-prototype" / "dist" / "food_environment_v1.json"
REVIEW_PATH = "audit/housing_fuel_source_review_2026-10-24.md"

WAVES = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
    "2020": "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; sources_official/CHARLS_2020_Codebook_extracted.txt",
}

CAVEATS = {
    "heating_energy": (
        "Nominal household heating-source proxy, not measured energy use or pollution dose. "
        "In 2011–2018, the source item is routed after the heating-availability question; "
        "2020 instead includes an explicit no-heating response in the source item. Preserve these "
        "different denominators and the 2020 household referent (XFinancialResp's house). "
        f"See {REVIEW_PATH}."
    ),
    "cooking_fuel_main": (
        "Nominal household cooking-fuel proxy, not measured fuel use or indoor pollutant dose. "
        "Code categories change: 2018/2020 include a no-cooking response, 2020 adds solar at 7 "
        "and shifts later codes. Do not turn blanks in earlier waves into no cooking or interpret "
        "numeric codes as an ordered dose. The 2020 household referent is XFinancialResp's house; "
        f"confirm household linkage before assigning it to a person. See {REVIEW_PATH}."
    ),
}

FIELDS = {
    "heating_energy": {
        "2011": "i021", "2013": "i021", "2015": "i021", "2018": "i021_w4", "2020": "i020"
    },
    "cooking_fuel_main": {
        "2011": "i022", "2013": "i022", "2015": "i022", "2018": "i022_w4", "2020": "i021"
    },
}


def apply_audit_rows() -> int:
    with AUDIT_PATH.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    updated = 0
    for row in rows:
        concept_id = row.get("concept_id", "")
        wave = row.get("wave", "")
        if concept_id not in FIELDS or FIELDS[concept_id].get(wave) != row.get("code", "").lower():
            continue
        row["mapping_status"] = (
            "official wave-specific questionnaire and Codebook reviewed; wording, response categories, "
            f"and routes verified; see {REVIEW_PATH}"
        )
        row["caveat"] = CAVEATS[concept_id]
        updated += 1
    expected = sum(len(wave_map) for wave_map in FIELDS.values())
    if updated != expected:
        raise ValueError(f"Expected {expected} heating/cooking rows; updated {updated}")
    with AUDIT_PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return updated


def apply_site_fields() -> int:
    data = json.loads(SITE_PATH.read_text(encoding="utf-8"))
    updated = 0
    for concept in data:
        concept_id = concept.get("concept_id", "")
        if concept_id not in FIELDS:
            continue
        concept["caveat"] = CAVEATS[concept_id]
        expected_codes = FIELDS[concept_id]
        for field in concept.get("source_fields", []):
            wave = str(field.get("wave", ""))
            if expected_codes.get(wave) != str(field.get("code", "")).lower():
                continue
            field["note"] = (
                "official wave-specific questionnaire and Codebook reviewed; question wording, "
                f"response categories, and route differences verified; see {REVIEW_PATH}"
            )
            field["source_document"] = WAVES[wave]
            updated += 1
    expected = sum(len(wave_map) for wave_map in FIELDS.values())
    if updated != expected:
        raise ValueError(f"Expected {expected} site fields; updated {updated}")
    SITE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return updated


def main() -> None:
    audit_rows = apply_audit_rows()
    site_fields = apply_site_fields()
    print(f"Reviewed fuel source rows: audit={audit_rows}, site={site_fields}; no response values/counts used")


if __name__ == "__main__":
    main()
