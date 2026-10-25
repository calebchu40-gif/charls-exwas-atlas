"""Create a row-level coverage ledger for the 2020 CHARLS COVID module.

Reads public official metadata and reviewed E/P crosswalks only. It does not
open respondent records or copy Codebook distributions.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = AUDIT / "raw_variable_catalog_v1.csv"
EXPOSURES = AUDIT / "pandemic_context_exposure_crosswalk_2020_v1.csv"
PHENOTYPES = AUDIT / "pandemic_context_phenotype_crosswalk_2020_v1.csv"
OUTPUT = AUDIT / "covid_module_field_coverage_2020_v1.csv"

EXCLUSIONS = {
    "id": ("join key", "Person identifier; required only for authorized local linkage, not an E/P concept."),
    "householdid": ("join key", "Household linkage key; not an E/P concept and not published as participant data."),
    "communityid": ("join key", "Community linkage key; not an E/P concept and not published as participant data."),
    "vb001_s5": ("exclusive response option", "Exclusive none option belongs to VB001 routing; it is not a separate exposure concept. Preserve its exact code in authorized-release QA."),
    "vb001_s999": ("nonresponse option", "Refusal option belongs to VB001 routing; it is not a separate exposure concept. Preserve its exact code in authorized-release QA."),
    "vb002_s4": ("exclusive response option", "Exclusive none option belongs to the conditional VB002 social-network outcome route; it is not an independent phenotype."),
    "vb002_s999": ("nonresponse option", "Refusal option belongs to the conditional VB002 route; it is not an independent phenotype."),
    "vb005_s6": ("exclusive response option", "No-quarantine response is an exclusive option; the derived XQuarantined indicator and reason-specific fields represent the construct without treating this option as a separate E concept."),
    "vb005_s997": ("nonresponse option", "Do-not-know response is not an exposure construct; preserve as a special response for release-specific coding QA."),
    "vb005_s999": ("nonresponse option", "Refusal response is not an exposure construct; preserve as a special response for release-specific coding QA."),
    "vb009_s997": ("nonresponse option", "Do-not-know response is not a location exposure; preserve as a special response for release-specific coding QA."),
    "vb009_s999": ("nonresponse option", "Refusal response is not a location exposure; preserve as a special response for release-specific coding QA."),
    "vb012_1": ("conditional timing component", "Year of last test is a timing component conditional on testing, not a separate phenotype."),
    "vb012_2": ("conditional timing component", "Month of last test is a timing component conditional on testing, not a separate phenotype."),
    "vd001_s5": ("exclusive response option", "No-restrictions response is an exclusive option, not a separate restriction exposure; preserve it for release-specific route and coding QA."),
    "vd001_s997": ("nonresponse option", "Do-not-know response is not a restriction exposure; preserve as a special response for release-specific coding QA."),
    "vd001_s999": ("nonresponse option", "Refusal response is not a restriction exposure; preserve as a special response for release-specific coding QA."),
    "xvcnotinquarantine": ("questionnaire wording constant", "Embedded text used to define the reference period; not a respondent-level measurement."),
    "xvcoutbreak": ("questionnaire wording constant", "Embedded text defining the outbreak-period wording; not a respondent-level measurement."),
    "xiwmonth": ("interview timing metadata", "Interview month is survey timing metadata; do not treat as pandemic dose or exposure without a separately specified temporal design."),
    "xiwyear": ("interview timing metadata", "Interview year is survey timing metadata; do not treat as pandemic dose or exposure without a separately specified temporal design."),
    "proxy_14": ("interview mode metadata", "Proxy response indicator is a data-quality/interview-mode attribute, not a primary E/P phenotype; retain for future measurement-quality review."),
    "versionid": ("release metadata", "Release/version identifier is administrative metadata, not a participant-level E/P concept."),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    raw = [r for r in read_csv(RAW) if r["wave"] == "2020" and r["module"] == "COVID_Module"]
    role_rows = [("E", r) for r in read_csv(EXPOSURES)] + [("P", r) for r in read_csv(PHENOTYPES)]
    mapped: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for role, row in role_rows:
        mapped.setdefault(row["code"].lower(), []).append((role, row))
    raw_codes = [r["variable"].lower() for r in raw]
    if len(raw_codes) != len(set(raw_codes)):
        raise SystemExit("Duplicate raw field codes in COVID module inventory")
    if set(raw_codes) != set(mapped) | set(EXCLUSIONS):
        missing = sorted(set(raw_codes) - set(mapped) - set(EXCLUSIONS))
        stale = sorted((set(mapped) | set(EXCLUSIONS)) - set(raw_codes))
        raise SystemExit(f"Coverage ledger mismatch; unclassified={missing}; stale={stale}")
    output: list[dict[str, str]] = []
    for field in raw:
        code = field["variable"].lower()
        entries = mapped.get(code, [])
        if entries:
            roles = ";".join(role for role, _ in entries)
            concepts = ";".join(row["concept_id"] for _, row in entries)
            labels = ";".join(row["concept_label"] for _, row in entries)
            status = "mapped candidate"
            kind = "E/P candidate"
            rationale = "Mapped to reviewed candidate metadata; eligibility and harmonization still require authorized-release and survey-design QA."
        else:
            kind, rationale = EXCLUSIONS[code]
            roles = concepts = labels = ""
            status = "reviewed non-E/P field"
        output.append({
            "wave": field["wave"], "module": field["module"], "field": field["variable"],
            "official_label": field["variable_label"], "role": roles, "coverage_status": status,
            "disposition": kind, "candidate_concept_ids": concepts, "candidate_concept_labels": labels,
            "review_rationale": rationale,
            "source_inventory": "audit/raw_variable_catalog_v1.csv",
            "candidate_sources": ";".join(row["source_document"] for _, row in entries),
        })
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(raw)} raw fields; {sum(r['coverage_status']=='mapped candidate' for r in output)} mapped E/P fields; {sum(r['coverage_status']=='reviewed non-E/P field' for r in output)} explicitly reviewed non-E/P fields; no respondent data or frequencies")


if __name__ == "__main__":
    main()
