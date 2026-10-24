"""Synchronize source-reviewed building, storey, entrance-step, and year-range fields."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from sync_food_crosswalk_index import sync_food_crosswalk_index

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit/food_environment_crosswalk_v1.csv"
SITE = ROOT / "site-prototype/dist/food_environment_v1.json"
LABELS = ROOT / "audit/housing_value_label_review_v1.csv"
REVIEW = "audit/housing_structure_access_review_2026-10-25.md"
QFILES = {
    "2011": "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "CHARLS_2018_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}

FIELDS: dict[tuple[str, str, str], str] = {}
for wave, code in [("2011", "i004"), ("2013", "i004"), ("2015", "i004"), ("2018", "i004"), ("2020", "i001")]:
    FIELDS[(wave, "building_structure", code)] = "Building material/structure categories are nominal. Retain each wave's response categories; categories are collapsed or differ across waves and must not be assigned an ordinal score or harmonized by matching labels alone."
for wave, codes in {
    "2011": ("i006", "i007"), "2013": ("i006", "i007"), "2015": ("i006", "i007"),
    "2018": ("i006", "i007"), "2020": ("i004", "i005"),
}.items():
    for code in codes:
        FIELDS[(wave, "building_stories", code)] = (
            "These are separate categorical housing descriptors: one-/multi-storey class and independent/compound dwelling status. "
            "Preserve field-specific categories and wave-specific routes; do not combine them into a numeric floor or a single ordinal exposure. "
            "They are distinct from the respondent's current floor position and elevator availability."
        )
for wave, code in [("2011", "i011"), ("2013", "i011"), ("2015", "i011"), ("2018", "i011")]:
    FIELDS[(wave, "entrance_steps", code)] = (
        "Household-flat entrance access item; in 2011–2015 it is routed after I010=No, and in 2018 after I010_W4=No. "
        "The questionnaire says not to count steps when an elevator is available. Preserve structural skips as ineligible/not asked, not zero or No. "
        "Categories and zero-step handling vary by wave; this is not an individual stair-climbing test."
    )
for wave in ("2011", "2013", "2015", "2018"):
    FIELDS[(wave, "housing_construction_year", "i005_1")] = (
        "Fallback interval for dwelling construction year when the exact year is unclear or missing; preserve separately from the exact-year field. "
        "Intervals are broad, overlapping at endpoints in source labels, and vary in final-category wording; do not convert to a point year or merge with move-in time."
    )


def validate_sources() -> dict[str, str]:
    texts = {w: re.sub(r"\s+", " ", (ROOT / "sources_official" / name).read_text(encoding="utf-8", errors="ignore").casefold()) for w, name in QFILES.items()}
    # In the 2011 baseline instrument, the fallback intervals are printed under
    # I005 rather than as a separately numbered I005_1 prompt; the Codebook stores
    # that response as I005_1. Validate both source representations.
    for wave, concept, code in FIELDS:
        if (wave, concept, code) == ("2011", "housing_construction_year", "i005_1"):
            continue
        if code.casefold() not in texts[wave]:
            raise ValueError(f"Official {wave} questionnaire does not contain {code}")
    route_checks = {
        "2011": "if i010 =2, ask i011",
        "2013": "if i010 = 2, ask i011",
        "2015": "if i010 = 2, ask i011",
        "2018": "if i010_w4 = 2, ask i011",
    }
    for wave, phrase in route_checks.items():
        if phrase not in texts[wave]:
            raise ValueError(f"Official {wave} entrance-step routing not found")
    if "if r is unclear about year, choose:" not in texts["2011"]:
        raise ValueError("Official 2011 I005 unclear-year fallback categories not found")
    if "ask i005_1 if i005 is missing" not in texts["2018"]:
        raise ValueError("Official 2018 fallback construction-year route not found")
    for wave in ("2013", "2015"):
        if "if r is unclear about year" not in texts[wave]:
            raise ValueError(f"Official {wave} unclear-year fallback instruction not found")
    return texts


def main() -> None:
    texts = validate_sources()
    with LABELS.open(encoding="utf-8-sig", newline="") as f:
        label_rows = {(r["wave"], r["code"].lower()): r for r in csv.DictReader(f)}
    with AUDIT.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f); columns, rows = reader.fieldnames or [], list(reader)
    updated = set()
    for row in rows:
        key = (row["wave"], row["concept_id"], row["code"].lower())
        if key not in FIELDS:
            continue
        wave, concept, code = key
        label = label_rows.get((wave, code))
        if not label or not label["value_labels"]:
            raise ValueError(f"Wave-specific Codebook labels missing for {wave} {code}")
        row["mapping_status"] = f"official {wave} questionnaire/Codebook wording, labels and applicable routing reviewed; release-specific special values, denominator, and household-person linkage require QA; see {REVIEW}"
        row["caveat"] = FIELDS[key] + " Confirm special-value storage, missingness, eligible denominator, and household/person linkage in the authorized release. Cross-wave equivalence is not established."
        row["code_value_labels"] = label["value_labels"]
        updated.add(key)
    if updated != set(FIELDS):
        raise ValueError(f"Crosswalk mismatch: missing={sorted(set(FIELDS)-updated)}")
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    sync_food_crosswalk_index(ROOT, {(w, code, concept) for w, concept, code in FIELDS})
    data = json.loads(SITE.read_text(encoding="utf-8")); site_updated = set()
    for concept in data:
        cid = concept.get("concept_id", "")
        for field in concept.get("source_fields", []):
            key = (str(field.get("wave", "")), cid, str(field.get("code", "")).lower())
            if key not in FIELDS:
                continue
            label = label_rows[(key[0], key[2])]
            status = f"official {key[0]} questionnaire/Codebook wording, labels and applicable routing reviewed; release-specific special values, denominator, and household-person linkage require QA; see {REVIEW}"
            field.update({"mapping_status": status, "caveat": FIELDS[key] + " Confirm special-value storage, missingness, eligible denominator, and household/person linkage in the authorized release. Cross-wave equivalence is not established.", "value_labels": label["value_labels"], "value_label_source": label["value_label_source"], "value_label_status": status, "note": status})
            site_updated.add(key)
    if site_updated != set(FIELDS):
        raise ValueError(f"Browser data mismatch: missing={sorted(set(FIELDS)-site_updated)}")
    SITE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Reviewed {len(updated)} source rows; verified the 2011 I005 fallback under the parent I005 question.")


if __name__ == "__main__":
    main()
