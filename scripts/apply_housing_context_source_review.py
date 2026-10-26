"""Apply official source review to household housing and indoor-context items."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from sync_food_crosswalk_index import sync_food_crosswalk_index

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit" / "food_environment_crosswalk_v1.csv"
SITE = ROOT / "site-prototype" / "dist" / "food_environment_v1.json"
RAW = ROOT / "audit" / "raw_variable_catalog_v1.csv"
REVIEW = "audit/housing_context_source_review_2026-10-24.md"
QUESTIONNAIRES = {
    "2011": "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "CHARLS_2018_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}
CODEBOOKS = {wave: f"CHARLS_{wave}_Codebook_extracted.txt" for wave in QUESTIONNAIRES}

REVIEWED = {
    (wave, "piped_gas_access", "i019" if wave != "2020" else "i018")
    for wave in QUESTIONNAIRES
} | {
    (wave, "residential_heating", "i020" if wave != "2020" else "i019")
    for wave in QUESTIONNAIRES
} | {
    ("2020", "tap_water_access", "i016"),
    ("2020", "waterworks_treatment", "i029"),
    ("2020", "air_cleaner_home", "i024"),
    ("2015", "air_cleaner_home", "i027_w3"),
    ("2018", "air_cleaner_home", "i027_w3"),
    ("2020", "floor_condition", "i027"),
    ("2020", "residence_move_in_time", "i002"),
    ("2020", "residence_move_in_time", "i003"),
} | {
    (wave, "elevator_access", "i009" if wave != "2020" else "i007")
    for wave in QUESTIONNAIRES
} | {
    ("2011", "home_accessibility", "i010"),
    ("2013", "home_accessibility", "i010"),
    ("2015", "home_accessibility", "i010"),
    ("2018", "home_accessibility", "i010_w4"),
    ("2020", "home_accessibility", "i009"),
} | {
    (wave, "running_water", "i017") for wave in ("2011", "2013", "2015", "2018")
} | {
    (wave, concept, code)
    for wave in QUESTIONNAIRES
    for concept, code in (("indoor_cleanliness", "i025"), ("indoor_temperature", "i026"))
}

CONCEPT_CAVEATS = {
    "piped_gas_access": (
        "Residence-level availability of coal/natural-gas supply, not proof that the household uses it "
        "for cooking/heating or a measure of combustion exposure. The 2020 question names "
        "XFinancialResp's house; confirm household-person linkage before person-level assignment. "
        f"Wave-specific item wording and yes/no categories were reviewed; see {REVIEW}."
    ),
    "residential_heating": (
        "Residence-level heating-availability candidate. Preserve questionnaire-specific wording and "
        "routes: 2011/2018 explicitly exclude earth-heating systems (土暖气) and heating-capable AC, and 2011–2018 "
        "heating-source routing differs from the 2020 item structure. The 2020 Codebook calls i019 "
        "Centralized Heating, while its questionnaire asks whether XFinancialResp's house has heating; "
        "retain both source label and question wording. Not a heating-energy or pollution-dose measure. "
        f"See {REVIEW} and audit/housing_fuel_source_review_2026-10-24.md."
    ),
    "tap_water_access": (
        "2020 asks whether XFinancialResp's house has tap water. This is household access, not a direct "
        "water-quality or contaminant measurement, and it is not automatically interchangeable with "
        "2011–2018 'running water' items. Confirm household-person linkage before person-level assignment."
    ),
    "running_water": (
        "Residence-level running-water access, not water quality, source or treatment, a contaminant assay, "
        "microbial/chemical measurement, "
        "or individual water intake. The reviewed 2011–2018 questions ask whether the residence has running water; "
        "2020 tap-water access is a distinct item and is not assumed equivalent. Verify household-person linkage, "
        "special values, eligible denominator, and missingness in the authorized release."
    ),
    "waterworks_treatment": (
        "2020 asks whether tap water is treated by waterworks; categories are Yes, No, and Do not know. "
        "Preserve Do not know and verify release-specific eligibility/missingness. This is reported "
        "treatment status, not a contaminant assay or verified water-quality result."
    ),
    "air_cleaner_home": (
        "2015 and 2018 ask whether the residence has an air cleaner (Yes/No); 2020 asks whether "
        "XFinancialResp's house has one (Yes/No). The 2020 questionnaire permits interviewer recording "
        "only when the interviewer is in the home and clearly knows the answer, otherwise asking the respondent. "
        "Presence does not establish use, filter condition, ventilation, pollutant concentration, or personal "
        "exposure. Preserve wave-specific household referents and confirm linkage before person-level assignment."
    ),
    "indoor_cleanliness": (
        "Household-level interviewer-recorded observation of indoor tidiness/cleanliness, with ordered response categories; "
        "higher codes indicate poorer reported condition. This is not a standardized hygiene audit or a measure "
        "of indoor pollutants. Preserve the 2011 source-version discrepancy over whether code 6 Not applicable "
        "is offered; do not infer or harmonize it without the release questionnaire/codebook version."
    ),
    "indoor_temperature": (
        "Household-level interviewer-recorded assessment of perceived indoor temperature, not a thermometer reading or "
        "personal thermal dose. Preserve the ordered hot-to-cold categories and the wave-specific Not applicable "
        "category; the 2011 source-version discrepancy is documented in the source review."
    ),
    "floor_condition": (
        "2020 household-level floor-condition category: flat covered, flat concrete, or uneven. The questionnaire "
        "instructs the interviewer to record it only when in the respondent's housing and clearly certain; "
        "otherwise ask the respondent. This is a dwelling-condition proxy, not a mobility or fall-risk test. "
        "Preserve the nominal categories; do not infer a severity scale."
    ),
    "residence_move_in_time": (
        "2020 I002/I003 refer to when the Household Financial Respondent moved into current housing, not when "
        "the building was constructed. I002 is a calendar year with questionnaire range 1900–2020 and -1 when "
        "the respondent cannot answer; I003 is a separate fallback elapsed-time bracket for unclear year. "
        "Preserve the two response formats and household-person referent; validate special-value storage and "
        "routing in the authorized release before analysis."
    ),
    "elevator_access": (
        "Household/building-level elevator availability, not elevator use, an individual's mobility, or a direct "
        "accessibility outcome. In 2011–2018, the item is asked on the multi-storey/above-ground-floor route; a "
        "structural skip must not be recoded as No. In 2020, I007 asks about an elevator in the respondent's "
        "housing and gives an interviewer-in-home/certainty instruction. Retain the wave-specific route and "
        "household/person linkage; the item is not directly harmonized across waves."
    ),
    "home_accessibility": (
        "Household/building-level presence of accessibility facilities such as a non-stair ramp; not a measure "
        "of the respondent's disability, mobility, or accessibility standard. Waves 2011–2015 list Yes/No; 2018 "
        "and 2020 add a distinct 'no steps on flat ground/do not need' category. Preserve that category rather "
        "than collapsing it into No. The 2011–2018 I010=No route asks the entrance-step item; 2020 wording and "
        "interviewer instructions differ. Confirm household/person linkage and release-specific storage before use."
    ),
}

FIELD_NOTES = {
    "piped_gas_access": {
        wave: "Official questionnaire/Codebook reviewed: residence has coal-gas or natural-gas supply; preserve 1=Yes/2=No. This records availability, not actual fuel use."
        for wave in ("2011", "2013", "2015", "2018")
    } | {
        "2020": "Official questionnaire/Codebook reviewed: asks whether XFinancialResp's house has coal-gas or natural-gas supply; preserve 1=Yes/2=No. Availability is not actual fuel use."
    },
    "residential_heating": {
        "2011": "Official August 2011 baseline household questionnaire (read-only Word rendering, printed p. 182) and Codebook reviewed: asks whether the residence has heating facilities, excluding earth-heating systems and heating-capable air conditioners; Yes skips to I022 and No proceeds to I021. This is facility availability, not individual heating use or dose.",
        "2013": "Official questionnaire/Codebook reviewed. The availability item and heating-source routes vary by wave; see the source audit and retain the distinct source fields.",
        "2015": "Official questionnaire/Codebook reviewed. The availability item and heating-source routes vary by wave; see the source audit and retain the distinct source fields.",
        "2018": "Official questionnaire/Codebook reviewed: asks whether the residence has heating, excluding earth-heating systems and heating-capable air conditioners; Yes skips to I022_W4 and No proceeds to I021_W4. This is facility availability, not individual heating use or dose.",
    } | {
        "2020": "Official questionnaire/Codebook reviewed: questionnaire asks whether XFinancialResp's house has heating; Codebook label says Centralized Heating. Preserve this wording discrepancy; do not silently narrow the questionnaire meaning."
    },
    "tap_water_access": {
        "2020": "Official questionnaire/Codebook reviewed: XFinancialResp's house has tap water; 1=Yes/2=No. Household access only, not water quality."
    },
    "running_water": {
        wave: "Official questionnaire/Codebook reviewed: asks whether the residence has running water; preserve 1=Yes/2=No. Household access only, not water quality."
        for wave in ("2011", "2013", "2015", "2018")
    },
    "waterworks_treatment": {
        "2020": "Official questionnaire/Codebook reviewed: asks whether tap water is treated by waterworks; preserve 1=Yes/2=No/997=Do not know. Do not recode 997 as No."
    },
    "air_cleaner_home": {
        "2015": "Official questionnaire/Codebook reviewed: I027_W3 asks whether the residence has an air cleaner; preserve 1=Yes/2=No.",
        "2018": "Official questionnaire/Codebook reviewed: I027_W3 asks whether the residence has an air cleaner; preserve 1=Yes/2=No.",
        "2020": "Official questionnaire/Codebook reviewed: presence of an air cleaner in XFinancialResp's house; 1=Yes/2=No. Questionnaire allows interviewer recording only when in the home and certain, otherwise ask respondent."
    },
    "indoor_cleanliness": {
        wave: "Official questionnaire/Codebook reviewed: I025 is interviewer-recorded household cleanliness/tidiness; preserve the wave's stated ordinal categories and Not applicable only where the source lists it."
        for wave in QUESTIONNAIRES
    },
    "indoor_temperature": {
        wave: "Official questionnaire/Codebook reviewed: I026 is interviewer-recorded household temperature assessment, not measured temperature; preserve hot-to-cold categories and the wave's stated Not applicable option."
        for wave in QUESTIONNAIRES
    },
    "floor_condition": {
        "2020": "Official 2020 questionnaire/Codebook reviewed: I027 ground condition; preserve 1=Flat covered, 2=Flat concrete, 3=Uneven. Interviewer records only when in R's housing and certain; otherwise ask R."
    },
    "residence_move_in_time": {
        "2020": "Official 2020 questionnaire/Codebook reviewed: I002 is Household Financial Respondent move-in year (1900–2020; interviewer enters -1 if unable to answer); I003 is the separate fallback category for unclear year. Preserve distinct formats; Codebook frequencies are not included."
    },
    "elevator_access": {
        **{
            wave: "Official questionnaire/Codebook reviewed: elevator availability is asked on the multi-storey residence route (I008 > 1 to I009); preserve 1=Yes/2=No and do not code a structural skip as No."
            for wave in ("2011", "2013", "2015", "2018")
        },
        "2020": "Official questionnaire/Codebook reviewed: I007 asks whether the respondent's housing has an elevator (1=Yes/2=No); interviewer records only when in the home and clearly certain, otherwise asks the respondent. Unlike earlier waves, this item is not shown behind the I008 > 1 route.",
    },
    "home_accessibility": {
        **{
            wave: "Official questionnaire/Codebook reviewed: I010 asks whether the residence has accessibility facilities such as a non-stair ramp; preserve 1=Yes/2=No. If No, the questionnaire routes to the entrance-step item."
            for wave in ("2011", "2013", "2015")
        },
        "2018": "Official questionnaire/Codebook reviewed: I010_W4 lists 1=Yes, 2=No, and 3=No steps on level ground/no need. Preserve category 3 separately; only category 2 routes to the entrance-step item.",
        "2020": "Official questionnaire/Codebook reviewed: I009 lists 1=Yes, 2=No, and 3=No steps on flat ground/do not need. Preserve category 3 separately. Interviewer records only when in the respondent's housing and clearly certain, otherwise asks the respondent.",
    },
}

FIELD_VALUE_LABELS = {
    (wave, "elevator_access"): "1=Yes; 2=No"
    for wave in QUESTIONNAIRES
} | {
    (wave, "running_water"): "1=Yes; 2=No"
    for wave in ("2011", "2013", "2015", "2018")
} | {
    (wave, "home_accessibility"): (
        "1=Yes; 2=No" if wave in {"2011", "2013", "2015"}
        else "1=Yes; 2=No; 3=Do not need"
    )
    for wave in QUESTIONNAIRES
}


def source_paths(wave: str, concept_id: str = "") -> str:
    if concept_id == "residential_heating" and wave == "2011":
        return (
            "sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc; "
            "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; "
            f"sources_official/{CODEBOOKS[wave]}"
        )
    questionnaire = QUESTIONNAIRES[wave]
    if concept_id == "running_water" and wave in {"2013", "2015"}:
        questionnaire = "CHARLS_2013_2015_housing_questionnaire_pages_extracted.txt"
    return f"sources_official/{questionnaire}; sources_official/{CODEBOOKS[wave]}"


def validate_sources() -> None:
    for wave, concept_id, code in REVIEWED:
        questionnaire = QUESTIONNAIRES[wave]
        if concept_id == "running_water" and wave in {"2013", "2015"}:
            questionnaire = "CHARLS_2013_2015_housing_questionnaire_pages_extracted.txt"
        q = (ROOT / "sources_official" / questionnaire).read_text(encoding="utf-8", errors="ignore").casefold()
        cb = (ROOT / "sources_official" / CODEBOOKS[wave]).read_text(encoding="utf-8", errors="ignore").casefold()
        if code.casefold() not in q or code.casefold() not in cb:
            raise ValueError(f"Official questionnaire/Codebook missing {wave} {code}")
        if (wave, concept_id, code) == ("2020", "air_cleaner_home", "i024"):
            if "record if interviewer is in r's housing and clearly know the answer, otherwise ask r" not in q:
                raise ValueError("2020 air-cleaner interview mode instruction not found")
        if (wave, concept_id, code) == ("2020", "floor_condition", "i027"):
            if "record if interviewer is in r's housing and clearly know the answer, otherwise ask r" not in q:
                raise ValueError("2020 floor-condition interviewer instruction not found")
        if (wave, concept_id, code) == ("2020", "residence_move_in_time", "i002"):
            for phrase in ("when did [ xfinancialresp] move into this housing", "1900, 2020", "enter “-1” if r cannot answer"):
                if phrase not in q:
                    raise ValueError(f"2020 move-in-year questionnaire phrase not found: {phrase}")
            if "i002: time house built" not in cb:
                raise ValueError("2020 move-in-year Codebook identifier not found")
        if (wave, concept_id, code) == ("2020", "residence_move_in_time", "i003"):
            for phrase in ("if respondent is unclear about year", "0-5 years", "more than 40 years"):
                if phrase not in q:
                    raise ValueError(f"2020 move-in fallback questionnaire phrase not found: {phrase}")
            if "i003: time interval house built" not in cb:
                raise ValueError("2020 move-in fallback Codebook identifier not found")
        if (wave, concept_id, code) in (("2015", "air_cleaner_home", "i027_w3"), ("2018", "air_cleaner_home", "i027_w3")):
            if "does your residence have an air cleaner in your home" not in q:
                raise ValueError(f"{wave} air-cleaner wording not found")
        if (wave, concept_id, code) == ("2020", "residential_heating", "i019"):
            if "i019 does [xfinancialresp]’s house have heating?" not in q or "i019: centralized heating" not in cb:
                raise ValueError("2020 heating questionnaire/Codebook label discrepancy not found")
        if concept_id in {"indoor_cleanliness", "indoor_temperature"}:
            starts = [match.start() for match in re.finditer(code.casefold(), q)]
            if not any("interviewer records it" in q[start:start + 700] for start in starts):
                raise ValueError(f"{wave} {code} interviewer-record instruction not found")
            if "not applicable" not in cb and wave != "2011":
                raise ValueError(f"{wave} {code} Codebook Not applicable category not found")
        if concept_id == "elevator_access":
            if wave == "2020":
                if "i007 does it have elevator?" not in q or "record if interviewer is in r's housing" not in q:
                    raise ValueError("2020 elevator wording/interviewer instruction not found")
            else:
                if not re.search(r"if\s+i008\s*>\s*1,\s*ask\s+i009", q):
                    raise ValueError(f"{wave} elevator route wording not found")
                if "i009" not in q or "1. yes" not in q or "2. no" not in q:
                    raise ValueError(f"{wave} elevator field/Yes-No categories not found")
            if not re.search(r"\b1\s+yes\b", cb) or not re.search(r"\b2\s+no\b", cb):
                raise ValueError(f"{wave} elevator Codebook response labels not found")
        if concept_id == "home_accessibility":
            if wave in {"2011", "2013", "2015"}:
                if "are there any handicapped facilities" not in q or not re.search(r"if\s+i010\s*=\s*2,\s*ask\s+i011", q):
                    raise ValueError(f"{wave} home-accessibility wording/route not found")
                if not re.search(r"\b1\s+yes\b", cb) or not re.search(r"\b2\s+no\b", cb):
                    raise ValueError(f"{wave} home-accessibility Codebook Yes/No labels not found")
            elif wave == "2018":
                if not re.search(r"i010_w4\s*=\s*2,\s*ask\s+i011", q) or "no steps on level ground, no need for handicapped facilities" not in q:
                    raise ValueError("2018 home-accessibility category/route not found")
                if "3 do not need" not in cb:
                    raise ValueError("2018 home-accessibility Codebook third category not found")
            else:
                if "i009 are there any handicapped facilities" not in q or "no steps on the flat ground, do not need handicapped facilities" not in q:
                    raise ValueError("2020 home-accessibility wording/category not found")
                if "3 do not need" not in cb:
                    raise ValueError("2020 home-accessibility Codebook third category not found")
    baseline_q = (ROOT / "sources_official" / "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt").read_text(encoding="utf-8", errors="ignore").casefold()
    household_q = (ROOT / "sources_official" / QUESTIONNAIRES["2011"]).read_text(encoding="utf-8", errors="ignore").casefold()
    baseline_cb = (ROOT / "sources_official" / CODEBOOKS["2011"]).read_text(encoding="utf-8", errors="ignore").casefold()
    if "i025 [interviewer records it]" not in baseline_q or "6. not applicable" not in baseline_q:
        raise ValueError("2011 baseline questionnaire I025 Not applicable source variant not found")
    if "i025" not in household_q or "not applicable" in household_q[household_q.find("i025"):household_q.find("i026")]:
        raise ValueError("2011 household-questionnaire I025 1–5 source variant not found")
    if "i025" not in baseline_cb or "not applicable" in baseline_cb[baseline_cb.find("i025"):baseline_cb.find("i026")]:
        raise ValueError("2011 Codebook I025 1–5 categories not found")


def main() -> None:
    validate_sources()
    with AUDIT.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        rows = list(reader)
    # I027_W3 was present in the 2018 raw variable catalogue and official
    # sources but was not yet represented in the housing crosswalk. Add it
    # from the metadata catalogue; never infer any respondent values.
    raw_rows = list(csv.DictReader(RAW.open(encoding="utf-8-sig", newline="")))
    for wave, concept_id, code in REVIEWED:
        if any((str(r["wave"]), str(r["concept_id"]), str(r["code"]).lower()) == (wave, concept_id, code) for r in rows):
            continue
        matches = [r for r in raw_rows if str(r["wave"]) == wave and str(r["variable"]).lower() == code]
        if len(matches) != 1:
            raise ValueError(f"Expected one raw catalogue row for missing mapping {(wave, concept_id, code)}; found {len(matches)}")
        if (wave, concept_id, code) != ("2018", "air_cleaner_home", "i027_w3"):
            raise ValueError(f"No reviewed insertion rule for {(wave, concept_id, code)}")
        source = matches[0]
        if concept_id in {"indoor_cleanliness", "indoor_temperature"}:
            raise ValueError(f"Missing reviewed household field should not be auto-inserted: {(wave, concept_id, code)}")
        rows.append({
            "concept_id": concept_id,
            "concept_label": "Air cleaner present in residence",
            "domain": "Indoor environment",
            "wave": wave,
            "code": code,
            "module": source["module"],
            "source_label": source["variable_label"],
            "code_value_labels": "1=Yes; 2=No",
            "mapping_status": "",
            "caveat": "",
        })
    found: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (str(row["wave"]), str(row["concept_id"]), str(row["code"]).lower())
        if key not in REVIEWED:
            continue
        wave, concept_id, code = key
        row["mapping_status"] = f"official {wave} questionnaire/Codebook wording, target and response categories reviewed; see {REVIEW}"
        row["caveat"] = CONCEPT_CAVEATS[concept_id]
        if (wave, concept_id) in FIELD_VALUE_LABELS:
            row["code_value_labels"] = FIELD_VALUE_LABELS[(wave, concept_id)]
        found.add(key)
    if found != REVIEWED:
        raise ValueError(f"Crosswalk mismatch; missing={sorted(REVIEWED-found)}, unexpected={sorted(found-REVIEWED)}")
    with AUDIT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    sync_food_crosswalk_index(ROOT, {(wave, code.lower(), concept) for wave, concept, code in REVIEWED})

    data = json.loads(SITE.read_text(encoding="utf-8"))
    updated: set[tuple[str, str, str]] = set()
    for concept in data:
        concept_id = concept.get("concept_id", "")
        if concept_id not in CONCEPT_CAVEATS:
            continue
        concept["caveat"] = CONCEPT_CAVEATS[concept_id]
        for field in concept.get("source_fields", []):
            wave = str(field.get("wave", ""))
            code = str(field.get("code", "")).lower()
            key = (wave, concept_id, code)
            if key not in REVIEWED:
                continue
            field["note"] = f"{FIELD_NOTES[concept_id][wave]} See {REVIEW}."
            if (wave, concept_id) in FIELD_VALUE_LABELS:
                field["value_labels"] = FIELD_VALUE_LABELS[(wave, concept_id)]
            field["source_document"] = source_paths(wave, concept_id)
            updated.add(key)
        for wave, expected_concept, code in sorted(REVIEWED):
            key = (wave, expected_concept, code)
            if expected_concept != concept_id or key in updated:
                continue
            matches = [r for r in raw_rows if str(r["wave"]) == wave and str(r["variable"]).lower() == code]
            if len(matches) != 1:
                raise ValueError(f"Expected one raw catalogue source for site mapping {key}")
            source = matches[0]
            concept["source_fields"].append({
                "wave": wave,
                "code": code,
                "module": source["module"],
                "source_label": source["variable_label"],
                "value_labels": FIELD_VALUE_LABELS.get((wave, concept_id), "1=Yes; 2=No"),
                "note": f"{FIELD_NOTES[concept_id][wave]} See {REVIEW}.",
                "source_document": source_paths(wave, concept_id),
            })
            updated.add(key)
    if updated != REVIEWED:
        raise ValueError(f"Site mismatch; missing={sorted(REVIEWED-updated)}")
    SITE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Reviewed {len(updated)} housing-context wave/field mappings; no respondent data or Codebook frequencies used")


if __name__ == "__main__":
    main()
