# Objective measurements are phenotype-only candidates by default

## Finding

The official `objective_measurement_crosswalk_v1.csv` defines objective clinical and physical measurements as phenotype candidates. The broad keyword discovery rule also tagged some of the same wave-specific source fields as `e,p` under `internal biomarker`, which created a second, misleading exposure role and duplicate public catalogue rows.

## Change

The catalog builder now checks exact `(wave, source field)` keys from the audited objective-measurement crosswalk before emitting the automatic `e,p` internal-biomarker discovery row. For those keys, the broad dual-role row is omitted; the separately reviewed, domain-specific P catalogue row and official P concept-source mapping remain. This applies only to fields listed in the objective-measurement crosswalk. Blood assay biomarker candidates and other internal measures retain their existing review-dependent role handling.

The current crosswalk contains 108 wave-field keys. The rebuild removed 36 automatic E/P dual-role rows. All 108 keys retain a source-backed P role, and none appears as an E role in the candidate series. The remaining 13 unlinked internal-measure E discovery candidates are outside this objective-measurement crosswalk and still require individual role review.

## Validation and interpretation

The targeted candidate-role and objective-measurement tests pass (9 tests). The complete metadata finalization pipeline rebuilt the public shards and candidate-pair index. Public E/P/C catalogue shards contain 4,790 / 2,093 / 980 rows. Metadata co-availability counts and candidate roles are not respondent counts, analytic eligibility, statistical results, or approval to test an association. No respondent-level records were read or published. Formal association models and actual pairwise analytic sample sizes remain 0.
