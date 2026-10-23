"""Apply questionnaire-backed metadata to exact CHARLS timed-walk fields."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
WAVES = ("2011", "2013", "2015")
CODES = {"qg002": "first", "qg003": "second"}
CONCEPT_ID = "walking_speed"
CONCEPT_LABEL = "计时步行表现（2.5米，两次计时）"

SOURCE_PATHS = {
    "2011": "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Biomarker_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
}

COMMON_NOTE = (
    "Official instrument defines two usual-pace timed walks over a 2.5-metre course; each raw trial is recorded in seconds. "
    "Age 60+ and walking-safety/site eligibility gates apply. Preserve qg002/qg003 as trial components of one phenotype; "
    "questionnaire-defined 993 (tried but unable) and 999 (chose not to do it) are status codes, not elapsed seconds. "
    "Do not convert them to time, treat routed absence as zero, derive speed, or average trials until the authorized release, "
    "valid values, measurement eligibility and a prespecified derivation are verified. Cross-wave harmonization is not approved."
)


def verify_official_sources() -> None:
    for wave in WAVES:
        questionnaire = ROOT / SOURCE_PATHS[wave].split("; ")[0]
        codebook = ROOT / f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        if not questionnaire.exists() or not codebook.exists():
            raise FileNotFoundError(f"Missing official timed-walk source for {wave}")
        qtext = questionnaire.read_text(encoding="utf-8", errors="replace").replace("\0", "").casefold()
        ctext = codebook.read_text(encoding="utf-8", errors="replace").casefold()
        for token in ("2.5", "normal pace", "two times", "993", "999"):
            if token not in qtext:
                raise ValueError(f"{wave} official questionnaire is missing walking-test anchor {token!r}")
        for code, trial in (("qg002", "time-1"), ("qg003", "time-2")):
            if f"{code} : walking speed {trial}" not in ctext and f"{code}: walking speed {trial}" not in ctext:
                raise ValueError(f"{wave} Codebook is missing {code} walking-time label")
    guide = ROOT / "sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt"
    guide_text = guide.read_text(encoding="utf-8", errors="replace").casefold()
    if "2.5 meters" not in guide_text or "two times" not in guide_text or "60 years or older" not in guide_text:
        raise ValueError("2011 National Baseline User's Guide lacks the expected timed-walk protocol anchors")


def update_record(row: dict[str, str]) -> dict[str, str]:
    wave = str(row.get("Source.Wave", ""))
    code = str(row.get("Variable.Name", "")).lower()
    trial = CODES[code]
    identity_note = (
        " The 2011 questionnaire uses LI identifiers while the Codebook uses QG release-variable names; retain this as a candidate semantic mapping and do not claim exact LI-to-QG item identity without a release crosswalk."
        if wave == "2011"
        else ""
    )
    note = COMMON_NOTE + identity_note
    sources = SOURCE_PATHS[wave]
    row.update({
        "Candidate.Status": "official questionnaire/Codebook timed-walk candidate; release eligibility and analytic derivation remain pending",
        "Harmonization.Status": note,
        "Review.Flag": "phenotype candidate; preserve first/second trial identity and status codes; do not treat trials as independent concepts or derive a speed/summary without prespecified rules and authorized-release validation",
        "Value.Labels": "",
        "Value.Label.Source": sources,
        "Value.Label.Review": "continuous timed measurement; seconds and non-completion status codes reviewed from official instruments; no categorical response labels or Codebook summaries copied",
        "Concept.Unit.Candidates": f"{CONCEPT_ID}=seconds",
        "Unit": "seconds",
        "Concept.ID.Candidates": CONCEPT_ID,
        "Concept.Label.Candidates": CONCEPT_LABEL,
        "Concept.Mapping.Source": "audit/objective_measurement_crosswalk_v1.csv",
        "Concept.Mapping.Status": "official timed-walk instrument and wave Codebook reviewed; candidate P mapping, not an approved analysis variable",
        "Concept.Mapping.Caveat": note,
        "candidate_concept_ids": CONCEPT_ID,
        "candidate_concept_labels": CONCEPT_LABEL,
        "candidate_concept_units": f"{CONCEPT_ID}=seconds",
        "value_labels": "",
        "value_label_source": sources,
        "value_label_review": "continuous timed measurement; seconds and non-completion status codes reviewed from official instruments; no categorical response labels or Codebook summaries copied",
        "harmonization_status": note,
        "concept_mapping_sources": "audit/objective_measurement_crosswalk_v1.csv",
        "concept_mapping_statuses": "official timed-walk instrument and wave Codebook reviewed; candidate P mapping, not an approved analysis variable",
        "concept_mapping_caveats": note,
    })
    return row


def apply() -> int:
    verify_official_sources()
    field_path = AUDIT / "charls_atlas_candidate_fields_v0.csv"
    fields = pd.read_csv(field_path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = (
        fields["Source.Wave"].astype(str).isin(WAVES)
        & fields["Variable.Name"].astype(str).str.lower().isin(CODES)
        & fields["epcf"].astype(str).str.lower().eq("p")
        & fields["category"].astype(str).str.lower().eq("physical function")
    )
    targets = fields.loc[selected]
    expected = {(wave, code) for wave in WAVES for code in CODES}
    observed = set(zip(targets["Source.Wave"].astype(str), targets["Variable.Name"].astype(str).str.lower()))
    if observed != expected or len(targets) < len(expected):
        raise ValueError(f"Timed-walk P catalogue coverage mismatch: expected={expected}, observed={observed}, rows={len(targets)}")

    for idx in fields.index[selected]:
        fields.loc[idx] = pd.Series(update_record(fields.loc[idx].to_dict()))
    fields.to_csv(field_path, index=False, encoding="utf-8-sig")

    records = fields.to_dict(orient="records")
    encoded = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    (AUDIT / "charls_atlas_candidate_fields_v0.json").write_text(encoded, encoding="utf-8")
    (ROOT / "site-prototype" / "dist" / "catalog.json").write_text(encoded, encoding="utf-8")
    print(f"Reviewed {len(targets)} exact P-catalog timed-walk rows across three waves; units are seconds, trial status codes remain distinct, and no respondent data/statistics were used.")
    return int(len(targets))


if __name__ == "__main__":
    apply()
