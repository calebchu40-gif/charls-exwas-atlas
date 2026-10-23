"""Review wave-specific BB004 residential-history metadata without forcing harmonization."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVES = ("2011", "2013", "2015", "2018")
DOCS = {
    "2011": ("sources_official/CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", "sources_official/CHARLS_2011_Codebook_extracted.txt"),
    "2013": ("sources_official/CHARLS_2013_Questionnaire_extracted.txt", "sources_official/CHARLS_2013_Codebook_extracted.txt"),
    "2015": ("sources_official/CHARLS_2015_Questionnaire_extracted.txt", "sources_official/CHARLS_2015_Codebook_extracted.txt"),
    "2018": ("sources_official/CHARLS_2018_Questionnaire_extracted.txt", "sources_official/CHARLS_2018_Codebook_extracted.txt"),
}
LABELS = "1=Yes; 2=No"
COMMON_REVIEW = "official wave questionnaire and Codebook reviewed; field meaning is wave-specific; no frequencies copied"
NOTES = {
    "2011": (
        "2011 BB004 has an unresolved official-source identity conflict: the baseline questionnaire asks whether the respondent lived in the same village/community as now when first moving to the permanent address, "
        "while the 2011 Codebook describes the field as whether the respondent lived in the same county/city as the first move. Keep response labels blank and retain this C record on HOLD FOR SOURCE VALIDATION, excluded from analysis until the released field identity is reconciled. "
        "Do not harmonize with later BB004 rows or infer a response meaning from the shared code name."
    ),
    "2013": (
        "2013 BB004 asks whether, when first moving to the permanent address, the respondent already lived in the same village/community as currently. A Yes response skips the conditional BB005 year item; No routes to that year. "
        "This is residential-history context, not current neighborhood quality or an environmental dose. Keep BB005 year separate, preserve routed missingness, and do not infer cross-wave equivalence or routine covariate use."
    ),
    "2015": (
        "2015 BB004 asks whether, when first moving to the permanent address, the respondent already lived in the same village/community as currently. A Yes response skips the conditional BB005 year item; No routes to that year. "
        "This is residential-history context, not current neighborhood quality or an environmental dose. Keep BB005 year separate, preserve routed missingness, and do not infer cross-wave equivalence or routine covariate use."
    ),
    "2018": (
        "2018 BB004 asks whether, when first moving to the current address BB001_W3, the respondent already lived in the same village/community as currently. A Yes response skips the conditional BB005_W3 year item; No routes to that year. "
        "This is residential-history context, not current neighborhood quality or an environmental dose. Keep BB005_W3 year separate, preserve routed missingness, and do not infer cross-wave equivalence or routine covariate use."
    ),
}


def update(row: dict, wave: str) -> None:
    row["Value.Label.Source"] = "; ".join(DOCS[wave])
    row["value_label_source"] = row["Value.Label.Source"]
    if wave == "2011":
        review = "questionnaire/Codebook field-identity conflict; response labels withheld; HOLD FOR SOURCE VALIDATION"
        row["Value.Labels"] = ""
        row["value_labels"] = ""
        row["Review.Flag"] = "HOLD FOR SOURCE VALIDATION: 2011 BB004 questionnaire and Codebook describe different geographic reference units"
    else:
        review = COMMON_REVIEW + "; 1=Yes/2=No; conditional year follow-up retained"
        row["Value.Labels"] = LABELS
        row["value_labels"] = LABELS
        row["Review.Flag"] = "C residential-history metadata; not a current neighborhood exposure or selected adjustment covariate"
    row["Value.Label.Review"] = review
    row["value_label_review"] = review
    row["Harmonization.Status"] = NOTES[wave]
    row["harmonization_status"] = NOTES[wave]


def main() -> None:
    for wave, (qdoc, cdoc) in DOCS.items():
        questionnaire = (ROOT / qdoc).read_text(encoding="utf-8", errors="replace").replace("\x00", "").casefold()
        codebook_lines = (ROOT / cdoc).read_text(encoding="utf-8", errors="replace").replace("\x00", "").splitlines()
        if "bb004" not in questionnaire:
            raise ValueError(f"Questionnaire missing BB004 in {wave}")
        if not any(line.lstrip().lstrip("•").strip().casefold().startswith("bb004") for line in codebook_lines):
            raise ValueError(f"Codebook missing BB004 heading in {wave}")
        if wave == "2011":
            if "same village/community" not in questionnaire or not any("county/city" in line.casefold() and "bb004" in line.casefold() for line in codebook_lines):
                raise ValueError("Expected 2011 questionnaire/Codebook identity conflict not found")
        else:
            if "same village/community" not in questionnaire:
                raise ValueError(f"Questionnaire meaning not confirmed for {wave}")
            codebook = "\n".join(codebook_lines).casefold()
            if "1 yes" not in codebook or "2 no" not in codebook:
                raise ValueError(f"Codebook Yes/No labels not confirmed for {wave}")

    codes_path = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
    fields = pd.read_csv(codes_path, dtype=str, encoding="utf-8-sig").fillna("")
    mask = fields["Variable.Name"].str.lower().eq("bb004") & fields["Source.Wave"].isin(WAVES) & fields["epcf"].str.lower().eq("c")
    found = set(fields.loc[mask, "Source.Wave"])
    if found != set(WAVES) or int(mask.sum()) != 4:
        raise ValueError(f"Expected four C rows for BB004; found waves={sorted(found)}, rows={int(mask.sum())}")
    for idx in fields.index[mask]:
        wave = fields.at[idx, "Source.Wave"]
        row = fields.loc[idx].to_dict()
        update(row, wave)
        for key in ("Value.Labels", "Value.Label.Review", "Value.Label.Source", "Harmonization.Status", "Review.Flag"):
            fields.at[idx, key] = row[key]
    fields.to_csv(codes_path, index=False, encoding="utf-8-sig")

    for path in (ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json", ROOT / "site-prototype/dist/catalog_c.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        selected = [r for r in rows if str(r.get("Variable.Name", "")).lower() == "bb004" and str(r.get("Source.Wave", "")) in WAVES and str(r.get("epcf", "")).lower() == "c"]
        if len(selected) != 4:
            raise ValueError(f"{path}: expected four C BB004 rows, found {len(selected)}")
        for row in selected:
            update(row, str(row["Source.Wave"]))
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    series_path = ROOT / "audit/charls_atlas_candidate_series_v0.csv"
    series = pd.read_csv(series_path, dtype=str, encoding="utf-8-sig").fillna("")
    series_mask = series["Variable.Name"].str.lower().eq("bb004") & series["epcf"].str.lower().eq("c")
    if int(series_mask.sum()) != 1:
        raise ValueError("Expected one grouped C candidate-series row for BB004")
    summary_review = "wave-specific BB004 review complete; 2011 questionnaire/Codebook identity conflict remains on HOLD FOR SOURCE VALIDATION; later Yes/No labels are not evidence of cross-wave equivalence; see field-level catalog"
    summary_note = "2011 county/city versus questionnaire village/community conflict unresolved; 2013/2015 permanent-address and 2018 current-address reference items retain conditional year follow-ups. Do not combine without release validation and a prespecified residential-history estimand."
    series.loc[series_mask, "value_labels"] = ""
    series.loc[series_mask, "value_label_review"] = summary_review
    series.loc[series_mask, "value_label_source"] = "; ".join(sorted({p for docs in DOCS.values() for p in docs}))
    series.loc[series_mask, "harmonization_status"] = summary_note
    series.to_csv(series_path, index=False, encoding="utf-8-sig")
    (ROOT / "audit/charls_atlas_candidate_series_v0.json").write_text(json.dumps(series.to_dict(orient="records"), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    audit_path = ROOT / "audit/residential_history_bb004_source_review_2011_2018_2026-10-24.md"
    lines = ["# BB004 residential-history source review, 2011–2018", "", "Reviewed official wave questionnaires and Codebooks. No respondent records, Codebook frequencies, or descriptive summaries were used.", "", "| Wave | Source interpretation | Catalog treatment |", "|---|---|---|"]
    for wave in WAVES:
        treatment = "Response labels withheld; HOLD FOR SOURCE VALIDATION pending field identity reconciliation." if wave == "2011" else "1=Yes; 2=No; retain conditional year follow-up and wave-specific reference point."
        lines.append(f"| {wave} | {NOTES[wave]} | {treatment} |")
    lines.extend(["", "Sources by wave:", ""])
    lines.extend(f"- {wave}: `{qdoc}`; `{cdoc}`" for wave, (qdoc, cdoc) in DOCS.items())
    lines.extend(["", "BB004 is residential-history information, not a direct environmental dose or current neighborhood-quality measure. The same variable name does not establish equivalence: the 2011 Codebook's geographic reference conflicts with its questionnaire, and the later question references differ in wording/routing. Keep each wave separate unless the released variable identity, eligibility, and target estimand are validated.", ""])
    audit_path.write_text("\n".join(lines), encoding="utf-8")
    print("Reviewed BB004 in four waves; later labels are wave-specific; 2011 source conflict remains locked.")


if __name__ == "__main__":
    main()
