# Wave 1 published denominator comparison (2026-10-27)

## Finding

The available public CHARLS documents report more than one Wave 1 denominator, tied to different files/fields:

- The National Baseline User Guide describes 17,708 successfully interviewed individuals.
- The 2011 Blood Data User Guide identifies all 17,708 main respondents and spouses as the target for blood collection; its completed blood collection count is 11,847.
- The 2011 Codebook lists 17,705 observations for the Demographic Background `ID` field (and its household/community ID fields), while the `ind weight ad2` field is listed with 17,708 observations.

These are documented counts from different files/fields. They cannot be treated as one interchangeable prepared-table row-count requirement. The difference does not by itself establish an error in the source data or in a derived table. The exact record-level explanation must be established from the authorized release and official join keys.

## Change to the protected preflight

Updated `scripts/audit_2011_pilot_design_frame.py` to retain the published denominator references separately and show local row-count comparisons only as diagnostics. A numeric match to any one guide/Codebook count no longer sets `frame_denominator_reconciled=true`. The gate remains false until person, Weight, PSU and Blood source files are verified and reconciled by documented IDs and eligibility. Current status remains `formal_model_gate=not_passed`; no association model is run by this audit.

The local preflight reads only the selected respondent fields needed to produce aggregate domain/weight/PSU QA, and writes its output beneath the protected local root. No IDs, row-level values, or local pair estimates are copied into this audit or the public site.

## Required reconciliation after authorized files arrive

1. Authenticate the exact Wave 1 All Data, Weight, PSU and Blood releases using the official listing/version and protected local hashes.
2. Read only the documented IDs, eligibility flags, weights and PSU keys from the official files in protected storage.
3. Compare row counts and unique/nonmissing IDs by file; identify the exact join coverage between the person file and Weight/Blood/PSU releases.
4. Verify whether the respondents absent from the person `ID` field are outside the blood-target frame, have a documented partial/interview route, or represent an intake/build defect. Do not infer the reason from aggregate counts alone.
5. Reconcile Blood User Guide target, response and `bloodweight` coverage separately, then review the official survey variance-design method before reopening the pilot model gate.

## Official references

- [CHARLS 2011 Wave 1 data/documentation page](https://charls.charlsdata.com/pages/Data/2011-charls-wave1/en.html) (lists the Codebook, All Data, PSU, Weight and Blood files separately)
- [CHARLS National Baseline User Guide](https://charls.pku.edu.cn/en/data/User2011.pdf)
- [CHARLS 2011 Blood Data User Guide](https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2011-charls-wave1/application/blood_user_guide_en_20140429.pdf)
- [CHARLS 2011 baseline page](https://charls.pku.edu.cn/en/Data/a2011_CHARLS_Wave1__Baseline_.htm) (Codebook download and checksum listing)
