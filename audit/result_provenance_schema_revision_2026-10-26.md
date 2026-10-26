# CHARLS ExWAS result provenance schema revision (2026-10-26)

## Issue found

The v2 result validator required every successful row to place an `SHA256:<64 hex>` token in its public `data_release` field and described it as an official release-file checksum. The Wave 1 intake runbook correctly says CHARLS may not publish checksums and that a locally calculated digest identifies received bytes but does not authenticate the release. Thus v2 could block otherwise valid source-verified work whenever CHARLS did not provide a checksum, while also encouraging publication of a private file digest.

## v3 resolution

- `data_release` records the official CHARLS release name/version and source identity; it no longer carries a raw file hash.
- `source_identity_status` must be `verified_official_source` for a successful fit; a local hash cannot satisfy this gate.
- `source_hash_status` distinguishes `official_checksum_recorded`, `private_local_sha256_recorded`, `unavailable_pending_authorized_file`, and `unresolved`.
- A successful fit requires one of the two recorded states and an opaque `source_manifest_id`. The protected local run manifest must actually contain acquisition provenance and the corresponding hash evidence; a status label alone does not validate a source.
- The actual SHA-256, download evidence, and local paths stay in authorized private storage. Public result metadata must never expose a participant file, local path, or private raw-file digest.
- Hash availability does not replace the source identity gate: if the authorized official release/version cannot be independently confirmed, the fit remains blocked even when a local file hash exists.

The versioned specification is [`EXWAS_result_schema_v3.csv`](EXWAS_result_schema_v3.csv). The validator now checks the allowed hash status and rejects path-like manifest references. `EXWAS_result_schema_v2.csv` is retained as the historical format; new result tables use v3.

## Verification and scope

The 15 focused synthetic result-validator tests pass, including successful rows with an opaque synthetic manifest ID and private-hash status, rejection of missing hash evidence, and rejection of a local path in the public manifest-reference field. `git diff --check` passes. No CHARLS data were opened, no model was fit, no private digest was copied, and the formal result count remains zero. Repository CI runs on push and is the next external verification.
