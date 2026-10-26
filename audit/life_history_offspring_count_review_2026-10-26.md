# 2014 Life History additional offspring-count review (2026-10-26)

## Scope and source interpretation

Reviewed C007, C009 and C017 in the official Life History Questionnaire (printed pp. 15–19; extracted pp. 19–23) against `DEMOGRAPHICBACKGROUNDS` Codebook fields. C007 screens for biological children, adopted children, or none among children not already mentioned. C009 counts additional biological children; C017 counts additional adopted children. The questionnaire places these questions after a preloaded child roster from earlier CHARLS rounds and routes to separate biological/adoption loops.

## Mapping and limitations

The builder maps five fields (`c007s1`–`c007s3`, `c009`, `c017`) to `life_history_additional_biological_and_adopted_children`, a respondent-level reproductive/family-structure E candidate. It deliberately calls these additional-child screen/count fields, not total parity: the values exclude children already mentioned in the roster, and the completeness/merge semantics must be checked in the authorized data release before deriving totals.

No child names, child-level dates, participant values, Codebook frequencies or association results are included. Biological and adopted categories stay separate; the three C007 screening choices are not interpreted as independent variables. The 2014 Life History release has no weight, so this candidate stays outside regular-wave weighted analysis unless its target population and design are separately justified.

The reproducible full-module ledger now maps these five fields to the candidate. Other offspring biography and sensitive relative-identity items remain individually deferred or excluded until source and target-referent review.
