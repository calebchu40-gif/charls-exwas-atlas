# Wave 2 preloaded birth-date and calendar review

**Status:** source-schema and questionnaire-route review only. This note does not freeze an age algorithm or authorize association models.

## Review performed

- Compared the official Wave 2 questionnaire and Codebook with metadata-only labels from the protected Wave 1 and Wave 2 prepared Stata files. No respondent values, IDs, or row-level records were read for this review.
- The Wave 2 prepared schema contains `zba002_1`–`zba002_3` (“When Were You Born”), `ba001_w2_1` (confirmation of the preloaded birth date), `ba002_1`–`ba002_3` (date reported after a “No”), `ba003` (calendar for the answer to BA002), and conditional `ba004` age.
- The Wave 1 schema contains `ba002_1`–`ba002_3`, `ba003` (calendar type), and conditional `ba004` age.
- The Wave 2 questionnaire routes a returning respondent with a stored birth date to `ba001_w2_1`; a “Yes” skips BA002/BA003 to BA005. A “No” leads to a newly reported BA002 date and BA003 calendar question. If date of birth is unknown/refused, BA003 is skipped and BA004 is asked.
- Therefore `ba003` is specifically the calendar for the newly reported BA002 date. It is not a general calendar flag for `zba002_*` and must not be copied onto the preloaded date without an independently documented linkage rule. Wave 1 `ba003` is a candidate calendar source only after exact respondent linkage, date agreement, and source precedence have been documented.
- CHARLS's official `lunar2solar` repository provides a transformation tool, but its availability does not resolve which date/calendar pair applies to every Wave 2 record. Any use must preserve provenance and distinguish the preloaded date, respondent-corrected date, calendar indicator, and conversion status.

## Analysis implications

1. Keep `ba004` as a conditional fallback only when a date is unavailable; do not treat its structural blanks as ordinary missing ages.
2. For a confirmed preloaded date, determine the date's original calendar using an official Wave 1 linkage/source record or an explicit official release transformation. A valid Wave 1-to-Wave 2 ID mapping alone is insufficient unless the matched date and calendar are reconciled.
3. For a corrected BA002 date, use its own BA003 value; validate special missing codes and incomplete month/day values before conversion.
4. Derive age against a verified interview date using a prespecified convention (completed years vs. survey-year age), with invalid/future dates, partial dates, leap-month conversions, and failures flagged rather than silently imputed.
5. Reconcile the resulting age with the official cross-sectional sample flags and CHARLS target population. Do not impose a universal age-45 cutoff on the Wave 2 cross-section because the official target also includes spouses.
6. Keep all coverage and discrepancy summaries inside approved private storage; publish no small cells or respondent-level birth dates.

## Remaining gates

- Identify the authoritative Wave 2 interview date field and exact Wave 1-to-Wave 2 birth-date linkage/provenance rule.
- Confirm whether the released preloaded date is already solar-converted or retains the originally reported calendar.
- Inspect numeric special-missing conventions, birthday partial-date rules, and the official lunar conversion implementation/version.
- Freeze an age derivation specification and independently review it before using it in any analytic model.

## Primary sources

- CHARLS, *2013 Wave 2 Codebook*, Demographic Background: `zba002_*`, `ba001_w2_1`, `ba002_*`, `ba003`, `ba004`.
- CHARLS, *Wave 2 Main Questionnaire*, Demographic Background, BA001_W2_1 through BA005 routing.
- CHARLS, [official lunar-to-solar conversion repository](https://github.com/charls-data/lunar2solar).
- CHARLS, [official sample design description](https://charls.pku.edu.cn/en/About/Sample.htm).

