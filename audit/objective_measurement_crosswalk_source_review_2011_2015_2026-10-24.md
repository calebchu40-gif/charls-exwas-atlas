# Objective measurement phenotype crosswalk: wave-specific source review

Updated 2026-10-24.

The objective-measurement candidate crosswalk now cites the official source set separately for each wave. The 2011 candidates point to the official Physical Examination Questionnaire, the 2011 Codebook and the baseline user guide; 2013 and 2015 candidates point to their respective Biomarker Questionnaires and Codebooks, with the wave-specific release note where available. A reproducible token-level check confirms that all 36 listed candidate field identifiers occur in each wave's extracted Codebook (2011, 2013 and 2015). The original Codebook display labels are also preserved for each field and wave; this makes visible differences such as the variable labels for waist circumference and grip readings. One 2013 weight label is clipped by a page boundary in the extracted source and is flagged as such rather than silently completed.

This change improves provenance but does not certify every candidate field mapping. The token-level Codebook check proves only that a code string occurs in the wave's Codebook; it does not prove item meaning, questionnaire routing, units, valid-value rules, or availability in a particular release file. The 2011 questionnaire/manual uses LI* item identifiers for some protocol content, whereas the release Codebook uses QA*/QB*/QC* field names. Similar wording is not enough to establish identity. The site therefore states that the LI and release-field identifiers are not presumed to map one-to-one. Across all three waves, the listed variable strings remain candidates until these item-level checks have been completed.

The website displays these 108 wave-specific Codebook field labels in the searchable objective-phenotype table, alongside the 45 concept-wave mappings. The label text is searchable and preserves source spelling/capitalization where extracted; the clipped 2013 QL002 string is visibly marked as a page-boundary extraction issue.

The page is scoped to 2011, 2013 and 2015 because those are the waves represented by the current official questionnaire/Codebook candidate crosswalk. A search of 2018 and 2020 Codebooks did not find the same QA–QM candidate identifiers; this code-name difference alone does not establish that no comparable physical measures exist in those waves. No 2018/2020 physical-measurement rows are inferred until the wave-specific measurement instruments and release documentation are identified and checked. The UI also directs visitors to the separate blood-biomarker catalogue for laboratory analytes and clarifies that 2013 field measurement is not blood testing.

The crosswalk is a metadata aid for a future phenotype catalogue. It contains no respondent observations, Codebook frequencies or summary statistics, or estimated associations. Repeated readings are preserved as separate source fields; derived summaries such as mean blood pressure, walking speed or grip-strength summaries require a prespecified rule before any model is fit. Structural skips are not treated as zero. Cross-wave pooling remains unapproved pending field-level comparability review.

## Sources

- `sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official.doc`
- `sources_official/CHARLS_2011_Codebook_extracted.txt`
- `sources_official/CHARLS_2011_National_Baseline_Users_Guide.pdf`
- `sources_official/CHARLS_2013_Biomarker_Questionnaire.pdf`
- `sources_official/CHARLS_2013_Codebook.pdf`
- `sources_official/CHARLS_2013_Wave2_Release_Note.pdf`
- `sources_official/CHARLS_2015_Biomarker_Questionnaire.pdf`
- `sources_official/CHARLS_2015_Codebook.pdf`
- `sources_official/CHARLS_2015_Blood_Release_Note.pdf`

The authoritative files are retained in `sources_official/`; the live website exposes only field metadata and source paths, not CHARLS respondent-level records.


## 2026-10-24 continued: 2018–2023 objective-measurement coverage boundary

The official CHARLS Wave 4 (2018) User’s Guide states that non-blood biomarkers, including anthropometrics and blood pressure, were collected in Waves 1–3, while whole-blood biomarkers were collected in Waves 1 and 3. This provides direct wave-level evidence for excluding Wave 4 (2018) from the current physical-measurement and blood-biomarker catalogues, rather than relying only on absence of same-named QA–QM fields. The 2018 Codebook token search remains a supporting metadata check, not the basis of this exclusion.

Wave labels and survey phases require care. CHARLS’s official data portal labels the released dataset “2020 CHARLS Wave 5”; the official release announcement dates its publication to 16 November 2023. Separately, CHARLS recruitment notices describe 2020 as a pandemic-specific survey and the 2021–2023 collection as the fifth regular survey, explicitly including physical examinations, biospecimens and wearable-band data collection. These statements concern different data-release/fieldwork references and do not establish that the later regular-survey measurements are present in the released 2020 questionnaire or files. As of this review, the CHARLS data portal lists the 2020 Wave 5 package, but the project has not obtained or validated any 2021–2023 regular-survey data/codebook package. Thus no 2021–2023 rows are added, and no inference is made that the later measures are unavailable forever.

The 2020 questionnaire and Codebook were checked for the existing objective-measurement candidate codes. Self-reported questions about whether a doctor or nurse checked blood pressure, or whether a respondent received physical examinations/tests, are care-use/history reports and are not direct measurements performed by the CHARLS field team. No 2020 objective-measurement records are inferred from these questions. The currently displayed 2011/2013/2015 crosswalk remains candidate metadata; it does not certify release-file availability or analytical eligibility. No respondent records, response frequencies, or Codebook descriptive statistics were used.

Sources checked on 2026-10-24:

- Local official extract: `sources_official/CHARLS_2018_Users_Guide_extracted.txt`; official PDF: https://charls.pku.edu.cn/en/data/User2018.pdf
- Local official extracts: `sources_official/CHARLS_2020_User_Guide_English_extracted.txt`, `sources_official/CHARLS_2020_Questionnaire_English_extracted.txt`, and `sources_official/CHARLS_2020_Codebook_extracted.txt`.
- CHARLS recruitment notice for the 2021–2023 fifth regular survey, including physical examination, biospecimen and wearable-band collection: https://charls.pku.edu.cn/info/1131/1761.htm
- Current CHARLS data portal page listing the 2020 Wave 5 package: https://charls.charlsdata.com/pages/data/111/en.html
- Official announcement of the 2020 Wave 5 data release: https://charls.pku.edu.cn/en/info/1190/1331.htm
