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
| `i020` | Whether the residence has heating facilities | Yes/No; codebook text labels Yes=1, No=2 | The official August 2011 baseline household questionnaire, read from a read-only Word rendering of the original DOC (printed pp. 182–183), defines this as having heating facilities **excluding earth-heating systems and heating-capable air conditioners**. Yes routes to `i022`; No continues to `i021`. This is a household facility indicator, not a measure of individual heating use, dose, or source. | One binary coefficient in K=150 after the released data coding/linkage/denominator is confirmed |
| `i021` | Main heating energy source | Solar, coal, natural gas, LPG, electric, crop residue/wood, other; codebook labels 1–7 | Asked only after `i020=No` in the baseline questionnaire. It is a routed subdomain, not an all-household exposure | Six contrasts vs electric within the eligible routed domain; K=90 with 15 blood outcomes |
| `i022` | Main source of cooking fuel | Coal, natural gas, marsh gas, LPG, electric, crop residue/wood, other; codebook labels 1–7 | Main household cooking-fuel category. Questionnaire routing and valid response handling must be confirmed from the released data | Six contrasts vs electric in K=150; K=105 pilot already covers it |

The predeclared scale-up arithmetic remains: K=150 = 10 exposure coefficients × 15 blood phenotypes (water 1 + cooking fuel 6 + electricity 1 + gas-supply 1 + heating indicator 1), contingent on validating the 2011 `i020` item. Separately, K=90 = six `i021` contrasts × 15 blood phenotypes in the `i020=No` route. Do not turn the routed `i021` values into missing-as-reference or claim population-wide heating-fuel associations.

## Item-version and rendering note for `i020`

The source of the exact 2011 wording is the official August 2011 Baseline Household Questionnaire DOC listed in `sources_official/SOURCES.md`, not the easily found CHARLS-hosted PDF at `https://charls.pku.edu.cn/wenjian/jiahuwenjuan.pdf`, whose cover identifies it as **Followup Questionnaire 2013**. A read-only Word rendering of the original DOC (printed pp. 182–183) confirms that `I020` asks whether the residence has heating facilities and explicitly excludes earth-heating systems and heating-capable air conditioners; Yes skips to `I022`, while No is followed by `I021`. The adjacent extracted-text convenience copy corrupts the Chinese characters, which is why its text-only search result was insufficient. Retain this distinction in the catalog: `i020` measures availability of the questionnaire-defined facility, and `i021` is a routed main-energy-source item among `i020=No` households. The released-file codes, linkage, valid denominator, and weighted support still require confirmation from the authenticated Wave 1 release.

**Official-URL byte check (2026-10-27):** downloaded the DOC again from the exact CHARLS baseline-page URL `https://charls.pku.edu.cn/sj/jiahuwenjuan2011.doc`; the 2,224,128-byte response matched the archived official DOC's SHA-1 `18efb28804fdbc975e3d334c845a179493bb6221`. This verifies that the archived wording/routing source is the current file served at that official URL as of the check; it does not authenticate any restricted data-release file or resolve the codebook-version match.

## Required work before writing production contrast code

1. Compare these items, labels, categories, and skip patterns to the exact authenticated Wave 1 release questionnaire/codebook and Stata variable/value labels. Record the source release/version and file hashes locally.
2. Verify whether each item resides in a household file or person file in that release, its household/person key, duplicate behavior, and the correct merge cardinality. Do not expand a household response to people until linkage is proven.
3. Define each item’s valid response, special/missing codes, and routed denominator from the actual release metadata. Keep structural skips separate from refusals, don't-knows, and ordinary missingness.
4. Reconcile the K=150 items to the blood-analysis frame and weight eligibility. For `i021`, additionally reconcile the `i020=No` route and blood-weight support; report its target domain precisely.
5. Freeze contrast reference levels, primary adjustment set, missingness rules, and the complete K=150/K=90 registers before inspecting association results. Preserve all planned hypotheses, marking non-estimable pairs with reasons.
6. Only after pilot validity/reproducibility, source/frame, and design gates pass, implement a separate protected K=150/K=90 runner. Do not repurpose the existing K=105 runner or interpret its batch q-values as final atlas-wide correction.

## Source locations

- `sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc` and adjacent `_extracted.txt` search copy; provenance details in `sources_official/SOURCES.md`.
- The 2011 DOC was rendered read-only in Word for printed pp. 182–183 to inspect the source wording because its plain-text extraction corrupts Chinese characters. The official 2011 DOC, rather than the 2013 follow-up PDF, controls the interpretation.
- [`CHARLS Questionnaire PDF`](https://charls.pku.edu.cn/wenjian/jiahuwenjuan.pdf) was checked during source triage; its cover identifies it as the 2013 follow-up questionnaire, so it is excluded as evidence of 2011 baseline wording.
- `sources_official/CHARLS_2011_Codebook_extracted.txt`, housing-characteristics section (near extracted lines 97,715–97,827). The source bundle notes that the corresponding 2011 codebook PDF is not available locally; therefore the extracted text is a provisional aid pending release-matched confirmation.
- Existing route decision and scale-up gate: `audit/wave1_scaleup_runner_gap_2026-10-27.md` and `audit/pilot_success_criteria_and_scale_up_2026-10-26.md`.

## Status

**Document review prepared; exposure release validation, field mapping, fitting, methods review, and release remain pending.** No participant-level data were read and no association was estimated in this review.
