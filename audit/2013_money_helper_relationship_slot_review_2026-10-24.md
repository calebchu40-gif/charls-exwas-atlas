# 2013 money-management helper relationship slots: source review (2026-10-24)

The 2013 official questionnaire's health/functioning module asks whether the respondent has difficulty managing money because of health or memory problems, then asks whether anyone helps and records up to two helpers. The repeated helper prompt is DB022_W2_9; DB022_W2_10/11 capture conditional grandchild/other relationship detail, and DB022_W2_12 asks whether another helper should be recorded. The official Codebook expands helper relationship choices into slot-specific source fields such as `db022_w2_9_1_s1` and `db022_w2_9_2_s1`.

This review covers the 62 fields that still carried the generic pending status. Two additional fields (`*_s64`, caregiver option) already had a specific review status and were left unchanged. The 62 rows remain role C as source-detail metadata: each is one relationship option in one of two helper slots, and none is an independently defined yes/no exposure or phenotype. The public catalogue retains the source field code and label for traceability but does not count these options as separate association constructs.

No blank was interpreted as “not selected” or “no helper.” The questionnaire route, up-to-two-helper limit, roster preloads, and absence of a verified analytic denominator prevent a population-wide binary interpretation from the option slots alone. The questionnaire/Codebook's source identity is documented; no cross-wave equivalence or analysis eligibility is claimed. Codebook frequencies were deliberately omitted.

Official local source extracts reviewed:

- `sources_official/CHARLS_2013_Questionnaire_extracted.txt`, health/functioning section, DB019_W2 and DB022_W2_9–DB022_W2_12.
- `sources_official/CHARLS_2013_Codebook_extracted.txt`, `db022_w2_9_1_s*` and `db022_w2_9_2_s*` field entries.

Generated metadata and propagation are maintained by `scripts/apply_c_placeholder_metadata_review.py`; regression coverage is in `tests/test_c_placeholder_metadata_review.py`. No respondent-level data were read.
