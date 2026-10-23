# Static atlas asset cache review (2026-10-23)

The public site serves its catalog JSON with GitHub Pages `Cache-Control: max-age=600` and an `ETag` (checked 2026-10-23 for `catalog.json?v=11` and `candidate_pair_explorer_v1.json?v=1`). The frontend previously used Fetch `cache: no-store` for every JSON request, which bypassed the browser's reusable HTTP cache on every visit.

Updated JSON fetches to `cache: no-cache`: the browser revalidates with the server and may reuse a matching cached representation after a `304 Not Modified`; changed responses are fetched normally. This preserves freshness while avoiding repeat transfer of unchanged assets. The public `catalog.json` is about 23 MB uncompressed and `candidate_pair_explorer_v1.json` about 6.3 MB; other topic catalogs add several more MB. This affects repeat visits only; the first visit still needs the data required by the current page, since data loading remains eager.

Validation: `node --check site-prototype/dist/app.js`; checked deployed response headers for ETag and max-age. Post-deployment verification should confirm the updated app script is served and inspect browser Network panel on a second load for conditional requests/cache reuse. This change does not affect catalog contents, the analysis state, or CHARLS data.
