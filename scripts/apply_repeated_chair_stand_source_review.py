"""Apply official-source notes to the five-times chair-stand phenotype."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WAVES = ("2011", "2013", "2015")
QUESTIONNAIRES = {
    "2011": "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt",
}


def verify_sources() -> dict[str, str]:
    texts = {}
    anchors = {
        "2011": ("li003", "li004", "li005", "li006", "li007", "li008", "five times", "usual pace", "fastest pace"),
        "2013": ("qh002", "qh003", "qh004", "qh005", "qh006", "five times", "usual pace", "fastest pace"),
        "2015": ("qh002", "qh003", "qh004", "qh005", "qh006", "five times", "usual pace", "fastest pace", "42 cm"),
    }
    for wave, relative in QUESTIONNAIRES.items():
        path = ROOT / relative
        if not path.exists():
            raise FileNotFoundError(path)
        text = path.read_bytes().decode("utf-8", errors="replace").replace("\x00", "").casefold()
        missing = [term for term in anchors[wave] if term.casefold() not in text]
        if missing:
            raise ValueError(f"{wave} official chair-stand questionnaire lacks expected anchors: {missing}")
        texts[wave] = text
    guide = (ROOT / "sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt").read_bytes().decode("utf-8", errors="replace").casefold()
    if "repeated chair stand" not in guide or "fastest pace five times" not in guide:
        raise ValueError("2011 official user guide lacks repeated chair-stand protocol anchors")
    return texts


def source_note(wave: str) -> tuple[str, str, str]:
    identity = (
        "2011 instrument uses LI003–LI008 while release candidates use QH002–QH006; exact LI-to-QH field identity remains unverified."
        if wave == "2011" else
        f"{wave} questionnaire and Codebook document the exact QH002–QH006 fields; this does not establish participant-level release availability or analytic eligibility."
    )
    semantics = (
        "Five-times sit-to-stand test: preserve completion/status, route-specific duration fields, completed stand count (0–5), and trunk/arm use separately. The questionnaire preamble says fastest pace, while the outcome prompt says usual pace; retain this source wording discrepancy rather than harmonizing it away."
    )
    caveat = (
        "993 means tried but unable and 999 means chose not to complete; preserve as statuses, not times/counts. Duration fields QH003/QH004 (2011 LI004/LI005) belong to different completion routes; do not merge or substitute one for the other. QH006 chair height and QH006_1 other-chair height are protocol metadata, not respondent height. Do not derive a summary score without release-specific validation and a prespecified rule. "
        + identity
    )
    status = (
        "official questionnaire and baseline user guide reviewed; candidate phenotype only; LI-to-QH field identity and release eligibility remain unverified"
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
        wave = row["wave"]
        if row["concept_id"] != "repeated_chair_stand" or wave not in WAVES:
            continue
        semantics, caveat, status = source_note(wave)
        row.update({
            "value_semantics": semantics,
            "source_status": status,
            "source_caveat": caveat,
            "unit": "",
            "codebook_presence": (
                "2011 QH* release candidates are semantically plausible; instrument uses LI003–LI008 and exact release-field identity was not established"
                if wave == "2011" else
                f"exact QH002–QH006 fields and labels are present in the {wave} questionnaire and Codebook; token presence does not establish release coverage or valid-value rules"
            ),
            "source_document": f"{QUESTIONNAIRES[wave]}; sources_official/CHARLS_{wave}_Codebook_extracted.txt" + ("; sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt" if wave == "2011" else ""),
        })
        updated += 1
    expected = {("repeated_chair_stand", wave) for wave in WAVES}
    observed = {(r["concept_id"], r["wave"]) for r in rows if r["concept_id"] == "repeated_chair_stand"}
    if observed != expected or updated != len(expected):
        raise ValueError(f"repeated chair-stand coverage mismatch: {observed}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "site-prototype/dist/objective_measurements_v1.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reviewed {updated} repeated chair-stand concept-wave rows; route-specific measures and wording conflict retained.")
    return updated


if __name__ == "__main__":
    apply()
