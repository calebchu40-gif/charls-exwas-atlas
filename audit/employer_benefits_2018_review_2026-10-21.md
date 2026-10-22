# 2018 employer benefit fields review (2026-10-21)

## Included as exposure candidates

- `FG001_s1`–`FG001_s11`: separate checkbox slots for current-employer fringe benefits (free lunch/breakfast/dinner, meal and transport allowances, free housing, housing allowance, company car, shuttle, other allowance, and None). The official questionnaire says select all that apply. The 2018 Codebook reports slot values `0=No` and `9=<selected option>`; published frequencies are deliberately excluded from the value-label layer. Each item remains a separate source field under one checklist concept. A skipped field is not interpreted as “not provided”; the `None` option is itself a selected checkbox and needs consistency checks against other selected options.
- `FD034_W4`: employer purchase of supplementary commercial medical insurance. The question describes outpatient-use supplementary coverage distinct from accident insurance. The Codebook labels are Yes/No. It remains a 2018-only employer/job exposure candidate, not individual coverage or a health outcome.
- `FG002_1_`–`FG002_10_`: monthly monetary values corresponding to selected FG001 fringe benefits. These remain ten slot-specific continuous E candidates (yuan/month), conditional on the corresponding selected benefit and current-employer route; do not merge these values with wages or household income.
- `FD030` and `FD031`: two 2018 P candidates. FD030 counts past-year days missed at the current job due to health problems and explicitly directs 0 when no days were missed; FD031 is fully paid days within FD030 and is asked only when FD030 is nonzero. Keep the current-job eligibility universe, paired inequality FD031<=FD030, and questionnaire range 0–366. Structural skips are not zero and these are work-function measures, not diagnoses.

Evidence: `sources_official/CHARLS_2018_Questionnaire_extracted.txt` (FG001 options and FD034 wording) and `sources_official/CHARLS_2018_Codebook_extracted.txt` (field labels and response coding). Metadata-only mapping; no individual records or frequency counts were read into this review.

## Deliberately not harmonized: workplace injury payout amount

`2018 FD033_W3` asks the maximum amount an employer's workplace-injury insurance would pay after a severe accident and has 445 observed values in the released Codebook summary, with a maximum of `99,999,999`. The comparable-looking `2015 FD033_W3` has the title “Money Pay When Accident Occurs”; same code alone does not establish same wording, universe, or scale. The 2018 questionnaire routes it after `FD032_W3=Yes`; it is an open amount and the maximum may be an extreme value or special code, which cannot be resolved from the available metadata. Therefore it is not mapped pending authorized-release data dictionary clarification and distribution checks. Do not use `99,999,999` as an amount or assume it is a sentinel without official confirmation.

No participant-level analysis, association estimates, or sample-size claims are produced by this mapping review.


## Related work-exposure series reviewed in this batch

- `FD010` (2013/2015/2018) is mapped as current-employer ownership type, with the official ten-category nominal menu. It is not merged with employer organization type or the separate prior-business ownership field.
- `FJ001`–`FJ003` (2013/2015) are mapped as wave-series candidates for current side-job count, weekly hours, and monthly income, excluding the main job per questionnaire wording. They remain separate from 2011 and 2018 concepts because those waves have different eligibility routes/scope. Questionnaire ranges/units are preserved; structural missingness is not zero.
Evidence: corresponding 2013/2015/2018 official questionnaires and codebooks. No respondent-level records or frequency counts were read.

## Additional employment history and business-size fields

- `FD011_1/_2` (2013/2015/2018) are mapped as current-employer start year/month components. They are not converted to tenure; month 0 may denote not remembered and must be checked before any derivation.
- `FL012` (2011/2013/2015) is retained as its three-category self-employment/family-business status (with employees, without employees, unpaid family-business worker), not collapsed to a binary employee indicator. Full questionnaire categories are used without frequencies.
- `2018 FL012_W4` is mapped separately as number of employees in the last self-employed business, range 0–9999; it is not treated as current-employer headcount.
- `FC018` (2011/2013/2015) is the planned age to stop work, not observed retirement. The questionnaire says 0 means plan to work until physically able; retain that value meaning.

These are candidate exposures only; routes and skips must be preserved, and no derivation or association model is implied.

## Additional work-status and location measures

- `FC014` (2011/2013/2015) identifies at least one hour of wage, self-employed, or unpaid family-business work in the preceding week, excluding agriculture. It is a separate weekly status from work in the past month/year.
- `FD009` (2013/2015) asks formal employee status of an establishment. It remains separate from the 2011 same-code “regular worker” item.
- `FB004` (2011/2013) records first workplace location. Because its category anchors differ by wave, the website retains separate official menus and presents it as a coarse retrospective location, not a geocoded environmental exposure.

Evidence: official 2011/2013/2015 questionnaires and corresponding wave Codebooks. Categories are shown without frequencies.
