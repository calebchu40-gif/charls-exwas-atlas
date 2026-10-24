"""Review self-employment business location categories; never publish address text."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit/work_exposure_crosswalk_v1.csv"
INDEX = ROOT / "audit/ep_concept_source_crosswalk_v1.csv"
SITE = ROOT / "site-prototype/dist/work_exposures_v1.json"
REVIEW = "audit/selfemployment_business_location_review_2026-10-25.md"
CONCEPT = "nonfarm_self_employment_business_location_2011_2020"
FIELDS = {
    "2011": ("fh006", "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", "1=This village/community; 2=Other village/community in this county/city; 3=Another county/city in this province; 4=Another province"),
    "2013": ("fh006", "CHARLS_2013_Questionnaire_extracted.txt", "1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other domestic location; 4=Abroad"),
    "2015": ("fh006", "CHARLS_2015_Questionnaire_extracted.txt", "1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other domestic location; 4=Abroad"),
    "2018": ("fh006", "CHARLS_2018_Questionnaire_extracted.txt", "1=Same as permanent address; 2=Other village/community in the permanent address's county/city/district; 3=Other domestic location; 4=Abroad"),
    "2020": ("fd002", "CHARLS_2020_Questionnaire_English_extracted.txt", "1=Same village/community as current residence; 2=Other village/community in same county/district; 3=Other county/district; 4=Hong Kong, Macao, Taiwan, or abroad; 999=Refuse to answer"),
}
STATUS = f"official wave-specific questionnaire/Codebook category wording and self-employment route reviewed; release special values, denominator and person linkage require QA; see {REVIEW}"
CAVEAT = (
    "Self-reported broad geographic category for the respondent's non-farm self-employment business. This is not a commute distance, measured pollution, or a geocoded exposure. "
    "Keep wave-specific categories and eligible business route; do not harmonize by code number alone. Questionnaire subfields may contain place names/address text and are deliberately excluded from the public atlas. "
    "Confirm authorized-release special values, eligibility, missingness and person linkage before analysis."
)


def norm(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8", errors="ignore").casefold())


def validate() -> None:
    for wave, (code, filename, _) in FIELDS.items():
        q = norm(ROOT / "sources_official" / filename)
        cb = norm(ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt")
        if code not in q or code not in cb:
            raise ValueError(f"Official {wave} business-location item missing in questionnaire or Codebook")
        if wave == "2011" and "mark 0 if there is no fixed address" not in q:
            raise ValueError("2011 no-fixed-address interviewer instruction missing")
        if wave == "2020" and ("999. refuse" not in q or "hong kong, macao, taiwan, or abroad" not in q):
            raise ValueError("2020 response options missing")


def main() -> None:
    validate()
    expected = {(w, v[0]) for w, v in FIELDS.items()}
    with AUDIT.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f); cols, rows = reader.fieldnames or [], list(reader)
    found = set()
    for row in rows:
        key = (row["wave"], row["code"].lower())
        if row["concept_id"] == CONCEPT and key in expected:
            row["mapping_status"] = STATUS
            row["questionnaire_review"] = STATUS + " Address/place-name subfields are excluded from public output."
            row["caveat"] = CAVEAT
            found.add(key)
    if found != expected:
        raise ValueError(f"Domain crosswalk rows missing: {expected-found}")
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");writer.writeheader();writer.writerows(rows)

    with INDEX.open(encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f); icols, irows=reader.fieldnames or [],list(reader)
    indexed=set()
    for row in irows:
        key=(row["Wave"],row["Source.Code"].lower())
        if row["Concept.ID"]==CONCEPT and key in expected:
            row["Mapping.Status"]=STATUS;row["Caveat"]=CAVEAT;row["Value.Labels"]=FIELDS[key[0]][2]
            row["Value.Semantics"]="official questionnaire/Codebook categories; no address text or frequencies"
            indexed.add(key)
    if indexed!=expected: raise ValueError(f"Source index rows missing: {expected-indexed}")
    with INDEX.open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=icols,lineterminator="\n");writer.writeheader();writer.writerows(irows)

    data=json.loads(SITE.read_text(encoding="utf-8")); site_found=set()
    for concept in data:
        if concept.get("concept_id")!=CONCEPT: continue
        concept["caveat"]=CAVEAT
        for field in concept.get("source_fields",[]):
            key=(str(field.get("wave","")),str(field.get("code","")).lower())
            if key not in expected: continue
            special = " 2011 interviewer code 0 for no fixed address requires release-level validation." if key[0] == "2011" else " 2020 includes refusal code 999." if key[0] == "2020" else ""
            field.update({"mapping_status":STATUS,"note":STATUS + special,"caveat":CAVEAT,"value_labels":FIELDS[key[0]][2],
                          "value_label_status":"Official questionnaire/Codebook categories reviewed; address text and frequencies omitted",
                          "value_label_source":f"sources_official/{FIELDS[key[0]][1]}; sources_official/CHARLS_{key[0]}_Codebook_extracted.txt"})
            site_found.add(key)
    if site_found!=expected: raise ValueError(f"Site rows missing: {expected-site_found}")
    SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Reviewed and synchronized {len(expected)} self-employment business location fields.")


if __name__=="__main__": main()
