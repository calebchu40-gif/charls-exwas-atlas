# GitHub Pages publication review (2026-10-22)

## Proposed site

The static site is served from `site-prototype/dist/`. The deployment workflow is `.github/workflows/deploy-pages.yml`; its artifact path is restricted to that directory. The checked directory contains 32 static files, including 29 JSON files and the HTML/JavaScript interface, totaling approximately 27.6 MB of JSON metadata at review time. `index.html` is the root entry point and `.nojekyll` is present.

The expected project-site URL is `https://calebchu40-gif.github.io/charls-exwas-atlas/`. GitHub Pages settings must select GitHub Actions as the publishing source. The first successful deployment determines the final live URL. The workflow is manual-only until the first publication is reviewed and confirmed.

## Content boundary

The published site contains variable names, labels, candidate exposure/phenotype roles, questionnaire/codebook-derived value labels, wave availability, units, routing notes, and review caveats. It does not contain respondent-level CHARLS records, local QA outputs, analysis sample counts, estimated associations, credentials, or the `sources_official/` source files. The website explicitly identifies the directory as a candidate inventory and reports zero reviewed association models.

The deployment action checks that the entry files exist, parses every top-level JSON file, and fails if common respondent-data or archive extensions appear inside the publication directory. The upload step names only `site-prototype/dist/`; no repository-wide upload is used.

## Hosting constraint

GitHub Docs state that Pages is available for public repositories on GitHub Free and for public or private repositories on Pro/Team/Enterprise plans; Pages content is publicly accessible by default. The user explicitly approved making the complete project repository public. The repository remains private pending GitHub account email re-authentication; after the owner completes that challenge, change visibility and choose GitHub Actions in Pages settings. No fallback public site repository is planned unless the owner later changes this preference.

Official references: [GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).


## Current status after owner visibility decision

On 2026-10-22 the owner stated that full public visibility is acceptable. GitHub Settings confirmed the repository is private and Pages is unavailable at the current account tier while private. The visibility flow reached GitHub “Confirm access” and requires the account owner to complete email verification. The project has not yet been made public and no site URL is live. The GitHub Pages artifact remains 32 static files (29 JSON files; 27.61 MB JSON), with zero `.dta`, `.sav`, `.rds`, `.parquet`, `.sqlite`, `.zip`, `.7z`, `.rar` or `.csv` files. Every JSON parses successfully.
