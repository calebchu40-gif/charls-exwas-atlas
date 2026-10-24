# GitHub Pages release verification — 2026-10-25

## Release identity

- Repository: `calebchu40-gif/charls-exwas-atlas`
- Commit deployed: `495e2aa4ae184d0da18798619eccf57c10c9e25c`
- Public site: https://calebchu40-gif.github.io/charls-exwas-atlas/
- Pages deployment: [run 40138358655](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40138358655), completed successfully.
- Metadata validation: [run 40138358564](https://github.com/calebchu40-gif/charls-exwas-atlas/actions/runs/40138358564), completed successfully.

## Live checks

The public homepage, application script, three role catalogues, alcohol-topic catalogue and cognition-topic catalogue returned HTTP 200. After normalizing Windows CRLF to LF, each fetched file matched the corresponding checked-in static asset by SHA-256:

| Asset | Rows / size | SHA-256 (LF-normalized where applicable) |
|---|---:|---|
| `index.html` | 75,955 bytes | `b0d436f2869332d2ca586b70f4c9b6512bfc2b8b103bc4d5bae037df19125940` |
| `app.js?v=86` | 67,828 bytes | `68c312f27878df28f7c57320d30d94361adf57b6b69a609a3f90a3f6b0a847e8` |
| `catalog_e.json` | 4,843 rows | `5dd324f834f12ed5e35e1ea8c596a6e4c698c81c8f97683da2c4c90e379b950c` |
| `catalog_p.json` | 2,068 rows | `4dfcf2ac1e169b8b02bbc3aac9aae3fddafdd1182c52c77134d1b303d4daaaf9` |
| `catalog_c.json` | 982 rows | `2dcd5acf1f5626abb7c8ef29ba2a3a8197a2b08d81f6f8cb2461c977fd6a2169` |
| `behavior_exposures_v1.json?v=4` | 38 concepts | `bd7fc8f186b31a3c444f004669746e9048e85db386a3d8e67f1980dbe2500ec0` |
| `cognition_items_v1.json?v=2` | 19 concepts | `cdea2631fce51e629ef67317c585d1d28cbafa92688e04d7df5bbbeefc98acab` |

The topic payload checks confirmed the five-wave subjective-memory field map (`dc004` in 2011–2018; `dc006` in 2020) and the 2020 `997=Don't Know` label. They also confirmed 13 wave-specific alcohol-frequency fields, including 2020 overall monthly frequency (`DA052`) and the documented 2011 routing caveat. The current JavaScript served as `app.js?v=86` contains the Chinese display labels for C-directory categories; the English values remain as source metadata keys.

## Interpretation

This verifies publication of the metadata-only release and that the public files match the reviewed local build. It does not indicate that any CHARLS microdata were published, that candidate variables passed analysis eligibility, or that an association model has run. The formal model count and actual pairwise analytic sample sizes remain zero.
