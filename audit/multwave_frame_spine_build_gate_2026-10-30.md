# Multwave respondent-spine review from official release headers

**Date:** 2026-10-30  
**Scope:** Metadata-only review of the CHARLS 2013, 2018, and 2020 All Data archives already checksum-verified against official release pages. The protected header report is `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\multwave_archive_headers_20261030.json`.

## Findings

The official Wave 2 (2013) All Data package contains `Weights.dta` with `crosssection` and `longitudinal` flags, plus a separate `PSU.dta`. The official Wave 4 (2018) and Wave 5 (2020) packages each contain `Sample_Infor.dta` with `crosssection`, interview year/month, and a separate `Weights.dta`. Their weights modules do not contain those sample flags. No Wave 4/5 lab biomarker module was found in these archive headers.

The current preparation code chooses `Sample_Infor` as the person spine for 2015, and otherwise defaults to `Demographic_Background` except for the optional Wave 1 weight-spine candidate. Therefore it does not currently use the released `Sample_Infor` frame for 2018 or 2020. The header review establishes a concrete implementation question: before building those wave tables, confirm from the corresponding official guides which Sample_Infor rows define the released cross-sectional respondent frame, how deceased/nonresponse rows are represented, and how the separate weights table maps to that frame. Do not infer eligibility from row counts or from successful ID linkage alone.

For Wave 2, the released weight flags are available in `Weights.dta`; any respondent table should preserve those flags and assess them against the official frame rather than deduplicate or filter based on positive weight as a substitute for eligibility. Wave 2 `PSU.dta` exposes community ID and geographic descriptors only; it does not by itself resolve the full original variance design.

## Safe next preparation sequence

1. Review the official 2018 and 2020 guides/release notes for Sample_Infor and cross-sectional eligibility semantics; record the exact source passages.
2. Specify a wave-specific person-spine rule and weight join before any full table build. Preserve frame-only records and missing module values; do not silently inner-join.
3. Produce protected aggregate frame reconciliation (IDs and flags only) against official guide denominators. Keep exact diagnostics private.
4. Continue to block association fitting until age/domain, module-specific measurement eligibility, weight applicability, PSU/variance, frozen model family, and independent methods review are all resolved.

This is a header/source-structure review, not an approved analysis frame, a sample-size estimate, or a model result. No respondent values were read in this review.
