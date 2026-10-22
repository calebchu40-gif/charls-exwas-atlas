# GitHub Pages publication review (2026-10-22)

## Proposed site

The static site is served from `site-prototype/dist/`. The deployment workflow is `.github/workflows/deploy-pages.yml`; its artifact path is restricted to that directory. The checked directory contains 33 static files, including 30 JSON files and the HTML/JavaScript interface, totaling 32.42 MiB for the full site payload. `index.html` is the root entry point and `.nojekyll` is present. The largest file is the metadata-only candidate-pair lookup; no respondent records or analysis estimates are included.

The expected project-site URL is `https://calebchu40-gif.github.io/charls-exwas-atlas/`. GitHub Pages settings must select GitHub Actions as the publishing source. The first successful deployment determines the final live URL. The workflow is manual-only until the first publication is reviewed and confirmed.

## Content boundary

The published site contains variable names, labels, candidate exposure/phenotype roles, questionnaire/codebook-derived value labels, wave availability, units, routing notes, and review caveats. It does not contain respondent-level CHARLS records, local QA outputs, analysis sample counts, estimated associations, credentials, or the `sources_official/` source files. The website explicitly identifies the directory as a candidate inventory and reports zero reviewed association models.

The deployment action checks that the entry files exist, parses every top-level JSON file, and fails if `.dta`, `.sav`, `.rds`, `.parquet`, `.sqlite`, `.zip`, `.7z`, `.rar` or `.csv` files appear inside the publication directory. The upload step names only `site-prototype/dist/`; no repository-wide upload is used.

## Hosting constraint

GitHub Docs state that Pages is available for public repositories on GitHub Free and for public or private repositories on Pro/Team/Enterprise plans; Pages content is publicly accessible by default. The user explicitly approved making the complete project repository public. The repository remains private pending GitHub account email re-authentication; after the owner completes that challenge, change visibility and choose GitHub Actions in Pages settings. No fallback public site repository is planned unless the owner later changes this preference.

Official references: [GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).


## Current status after owner visibility decision

On 2026-10-22 the owner stated that full public visibility is acceptable. GitHub Settings confirmed the repository is private and Pages is unavailable at the current account tier while private. GitHub requires the account owner to complete email verification before changing repository visibility. The project has not yet been made public and no site URL is live. The latest Pages artifact is 33 static files (30 JSON files; 32.42 MiB total), with zero `.dta`, `.sav`, `.rds`, `.parquet`, `.sqlite`, `.zip`, `.7z`, `.rar` or `.csv` files. Every JSON parses successfully.

## Release checklist for the owner

1. Complete the email verification GitHub requests for the signed-in account. Keep the repository page open; GitHub may return to the visibility-confirmation dialog afterward.
2. In **Settings → General → Danger Zone → Change repository visibility**, set this repository to **Public** and confirm the repository name when prompted. The owner has explicitly approved public visibility.
3. Open **Settings → Pages**, select **GitHub Actions** as the build and deployment source, and save.
4. Open **Actions → Deploy public atlas site → Run workflow**, choose `main`, and run it. Check for a green completion, then open the `github-pages` deployment URL shown by the workflow.

Expected project URL: `https://calebchu40-gif.github.io/charls-exwas-atlas/`. Do not report this as live until the deployment succeeds and the page opens outside the local workspace. The repository’s default branch is `main`.

The 32.42 MiB figure is the full static directory size (33 files); earlier notes describing 32.30 MiB as JSON-only were inaccurate. Latest generated catalog counts remain 7,544 field rows, 1,408 unique E/P concepts and 6,598 E/P source mappings. The cognition-specific memo’s 7,548/1,409 figures were captured at an intermediate build and are superseded by the canonical build outputs and current directory snapshot.
