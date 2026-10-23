# Cross-wave internet and digital behavior metadata review

Updated 2026-10-24. This review traces the existing CHARLS social-activity crosswalk entries for internet access and related digital behavior across 2011, 2013, 2015 and 2018. It is a source-metadata review; it does not use respondent-level data or report prevalence.

## Source interpretation

The 2011, 2013, 2015 and 2018 questionnaires include internet use as option 10 in DA056, a checklist of activities during the last month. This is not the same question as the dedicated “used the Internet in the past month” screen introduced in the 2020 DA040 module. The catalogue therefore retains the legacy items as `internet_use_social_activity` and preserves their distinct source wording.

The 2015 and 2018 questionnaires route DA056_W3 device questions after DA056 option 10. The 2018 questionnaire additionally routes DA056_W4_1 internet activities, DA056_W4_2 mobile payment and DA056_W4_3 WeChat use to the internet-use response; DA056_W4_4 asks about WeChat Moments only after WeChat use. These are separate concepts and are not merged into a single digital-use score.

The 2018 Codebook supports field-level category labels, including `0=No` for the multi-response device/activity options and `1=Yes; 2=No` for the binary questions. The official Codebooks for 2011, 2013 and 2015 identify the internet option and device categories, but the available summaries do not establish how unselected options are stored in respondent records. Their value-label fields are deliberately blank; the catalogue does not infer “No” from absence or treat option indices as respondent responses. Verify these details against an authorized release before analysis.

DA057 social-activity frequency is a different construct and remains outside this digital-use mapping. “Other” free text is not standardized. Codebook descriptive counts and frequencies are excluded from the public catalogue.

## Catalogue changes

The audited source crosswalk assigns the internet-use checklist, five device options, six internet activity options, mobile payment, WeChat and WeChat Moments to distinct concepts under the `behavior` / `internet and digital technology use` category. Existing mappings are reclassified in place, one source field per wave is preserved, and concept/value-label provenance follows the source crosswalk into the main candidate directory. These rows remain candidate exposures, not pre-approved analysis variables.

Official evidence was read from `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt`, `CHARLS_2011_Codebook_extracted.txt`, and the corresponding 2013, 2015 and 2018 extracted questionnaires and Codebooks. The 2018 routing and labels are documented around the DA056 section; older-wave coding uncertainty is stated explicitly above and in each field record.

## Checks

Regression tests verify concept separation, wave coverage, 2018 routes and labels, omission of unverified 2015 labels, and the absence of Codebook frequencies. The generated catalogue is also checked for duplicate wave/code/role records and for agreement between its role totals and the downloadable site data. Formal association models remain 0; this review adds metadata only.
