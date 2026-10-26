# Wave 1 household exposure field review for post-pilot scale-up (2026-10-27)

## Purpose and evidence boundary

This is a source-document review to prepare the next household-environment block after a valid pilot. It uses the public 2011 baseline household questionnaire and the locally archived 2011 CHARLS codebook text listed in `sources_official/SOURCES.md`. It does not inspect respondent microdata, establish the exact codebook/data-release match, confirm field names in the authorized Stata files, or approve any model run.

The questionnaire DOC is identified in `SOURCES.md` as the August 2011 baseline questionnaire linked from CHARLS. Its adjacent extracted text is a search aid. The local codebook PDF is not present, and the available extracted text must be checked against the authenticated release/codebook version before data coding. Codebook frequency totals below are documentation context only; they are not expected analytic denominators and must not be used as observed-data validation targets.

## Questionnaire evidence and model consequences

| Item | Questionnaire meaning | Response structure in available official documentation | Eligibility/routing interpretation | Planned use |
|---|---|---|---|---|
| `i016` | Whether the residence has electricity | Yes/No; codebook labels Yes=1, No=2 | Household residence item; person-level linkage and eligible denominator still require release review | One binary coefficient in K=150, reference fixed in the frozen plan |
| `i017` | Whether the residence has running water | Yes/No; codebook labels Yes=1, No=2 | Same denominator/linkage review; existing K=105 runner already treats 1 vs 2 as the water contrast | One binary coefficient in K=150 |
| `i019` | Whether the residence has a coal-gas or natural-gas supply | Yes/No; codebook labels Yes=1, No=2 | Wording is a household supply/access proxy; do not relabel it as individual fuel use or exposure dose | One binary coefficient in K=150 |
| `i020` | Whether the residence has heating | Yes/No; questionnaire wording includes heating facilities and air-conditioning heating | The questionnaire routes Yes directly to `i022`; No continues to `i021` | One binary coefficient in K=150, subject to confirmed code and valid denominator |
| `i021` | Main heating energy source | Solar, coal, natural gas, LPG, electric, crop residue/wood, other; codebook labels 1–7 | Asked only after `i020=No` in the baseline questionnaire. It is a routed subdomain, not an all-household exposure | Six contrasts vs electric within the eligible routed domain; K=90 with 15 blood outcomes |
| `i022` | Main source of cooking fuel | Coal, natural gas, marsh gas, LPG, electric, crop residue/wood, other; codebook labels 1–7 | Main household cooking-fuel category. Questionnaire routing and valid response handling must be confirmed from the released data | Six contrasts vs electric in K=150; K=105 pilot already covers it |

The predeclared scale-up arithmetic remains: K=150 = 10 exposure coefficients × 15 blood phenotypes (water 1 + cooking fuel 6 + electricity 1 + gas-supply 1 + heating availability 1). Separately, K=90 = six `i021` contrasts × 15 blood phenotypes in the `i020=No` route. Do not turn the routed `i021` values into missing-as-reference or claim population-wide heating-fuel associations.

## Required work before writing production contrast code

1. Compare these items, labels, categories, and skip patterns to the exact authenticated Wave 1 release questionnaire/codebook and Stata variable/value labels. Record the source release/version and file hashes locally.
2. Verify whether each item resides in a household file or person file in that release, its household/person key, duplicate behavior, and the correct merge cardinality. Do not expand a household response to people until linkage is proven.
3. Define each item’s valid response, special/missing codes, and routed denominator from the actual release metadata. Keep structural skips separate from refusals, don't-knows, and ordinary missingness.
4. Reconcile the K=150 items to the blood-analysis frame and weight eligibility. For `i021`, additionally reconcile the `i020=No` route and blood-weight support; report its target domain precisely.
5. Freeze contrast reference levels, primary adjustment set, missingness rules, and the complete K=150/K=90 registers before inspecting association results. Preserve all planned hypotheses, marking non-estimable pairs with reasons.
6. Only after pilot validity/reproducibility, source/frame, and design gates pass, implement a separate protected K=150/K=90 runner. Do not repurpose the existing K=105 runner or interpret its batch q-values as final atlas-wide correction.

## Source locations

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc` and adjacent `_extracted.txt` search copy; provenance details in `sources_official/SOURCES.md`.
- `sources_official/CHARLS_2011_Codebook_extracted.txt`, housing-characteristics section (near extracted lines 97,715–97,827). The source bundle notes that the corresponding 2011 codebook PDF is not available locally; therefore the extracted text is a provisional aid pending release-matched confirmation.
- Existing route decision and scale-up gate: `audit/wave1_scaleup_runner_gap_2026-10-27.md` and `audit/pilot_success_criteria_and_scale_up_2026-10-26.md`.

## Status

**Document review prepared; exposure release validation, field mapping, fitting, methods review, and release remain pending.** No participant-level data were read and no association was estimated in this review.
