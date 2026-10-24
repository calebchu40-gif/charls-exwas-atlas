"""Source-review current-workplace location context fields (2011-2018)."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit/work_exposure_crosswalk_v1.csv"
INDEX = ROOT / "audit/ep_concept_source_crosswalk_v1.csv"
SITE = ROOT / "site-prototype/dist/work_exposures_v1.json"
REVIEW = "audit/workplace_location_context_review_2026-10-25.md"
CONCEPT = "current_workplace_location_relative_to_residence_2011_2018"
FILES = {
    "2011": "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "CHARLS_2018_Questionnaire_extracted.txt",
}
LABELS = {
    "2011": "1=This village/community; 2=Other village/community in this county/city; 3=Another county/city in this province; 4=Another province",
    "2013": "1=The Same as Permanent Address; 2=Another Village in Permanent Address's County; 3=Other; 4=Abroad",
    "2015": "1=The Same as Permanent Address; 2=Another Village in Permanent Address's County; 3=Other; 4=Abroad",
    "2018": "1=Same as the Residence; 2=Other village/community in the permanent address's county/city/district; 3=Other domestic location; 4=Abroad",
}
COMMON = (
    "Current workplace geographic-context item among respondents routed to the employed-work module. "
    "This is a coarse self-reported location category, not commute distance, air pollution, or a measured environmental dose. "
    "Keep wave-specific categories and eligible current-work denominator; do not pool categories across waves without a separate equivalence review. "
    "Verify released-file special values, item availability and person linkage in the authorized release."
)
STATUS = f"official wave-specific questionnaire/Codebook wording, response labels and applicable route reviewed; release storage, eligible denominator and person linkage require QA; see {REVIEW}"


def compact(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8", errors="ignore").casefold())


def validate_sources() -> None:
    for wave, filename in FILES.items():
        q = compact(ROOT / "sources_official" / filename)
        cb = compact(ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt")
        if "fd004" not in q or "where is your workplace" not in q or "fd004" not in cb:
            raise ValueError(f"Official {wave} FD004 questionnaire/Codebook source missing")
        if wave == "2011" and "another county/city in this province" not in q:
            raise ValueError("2011 FD004 response anchor missing")
        if wave in {"2013", "2015"}:
            if "the same as permanent address" not in q or "abroad" not in q:
                raise ValueError(f"{wave} FD004 residence anchor/abroad option missing")
            if not re.search(r"if r is working for individual farmer or resident household \(fd002\s*=\s*6\s*;\s*7\), skip to fd011", q):
                raise ValueError(f"{wave} FD002=6/7 routing not found")
        if wave == "2018":
            for phrase in ("same as the permanent address", "3. other", "4. abroad"):
                if phrase not in q:
                    raise ValueError(f"2018 FD004 anchor missing: {phrase}")


def main() -> None:
    validate_sources()
    with AUDIT.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f); cols, rows = reader.fieldnames or [], list(reader)
    expected = {(w, "fd004") for w in FILES}
    seen = set()
    for row in rows:
        key = (row["wave"], row["code"].lower())
        if row["concept_id"] != CONCEPT or key not in expected:
            continue
        wave = key[0]
        row["mapping_status"] = STATUS
        row["questionnaire_review"] = STATUS + " 2013/2015 FD002=6/7 skips FD004 to FD011; 2018 retains wave-specific employer-change routing. 2020 FD004 is employee count and excluded."
        row["caveat"] = COMMON + (" 2011 uses village/community and county/province anchors; 2013/2015 refer to permanent address and include abroad; 2018 uses its own permanent/current-residence wording and location detail. 2013/2015 FD002=6/7 routes skip this field. The same code in 2020 means number of employees and is excluded." )
        seen.add(key)
    if seen != expected:
        raise ValueError(f"Domain crosswalk coverage mismatch: {expected-seen}")
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)

    # Keep the E/P source index consistent with its domain crosswalk.
    with INDEX.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f); icols, irows = reader.fieldnames or [], list(reader)
    indexed = set()
    for row in irows:
        key = (row["Wave"], row["Source.Code"].lower())
        if row["Concept.ID"] != CONCEPT or key not in expected:
            continue
        row["Mapping.Status"] = STATUS
        row["Caveat"] = COMMON + " Preserve wave-specific response labels."
        row["Value.Labels"] = LABELS[key[0]]
        row["Value.Semantics"] = "official questionnaire/Codebook response categories; frequencies omitted"
        indexed.add(key)
    if indexed != expected:
        raise ValueError(f"E/P source index coverage mismatch: {expected-indexed}")
    with INDEX.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=icols, lineterminator="\n"); writer.writeheader(); writer.writerows(irows)

    data = json.loads(SITE.read_text(encoding="utf-8")); site_seen = set()
    for concept in data:
        if concept.get("concept_id") != CONCEPT:
            continue
        concept["caveat"] = COMMON + " 2020 FD004 is a different employee-count item and is not included."
        for field in concept.get("source_fields", []):
            key = (str(field.get("wave", "")), str(field.get("code", "")).lower())
            if key not in expected:
                continue
            route_note = " 2013/2015 FD002=6/7 respondents skip to FD011." if key[0] in {"2013", "2015"} else ""
            field.update({"mapping_status": STATUS, "note": STATUS + route_note, "caveat": COMMON, "value_labels": LABELS[key[0]],
                          "value_label_status": "Official wave-specific questionnaire/Codebook labels reviewed; frequencies omitted",
                          "value_label_source": f"sources_official/{FILES[key[0]]}; sources_official/CHARLS_{key[0]}_Codebook_extracted.txt"})
            site_seen.add(key)
    if site_seen != expected:
        raise ValueError(f"Site payload coverage mismatch: {expected-site_seen}")
    SITE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Reviewed and synchronized {len(expected)} current-workplace location fields.")


if __name__ == "__main__":
    main()
