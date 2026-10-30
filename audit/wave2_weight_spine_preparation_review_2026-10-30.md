# Wave 2 sample-frame and weight-spine preparation review

**Date:** 2026-10-30  
**Source:** Checksum-verified official 2013 All Data package and official Wave 2 Release Note. The archive and metadata-only provenance manifest are under `%LOCALAPPDATA%\\CHARLS_ExWAS_Atlas\\incoming_2013_all_data`.

## Official release rule

The official [Wave 2 Release Note](https://charls.pku.edu.cn/wenjian/fabushuoming.pdf) describes separate cross-sectional and longitudinal weights and says `crosssection` and `longitudinal` identify different sample memberships. It specifically warns that the cross-sectional sample is not necessarily the longitudinal sample, because Wave 2 includes tracked baseline respondents, nonresponse samples, and refreshment samples, and the baseline interview frame had errors. The two indicators must therefore be retained separately; one cannot infer either analytic population from the other or from a positive weight alone.

The Wave 2 `Weights.dta` header contains both membership flags, individual/household weights, and `Biomarker_weight`; the official All Data archive also contains a separate PSU module and respondent modules. The official release page identifies this archive as the Wave 2 package and publishes the SHA-1 used by the protected intake manifest: [2013 Wave 2 data page](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html).

## Preparation decision

For a frame-preserving respondent table, use every nonmissing person ID in the official Weights module as a **candidate frame spine**, without filtering on either membership flag or any weight. Left-join respondent modules by ID and preserve absent module rows as missing. This retains the official cross-sectional/longitudinal distinction for later estimand-specific decisions and avoids defaulting to a Demographic_Background-only denominator. Household weights remain separate from person weights; Biomarker_weight must not be conflated with the general cross-sectional individual weights.

The builder now offers the explicit opt-in `--wave2-weight-spine-candidate` for this unfiltered Wave 2 preparation. The word *candidate* is intentional: it creates a reconciliation surface, not an approved analytic population. The first build exposed a bookkeeping issue: string keys normalized to missing were excluded from the spine, but the source QA field counted only native missing values. The QA code now counts normalized missing keys consistently, and the table is being rebuilt from the corrected clean revision before its manifest is used. The protected audit compares frame IDs and flags, checks module linkage without emitting IDs, and separately assesses the correct weight for each measurement target.

## Gates still open

This does not choose the wave-specific estimand or prove any pair is measured for the cross-sectional sample. The 2013 PSU file exposes community identifiers and geographic descriptors but does not resolve the full multistage design/variance specification. Age-domain rules, routes, field-specific measurement eligibility, weights for each outcome class, final PSU/variance method, frozen analysis family, and independent review remain prior to any model fit.

No respondent values or IDs were read for this source/document review; no association was fitted. Prepared files and exact audit diagnostics must remain in protected local storage.
