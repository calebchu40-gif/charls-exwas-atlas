# Wave 1 fasting-status source reconciliation

**Checked:** 2026-10-30
**Status:** Source-level field/code mapping resolved; analytic handling remains a draft for independent methods review. No participant outcome values or fasting-status values were read, and no association model was fitted.

## Source chain

1. The official CHARLS Wave 1 Blood data header labels `qc1_va003` as **“Fasting”** (integer storage). The header has no value-label set; no record values were inspected.
2. The official CHARLS 2011 *Blood Sample Fieldwork Plan*, Appendix 2, “静脉血样采集和处理记录表,” includes the field “是否空腹” and documents **1=是 (Yes), 2=否 (No)**. The plan's body says staff record fasting status before blood collection. The document is linked from the [official CHARLS 2011 documentation page](https://charls.pku.edu.cn/wd/a2011nqgjxdc.htm); direct document URL: [`jixiandiaochaxueyebiaobenxianchanggongzuofangan.doc`](https://charls.pku.edu.cn/wenjian/jixiandiaochaxueyebiaobenxianchanggongzuofangan.doc).
3. The official 2011 Blood Users' Guide states that overnight fasting was requested, non-fasting samples were still collected, and fasting status was recorded. The fieldwork form and the Stata field label jointly support mapping `qc1_va003` to the fasting-status item and coding 1=Yes, 2=No.

## Proposed analytic handling (not frozen)

- For glucose (`newglu`) and triglycerides (`newtg`), a plausible primary candidate is restriction to `qc1_va003 == 1` (fasting), with an all-observed-blood-sample sensitivity that includes fasting status as a binary measurement-condition covariate. The independent reviewer must choose/approve the estimand and assess whether the released blood weight supports the fasting-only subpopulation.
- Values other than 1 or 2 must remain unclassified until a source or metadata review resolves them; they must not be silently recoded.
- This source reconciliation does not decide finite numeric special codes in `newglu`/`newtg`, analyte validity, transformations, complete-case selection, weight adjustment for fasting participation, or the 45+ age-domain estimand.
- All 14 coefficients remain registered but are not approved for fitting. The candidate configuration may encode the source-supported `restrict` rule while remaining explicitly `draft_not_frozen`; model readiness remains closed until all source, design, outcome-rule, and independent-review gates pass.

## Reproducibility and privacy

The official fieldwork plan is held in `private/source_documents/` with owner-only permissions. The `qc1_va003` label was read from the metadata header of the user-authorized Wave 1 Blood release using metadata-only mode. No participant values, subgroup counts, or pair-level QA are included here. The corresponding private review packet binds the source file identity and draft-config hash.
