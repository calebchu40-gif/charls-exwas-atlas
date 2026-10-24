"""Review household electricity and bathing-facility metadata from official sources."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from sync_food_crosswalk_index import sync_food_crosswalk_index

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit/food_environment_crosswalk_v1.csv"
SITE = ROOT / "site-prototype/dist/food_environment_v1.json"
REVIEW = "audit/electricity_bathing_source_review_2026-10-25.md"
QUESTIONNAIRES = {
    "2011": "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "CHARLS_2018_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}
FIELDS = {
    **{(w, "electricity_access", "i016" if w != "2020" else "i015"): "1=Yes; 2=No" for w in ("2011", "2013", "2018", "2020")},
    **{(w, "bathing_facility", "i018" if w != "2020" else "i017"): ("1=Hot water provided; 2=Water heater installed by the household; 3=No" if w != "2020" else "1=Unified hot water supply; 2=Water heater; 3=No") for w in QUESTIONNAIRES},
}


def status(wave: str, concept: str) -> str:
    detail = "yes/no response categories" if concept == "electricity_access" else "nominal response categories"
    return f"official {wave} questionnaire/Codebook wording, household referent and {detail} reviewed; release storage, eligible denominator and person-household linkage require QA; see {REVIEW}"


def caveat(wave: str, concept: str) -> str:
    if concept == "electricity_access":
        target = "XFinancialResp's house" if wave == "2020" else "the residence"
        return (f"Household/residence-level electricity availability for {target}; this is not an individual dose or a measure of electricity reliability, duration, source, or indoor pollution. "
                "Preserve Yes/No and verify release-specific special values, missingness, eligible denominator, and linkage from household referent to the analytic person before use. "
                "Wave-specific target wording is retained; cross-wave equivalence and individual exposure assignment are not established.")
    wording = "unified hot-water supply; water heater; no facility" if wave == "2020" else "hot water provided; household-installed water heater; no facility"
    return (f"Residence-level in-house shower/bath facility type; the questionnaire lists {wording}. Treat categories as nominal, not an ordinal comfort/quality scale; do not infer bathing frequency, water temperature, hygiene, or personal exposure. "
            "Preserve the wave-specific response wording, verify authorized-release storage, special values, missingness, and eligible denominator, and confirm household-person linkage. Cross-wave equivalence is unapproved.")


def validate_sources() -> None:
    for (wave, concept, code), labels in FIELDS.items():
        qname = QUESTIONNAIRES[wave]
        q = re.sub(r"\s+", " ", (ROOT / "sources_official" / qname).read_text(encoding="utf-8", errors="ignore").casefold())
        cbname = f"CHARLS_{wave}_Codebook_extracted.txt"
        cb = (ROOT / "sources_official" / cbname).read_text(encoding="utf-8", errors="ignore").casefold()
        if concept == "electricity_access":
            question = "does [xfinancialresp]’s house have electricity" if wave == "2020" else "does your residence have electricity"
        else:
            question = "is there in-house shower or bath facility? what type?"
        if question not in q:
            raise ValueError(f"Official {wave} questionnaire question missing for {code}")
        if code.casefold() not in cb:
            # A documented Codebook omission is not silently promoted to reviewed.
            if not (wave == "2015" and concept == "electricity_access" and "does your residence have electricity" in q):
                raise ValueError(f"Official {wave} Codebook field missing for {code}")


def main() -> None:
    validate_sources()
    with AUDIT.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns, rows = reader.fieldnames or [], list(reader)
    updated = set()
    for row in rows:
        key = (row["wave"], row["concept_id"], row["code"].lower())
        if key not in FIELDS:
            continue
        row["mapping_status"] = status(key[0], key[1])
        row["caveat"] = caveat(key[0], key[1])
        row["code_value_labels"] = FIELDS[key]
        updated.add(key)
    if updated != set(FIELDS):
        raise ValueError(f"Crosswalk coverage mismatch: missing={sorted(set(FIELDS)-updated)}")
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    sync_food_crosswalk_index(ROOT, {(w, code, concept) for w, concept, code in FIELDS})

    data = json.loads(SITE.read_text(encoding="utf-8"))
    site_updated = set()
    for concept in data:
        cid = concept.get("concept_id", "")
        for field in concept.get("source_fields", []):
            key = (str(field.get("wave", "")), cid, str(field.get("code", "")).lower())
            if key in FIELDS:
                field.update({"mapping_status": status(key[0], cid), "caveat": caveat(key[0], cid), "value_labels": FIELDS[key], "note": status(key[0], cid)})
                field["value_label_source"] = f"sources_official/{QUESTIONNAIRES[key[0]]}; sources_official/CHARLS_{key[0]}_Codebook_extracted.txt"
                field["value_label_status"] = "Official questionnaire and Codebook response categories reviewed; do not infer frequencies."
                site_updated.add(key)
        if cid in {"electricity_access", "bathing_facility"}:
            concept["caveat"] = caveat("2020", cid) + " " + caveat("2011", cid)
    if site_updated != set(FIELDS):
        raise ValueError(f"Browser data coverage mismatch: missing={sorted(set(FIELDS)-site_updated)}")
    SITE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Reviewed and synchronized {len(site_updated)} household electricity/bathing fields; no participant data or frequencies used.")


if __name__ == "__main__":
    main()
