# CHARLS lunar-to-solar utility: pinned reference and age-pipeline decision

Date checked: 2026-10-27

## Source identity

- CHARLS-maintained repository: [charls-data/lunar2solar](https://github.com/charls-data/lunar2solar)
- Retrieved branch: `main`; commit: `2284ccffdd74f057c234a446585ec32034b2d50d`
- Repository license: MIT (copyright China Health and Retirement Longitudinal Study, 2023). Preserve the license notice if any source files are redistributed.
- The repository README instructs Stata users to install all three files from `src` into Stata's `PERSONAL` directory. The help file describes a string date with eight digits, range 19000101–20401128, and an explicit `leap` option for leap lunar months.
- SHA-256 at the pinned commit:

| File | SHA-256 |
|---|---|
| `src/lunar2solar.ado` | `14A3D7E28B3143E7F7276FECBD8F226E79EE77F395CCEF1B0BCD35A453B932A1` |
| `src/lunar2solar.mmat` | `EBEC9FE5109295A347894EC6173AA3750ADBB270329F0BA357D2778636D20AA2` |
| `src/lunar2solar.sthlp` | `4719F19274784EE217F49270B01976A799F88269996761516808FB002C431320` |

The source was cloned to a temporary local reference directory to inspect its README, help, implementation, and license. It was not copied into the project repository, installed in Stata, or run against CHARLS values. The current Windows environment has no `stata`, `stata-se`, or `stata-mp` executable on PATH, so no execution test is claimed.

## Age derivation implication

The Harmonized CHARLS Version D age description is the documented cross-wave reference for Waves 1–4; it uses interview year/month and latest reported birth year/month, assigns June when birth month is missing, permits a self-reported-age fallback for missing birth year in Waves 1–2 only, and requires lunar-to-solar conversion when the source date is lunar. The pinned CHARLS utility establishes a suitable official conversion implementation, but does not by itself determine which release-specific birth-date route or leap-month flag applies to each respondent.

Before an analysis age can be created, the authorized wave release must provide the relevant raw birth date, calendar type, interview year/month, respondent route/eligibility, and any prior-wave/date-confirmation fields. The pipeline must preserve source and special-missing statuses, convert only records explicitly identified as lunar, pass the leap-month indicator when applicable, and retain Gregorian dates as such. It must not infer missing dates or silently substitute a third-party harmonized age. Synthetic tests should cover valid/invalid dates, missing birth month/year, leap lunar month, conversion failure, and Wave 1/2 versus Wave 3/4 fallback rules before protected participant-level derivation.

The resulting age values and DOB fields must remain in the authorized protected workspace. Only disclosure-reviewed aggregate QA may leave that workspace. The provisional Harmonized CHARLS D age candidate remains a comparison reference, not the production age input.

## Execution decision

No age derivation or association model was run in this work item. Continue source-free preparation until the authenticated official inputs and Stata-compatible execution environment are available. On intake, verify file/module identity first, then test the pinned utility on synthetic dates, reconstruct age under the release-specific routes, and compare only aggregate coverage/disagreement summaries against the Harmonized reference.

