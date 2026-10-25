# CHARLS 2011 pastime-work occupation and industry coding review

Updated 2026-10-25. This review uses the official 2011 household questionnaire, 2011 Codebook, 2011 National Baseline User Guide, and the Wave 4 User Guide. It does not inspect respondent-level records or reproduce Codebook frequency tables.

## Finding

The 2011 household questionnaire asks FM055 only after FM054=Yes, for a description of the respondent's current paid pastime job, and instructs the interviewer to record the work content. The item is open text, not a numeric response menu. The 2011 Codebook separately lists `fm055_gb` (GB occupation), `fm055_isco` (ISCO occupation), and `fm055_indc` (industry) child fields. These are three different coding variables and must remain separate from one another and from the original text.

The 2011 National Baseline User Guide (section 5) directly describes labor-module coding: three coders independently code open-text work descriptions, a manager resolves mismatches, the guide names a standard Chinese GB six-digit occupation table with added categories, and industry is coded at two digits. It also mentions a correspondence between Chinese occupation codes and SITC and says both codes are reported in public-use data. This is stronger survey-era context than the later Wave 4 guide, but it does not name a dated GB edition, supply the lookup, or explicitly map the three FM055 child fields to the described codes. In particular, the Codebook's `fm055_isco` field is not explained by the guide's discussion of Chinese GB codes and SITC. The 2011 guide therefore narrows the documentation gap but does not resolve exact field-to-classification identity or provide a verified category lookup. The Wave 4 User Guide separately documents a later coding workflow for listed questions that exclude FM055; it cannot substitute for the 2011 field-specific mapping.

## Catalog and website treatment

- Retain the three coded child fields as separate metadata candidates so users can discover their existence.
- Exclude FM055 free text from the public index and do not expose code frequencies.
- Mark all three coded candidates `DO NOT ANALYZE` until the 2011 coding edition and official category lookup are verified.
- Do not treat numeric codes as a quantitative scale, convert GB to ISCO, or create an occupational exposure score from these codes.
- Before any grouped category counts are published, review small-cell disclosure risk under the relevant CHARLS release terms.

## Traceability

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` — FM054–FM056 route and open-text FM055 instruction.
- `sources_official/CHARLS_2011_Codebook_extracted.txt` — FM055 coded child-field identities; no category labels are inferred from frequency rows.
- `sources_official/CHARLS_2011_National_Baseline_Users_Guide_extracted.txt` — section 5, labor-module coding workflow and the GB/industry coding granularity; official source: [2011 National Baseline User Guide](https://charls.pku.edu.cn/en/data/User2011.pdf).
- `sources_official/CHARLS_2018_Users_Guide_extracted.txt` — Section 5, coding workflow and scope of the Wave 3/4 occupation and industry coding procedures.
- `scripts/build_retirement_history_exposure_crosswalk.py` — candidate status/note and synchronized browser metadata.

