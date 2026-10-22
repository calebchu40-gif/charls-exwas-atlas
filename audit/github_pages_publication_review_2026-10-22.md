# GitHub Pages publication review (2026-10-22)

## Proposed site

The static site is served from `site-prototype/dist/`. The deployment workflow is `.github/workflows/deploy-pages.yml`; its artifact path is restricted to that directory. The checked directory contains 32 static files, including 29 JSON files and the HTML/JavaScript interface, totaling approximately 27.6 MB of JSON metadata at review time. `index.html` is the root entry point and `.nojekyll` is present.

The expected project-site URL is `https://calebchu40-gif.github.io/charls-exwas-atlas/`. GitHub Pages settings must select GitHub Actions as the publishing source. The first successful deployment determines the final live URL. The workflow is manual-only until the first publication is reviewed and confirmed.

## Content boundary

The published site contains variable names, labels, candidate exposure/phenotype roles, questionnaire/codebook-derived value labels, wave availability, units, routing notes, and review caveats. It does not contain respondent-level CHARLS records, local QA outputs, analysis sample counts, estimated associations, credentials, or the `sources_official/` source files. The website explicitly identifies the directory as a candidate inventory and reports zero reviewed association models.

The deployment action checks that the entry files exist, parses every top-level JSON file, and fails if common respondent-data or archive extensions appear inside the publication directory. The upload step names only `site-prototype/dist/`; no repository-wide upload is used.

## Hosting constraint

GitHub Docs state that Pages is available for public repositories on GitHub Free and for public or private repositories on Pro/Team/Enterprise plans; Pages content is publicly accessible by default. The account plan and Pages setting still need to be confirmed in the project settings. If the current private repository cannot use Pages on its plan, retain this source repository as private and deploy only the static directory from a separate public site repository.

Official references: [GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).
