# Objective measurement phenotype crosswalk: wave-specific source review

Updated 2026-10-24.

The objective-measurement candidate crosswalk now cites the official source set separately for each wave. The 2011 candidates point to the official Physical Examination Questionnaire, the 2011 Codebook and the baseline user guide; 2013 and 2015 candidates point to their respective Biomarker Questionnaires and Codebooks, with the wave-specific release note where available. A reproducible token-level check confirms that all 36 listed candidate field identifiers occur in each wave's extracted Codebook (2011, 2013 and 2015).

This change improves provenance but does not certify every candidate field mapping. The token-level Codebook check proves only that a code string occurs in the wave's Codebook; it does not prove item meaning, questionnaire routing, units, valid-value rules, or availability in a particular release file. The 2011 questionnaire/manual uses LI* item identifiers for some protocol content, whereas the release Codebook uses QA*/QB*/QC* field names. Similar wording is not enough to establish identity. The site therefore states that the LI and release-field identifiers are not presumed to map one-to-one. Across all three waves, the listed variable strings remain candidates until these item-level checks have been completed.

The crosswalk is a metadata aid for a future phenotype catalogue. It contains no respondent observations, frequencies, or estimated associations. Repeated readings are preserved as separate source fields; derived summaries such as mean blood pressure, walking speed or grip-strength summaries require a prespecified rule before any model is fit. Structural skips are not treated as zero. Cross-wave pooling remains unapproved pending field-level comparability review.

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
