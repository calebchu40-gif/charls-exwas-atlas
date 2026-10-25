# 2011 DA010 selected-option storage status synchronization

## Scope

This review propagates the existing aggregate-only local QA for the 32 Wave 1 `DA010` response-slot fields (eight disease items × four options) into the wave-resolved exposure/phenotype crosswalk and public metadata catalog. It does not add or remove a concept, infer participant-level responses, or approve an association model.

## Evidence and interpretation

The baseline questionnaire identifies DA010 as “check all that apply” and includes “None of the above.” The official Codebook's selected-option field indices match the nonmissing response codes observed in the protected local prepared table. The prior aggregate-only QA also found “None of the above” co-occurring with another treatment option in seven disease groups and DA010 answers in records where the DA007 doctor-diagnosis response is No in all eight groups. These patterns do not establish invalid responses: the questionnaire routes DA010 using disease-item indices and, for a subset of diseases, DA008 self-awareness. DA007/DA008 alone do not define the complete eligible denominator.

The catalog therefore records the selected category and the observed selected-code corroboration while keeping unselected storage, blank-versus-skip meaning, route denominator, and cross-wave harmonization unresolved. It does not interpret an empty response slot as “No.” All 32 fields retain the no-analysis status in their label/mapping metadata, and their pre-existing review flags are preserved. The separate official triage inventory remains 92 unique wave-field locks; this metadata synchronization does not add formal inventory locks.

## Implementation and validation

Added `scripts/apply_2011_chronic_treatment_storage_review.py` to both full and finalization-only metadata build sequences. The updater validates official questionnaire and Codebook anchors, requires exactly the 32 intended fields in each target table, synchronizes the audit CSV/JSON and public site catalog, preserves existing review flags and formal lock inventory, and is idempotent. For this already-built topic, `scripts/finalize_2011_chronic_treatment_review.py` provides a fast downstream refresh (updater, shards, pair browser, label summary, lock validation); changes to upstream mappings still require the full metadata build. The local aggregate-only QA remains in `scripts/audit_2011_chronic_treatment_storage.py`; its private output contains only boolean group checks and is not committed.

Validation: full finalization-only metadata rebuild completed; the targeted updater synchronizes 32 fields in the ancillary map, concept-source crosswalk, candidate-field CSV/JSON, and site catalog. The fast downstream refresh was also run and passed with 92 locks. All 417 Python tests pass. No participant-level values, identifiers, frequencies, or association estimates were published.
