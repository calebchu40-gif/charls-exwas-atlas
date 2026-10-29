# Wave 1 age-interval candidate: source, limits, and review status

**Status:** provisional protected preparation only. Not a frozen model covariate, survey-design approval, or permission to run association models.

## Source lineage and synthetic conversion evidence

CHARLS's official [`lunar2solar` help](https://github.com/charls-data/lunar2solar/blob/main/src/lunar2solar.sthlp) says its lunar-to-solar conversion is based on [`lidaobing/python-lunardate`](https://github.com/lidaobing/python-lunardate). The official ado creates ordinary and leap lookup tables with 49,949 and 1,521 rows, respectively. A synthetic-only exhaustive audit compared pinned package source versions 0.1.4 and 0.1.5 over the official documented numeric range. They enumerated the same 49,949 ordinary and 1,521 leap dates, with identical valid-date coverage and no output differences. This agrees with the official lookup dimensions, but is not a direct comparison of individual mappings to `lunar2solar.mmat`; both Python versions share lineage.

The official command selects the leap-month table only when the `leap` option is supplied; otherwise it uses the ordinary table. The official CHARLS Wave 1 birth-date questionnaire asks whether the reported date is solar or lunar but provides no separate leap-month response. The candidate therefore does not invent a leap flag: for lunar year/months that could refer to an unmarked leap month, it retains only a broad birth-year age interval. The Stata utility's stated range is 1900-01-01 through 2040-11-28.

## Candidate construction

The protected derivation reads only the source-bound Wave 1 birth year/month/day, calendar type, conditional self-reported age, and official Weight interview year/month. Before reading values, it checks the reviewed source identities and hashes, the current prepared respondent-frame hash, the official Weight file hash, and the hash of the protected age-input table.

- Complete solar dates are validated with Gregorian calendar rules.
- Complete lunar dates use the pinned 0.1.4 source only where the month is not leap-ambiguous; candidate age is still an interval because CHARLS provides interview month but not interview day.
- Possible leap-month dates and incomplete/unknown calendar dates use conservative completed-age bounds from birth year and interview year; a known solar birth month can narrow those bounds when it differs from interview month.
- The conditional self-reported age is retained only as a source candidate when a valid birth year is unavailable.
- Invalid or out-of-range dates remain unresolved. Candidate age bounds and 45+ status are not used to filter the respondent frame.

The row-level candidate table and detailed route counts are stored only in owner-controlled `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\age_inputs_2011\\` and `qa_outputs\\`. They are not in Git, OneDrive, the server, or the public site. The public repository contains the derivation code and method description, not the private output.

## What remains unresolved

The interval is a measurement-error representation, not a replacement for the exact interview date or an adjudicated age model. A methods reviewer must decide whether the intervals support an age adjustment (and what sensitivity analyses to use), whether and how to define any 45+ domain, and whether conditional self-reported ages are comparable. The main blood-sample estimand includes eligible main respondents and spouses; the candidate 45+ classification does not determine sample eligibility. The final Wave 1 PSU/variance design is separately unresolved. No association model was fitted and no result was prepared for release.

## Reproduction and implementation

- Synthetic release-domain comparison: [`scripts/audit_lunardate_release_domain.py`](../scripts/audit_lunardate_release_domain.py).
- Protected official age-input preparation: [`scripts/prepare_wave1_official_age_inputs.py`](../scripts/prepare_wave1_official_age_inputs.py).
- Protected provisional age-interval derivation: [`scripts/derive_wave1_age_intervals.py`](../scripts/derive_wave1_age_intervals.py).
- Earlier source and calendar-route review: [`charls_official_lunar_conversion_implementation_review_2026-10-29.md`](charls_official_lunar_conversion_implementation_review_2026-10-29.md).
