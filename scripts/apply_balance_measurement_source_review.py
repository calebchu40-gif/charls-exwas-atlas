"""Apply wave-aware official-source notes to standing-balance phenotypes."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVES = ("2011", "2013", "2015")
CONCEPTS = {
    "balance_semi_tandem": {"codes": "qd002;qd003;qd004", "label": "半串联站立平衡"},
    "balance_full_tandem": {"codes": "qe002;qe003;qe004", "label": "全串联站立平衡"},
    "balance_side_by_side": {"codes": "qf002;qf003;qf004", "label": "并足站立平衡"},
}
QUESTIONNAIRES = {
    "2011": "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt",
}


def verify_sources() -> dict[str, str]:
    texts = {}
    anchors = {
        "2011": ("li879", "li880", "li881", "li896", "li897", "li898", "li886", "li887", "li888", "age>=70", "seconds"),
        "2013": ("qd002", "qd003", "qd004", "qe002", "qe003", "qe004", "qf002", "qf003", "qf004", "70 years old or above", "60 seconds"),
        "2015": ("qd002", "qd003", "qd004", "qe002", "qe003", "qe004", "qf002", "qf003", "qf004", "70 years old or above", "60 seconds"),
    }
    for wave, relative in QUESTIONNAIRES.items():
        path = ROOT / relative
        if not path.exists():
            raise FileNotFoundError(path)
        text = path.read_bytes().decode("utf-8", errors="replace").replace("\x00", "").casefold()
        missing = [term for term in anchors[wave] if term.casefold() not in text]
        if missing:
            raise ValueError(f"{wave} official balance-test questionnaire lacks expected anchors: {missing}")
        texts[wave] = text
    return texts


def source_note(wave: str, concept_id: str) -> tuple[str, str, str]:
    identity = (
        "The 2011 instrument records this test under LI* item identifiers while release Codebook fields use QD/QE/QF*; exact one-to-one release-field identity remains unverified."
        if wave == "2011" else
        f"The {wave} questionnaire and wave Codebook use these exact QD/QE/QF* fields; this confirms instrument metadata, not participant-level release availability or analysis eligibility."
    )
    if concept_id == "balance_semi_tandem":
        protocol = "Hold the semi-tandem position up to 10 seconds. Preserve full-duration completion, elapsed time when the full 10 seconds is not achieved, and compensatory-movement response as separate fields."
    elif concept_id == "balance_full_tandem":
        protocol = "The target duration is 30 seconds for age 70 or older and 60 seconds for younger participants. Preserve target duration, full-duration completion, elapsed time, and compensatory movement separately; these are not interchangeable outcomes."
    else:
        protocol = "Hold the side-by-side position up to 10 seconds. Preserve full-duration completion, elapsed time when the full 10 seconds is not achieved, and compensatory-movement response as separate fields."
    semantics = protocol + " Preserve 993 (tried but unable) and 999 (chose not) as test-status codes, not durations. A routed-out or unasked measurement is not zero seconds."
    caveat = protocol + " Retain safety/consent and preceding-test routes; do not assign zero to unasked duration or movement fields. Cross-wave comparability and release-specific valid/missing codes remain unapproved. " + identity
    status = (
        "official questionnaire and baseline user guide reviewed; candidate phenotype only; LI-to-Q-field identity and release eligibility remain unverified"
        if wave == "2011" else
        "exact wave questionnaire and Codebook reviewed; candidate phenotype only; authorized-release availability and analytic eligibility remain unverified"
    )
    return semantics, caveat, status


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
        semantics, caveat, status = source_note(wave, cid)
        row.update({
            "value_semantics": semantics,
            "source_status": status,
            "source_caveat": caveat,
            "codebook_presence": (
                "2011 QD/QE/QF* release Codebook candidates are semantically plausible; questionnaire uses LI* items and no exact field crosswalk was located"
                if wave == "2011" else
                f"exact {cid.replace('balance_', 'Q').replace('semi_tandem', 'D').replace('full_tandem', 'E').replace('side_by_side', 'F')}* source fields are present in the wave questionnaire and Codebook; token presence does not establish release coverage or valid-value rules"
            ),
            "source_document": (
                f"{QUESTIONNAIRES[wave]}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
                + ("; sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt" if wave == "2011" else "")
            ),
            "unit": "",
        })
        updated += 1
    expected = {(cid, wave) for cid in CONCEPTS for wave in WAVES}
    observed = {(r["concept_id"], r["wave"]) for r in rows if r["concept_id"] in CONCEPTS}
    if observed != expected or updated != len(expected):
        raise ValueError(f"balance-measurement coverage mismatch: {observed}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "site-prototype/dist/objective_measurements_v1.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Reviewed {updated} balance-test concept-wave rows; 2011 field-identity uncertainty and conditional duration/status semantics retained.")
    return updated


if __name__ == "__main__":
    apply()
