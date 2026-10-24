# Objective measurements are phenotype-only candidates by default

## Finding

The official `objective_measurement_crosswalk_v1.csv` defines objective clinical and physical measurements as phenotype candidates. The broad keyword discovery rule also tagged some of the same wave-specific source fields as `e,p` under `internal biomarker`, which created a second, misleading exposure role and duplicate public catalogue rows.

## Change

The catalog builder now checks exact `(wave, source field)` keys from the audited objective-measurement crosswalk before emitting the automatic `e,p` internal-biomarker discovery row. For those keys, the broad dual-role row is omitted; the separately reviewed, domain-specific P catalogue row and official P concept-source mapping remain. This applies only to fields listed in the objective-measurement crosswalk. Blood assay biomarker candidates and other internal measures retain their existing review-dependent role handling.

The current crosswalk contains 108 wave-field keys. The rebuild removed 36 automatic E/P dual-role rows. All 108 keys retain a source-backed P role, and none appears as an E role in the candidate series. The remaining 13 unlinked internal-measure E discovery candidates are outside this objective-measurement crosswalk and still require individual role review.

## Validation and interpretation

The targeted candidate-role and objective-measurement tests pass (9 tests). The complete metadata finalization pipeline rebuilt the public shards and candidate-pair index. Public E/P/C catalogue shards contain 4,790 / 2,093 / 980 rows. Metadata co-availability counts and candidate roles are not respondent counts, analytic eligibility, statistical results, or approval to test an association. No respondent-level records were read or published. Formal association models and actual pairwise analytic sample sizes remain 0.

The full Python test suite passes (373 tests); all 34 static JSON files parse, JavaScript syntax and Python compilation pass, all 92 `DO NOT ANALYZE` locks match the triage list, and `git diff --check` passes. Commit `53f40e5` was pushed to `main`; GitHub Pages Deploy run [40122389529](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40122389529) completed successfully. The public homepage returned HTTP 200 and live E/P/C shard counts matched the local build.

## 后续更新（2026-10-25）

原审计中所述 13 个交叉表外的内部生物标志物 E 发现项，已由 [`internal_biomarker_exposure_role_review_2026-10-25.md`](internal_biomarker_exposure_role_review_2026-10-25.md) 作出明确的可选内部E候选决定，并在血检 crosswalk 中补齐 E/P 来源角色。该决定只涉及实验室血液分析物，不扩大客观体格/功能测量角色；客观测量仍为 P-only 候选。候选配对仍需遵守血检权重、子样本资格、波次校准和非方向性解释限制。
