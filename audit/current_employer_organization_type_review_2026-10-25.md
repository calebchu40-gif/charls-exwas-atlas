# Current employer organization type review — 2026-10-25

Reviewed the current employer/work-unit type item in all five available wave packages: `FD002` in 2011–2018 and `FC002` in 2020. The response menu describes government, public institutions, NGOs, firms, individual firms, farmers, individual households and other employers; 2020 additionally lists `997` for “Do not know.” Retain these as nominal categories with wave-specific wording. Do not calculate an ordinal score or treat this as a direct environmental exposure.

The surrounding work module contains interviewer routing and re-interview carry-forward logic. A missing detail can reflect a structural skip or a previously recorded same employer; it is not “no employer.” Confirm released-field storage, current-worker eligibility, carried-forward values and person linkage before analysis. No respondent values or Codebook frequencies were used.

Reproduce the official-text checks and metadata synchronization with `python scripts/apply_employer_organization_type_review.py`.
