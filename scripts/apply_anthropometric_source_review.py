"""Apply official-source notes and explicit units to core anthropometry."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVES = ("2011", "2013", "2015")
CONCEPTS = {
    "standing_height": {"codes": "qi002", "unit": "cm"},
    "arm_length": {"codes": "qj002", "unit": "cm"},
    "knee_height": {"codes": "qk002", "unit": "cm"},
    "body_weight": {"codes": "ql002", "unit": "kg"},
    "waist_circumference": {"codes": "qm002", "unit": "cm"},
}
QUESTIONNAIRES = {
    "2011": "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt",
}
CODE_FAMILIES = {"standing_height": "QI", "arm_length": "QJ", "knee_height": "QK", "body_weight": "QL", "waist_circumference": "QM"}
MANUAL_ITEMS = {"standing_height": "LI011", "arm_length": "LI015", "knee_height": "LI019", "body_weight": "LI841", "waist_circumference": "LI907"}


def verify_sources() -> dict[str, str]:
    texts = {}
    for wave, relative in QUESTIONNAIRES.items():
        path = ROOT / relative
        if not path.exists():
            raise FileNotFoundError(path)
        text = path.read_bytes().decode("utf-8", errors="replace").replace("\x00", "").casefold()
        required = (
            ("li011", "li015", "li019", "li841", "li907", "150kg", "993", "999")
            if wave == "2011" else
            tuple(f"{fam}002" for fam in ("qi", "qj", "qk", "ql", "qm")) + ("150kg", "993", "999")
        )
        missing = [term for term in required if term not in text]
        if missing:
            raise ValueError(f"{wave} official anthropometry questionnaire lacks expected anchors: {missing}")
        if wave != "2011" and ("qj003" not in text or "qk003" not in text or "ql004" not in text or "qm005" not in text):
            raise ValueError(f"{wave} official questionnaire lacks measurement-context fields")
        texts[wave] = text
    return texts


def source_note(wave: str, concept_id: str) -> tuple[str, str, str, str]:
    unit = CONCEPTS[concept_id]["unit"]
    identity = (
        f"The 2011 instrument records this measure as {MANUAL_ITEMS[concept_id]}; the release Codebook candidate uses {CODE_FAMILIES[concept_id]}002. Exact one-to-one release-field identity remains unresolved."
        if wave == "2011" else
        f"The {wave} questionnaire and wave Codebook document the exact {CODE_FAMILIES[concept_id]}002 measurement field; this does not establish participant-level release availability or analytic eligibility."
    )
    if concept_id == "standing_height":
        semantics = "Single standing-height reading in cm; preserve consent/completion, positioning and compliance context separately. Do not derive BMI in this metadata catalog."
        context = "Stadiometer protocol and noncompletion codes 993/999 are documented."
    elif concept_id == "arm_length":
        semantics = "Upper-arm length reading in cm; preserve measured arm side (2011 LI016_0; 2013/2015 QJ003) and compliance as separate context fields."
        context = "Do not combine side/context metadata with the length value; noncompletion codes 993/999 remain statuses."
    elif concept_id == "knee_height":
        semantics = "Knee-height reading in cm; preserve measured leg (2011 LI020_0; 2013/2015 QK003) and compliance as separate context fields."
        context = "Do not combine leg/context metadata with the height value; noncompletion codes 993/999 remain statuses."
    elif concept_id == "body_weight":
        semantics = "Measured body weight in kg, separate from the eligibility route and measurement-quality fields. The questionnaire routes out at the 150 kg threshold; do not interpret routed cases as zero or missing-at-random."
        context = "Keep eligibility, shoes, compliance and surface/context variables separate; preserve 993/999 as measurement statuses."
    else:
        semantics = "Waist circumference reading in cm; preserve consent/completion and clothing/context fields separately. Do not derive a health classification here."
        context = "The questionnaire records bulky-clothing context (2013/2015 QM005) and special noncompletion codes 993/999; 2011 route and clothing wording remain wave-specific."
    caveat = context + " Valid ranges, release-specific missing-code implementation, and cross-wave comparability require separate verification. " + identity
    status = (
        "official questionnaire and baseline user guide reviewed; candidate phenotype only; LI-to-Q-field identity and release eligibility remain unverified"
        if wave == "2011" else
        "exact wave questionnaire and Codebook reviewed; candidate phenotype only; authorized-release availability and analytic eligibility remain unverified"
    )
    return semantics, caveat, status, unit


def apply() -> int:
    verify_sources()
    path = ROOT / "audit/objective_measurement_crosswalk_v1.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        headers = list(rows[0])
    updated = 0
    for row in rows:
        cid, wave = row["concept_id"], row["wave"]
        if cid not in CONCEPTS or wave not in WAVES:
            continue
        semantics, caveat, status, unit = source_note(wave, cid)
        family = CODE_FAMILIES[cid]
        row.update({
            "value_semantics": semantics,
            "source_status": status,
            "source_caveat": caveat,
            "unit": unit,
            "codebook_presence": (
                f"2011 {family}* release Codebook candidate is semantically plausible; questionnaire uses {MANUAL_ITEMS[cid]}, and exact release-field identity was not established"
                if wave == "2011" else
                f"exact {family}002 measurement field and label are present in the wave questionnaire and Codebook; token presence does not establish release coverage or valid-value rules"
            ),
            "source_document": f"{QUESTIONNAIRES[wave]}; sources_official/CHARLS_{wave}_Codebook_extracted.txt" + ("; sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt" if wave == "2011" else ""),
        })
        updated += 1
    expected = {(cid, wave) for cid in CONCEPTS for wave in WAVES}
    observed = {(r["concept_id"], r["wave"]) for r in rows if r["concept_id"] in CONCEPTS}
    if observed != expected or updated != len(expected):
        raise ValueError(f"anthropometric source coverage mismatch: {observed}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "site-prototype/dist/objective_measurements_v1.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reviewed {updated} anthropometric concept-wave rows; units, side/context fields and unresolved 2011 identities retained.")
    return updated


if __name__ == "__main__":
    apply()
