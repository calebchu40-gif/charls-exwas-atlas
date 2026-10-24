# Candidate-role versus approved crosswalk coverage review

Reviewed 2026-10-24 using the generated candidate-series inventory, the audited concept-source crosswalk, and the public site text. This review reads only variable-level metadata; it does not access CHARLS respondent records, frequencies, sample counts, or model estimates.

## Finding

The automated discovery catalogue contains 49 wave-field rows with an `E/P` role label that do not have an approved `E` concept-source link. All 49 are internal clinical/physiological biomarkers, spanning 25 distinct source codes: 25 rows in 2011, 12 in 2013, and 12 in 2015. Every one of those fields has a corresponding audited `P` role in the concept-source crosswalk. No `P` candidate wave-field row is missing an approved `P` source link, and no unlinked `E` row falls outside the internal-biomarker discovery category.

The discrepancy is intentional at the discovery stage: the broad catalogue keeps internal biomarkers searchable as possible variables, while the reviewed crosswalk treats these clinical and physical measurements as phenotype candidates. They are not external environmental exposures by default. A future study may define a biomarker as an exposure for a specific estimand, but that requires an explicit rationale, time-order interpretation, and removal of same-concept self-pairs before it is linked as an E source.

## Site and validation

The public blood-biomarker panel already explains that automated dual-role labels are discovery/review labels and do not constitute approved E mappings. A regression test now compares every E/P candidate field-wave-role key with the approved crosswalk and permits only this documented internal-biomarker exception, with a matching P link for each row. This prevents later metadata expansion from silently increasing formal E/P co-availability based on an automated keyword role.

The counts above describe source-field metadata only. They are not analyte counts, eligible sample counts, pairwise-complete Ns, or association results.
