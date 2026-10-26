"""Build a metadata-only inventory for the 2014 Life History Demographic Backgrounds module."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources_official" / "CHARLS_Life_History_codebook_extracted.txt"
QUESTIONNAIRE = ROOT / "sources_official" / "CHARLS_Life_History_Questionnaire_extracted.txt"
OUTPUT = ROOT / "audit" / "life_history_demographic_backgrounds_inventory_2014_v1.csv"
REPORT = ROOT / "audit" / "life_history_demographic_backgrounds_inventory_review_2026-10-26.md"

FIELD_RE = re.compile(r"\s*[•·]\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*)")
KEYS = {"id", "householdid", "communityid"}


def extract_module_fields() -> list[tuple[str, str]]:
    text = SOURCE.read_text(encoding="utf-8")
    start = text.find("CHARLSCodeBook 2 DEMOGRAPHICBACKGROUNDS")
    end = text.find("CHARLSCodeBook 3 FAMILYINFORMATION", start)
    if start < 0 or end < 0:
        raise ValueError("Could not locate official Codebook DemographicBackgrounds section")
    fields = []
    for line in text[start:end].splitlines():
        match = FIELD_RE.match(line)
        if match:
            fields.append((match.group(1), match.group(2).strip()))
    codes = [code.casefold() for code, _ in fields]
    if len(fields) != 1920 or len(set(codes)) != len(codes):
        raise ValueError(f"Expected 1,920 unique Codebook fields, found {len(fields)}")
    return fields


def questionnaire_section_headings() -> list[str]:
    text = QUESTIONNAIRE.read_text(encoding="utf-8")
    headings = []
    for line in text.splitlines():
        cleaned = line.strip()
        if re.search(r"Section|SECTION", cleaned) and any(
            token in cleaned.casefold()
            for token in ("spouse", "children", "hukou", "demographic")
        ):
            headings.append(cleaned[:180])
    return list(dict.fromkeys(headings))


def main() -> None:
    fields = extract_module_fields()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["module", "code", "official_codebook_label", "initial_disposition", "disposition_note"],
        )
        writer.writeheader()
        for code, label in fields:
            if code.casefold() in KEYS:
                disposition = "excluded_linkage_key"
                note = "Join identifier only; never expose participant or geographic linkage values."
            else:
                disposition = "pending_questionnaire_review"
                note = "Official field identity recorded; questionnaire item, referent, route, sensitivity and candidate role not yet adjudicated."
            writer.writerow(
                {
                    "module": "DEMOGRAPHICBACKGROUNDS",
                    "code": code,
                    "official_codebook_label": label,
                    "initial_disposition": disposition,
                    "disposition_note": note,
                }
            )

    headings = questionnaire_section_headings()
    report = [
        "# 2014 Life History DEMOGRAPHICBACKGROUNDS: official-field inventory checkpoint (2026-10-26)",
        "",
        "## Scope and evidence",
        "",
        "The inventory parser reads only field identifier and field-title lines from the official Life History Codebook's `2 DEMOGRAPHICBACKGROUNDS` section and stops at `3 FAMILYINFORMATION`. It does not copy or parse the Codebook frequency tables, extrema, or respondent values. Questionnaire section headings were inspected to establish the module's broad organization; the questions and routes still require item-by-item review before mapping.",
        "",
        "The official Codebook contains **1,920 unique fields** in this module. The current Life History crosswalk has no `DEMOGRAPHICBACKGROUNDS` rows, so this is a true coverage gap rather than an already mapped module. The generated CSV gives every field a unique initial state: three linkage keys are excluded, and 1,917 substantive/metadata fields remain pending questionnaire-level adjudication. These 1,917 are not 1,917 independent exposures or outcomes.",
        "",
        "## Initial disposition",
        "",
        "| Initial disposition | Fields | Interpretation |",
        "| --- | ---: | --- |",
        "| `pending_questionnaire_review` | 1,917 | Field title alone is insufficient to determine respondent vs relative referent, question route, repeated episode structure, sensitivity, or E/P/C role. |",
        "| `excluded_linkage_key` | 3 | ID, householdID, communityID; join keys excluded from the public concept catalog. |",
        "| **Total** | **1,920** | Exact official Codebook module inventory. |",
        "",
        "## Questionnaire organization observed",
        "",
        "The module covers repeated spouse/partner histories and later family/child and hukou-related material. This is retrospective special-wave content, not another regular CHARLS follow-up wave. Repeated partner/child slots, household/relative referents, preload identity fields, open text, sensitive political/religious/ethnic details, and routing/response-process variables need separate decisions. A codebook label such as `TheYearofBirth` or `TheHighestLevelofEducation` is not enough to infer whose characteristic it represents.",
        "",
        "Questionnaire section headings located by the source extract:",
        "",
    ]
    report.extend(f"- `{heading}`" for heading in headings[:30])
    report.extend(
        [
            "",
            "## Next source-review sequence",
            "",
            "1. Review spouse/partner items against the questionnaire routes and response categories; exclude names and direct identifiers; preserve current/former spouse versus unmarried partner, marriage/cohabitation, event year, residence transition, and hukou transitions as distinct constructs.",
            "2. Review respondent-versus-relative party/ethnicity/religion selections with special privacy and data-minimization handling; do not publish individual-level sensitive responses or frequencies.",
            "3. Continue to children and hukou sections, distinguishing respondent characteristics, child/relative roster descriptors, family context, linkage/preload fields, and questionnaire-process fields.",
            "4. Each batch must update the crosswalk and this inventory through a fail-closed build: every field gets one and only one mapped, deferred, C-only, sensitive exclusion, linkage-key, or source-metadata disposition. Life History remains separate from regular-wave weighted E/P analysis because its release note provides no weight.",
            "",
            "## Reproducibility",
            "",
            "Run `python scripts/build_life_history_demographic_background_inventory.py` to regenerate the inventory and this note from the official extracted Codebook and Questionnaire. Only identifiers and field-title metadata are emitted; Codebook summary statistics and participant data are never read into the output.",
            "",
        ]
    )
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"Fields: {len(fields)}; linkage keys: {len(KEYS)}; pending review: {len(fields) - len(KEYS)}")
    print(f"Inventory: {OUTPUT}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
