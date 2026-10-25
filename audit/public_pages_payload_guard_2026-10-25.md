# GitHub Pages payload guard (2026-10-25)

## Change

The Pages workflow previously rejected a short list of data and archive suffixes. That left uncommon statistical formats and unknown binary types able to pass the payload check. Deployment now calls `scripts/validate_public_site_payload.py`, which uses a browser-asset allowlist, requires non-empty `index.html` and `app.js`, and parses every JSON file recursively before packaging.

Allowed files are HTML, JavaScript, CSS, JSON, common web images, web fonts, and `.nojekyll`. This includes the current site catalog format and blocks common CHARLS/data formats (including DTA, SAS, SPSS, XPT, R, spreadsheet, database, columnar, and archive files) as well as unrecognized extensions. The packaging step remains limited to `site-prototype/dist` and removes the master `catalog.json` from the published artifact.

## Verification

- Four focused tests cover accepted browser assets, case-insensitive rejection of common data/archive formats, rejection of unknown types and malformed JSON, and required entry points.
- The local payload check passed for the current site bundle.
- Full Python test suite: 421 tests passed.

## Scope

This is a deployment-time safeguard for accidental file inclusion; it does not replace repository access controls or a human review of the public payload.
