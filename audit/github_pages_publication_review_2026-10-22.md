# GitHub Pages publication review (2026-10-22)

## Proposed site

The static site is served from `site-prototype/dist/`. The deployment workflow is `.github/workflows/deploy-pages.yml`; its artifact path is restricted to that directory. The checked directory contains 33 static files, including 30 JSON files and the HTML/JavaScript interface, totaling 32.42 MiB for the full site payload. `index.html` is the root entry point and `.nojekyll` is present. The largest file is the metadata-only candidate-pair lookup; no respondent records or analysis estimates are included.

The expected project-site URL is `https://calebchu40-gif.github.io/charls-exwas-atlas/`. GitHub Pages settings must select GitHub Actions as the publishing source. The first successful deployment determines the final live URL. After initial publication, pushes to `main` that change `site-prototype/dist/**` or the deployment workflow trigger a deployment; manual dispatch remains available.

## Content boundary

The published site contains variable names, labels, candidate exposure/phenotype roles, questionnaire/codebook-derived value labels, wave availability, units, routing notes, and review caveats. It does not contain respondent-level CHARLS records, local QA outputs, analysis sample counts, estimated associations, credentials, or the `sources_official/` source files. The website explicitly identifies the directory as a candidate inventory and reports zero reviewed association models.

The deployment action checks that the entry files exist, parses every top-level JSON file, and fails if `.dta`, `.sav`, `.rds`, `.parquet`, `.sqlite`, `.zip`, `.7z`, `.rar` or `.csv` files appear inside the publication directory. The upload step names only `site-prototype/dist/`; no repository-wide upload is used.

## Hosting constraint

GitHub Docs state that Pages is available for public repositories on GitHub Free and for public or private repositories on Pro/Team/Enterprise plans; Pages content is publicly accessible by default. The user explicitly approved making the complete project repository public. The repository is now public and Pages is deployed. An unauthenticated Pages API request returned 404 during verification, but the deployed public site and its assets returned HTTP 200; the live HTTP result is authoritative for visitor availability. No fallback public site repository is planned unless the owner later changes this preference.

Official references: [GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).


## Current status after owner visibility decision

On 2026-10-22 the owner approved full public visibility and changed the repository to public. The unauthenticated GitHub API confirmed `private=false`. The owner selected GitHub Actions in Pages settings and manually started deployment Run #1 (`39809424951`); GitHub reported **Success**. External HTTP GET/HEAD checks returned 200 for the site root, `app.js`, and `candidate_pair_explorer_v1.json`. Live URL: `https://calebchu40-gif.github.io/charls-exwas-atlas/`. The latest Pages artifact is 33 static files (30 JSON files; 32.42 MiB total), with zero `.dta`, `.sav`, `.rds`, `.parquet`, `.sqlite`, `.zip`, `.7z`, `.rar` or `.csv` files. Every JSON parses successfully.

## Release checklist for the owner

Initial publication completed. Site asset and deployment-workflow changes pushed to `main` now deploy automatically. For a manual redeploy, open **Actions → Deploy public atlas site → Run workflow**, choose `main`, and run it; verify a green completion and check the deployed URL.

## 2026-10-23 automatic deployment verification

Commit `3f859ef` synchronized 217 healthcare-access field review states into the main catalogue and updated the site renderer. GitHub Actions run [`39872665197`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/39872665197) completed successfully. The public `catalog.json` returned HTTP 200 and its 2011 `ed005_1_` record showed the reviewed continuous-count/routing status; `app.js` returned HTTP 200 with the updated status renderer. This confirms the automatic push deployment path.

Live project URL: `https://calebchu40-gif.github.io/charls-exwas-atlas/`. The repository’s default branch is `main` and visibility is public.

The 32.42 MiB figure is the full static directory size (33 files); earlier notes describing 32.30 MiB as JSON-only were inaccurate. Latest generated catalog counts remain 7,544 field rows, 1,408 unique E/P concepts and 6,598 E/P source mappings. The cognition-specific memo’s 7,548/1,409 figures were captured at an intermediate build and are superseded by the canonical build outputs and current directory snapshot. GitHub displayed non-blocking Node.js 20 deprecation and runner-image migration notices; deployment completed successfully.

## 2026-10-23 chronic-treatment label release

Commit `190837f` was pushed to `main`. GitHub Actions deployment run [`39874593820`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/39874593820) completed successfully. External requests to the site root, `catalog.json`, and `app.js` returned HTTP 200. The live catalog (7,544 rows) contains the reviewed labels for 68 2018 chronic-treatment fields; representative entries include `da010_w4_2__s99` (`99=Never Had the Disease`) and the hypertension, diabetes, cancer, stroke, and mental-health options. The renderer contains the simplified-Chinese status explanation. Published directory: 33 files / 34,098,109 bytes; blocked data/archive extensions: zero.

## 2026-10-23 cross-wave treatment labels

Commit `df0930a` added 125 selected-option labels independently transcribed from the 2011, 2013, and 2015 official Codebooks. GitHub Actions run [`39875503802`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/39875503802) completed successfully. Live `catalog.json` returned HTTP 200; spot checks confirmed 2011/2013/2015 values appear with `DO NOT ANALYZE` and the unselected-storage warning, while 2018 retains its separate `0=No` response categories. Live `app.js` contains Chinese translations for both review states. Across four waves, the site now indexes 193 wave-specific treatment-field label sets (21/52/52/68), not 193 independent outcomes. The data remain metadata only; no respondent observations or analysis results were published.

## 2026-10-23 2011 header-normalization correction

Commit `4e57ae7` corrected the 2011 treatment-code parser for official Codebook headings that spell variable components with spaces (for example, `da010 2 s4`). This restored 32 2011 option labels omitted from the previous deployment. GitHub Pages run [`39876436833`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/39876436833) succeeded. Live `catalog.json` returned HTTP 200 and shows 2011 `da010_2_s1`, `_s2`, and `_s4` option descriptions; their review state says unselected storage/routed denominator unverified and `DO NOT ANALYZE`. The live site has 225 chronic-treatment wave-field label sets across four waves (53/52/52/68), not 225 unique outcomes. `app.js` contains the matching Chinese warning.


## 2026-10-23 survey-design methods disclosure

The homepage methods section now summarizes wave-specific weighting/sample-flag constraints and links to `audit/survey_design_weight_review_v1.md`. It explicitly marks the 2013 prepared-table flag loss as a rebuild blocker, treats `communityID` as a PSU candidate pending exact-release matching, and states that no project-verified variance-stratum ID or replicate weights are currently available. It does not present geography as a substitute stratum or claim complete design-adjusted inference. A regression test guards this disclosure.


Commit `a47c401` added the survey-design disclosure. GitHub Actions run [`39876991302`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/39876991302) completed successfully in 19 seconds. The live homepage returned HTTP 200 and includes the new card and audit link.
