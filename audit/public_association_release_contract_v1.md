# Public association-result release contract v1

## Purpose and boundary

The site may publish an association family only after the private result table passes `EXWAS_result_schema_v3.csv` validation and a separate private disclosure-review CSV explicitly approves every hypothesis in the family. This is an additional release gate, not a substitute for CHARLS authorization, official-source verification, survey-design review, pair-level estimability review, or the user's institutional/legal disclosure obligations. CHARLS microdata, respondent rows, private hashes, local paths, and the review file itself must never be copied into GitHub or Pages.

No numeric small-cell cutoff is invented here. The reviewer must apply the controlling CHARLS terms and applicable research/ethics policy to the exact proposed aggregate payload. A review applies only to the exact result CSV bytes recorded by SHA-256 in each review row; changing the result CSV invalidates the review.

## All-or-nothing family rule

The disclosure file must have exactly one decision for every `analysis_id` in the validated result table, with no extras. A decision is either `approved_public_aggregate` or `withheld`. If any one hypothesis in a declared `multiple_testing_family` is withheld, the whole family is omitted. A family can be exported only if the complete declared K rows are present and every row is approved. This preserves the frozen testing family and avoids a selectively published subset.

## Protected review record

Use `audit/templates/disclosure_review_template.csv` as the header. Keep the filled CSV under the authorized local `%LOCALAPPDATA%/CHARLS_ExWAS_Atlas` directory and outside Git/synchronized folders.

- `analysis_id`: exact stable identifier from the private result table.
- `decision`: `approved_public_aggregate` or `withheld`.
- `review_record_id`: opaque reference to the private review record; do not use a path or name.
- `reviewer_reference`: non-identifying role/code, not a person's name or contact details.
- `reviewed_at`: ISO-8601 timestamp including time zone.
- `reviewed_result_sha256`: SHA-256 of the exact complete private result CSV reviewed. This hash remains private.

The reviewer should assess the proposed table as a whole, including estimates, intervals, multiplicity values, sample counts, fit messages, population labels, and whether cross-row or external-data linkage could identify respondents. A technical pass from the exporter does not itself establish that the substantive disclosure decision was correct.

## Export procedure

1. Confirm the private result CSV passes `scripts/validate_exwas_result_table.py`, including official-source/design and pair-review requirements for successful fits.
2. Complete the private review CSV against that exact result CSV. If a file changes afterward, recalculate the hash and repeat disclosure review.
3. From the project root, run `python scripts/build_public_association_release.py --results <protected-result.csv> --review <protected-review.csv> --publish` using paths under the protected local workspace.
4. Inspect `site-prototype/dist/association_results_v1.json`; then run `python scripts/validate_public_site_payload.py site-prototype/dist`. The Pages workflow independently runs the same strict payload validator.
5. Only the allowlisted browser JSON is tracked/published. Reviewer identities, review records, hashes, and local paths are not included. The browser refuses incomplete K families, unexpected keys, or rows not marked approved.

The builder requires `--publish`, checks that both input files resolve under the protected workspace, and writes only inside `site-prototype/dist`. When no complete family is approved, it exits without producing a public payload. At present no such payload is present in `site-prototype/dist`, and the atlas still reports zero formal, reviewed association results.
