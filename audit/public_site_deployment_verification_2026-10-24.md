## Follow-up deployment — 2011/2013 hukou life-course C/E links (v102; 2026-10-25)

Commit `c449721` passed metadata validation [#444 / `40164311499`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40164311499) and Pages deploy [#223 / `40164311578`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40164311578). Cache-busted public requests confirmed that the homepage references `app.js?v=102`; the app bundle, E/P/C catalogue shards, and candidate-pair index match the committed local build. The C shard contains all 16 exact 2011/2013 hukou life-course rows with official Questionnaire/Codebook paths and conditional-route/no-self-adjustment cautions. No participant data, descriptive frequencies, association estimates, or pairwise complete-case Ns are published.

## Follow-up deployment — social participation/care C/E links (v101; 2026-10-25)

Commit `7a9709f` passed metadata validation [#442 / `40163665219`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40163665219) and Pages deploy [#222 / `40163665220`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40163665220). Cache-busted public requests confirmed that the homepage references `app.js?v=101`; app, E/P/C catalogue shards, candidate-pair index and social-exposure JSON match the local build. The C shard contains all four exact wave-field social participation/care links, including the 2013 questionnaire/Codebook discrepancy and the 2020 questionnaire and Codebook paths. No respondent data, numeric Codebook frequencies, association estimates or pairwise complete-case Ns are published.

## Follow-up deployment — historical hukou/location C/E links (v100; 2026-10-25)

Commit `4b358a3` passed metadata validation [#440 / `40162584659`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40162584659) and Pages deploy [#221 / `40162584678`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40162584678). The cache-busted public homepage references `app.js?v=100`; app, E/P/C catalogues match the committed build byte-for-byte, while homepage and candidate-pair JSON match after line-ending normalization. The public C catalogue contains all seven exact wave+field historical hukou/location overlap rows. No respondent-level records, descriptive frequencies, association estimates, or pairwise complete-case Ns are published.

## Follow-up deployment — residential-settlement C/E source links (2026-10-25)

Commit `3eeacfd` passed metadata validation [#439 / `40161982644`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40161982644) and Pages deploy [#220 / `40161982719`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40161982719). Cache-busted public assets returned HTTP 200; the homepage references `app.js?v=99`, the app bundle and E/P shards and pair index matched the local commit, and the C shard contains both exact settlement-context rows. Wave-specific categories and the no-numeric-pooling caveat are public.

## Follow-up deployment — household-electricity C/E source links (2026-10-25)

Commit `52a8439` passed metadata validation [#438 / `40161450433`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40161450433) and Pages deploy [#219 / `40161450411`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40161450411). The v98 site now references `app.js?v=98`; cache-busted requests confirmed HTTP 200 for homepage, app, E/P/C catalogues and candidate-pair explorer. E/P, C key coverage, and pair explorer match the committed build; all three exact-wave electricity-overlap rows are present with household-scope cautions. No participant data or association results are published.

## Follow-up deployment — partner-context C/E source links (2026-10-25)

Commit `ef09207` passed Pages deploy [#218 / `40160837604`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40160837604) and validation [#437 / `40160837599`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40160837599); both validation jobs succeeded. Cache-busted public requests confirmed HTTP 200 for the v97 homepage, app bundle and E/P/C catalogues plus candidate-pair JSON. App/index matched after line-ending normalization; E/P and pair-index matched byte-for-byte; the C catalogue had 982 rows with all six reviewed partner-context overlaps and no extra/missing wave-field keys. No participant records, outcome distributions, or fitted models are served.

# Public-site deployment verification — 2026-10-24

## Follow-up deployment — formal-schooling C/E source links (2026-10-25)

Commit `67ee4a0` passed Pages deploy [#217 / `40160109124`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40160109124) and metadata validation [#436 / `40160109096`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40160109096). The live site served v96 and the public C catalogue included the nine formal-schooling overlap rows with role-specific route caveats. The subsequent partner-context C/E overlap update is local v97 and is not part of this release.

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

## Follow-up validation — pandas compatibility (2026-10-24)

Commit `1339afd` removes deprecated in-place `DataFrame.drop` calls from the guarded Wave 2 official-weight merge. The merge's ID matching, overlap-conflict checks, output ordering and no-overwrite behavior are unchanged. All 263 local tests pass using both pytest and the exact `unittest discover` command used in CI; the pandas 3.1 deprecation warnings are gone. GitHub Validate run [#236 / `40056492623`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40056492623) succeeded. This was a pipeline/documentation change and did not alter public site assets, so it did not require a Pages deployment.

## Follow-up deployment — age-domain disclosure (2026-10-24)

Commit `c274aaf` clarifies that CHARLS interviews an age-eligible main respondent and spouse, and the Wave 4 individual cross-sectional weights apply to both. The methods panel now warns that `crosssection` alone does not mean every record is age 45 or older; analyses must define the age domain and spouse-record handling from the official release. GitHub Validate [#240 / `40057380931`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40057380931) and Pages Deploy [#117 / `40057380880`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40057380880) succeeded. A cache-busted public homepage request returned HTTP 200 and contained the new note. No sample counts, respondent data, or model results changed.

## Follow-up deployment — adult-education and chronic-disease C metadata (2026-10-25)

Commit `40539e9` passed GitHub Validate [#435 / `40159198184`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40159198184) and Pages Deploy [#216 / `40159198219`](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40159198219). The public site references `app.js?v=95`. Cache-busted requests to the homepage, app bundle, E/P/C shards, and candidate-pair JSON returned HTTP 200; the app and E/P/C JSON matched the committed build byte-for-byte, while HTML and pair JSON matched after line-ending normalization. The deployed C shard contains the adult-education source-mapped context rows and chronic diagnosis-age metadata. No respondent data, association estimates, or pairwise complete-case Ns were published.
