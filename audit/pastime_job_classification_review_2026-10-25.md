# CHARLS 2011 pastime-work occupation and industry coding review

Updated 2026-10-25. This review uses the official 2011 household questionnaire, 2011 Codebook, and CHARLS Wave 4 User Guide. It does not inspect respondent-level records or reproduce Codebook frequency tables.

## Finding

The 2011 household questionnaire asks at FM055 for a description of the specific paid pastime job and instructs the interviewer to record the work content. The questionnaire item is open text, not a numeric response menu. The 2011 Codebook separately lists `fm055_gb` (GB occupation), `fm055_isco` (ISCO occupation), and `fm055_indc` (industry) child fields. These are three different coding variables and must remain separate from one another and from the original text.

CHARLS Wave 4 User Guide describes a supervised, double-coding workflow for occupation and industry items in specified work-module questions. It says the Wave 4 procedures continued those used in Wave 3, that occupations used a six-digit Chinese GB classification with a few added categories, and that industries used two-digit codes. The listed questions do not include FM055. Therefore, this guide does not establish the edition or lookup for the 2011 FM055 child fields, and the Wave 3/4 procedure cannot be assumed to apply to them. The official materials reviewed here do not provide a verified FM055 code lookup or crosswalk that would justify mapping the codes to occupational exposures.

## Catalog and website treatment

- Retain the three coded child fields as separate metadata candidates so users can discover their existence.
- Exclude FM055 free text from the public index and do not expose code frequencies.
- Mark all three coded candidates `DO NOT ANALYZE` until the 2011 coding edition and official category lookup are verified.
- Do not treat numeric codes as a quantitative scale, convert GB to ISCO, or create an occupational exposure score from these codes.
- Before any grouped category counts are published, review small-cell disclosure risk under the relevant CHARLS release terms.

## Traceability

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt` — FM054–FM056 route and open-text FM055 instruction.
- `sources_official/CHARLS_2011_Codebook_extracted.txt` — FM055 coded child-field identities; no category labels are inferred from frequency rows.
- `sources_official/CHARLS_2018_Users_Guide_extracted.txt` — Section 5, coding workflow and scope of the Wave 3/4 occupation and industry coding procedures.
- `scripts/build_retirement_history_exposure_crosswalk.py` — candidate status/note and synchronized browser metadata.

