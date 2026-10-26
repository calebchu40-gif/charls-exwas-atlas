# CHARLS ExWAS Atlas catalog delivery audit (2026-10-26)

## Objective audited

This project deliverable is the CHARLS candidate exposure/phenotype metadata atlas: a searchable catalog informed by the structure of the NHANES Phenome-Exposome Atlas, with CHARLS-specific source mapping and caveats. It is not a claim that all candidate pairs have been analyzed or that CHARLS contains NHANES-scale environmental chemical measurements.

## Evidence by requirement

| Requirement | Current evidence | Assessment |
|---|---|---|
| Systematically catalog candidate E/P concepts across regular CHARLS waves | `audit/ep_concept_mapping_coverage_v1.md`: 1,625 distinct E/P candidate concepts and 8,341 concept-to-source mappings across 2011, 2013, 2015, 2018, and 2020. All 8,341 E/P links match the generated field catalog; no E/P field is left without a candidate Concept ID. | Delivered as a discovery catalog; concept counts are not analytic eligibility counts. |
| Preserve official field identity, wave, labels, and review status | `audit/ep_concept_source_crosswalk_v1.csv`, generated E/P shards, official sources in `sources_official/`, and the source-specific review files. Wave labels, measurement levels, units, conditional routes, codebook labels, and unresolved conflicts remain attached to source rows rather than being silently pooled. | Delivered with explicit unresolved items and analysis locks. |
| Provide NHANES-inspired search and query presentation adapted to CHARLS | `site-prototype/` and `site-prototype/dist/` provide searchable E/P/C catalogs, concept/source mapping, wave filters, and a metadata co-availability pair explorer. The explorer labels candidate pairs as metadata co-availability, not statistical results or sample sizes. | Delivered as an interactive metadata atlas. |
| Include special 2014 Life History fields without conflating them with regular waves | Dedicated Life History directory: 195 candidate concepts / 6,103 source-field mappings (E=6,042, P=61), with all 1,920 `DEMOGRAPHICBACKGROUNDS` fields given a disposition. The official release's no-weight and special-sample restrictions are shown; the directory is separate from regular-wave weighted pair scans. | Delivered with source-level disposition and scope caveats. |
| Keep public content within CHARLS data-use requirements | `audit/charls_data_access_license_review_2026-10-24.md` records the official restrictions. Public site payloads contain field/concept metadata and method text only; participant-level answers/observations, Codebook frequencies, identifiers, and unvalidated associations are not published. | Delivered; every researcher must obtain their own authorized access. |
| Update handoff materials and verify the hosted site | `README.md`, `site-prototype/README.md`, `CHANGELOG.md`, and `audit/active_work_status_2026-10-26.md` document the current state and reproducible project files. Live site is app v191 / JSON v57; Validate #645 and Pages Deploy #323 succeeded; live endpoints returned HTTP 200 and the JSON counts/fields were checked. | Delivered and live-verified. |

## Deliberate non-claims and gates

- Formal association models and pairwise analytic sample sizes remain zero. The catalog does not display unvalidated associations.
- Candidate inclusion does not mean a variable is analysis-ready. Release-specific coding, routed denominators, biomarker sub-sample weights, PSU/variance design, and the target estimand remain field- or pair-specific gates.
- Some fields retain `DO NOT ANALYZE`, `pending release validation`, or conditional-route caveats. Those are explicit audit outcomes, not missing catalog rows; do not clear them without authoritative evidence.
- The 2014 Life History survey is a separate special retrospective survey with no released weight. It must not be treated as a sixth regular wave or silently pooled into the regular-wave ExWAS pair matrix.
- CHARLS lacks the NHANES environmental-chemical measurement panels described in the reference atlas. Housing, household, community, behavioral, socioeconomic, and physiological candidates must keep their actual measurement level and interpretation.

## Regeneration and maintenance

Use the project build instructions in `README.md` and `site-prototype/README.md`. Public content is built from source crosswalks and official documentation; never copy licensed participant-level files into the repository or Pages package. Recheck official CHARLS release notes and data-use terms before adding a new wave or changing an existing source mapping.
