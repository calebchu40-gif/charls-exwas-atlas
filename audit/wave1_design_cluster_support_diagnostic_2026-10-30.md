# Wave 1 design-cluster support diagnostic

This diagnostic prepares restricted design-support information for the Wave 1 methods review. It is not an association analysis, a variance estimator, or approval of the approximate design.

## Inputs and output boundary

The script reads only the protected prepared person key and community key, the official Blood key and `bloodweight`, the protected provisional age-interval fields, and the official PSU community key. It validates source provenance, table hashes, key uniqueness, person/Blood/age linkage, and PSU-community coverage before summarizing. It does not read exposure answers, biomarkers, names, dates of birth, or geographic labels.

The aggregate JSON is written to `private/qa_outputs/wave1_design_cluster_support_private.json` on the authorized server and must remain private. Do not copy its exact cell counts or weight summaries into GitHub, OneDrive, the public website, or collaborator bundles.

## Prespecified diagnostic summaries

For the positive finite `bloodweight` observed sample, the lower-bound age-45+ domain, and the upper-bound age-45+ sensitivity domain, report:

- respondent-record and distinct-cluster counts;
- communities containing one observed record and two or more observed records;
- cluster-size minimum and maximum;
- a one-stage WR reference degrees-of-freedom count (`number of clusters - 1`);
- weight coefficient of variation and Kish weight effective sample size.

Each summary is calculated for the user-selected `communityID` PSU candidate and, separately, the six-character ID-prefix grouping. The prefix grouping is only a structural sensitivity candidate; this audit does not identify it as the original first-stage PSU.

## Interpretation limits

The summaries characterize support in the observed, positively weighted blood sample. They are not approved model sample sizes. A community with one observed record is not automatically a singleton PSU under a final stratified design. The reference degrees of freedom do not account for omitted strata, PPS selection, the unknown final split-community mapping, or other stages. Weight CV and Kish effective N do not substitute for design-based variance. The reviewer must evaluate whether the selected approximate target and its uncertainty statement are defensible.

The audit makes no estimate and cannot authorize the 105-coefficient pilot. The readiness record remains a separate hash-bound review gate.
