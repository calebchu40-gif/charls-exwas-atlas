# Multwave respondent-spine review from official release headers

**Date:** 2026-10-30  
**Scope:** Metadata-only review of the CHARLS 2013, 2018, and 2020 All Data archives already checksum-verified against official release pages. The protected header report is `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\multwave_archive_headers_20261030.json`.

## Findings

The official Wave 2 (2013) All Data package contains `Weights.dta` with `crosssection` and `longitudinal` flags, plus a separate `PSU.dta`. The official Wave 4 (2018) and Wave 5 (2020) packages each contain `Sample_Infor.dta` with `crosssection`, interview year/month, and a separate `Weights.dta`. Their weights modules do not contain those sample flags. The released value labels define `crosssection` as `0 No` / `1 Yes` and `died` as `0 Alive` / `1 Died`. No Wave 4/5 lab biomarker module was found in these archive headers.

The official Wave 4 guide states that `crosssection` in Sample_Info identifies the cross-sectional sample; its cross-sectional individual weights are constructed from sampling probabilities, account for death and divorce, and apply to main respondents and spouses, including proxy and partial interviews. Other interviewed non-sample people do not receive weights. The Wave 5 guide likewise states that the `crosssection` flag identifies the cross-sectional sample; its weights apply to the representative sample, including proxy and partial interviews, while other interviewed non-sample people receive no weights. These statements are in the official [2018 User's Guide](https://charls.pku.edu.cn/en/data/User2018.pdf), section 6, and [2020 User Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_User_Guide_English.pdf), section 5. Both guides list Sample_Info and Weights as separate released datasets.

The builder previously chose `Sample_Infor` as the person spine for 2015, and otherwise defaulted to `Demographic_Background` except for the optional Wave 1 weight-spine candidate. That would omit the official sample-frame flags from Wave 4/5 prepared tables. The implementation now selects the full `Sample_Infor` table as the Wave 4/5 spine, preserving every source frame row and the `crosssection`/`died` labels. It does not filter rows at build time; model-specific inclusion must still apply the official flag, chosen weight, observed module eligibility, and estimand. Positive weight alone is not used to define the sample.

## Protected preparation and frame/weight audit

After rechecking each archive SHA-1 against its protected intake manifest, built Wave 4 and Wave 5 respondent preparation tables under `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\derived_wave_tables_2018_2020_sample_info_spine_20261030`. The builder records input/output hashes and uses the full Sample_Infor table as the left-hand spine. A protected aggregate check verified unique respondent keys, preserved crosssection and died flags, and one-to-one joins for person-level weights. The `crosssection` codes were complete and within the official 0/1 labels; positive `INDV_weight_ad2` values aligned with cross-sectional membership in both directions. Detailed counts and hashes are stored only in `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\qa_outputs\\wave4_wave5_frame_weight_reconciliation_20261030.json` and per-wave merge QA files.

This closes a **preparation-structure** issue only. It does not establish that a particular exposure/outcome pair is observed for the representative sample, settle the analysis-specific weight choice, approve an age domain, or supply the complete variance design. The prepared tables and all detailed QA remain in protected local storage; no participant data or counts were copied to the repository or website.

For Wave 2, the released weight flags are available in `Weights.dta`; any respondent table should preserve those flags and assess them against the official frame rather than deduplicate or filter based on positive weight as a substitute for eligibility. Wave 2 `PSU.dta` exposes community ID and geographic descriptors only; it does not by itself resolve the full original variance design.

## Safe next preparation sequence

1. Review pair-specific module availability, valid values, interview routes and measurement eligibility on the prepared Wave 4/5 tables, then define analytic denominators without treating frame rows as observed measurements.
2. Resolve wave-specific age/domain and the intended population estimand before choosing between corrected and uncorrected official individual weights.
3. Do not treat preparation success as model eligibility. Continue to block association fitting until PSU/variance, frozen model family, and independent methods review are also resolved.

This is a source/frame implementation review, not an approved analysis frame, sample-size estimate, or model result. The guide statements and metadata labels are release documentation; no respondent values were read in the metadata review. Prepared microdata and detailed frame/weight diagnostics remain in protected local storage.
