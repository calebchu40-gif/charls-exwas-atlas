"""Synchronize final reviewed housing aliases and Wave 4 area metadata.

Only public metadata is changed. No participant-level records are accessed.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from sync_food_crosswalk_index import sync_food_crosswalk_index

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit/food_environment_crosswalk_v1.csv"
SITE = ROOT / "site-prototype/dist/food_environment_v1.json"
REVIEW = "audit/housing_context_source_review_2026-10-24.md"

ROWS = {
    ("2015", "air_cleaner", "i027_w3"): {
        "status": "official 2015 questionnaire/Codebook wording, target and response categories reviewed; see " + REVIEW,
        "caveat": "Catalog alias only: this is the same 2015 I027_W3 household air-cleaner-presence item mapped under air_cleaner_home. Do not count it as a distinct exposure or duplicate association. Presence does not establish use, filtration performance, pollutant concentration, or personal exposure. See " + REVIEW + ".",
        "labels": "1=Yes; 2=No",
        "note": "Official questionnaire/Codebook reviewed: duplicate alias of air_cleaner_home, same 2015 I027_W3 source item (1=Yes/2=No). Do not count as a distinct exposure. See " + REVIEW + ".",
    },
    ("2018", "dwelling_area", "i000_w4_11"): {
        "status": "official 2018 questionnaire confirms usable floor area in square metres; non-ownership route; special values and eligible denominator require authorized-release QA",
        "caveat": "2018 usable floor area in square metres, asked when the main respondent/spouse does not own property rights to the current home. Keep separate from i000_w4_12, which is asked on the ownership route and measures floor area. The routes select different respondents/households and the fields are not substitutes. Confirm authorized-release special values, missingness, and eligible denominator; cross-wave equivalence is unapproved.",
        "labels": "",
        "note": "Official 2018 questionnaire confirms usable floor area (square metres) on the no-ownership route (I000_W4_4 not 1/9); preserve separately from I000_W4_12 on the ownership route. Special values and eligibility require authorized-release QA. See " + REVIEW + ".",
    },
    ("2018", "dwelling_area", "i000_w4_12"): {
        "status": "official 2018 questionnaire confirms floor area in square metres; ownership route; special values and eligible denominator require authorized-release QA",
        "caveat": "2018 floor area in square metres, asked when the main respondent/spouse owns property rights to the current home. Keep separate from i000_w4_11, which is usable floor area on the no-ownership route. The routes select different respondents/households and the fields are not substitutes. Confirm authorized-release special values, missingness, and eligible denominator; cross-wave equivalence is unapproved.",
        "labels": "",
        "note": "Official 2018 questionnaire confirms floor area (square metres) on the ownership route (I000_W4_4=1/9); preserve separately from I000_W4_11 on the no-ownership route. Special values and eligibility require authorized-release QA. See " + REVIEW + ".",
    },
}


def validate_source() -> None:
    q = re.sub(r"\s+", " ", (ROOT / "sources_official/CHARLS_2018_Questionnaire_extracted.txt").read_text(encoding="utf-8", errors="ignore").casefold())
    if "what is the usable area of the house you are living in" not in q or "what is the floor area of the house you are living in" not in q:
        raise ValueError("Official 2018 area question wording was not found")
    if not re.search(r"skip to the i000_w4_12 if the main respondent or his/her spouse owns property right", q):
        raise ValueError("Official 2018 ownership route to I000_W4_12 was not found")
    if not re.search(r"ask i000_w4_11 then skip to i000_w4_13 if the main respondent or his/her spouse owns no property right", q):
        raise ValueError("Official 2018 no-ownership route to I000_W4_11 was not found")
    air = (ROOT / "sources_official/CHARLS_2015_Questionnaire_extracted.txt").read_text(encoding="utf-8", errors="ignore").casefold()
    if "i027_w3" not in air or "air cleaner" not in air:
        raise ValueError("Official 2015 air-cleaner item was not found")


def main() -> None:
    validate_source()
    with AUDIT.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns, rows = reader.fieldnames or [], list(reader)
    found = set()
    for row in rows:
        key = (row["wave"], row["concept_id"], row["code"].lower())
        if key not in ROWS:
            continue
        item = ROWS[key]
        row["mapping_status"] = item["status"]
        row["caveat"] = item["caveat"]
        row["code_value_labels"] = item["labels"]
        found.add(key)
    if found != set(ROWS):
        raise ValueError(f"Expected exact metadata rows; missing={sorted(set(ROWS)-found)}")
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    sync_food_crosswalk_index(ROOT, {(w, code, concept) for w, concept, code in ROWS})

    data = json.loads(SITE.read_text(encoding="utf-8"))
    site_found = set()
    for concept in data:
        cid = concept.get("concept_id", "")
        for field in concept.get("source_fields", []):
            key = (str(field.get("wave", "")), cid, str(field.get("code", "")).lower())
            if key not in ROWS:
                continue
            item = ROWS[key]
            field.update({"mapping_status": item["status"], "caveat": item["caveat"], "note": item["note"], "value_labels": item["labels"]})
            if cid == "dwelling_area":
                field["unit"] = "square metres"
            site_found.add(key)
    if site_found != set(ROWS):
        raise ValueError(f"Expected exact site fields; missing={sorted(set(ROWS)-site_found)}")
    SITE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synchronized {len(found)} reviewed housing metadata rows and source-index entries; no participant data used.")


if __name__ == "__main__":
    main()
