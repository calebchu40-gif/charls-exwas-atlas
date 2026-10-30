# Wave 3 lunar birth-date conversion: route limits and conservative interval plan (2026-10-30)

## Status and scope

This note resolves what the CHARLS-maintained conversion command can and cannot tell us. It is documentation-only: no respondent date was read or converted, no age was derived, and no model was fitted. Age, survey-design and independent-review gates remain closed.

## Official implementation contract

The pinned CHARLS-maintained `lunar2solar` Stata ado accepts an 8-digit string date (`YYYYMMDD`) and documents support from `19000101` through `20401128`. Its default uses the ordinary lunar-month matrix. The `leap` option switches the entire invocation to a separate leap-month matrix. The program builds the matrices using 49,949 ordinary-date rows and 1,521 leap-date rows; its help points to `lidaobing/python-lunardate` as the conversion basis.

The Wave 3 questionnaire route reviewed for this project records whether the reported birth date is solar or lunar (`ba003`), but the reviewed fields do not provide a separate per-person leap-month indicator. Therefore an exact lunar-to-solar date cannot be selected for every lunar DOB just by calling the official ado once with its default. The global `leap` option must not be treated as a respondent-level fact.

## Safe candidate-set approach for later review

For a valid lunar DOB, an implementation can retain the ordinary-table mapping and, only when that same lunar key is represented in the official leap table, the alternate leap-table mapping as separate possible solar DOBs. It must not choose between them without an official per-person indicator. For a valid solar DOB, retain the reported solar date without lunar conversion. Keep source route, calendar code, raw component validity, conversion-table version/hash, and the candidate-set reason in the private derivation record.

Because CHARLS interview timing gives year and month but not interview day, calculate the completed-age minimum and maximum over every admissible birth-date candidate and every day in the recorded interview month. Unknown or partial DOB components require a separately specified broad candidate set; invalid and unrouted records remain unclassified. A threshold domain such as 45+ is assignable only when the entire resulting age interval lies on one side of the threshold. Otherwise retain an unresolved domain. This avoids false precision and does not infer eligibility from a midpoint.

This is a candidate method, not an approved CHARLS age specification. The official ordinary and leap lookup matrices have now been parsed from the hash-pinned `.mmat`, and every row matched pinned Python 0.1.4 with no mapping differences. This closes the converter-table parity subgate, including all valid month-boundary and leap-month keys. Remaining gates include invalid/partial respondent date handling, interview-month interval implementation, exact Wave 3 response routing, source checksum/version binding for any derived age table, and independent age-method review. Preserve the official utility's documented date domain, its merge behavior, and exact response coding. No participant-level age estimate or age-domain selection is authorized by this source-only validation.

## Current decision

Do not use a single default conversion for all lunar dates, do not infer a leap indicator, and do not replace missing month/day with January/first-of-month. Keep existing provisional age intervals as exploratory bounds only; this note does not expand readiness. The blood-target primary frame remains separate from the optional age-45+ secondary domain, but age adjustment and any age-specific claim remain unresolved.

## Sources inspected

- `references/charls_lunar2solar/src/lunar2solar.ado` and `.sthlp` (pinned CHARLS-maintained utility; its documented `leap` behavior and input range).
- `audit/wave3_age_covariate_route_review_2026-10-30.md` (2015 Codebook/questionnaire BA002/BA003/BA004_W3 route).
- `scripts/verify_official_lunar_table_parity.py` and `audit/wave1_age_interval_candidate_review_2026-10-29.md` (direct source-only comparison against the official matrices; no participant dates used).
