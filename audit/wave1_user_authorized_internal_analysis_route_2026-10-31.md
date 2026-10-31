# User-authorized internal Wave 1 analysis route

This route separates permission to compute from independent methods review and public release. When the user explicitly authorizes an internal run, the executor can use a private, hash-bound configuration without claiming an independent review. The ordinary review-gated route remains available.

Before reading the prepared respondent table, the internal route still verifies the official Wave 1 source manifest, prepared-table and age-candidate hashes, registered analysis-plan fingerprint, configuration hash, and private output location. It writes a run manifest identifying the authorization route and marks public release as not approved.

The user-authorized route is not a shortcut for choosing favorable results: it runs the complete registered family, retains all registered outcomes and contrasts, records the selected survey design and limitations, and does not select pairings by p-value. Public result release remains a separate decision after methods, reproducibility, and disclosure review.