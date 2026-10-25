# Clean-checkout GitHub Actions failure and repair (2026-10-26)

## Failure evidence

GitHub Validate #520 (commit `92206df`) failed in `Run unit tests`. Its public check annotations identify `FileNotFoundError` for `audit/raw_variable_catalog_v1.csv` in seven community module test setups. The file is excluded by `.gitignore` and exists only as a local metadata QA artifact. It contains module row-count metadata and source archive names; it is intentionally not uploaded to the public repository. The tests passed locally because that private/local artifact was present.

## Repair

Created `audit/community_field_inventory_2011_v1.csv`, a sanitized 719-row community field inventory with only four columns: wave, module, CHARLS variable name, and official variable label. It has no module row counts, source archive names, respondent values, answer frequencies or analytical results. Updated the seven tests to read this inventory, and added `tests/test_sanitized_community_inventory.py` to guard its schema and contents.

## Verification and status

The complete local suite passes (508 tests). Public-site payload validation passes; all 92 `DO NOT ANALYZE` locks reconcile; JavaScript syntax, deferred data loading and `git diff --check` pass. GitHub Validate for the repair commit is pending. The separate Part E site update was published successfully by Pages Deploy #258 (app v132), verified in the live community catalogue.
