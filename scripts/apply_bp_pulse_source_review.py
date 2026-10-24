"""Apply official questionnaire-backed source notes to BP and pulse candidates."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
WAVES = ("2011", "2013", "2015")
CONCEPTS = {
    "systolic_bp": {"codes": ("qa003", "qa007", "qa011"), "label": "收缩压"},
    "diastolic_bp": {"codes": ("qa004", "qa008", "qa012"), "label": "舒张压"},
    "pulse_rate": {"codes": ("qa005", "qa009", "qa013"), "label": "脉搏"},
}
QUESTIONNAIRES = {
    "2011": "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt",
}


def verify_sources() -> dict[str, str]:
    texts = {}
    for wave, relative in QUESTIONNAIRES.items():
        path = ROOT / relative
        if not path.exists():
            raise FileNotFoundError(path)
        text = path.read_bytes().decode("utf-8", errors="replace").replace("\x00", "").casefold()
        required = ("omron hem-7200", "three", "993", "999", "which arm", "how compliant", "what was r", "within the 30 minutes")
        missing = [term for term in required if term.casefold() not in text]
        if missing:
            raise ValueError(f"{wave} official questionnaire lacks expected BP protocol anchors: {missing}")
        for code in ("qa003", "qa004", "qa005", "qa007", "qa008", "qa009", "qa011", "qa012", "qa013"):
            if code not in text:
                # 2011 instruments use LI* item identifiers; the Codebook's QA* names
                # must not be asserted as one-to-one instrument field identities.
                if wave != "2011":
                    raise ValueError(f"{wave} questionnaire is missing exact published field {code}")
        if wave != "2011" and "mmhg" not in text:
            raise ValueError(f"{wave} questionnaire does not state blood-pressure unit mmHg")
        texts[wave] = text
    return texts


def source_note(wave: str, concept_id: str) -> tuple[str, str, str, str]:
    identity = (
        "2011 questionnaire measures this construct under LI* identifiers; the release Codebook has candidate QA* fields. "
        "The semantic mapping is plausible but LI-to-QA one-to-one field identity remains unverified, so retain as a candidate."
        if wave == "2011"
        else "2013/2015 Biomarker Questionnaire records these exact QA* fields and the matching wave Codebook labels; this confirms source meaning, not participant-level release availability or analysis eligibility."
    )
    shared = (
        "The official questionnaire documents three readings using an Omron HEM-7200 monitor, with the respondent asked to remain seated, relaxed and quiet; "
        "the cuff/arm, test position, compliance and recent smoking/exercise/alcohol/food within 30 minutes are recorded separately as measurement context. "
        "993 means tried but unable and 999 means chose not to complete, as defined for the systolic field; preserve these as status/route codes, never as measured values. "
        "Routed or unmeasured records are not zero. Keep the three readings separate until a release-specific valid-value and prespecified summary rule is approved. "
        "Protocol similarity does not by itself approve pooled cross-wave analysis. " + identity
    )
    if concept_id == "systolic_bp":
        return ("Three repeated systolic readings; questionnaire explicitly records mmHg. Preserve each reading and the 993/999 non-completion status codes.", "mmHg", shared, "systolic")
    if concept_id == "diastolic_bp":
        return ("Three repeated diastolic readings; questionnaire explicitly records mmHg. Preserve each reading separately; do not impute from a systolic status code.", "mmHg", shared, "diastolic")
    return ("Three pulse readings are collected alongside the BP measurements. The questionnaire labels the unit only as ‘P’ and does not explicitly state a pulse unit; leave unit unresolved rather than infer beats/minute.", "", shared + " No explicit pulse unit was located in the questionnaire; unit remains blank.", "pulse")


def update_crosswalk(texts: dict[str, str]) -> int:
    path = AUDIT / "objective_measurement_crosswalk_v1.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        headers = list(rows[0])
    if "unit" not in headers:
        headers.append("unit")
    count = 0
    for row in rows:
        cid, wave = row["concept_id"], row["wave"]
        if cid not in CONCEPTS or wave not in WAVES:
            continue
        semantics, unit, note, kind = source_note(wave, cid)
        row["value_semantics"] = semantics
        row["unit"] = unit
        row["source_status"] = (
            "official questionnaire, wave Codebook and repeated-measure protocol reviewed; candidate phenotype only; 2011 release-field identity remains unresolved"
            if wave == "2011" else
            "exact wave questionnaire field and Codebook label reviewed; candidate phenotype only; authorized-release and analysis eligibility remain unverified"
        )
        row["source_caveat"] = note
        row["codebook_presence"] = (
            "2011 QA* candidate labels are present in the release Codebook; questionnaire uses LI* IDs, and no one-to-one release crosswalk was located"
            if wave == "2011" else
            "exact QA* measurement fields and labels are present in the wave questionnaire and Codebook; token presence does not establish release coverage or valid-value rules"
        )
        if unit:
            row["source_caveat"] += " Blood pressure unit is explicitly mmHg."
        else:
            row["source_caveat"] += " No explicit pulse unit was located in the questionnaire; unit remains blank."
        count += 1
    for row in rows:
        row.setdefault("unit", "")
    expected = {(cid, wave) for cid in CONCEPTS for wave in WAVES}
    observed = {(row["concept_id"], row["wave"]) for row in rows if row["concept_id"] in CONCEPTS}
    if observed != expected or count != len(expected):
        raise ValueError(f"BP/pulse crosswalk coverage mismatch: {observed}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    encoded = json.dumps(rows, ensure_ascii=False, indent=2)
    (ROOT / "site-prototype/dist/objective_measurements_v1.json").write_text(encoded, encoding="utf-8")
    return count


def apply() -> None:
    texts = verify_sources()
    n_crosswalk = update_crosswalk(texts)
    print(f"Reviewed {n_crosswalk} BP/pulse concept-wave rows covering 27 P-role wave-field mappings; 2011 field identity caveat and unresolved pulse unit retained.")


if __name__ == "__main__":
    apply()
