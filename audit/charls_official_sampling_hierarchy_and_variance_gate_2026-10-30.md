# CHARLS official sampling hierarchy and variance-design gate

**Date:** 2026-10-30  
**Status:** Official design facts documented; executable variance specification remains unresolved. No model authorization.

## Officially documented design facts

The official CHARLS sample page describes the 2011 national baseline as a multi-stage probability sample. County-level units were ordered/stratified by region, urban district versus rural county, and GDP per capita before county selection by PPS. Three village/neighborhood units were then selected by PPS within each county-level unit; these village/neighborhoods are described as the sample's PSUs. Dwelling units were sampled inside communities, then eligible households and respondents were selected under age and spouse rules. The official Wave 1 user guide provides the fuller sampling narrative, while Wave 4's guide summarizes the baseline as stratified, multistage PPS. See [CHARLS Sample](https://charls.pku.edu.cn/en/About/Sample.htm), [Wave 1 User Guide](https://charls.pku.edu.cn/en/data/User2011.pdf), and [Wave 4 User Guide](https://charls.pku.edu.cn/en/data/User2018.pdf).

These sources establish the hierarchy and baseline target concept; they do **not** by themselves establish which released variables identify every stage/stratum needed for Taylor-linearized variance or replicate-weight variance in each wave. The Wave 2 release page publishes separate PSU and weight files, but publication of those files is not equivalent to a complete executable variance specification. The Wave 2 PSU header review found community/geographic descriptors, but no documented full county-stage/stratum/replicate design fields. See the [official Wave 2 release page](https://charls.charlsdata.com/pages/Data/2013-charls-wave2/en.html).

## Analysis consequence

- Preserve released sample markers and weights separately; weights address unequal selection/nonresponse for point estimation but do not, alone, encode every covariance component needed for design-based standard errors.
- Do not invent strata from region, urban/rural labels, community IDs, or sort order. Do not claim a community-only cluster declaration is the full CHARLS design merely because a forum post proposed one.
- For each wave and outcome module, require a documented mapping from the released sample frame to the available variance identifiers and an independently reviewed variance method before fitting official association models. Until then, outputs are limited to metadata/frame QA and genuinely unweighted descriptive engineering diagnostics kept private.
- This uncertainty is a methodological gate, not a reason to stop catalog work: candidate field mapping, question routes, module-specific outcome weights, missing-value semantics, age rules, and public-site release controls can continue independently.

## What this review does not establish

It does not decide whether to use a particular weight, denominator, age domain, or variance estimator; it does not establish that Wave 2's 2013 design is identical to Wave 1; and it does not authorize any participant-level association fit. Formal CHARLS ExWAS association models remain 0.
