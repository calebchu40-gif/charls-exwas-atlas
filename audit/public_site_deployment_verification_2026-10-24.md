# Public-site deployment verification — 2026-10-24

Repository: `calebchu40-gif/charls-exwas-atlas`  
Commit: `a5a42e4` (`Rebuild CHARLS digital and phenotype metadata consistently`)  
Public site: https://calebchu40-gif.github.io/charls-exwas-atlas/

## Deployment evidence

- GitHub Actions metadata validation run `40042411927`: success.
- GitHub Pages deploy run `40042411919`: success.
- Cache-busted homepage and public directory assets responded HTTP 200 after deployment.
- Live E/P/C field-wave directory counts: 4,739 / 2,104 / 990.
- Live catalogue retained the 15 Wave 5 digital-behavior candidate fields, the single-wave DA029 subjective life-expectancy phenotype with official ordinal labels, and reviewed legacy digital crosswalk entries.
- All 89 exact wave+field formal-analysis lock keys were found in the public E/P/C shards.
- Pair index reports `metadata_candidate_pairs_only`. Formal association models and pairwise complete-case Ns remain 0.
- `catalog.json` returns 404; there is no monolithic raw export. No respondent-level CHARLS data or Codebook descriptive frequencies were found in the public static assets.

## Scope and method

Verification used the public GitHub Pages origin, cache-busted requests to the deployed site assets, and the generated public directory shards. These checks establish that the expected metadata build is live; they do not establish release-file coverage, respondent eligibility, analysis Ns, model validity, or statistical associations. All wave-specific restrictions and 89 analysis locks remain in force.

## Follow-up deployment — 2026-10-24

Commit `0eaf332` (`Review CHARLS blood pressure and pulse metadata`) was pushed to `main`. GitHub Actions confirmed:

- Pages deploy run [#106 / `40044331718`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40044331718): success.
- Metadata validation run [#195 / `40044331712`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40044331712): success.

Cache-busted requests to the public `objective_measurements_v1.json` and `catalog_p.json` returned HTTP 200. The objective-measurement asset contains three waves each for systolic BP, diastolic BP and pulse; systolic/diastolic show `mmHg`, pulse unit remains blank, and the 2011 unresolved LI-to-QA identity is explicit. Public P-catalog rows show the corresponding concept units and keep 993/999 as non-completion/status codes, with the 2013/2015 exact field-source status. The objective-measurement asset URL cache key was advanced to `v=3`.

## Follow-up deployment — C-catalogue labels (2026-10-24)

Commit `7e71278` adds Chinese display labels for all 83 distinct C-catalogue subcategories and preserves each English source phrase for search and hover details. Commit `6f2afa6` advances the homepage app-script cache key to `v=63`.

Direct public requests confirmed HTTP 200 for the homepage, `app.js?v=63`, and `catalog_c.json`. The deployed homepage references `app.js?v=63`; the deployed app bundle contains the C-subcategory renderer and localization dictionary. The live C catalogue has 992 field-wave rows and 83 unique subcategories, with no untranslated categories. No catalog source rows, respondent data, model eligibility or association results changed.
