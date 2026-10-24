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
