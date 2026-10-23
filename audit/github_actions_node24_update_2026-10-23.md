# GitHub Actions Node runtime update (2026-10-23)

The deployment run exposed GitHub's notice that several pinned JavaScript actions were targeting Node 20 and would be forced to Node 24. Updated the Pages workflow to checkout v5, configure-pages v6, upload-pages-artifact v4, and deploy-pages v5. Updated the metadata validation workflow to checkout v5, setup-python v6, and setup-node v5. The chosen releases use Node 24 while retaining the workflow inputs and Pages artifact flow; GitHub's Pages documentation recommends upload-pages-artifact v4 and deploy-pages v4 or newer.

The deployment still packages only `site-prototype/dist/` into `_site`, removes the build-only master catalog, validates JSON and blocks respondent-data/archive extensions before upload. No data or site content changed in this workflow-only update.

The first upgrade run revealed that `upload-pages-artifact@v4` still bundles `actions/upload-artifact@v4`, which emitted a Node 20 deprecation warning. The official `actions/upload-pages-artifact` main revision `5f327015a708106f6f1b7c9a633901af30fe80cb` was inspected directly; its composite manifest uses the immutable `actions/upload-artifact` v7.0.1 commit, which runs on Node 24. The Pages workflow now pins that reviewed upstream revision by SHA rather than a floating branch. All other action versions remain as above.

Validation: the metadata validation workflow succeeded on commit `9affa8e`. Pages deployment workflow run #28 for commit `343cbf8` succeeded, though its nested v4 artifact action emitted the warning described above. Final Pages workflow verification for the pinned Node 24 artifact action is pending.
