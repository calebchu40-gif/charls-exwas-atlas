# Multwave respondent-spine review from official release headers

**Date:** 2026-10-30  
**Scope:** Metadata-only review of the CHARLS 2013, 2018, and 2020 All Data archives already checksum-verified against official release pages. The protected header report is `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\multwave_archive_headers_20261030.json`.

## Findings

The official Wave 2 (2013) All Data package contains `Weights.dta` with `crosssection` and `longitudinal` flags, plus a separate `PSU.dta`. The official Wave 4 (2018) and Wave 5 (2020) packages each contain `Sample_Infor.dta` with `crosssection`, interview year/month, and a separate `Weights.dta`. Their weights modules do not contain those sample flags. The released value labels define `crosssection` as `0 No` / `1 Yes` and `died` as `0 Alive` / `1 Died`. No Wave 4/5 lab biomarker module was found in these archive headers.

The official Wave 4 guide states that `crosssection` in Sample_Info identifies the cross-sectional sample; its cross-sectional individual weights are constructed from sampling probabilities, account for death and divorce, and apply to main respondents and spouses, including proxy and partial interviews. Other interviewed non-sample people do not receive weights. The Wave 5 guide likewise states that the `crosssection` flag identifies the cross-sectional sample; its weights apply to the representative sample, including proxy and partial interviews, while other interviewed non-sample people receive no weights. These statements are in the official [2018 User's Guide](https://charls.pku.edu.cn/en/data/User2018.pdf), section 6, and [2020 User Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_User_Guide_English.pdf), section 5. Both guides list Sample_Info and Weights as separate released datasets.

The builder previously chose `Sample_Infor` as the person spine for 2015, and otherwise defaulted to `Demographic_Background` except for the optional Wave 1 weight-spine candidate. That would omit the official sample-frame flags from Wave 4/5 prepared tables. The implementation now selects the full `Sample_Infor` table as the Wave 4/5 spine, preserving every source frame row and the `crosssection`/`died` labels. It does not filter rows at build time; model-specific inclusion must still apply the official flag, chosen weight, observed module eligibility, and estimand. Positive weight alone is not used to define the sample.

For Wave 2, the released weight flags are available in `Weights.dta`; any respondent table should preserve those flags and assess them against the official frame rather than deduplicate or filter based on positive weight as a substitute for eligibility. Wave 2 `PSU.dta` exposes community ID and geographic descriptors only; it does not by itself resolve the full original variance design.

## Safe next preparation sequence

1. Build Wave 4/5 preparation tables from the checksum-verified official All Data archives using the Sample_Infor spine; preserve frame-only records and missing module values rather than silently inner-joining.
2. Produce protected aggregate frame/weight reconciliation (IDs, flags, and weight fields only) against official guide definitions. Keep exact diagnostics private.
3. Do not treat preparation success as model eligibility. Continue to block association fitting until age/domain, module-specific measurement eligibility, weight applicability, PSU/variance, frozen model family, and independent methods review are all resolved.

This is a source/frame implementation review, not an approved analysis frame, sample-size estimate, or model result. The guide statements and metadata labels are release documentation; no respondent values were read in the review.
