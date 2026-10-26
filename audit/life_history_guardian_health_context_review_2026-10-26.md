# 2014 Life History childhood guardian-context review (2026-10-26)

## Scope and sources

Reviewed Section H (Parent Mental Health) of the official 2014 Life History Questionnaire against FAMILYINFORMATION Codebook field identities. The section includes caregiver emotional health, substance-related behaviors, broader behavior/justice-system history, and prolonged illness/disability. The Codebook is used only for field identities and labels; no response frequencies or participant values are included.

## Mapping decisions

| Concept group | Source fields | Decision and key boundary |
|---|---|---|
| Childhood female/male guardian anxiety and depressive symptoms | `h1_[ab]`, `h2_[ab]`, `h3_[ab]`, `h4_[ab]`, `h5_[ab]`, `h8_[ab]` (12) | Separate symptom, duration, related-symptom and interference items; not a clinical diagnosis or derived score. H4/H5/H8 follow the H3 depression route. |
| Childhood female/male guardian substance-use behaviors | `h9_[ab]s1-s5`, `h10_[ab]`, `h11_[ab]`, `h14_[ab]` (16) | Preserve separate alcohol/smoking/drug/gambling options and the none option. H10 follows alcohol; H11/H14 follow drug. Do not recode blank checkbox slots as No. |
| Childhood female/male guardian behavioral and justice-system history | `h15_[ab]s1-s6`, `h16_[ab]` (14) | Keep each H15 option slot and H16 charge field distinct. Female/male H16 option sets differ; do not harmonize them by position. |
| Childhood female/male guardian prolonged illness and disability | `h17_[ab]`, `h18_[ab]`, `h19_[ab]` (6) | Keep prolonged bed illness, serious physical deformity and mental abnormality as distinct family-context items, not respondent diagnoses. |

In the questionnaire, the female/male guardian is explicitly the caregiver represented by A4a/A4b, not necessarily a biological mother/father. If no corresponding guardian raised the respondent (A4a/A4b=5), the section is skipped. These routing rules are retained as caveats; absence or skip is not No. The questionnaire's stated routing and the exact stored representation still need verification in the authorized release.

## Atlas disposition

Added four provisional E-role discovery concepts and 48 field mappings to the independent 2014 special-survey catalog. “E” denotes candidate childhood family context, not a measured biological dose or an established causal exposure. These fields are not merged with the respondent's mental-health outcomes and do not enter the regular five-wave co-availability matrix. Legal/behavioral history is metadata-only; no respondent reports or small-cell summaries are published.

## Reproducibility

The source-specific builder is `scripts/build_life_history_exposure_crosswalk.py`; the generated field crosswalk and special-survey JSON are regenerated from official field labels and this audit's explicit concept definitions. The independent Life History catalog now has 26 concept groups and 529 source-field mapping rows (516 E-role, 13 P-role). These are not 529 independent variables or analysis-ready measures.

