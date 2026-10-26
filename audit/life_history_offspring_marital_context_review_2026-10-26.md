# 2014 Life History offspring first-marriage context review (2026-10-26)

## Official sources reviewed

Reviewed CHARLS 2014 Life History Questionnaire pages 23–25 (C034–C038a1) and the matching `DEMOGRAPHICBACKGROUNDS` Codebook fields. The source files are `sources_official/CHARLS_Life_History_Questionnaire.pdf`, `sources_official/CHARLS_Life_History_Questionnaire_extracted.txt`, `sources_official/CHARLS_Life_History_codebook.pdf`, and `sources_official/CHARLS_Life_History_codebook_extracted.txt`. Codebook use is limited to field identities and response/category labels; descriptive frequencies and value summaries are not copied or used.

## Candidate mappings

| Candidate | Item and source-field family | Mapped fields | What the field family says |
| --- | --- | ---: | --- |
| Offspring ever-married status context | C034; `c034_1_`–`c034_18_` | 18 | Yes/no reported for each child slot.
| Spouse age difference context at first marriage | C035; `c035_1_`–`c035_18_`, plus `c035_2_1_`–`c035_2_18_` and `c035_3_1_`–`c035_3_18_` | 54 | Base response category plus reported years older/younger when those routes apply.
| Offspring spouse education at first marriage | C036; `c036_1_`–`c036_18_` | 18 | Highest education category reported for the child's spouse at the child's first marriage.
| Offspring spouse hukou at first marriage | C037a1; `c037a1_1_`–`c037a1_18_` | 18 | Agricultural, non-agricultural, or unified residence hukou.
| Offspring first-marriage relationship continuity | C038a1; `c038a1_1_`–`c038a1_18_` | 18 | Whether the child still lives with the spouse from the first marriage, with temporary separation explicitly not counted as a breakup.
| **Total** |  | **126** | Repeated child slots remain source components, not independent sample observations.

The questionnaire asks C034–C038a1 only for children born before December 12, 1998, children who died after age 12, or children with missing birth dates. C035 follows only a Yes to C034. C036, C037a1, and C038a1 are within the first-marriage route; the source distinguishes temporary separation from relationship breakdown. These eligibility and routing details make this a selected, conditional family-history domain, not a census of all offspring.

## Exact relative timeline fields excluded

Excluded from the candidate E/P map (but explicitly dispositioned in the exhaustive ledger): 18 C034 first-marriage year fields (`c034_1_1_`–`c034_1_18_`), 18 C035 exact spouse birth-year fields (`c035_1_1_`–`c035_1_18_`), and 18 C038a1 relationship-breakdown/divorce-year fields (`c038a1_1_1_`–`c038a1_1_18_`). The C035 base category can indicate which age-report route applied, but its exact-year value is in a separate field that remains excluded. Do not derive respondent age, child age, relationship duration, or a precise event timeline from these metadata.

## Interpretation and publication boundary

These five constructs are classified as E-role family/social-context candidates for directory browsing only. They are about the respondent's offspring and offspring spouses, not the respondent's clinical outcomes, not direct environmental measurements, and not proof of any shared household exposure. Preserve child-slot and conditional-route structure; never pool slot rows as independent observations, infer a No from a blank, or aggregate children without a prespecified estimand and authorized-data validation. The public payload contains only item identifiers, codebook labels, conceptual mapping and caveats—not names, individual responses, frequencies, linkage keys, or exact relative dates.

These variables come from the retrospective 2014 special Life History module. The official release says it has no survey weight, so the fields are not added to the regular five-wave pair-coavailability universe or to weighted regular-wave association models. A future analysis would require authorized microdata, an explicit estimand, age/eligibility/route handling, a defensible design approach, and appropriate ethics and disclosure review.

## Reproducible state

Definitions live in `scripts/build_life_history_exposure_crosswalk.py`; regenerated outputs are `audit/life_history_exposure_crosswalk_v1.csv`, `audit/life_history_demographic_backgrounds_full_coverage_2014_v1.csv`, and `site-prototype/dist/life_history_exposures_v1.json`. The deployed build is app v188 / JSON v54: 189 concepts / 6,041 field rows (E=5,980, P=61); Deploy #320 and Validate #638 succeeded, and public homepage/JSON returned HTTP 200. The 1,920-field demographic-background ledger has 1,189 mapped candidates, 260 C-only interview/roster/family-context fields, 204 deferred sensitive relative-identity fields, 264 date/linkage/release exclusions plus 3 separate join-key exclusions.  No association model has been fit.
