# GitHub Actions Node runtime update (2026-10-23)

The deployment run exposed GitHub's notice that several pinned JavaScript actions were targeting Node 20 and would be forced to Node 24. Updated the Pages workflow to checkout v5, configure-pages v6, upload-pages-artifact v4, and deploy-pages v5. Updated the metadata validation workflow to checkout v5, setup-python v6, and setup-node v5. The chosen releases use Node 24 while retaining the workflow inputs and Pages artifact flow; GitHub's Pages documentation recommends upload-pages-artifact v4 and deploy-pages v4 or newer.

The deployment still packages only `site-prototype/dist/` into `_site`, removes the build-only master catalog, validates JSON and blocks respondent-data/archive extensions before upload. No data or site content changed in this workflow-only update.

Validation: pending local workflow checks and GitHub Actions runs after push.
