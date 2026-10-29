# Public association-result release contract v1

## Purpose and boundary

The site may publish an association family only after the private result table passes `EXWAS_result_schema_v3.csv` validation and a separate private disclosure-review CSV explicitly approves every hypothesis in the family. This is an additional release gate, not a substitute for CHARLS authorization, official-source verification, survey-design review, pair-level estimability review, or the user's institutional/legal disclosure obligations. CHARLS microdata, respondent rows, private hashes, local paths, and the review file itself must never be copied into GitHub or Pages.

The browser-payload validator also enforces status consistency: successful fits may use a verified or explicitly approximate variance label, while every non-success row must use `Design not fit-ready` and contain no numeric result fields. This is a schema consistency guard; it does not independently approve a survey design or make an approximate variance suitable for a particular estimand.

No numeric small-cell cutoff is invented here. The reviewer must apply the controlling CHARLS terms and applicable research/ethics policy to the exact proposed aggregate payload. A review applies only to the exact result CSV bytes recorded by SHA-256 in each review row; changing the result CSV invalidates the review.

## All-or-nothing family rule

The disclosure file must have exactly one decision for every `analysis_id` in the validated result table, with no extras. A decision is either `approved_public_aggregate` or `withheld`. If any one hypothesis in a declared `multiple_testing_family` is withheld, the whole family is omitted. A family can be exported only if the complete declared K rows are present and every row is approved. This preserves the frozen testing family and avoids a selectively published subset.

For a release presented as atlas-wide discovery results, the family must contain the complete, frozen set of **predeclared primary exposure–phenotype–wave hypotheses** across the declared release scope, including non-estimable hypotheses as rows. Recompute BY-FDR and Bonferroni over that entire primary family after all planned batches are assembled. Batch-local q values are exploratory only and cannot be released under atlas-wide discovery language. The current exporter validates the declared family it receives but does not determine whether the research scope is complete; that completeness needs a versioned protected finalization manifest/review. See `multiplicity_primary_family_reconciliation_2026-10-27.md`.

The protected helper `scripts/finalize_atlas_primary_family.py` implements the table-level finalization step. It requires a private manifest listing every expected primary `analysis_id`, a single primary `model_id`, all schema-valid batch CSVs, and a separate scope-review record whose SHA-256 binds to the exact manifest. It fails closed on missing/extra/duplicate IDs or unresolved fit statuses and writes the result and hash record only under `%LOCALAPPDATA%/CHARLS_ExWAS_Atlas`. Templates are `audit/templates/atlas_primary_family_manifest.template.json` and `audit/templates/atlas_primary_scope_review.template.json`. This helper does not decide which hypotheses belong in the atlas or validate reviewer qualifications; that scope must already be frozen and independently reviewed.

## Protected review record

Use `audit/templates/disclosure_review_template.csv` as the header. Keep the filled CSV under the authorized local `%LOCALAPPDATA%/CHARLS_ExWAS_Atlas` directory and outside Git/synchronized folders.

- `analysis_id`: exact stable identifier from the private result table.
- `decision`: `approved_public_aggregate` or `withheld`.
- `review_record_id`: opaque reference to the private review record; do not use a path or name.
- `reviewer_reference`: non-identifying role/code, not a person's name or contact details.
- `reviewed_at`: ISO-8601 timestamp including time zone.
- `reviewed_result_sha256`: SHA-256 of the exact complete private result CSV reviewed. This hash remains private.

The reviewer should assess the proposed table as a whole, including estimates, intervals, multiplicity values, sample counts, private fit messages, design notes, population labels, and whether cross-row or external-data linkage could identify respondents. Free-text `fit_message` and full `variance_design` notes are retained only in the protected result table for review. They are deliberately excluded from the browser payload: the site receives controlled `fit_status` and one of three fixed variance labels (`Survey design verified`, `Approximate variance; official stratum unavailable`, or `Design not fit-ready`). A technical pass from the exporter does not itself establish that the substantive disclosure decision was correct.

## Export procedure

1. Confirm the private result CSV passes `scripts/validate_exwas_result_table.py`, including official-source/design and pair-review requirements for successful fits, and confirm its primary multiplicity family is the complete frozen atlas-wide scope rather than a staged block.
   For staged inputs, first run `python scripts/finalize_atlas_primary_family.py --manifest <protected-manifest.json> --scope-review <protected-scope-review.json> --batches <protected-batch-1.csv> <protected-batch-2.csv> --output <new-protected-final.csv>`; include every planned batch and never put these paths or files in Git/OneDrive/public storage.
2. Complete the private review CSV against that exact result CSV. If a file changes afterward, recalculate the hash and repeat disclosure review.
3. From the project root, run `python scripts/build_public_association_release.py --results <protected-result.csv> --review <protected-review.csv> --publish` using paths under the protected local workspace.
4. Inspect `site-prototype/dist/association_results_v1.json`; then run `python scripts/validate_public_site_payload.py site-prototype/dist`. The Pages workflow independently runs the same strict payload validator.
5. Only the allowlisted browser JSON is tracked/published. Reviewer identities, review records, hashes, and local paths are not included. The browser refuses incomplete K families, unexpected keys, or rows not marked approved.

The builder requires `--publish`, checks that both input files resolve under the protected workspace, and writes only inside `site-prototype/dist`. When no complete family is approved, it exits without producing a public payload. At present no such payload is present in `site-prototype/dist`, and the atlas still reports zero formal, reviewed association results.
