"""Transcribe wave/field-specific parent-visit categories without frequencies."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MAPPING = AUDIT / "social_exposure_crosswalk_v1.csv"
CODEBOOK_HEADER = {
    "2011": re.compile(r"•\s*cd002\s+(\d+)\s*:", re.I),
    "2013": re.compile(r"•\s*cd002_(\d+)_\s*:", re.I),
    "2015": re.compile(r"•\s*cd002_(\d+)_\s*:", re.I),
    "2018": re.compile(r"(?:^|\n)\s*cd002_w4_(\d+)_\s*:", re.I),
}
VALUE_LINE = re.compile(r"^\s*(\d+)\s+(.+?)\s*$")
COUNT_TAIL = re.compile(r"\s+[\d,]+\s+[\d.]+\s*$")


def extract_wave_labels(wave: str) -> dict[str, list[tuple[int, str]]]:
    text = (ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt").read_text(
        encoding="utf-8", errors="replace"
    )
    entries = list(CODEBOOK_HEADER[wave].finditer(text))
    out: dict[str, list[tuple[int, str]]] = {}
    for i, match in enumerate(entries):
        slot = match.group(1)
        start = match.end()
        end = entries[i + 1].start() if i + 1 < len(entries) else min(len(text), start + 10000)
        categories: list[tuple[int, str]] = []
        for line in text[start:end].splitlines():
            parsed = VALUE_LINE.match(line)
            if not parsed:
                continue
            code, label = parsed.groups()
            label = COUNT_TAIL.sub("", label).strip()
            # Some extracted rows append page/header debris after the count tail.
            label = re.split(r"\\n|\s+CONTENTS\s+\d+|\s+Page\s+\d+", label)[0].strip()
            if label and label.lower() not in {"no", "%", "freq."}:
                categories.append((int(code), label))
        # Retain first occurrence and discard accidental numeric summary lines.
        unique: dict[int, str] = {}
        for code, label in categories:
            # These frequency items use response codes 1–10. The extracted
            # tables may place N / percent summaries or roster names below
            # the value-label table; never mistake those rows for categories.
            if 1 <= code <= 10 and label and not re.fullmatch(r"[\d,.]+", label):
                unique.setdefault(code, label)
        if unique:
            out[f"cd002_{slot}_" if wave != "2018" else f"cd002_w4_{slot}_"] = sorted(unique.items())
    return out


def main() -> None:
    crosswalk = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    if "value_label_status" not in crosswalk:
        crosswalk["value_label_status"] = ""
    parent = crosswalk[crosswalk["concept_id"].eq("parent_visits")].copy()
    if len(parent) != 33:
        raise SystemExit(f"Expected 33 parent-visit source mappings; found {len(parent)}")
    labels_by_wave = {wave: extract_wave_labels(wave) for wave in ("2011", "2013", "2015", "2018")}
    complete = partial = 0
    for idx, row in parent.iterrows():
        wave, code = str(row["wave"]), str(row["code"]).lower()
        labels = labels_by_wave.get(wave, {}).get(code)
        if not labels:
            raise SystemExit(f"Official Codebook categories not located for {wave}/{code}")
        value_labels = "; ".join(f"{code}={label}" for code, label in labels)
        # A field-level Codebook may omit unobserved categories. Never fill such gaps
        # from another roster slot or wave.
        full = [code for code, _ in labels] == list(range(1, 11))
        coverage = "complete listed 1-10 set" if full else "partial Codebook category set; unlisted categories not inferred"
        if full:
            complete += 1
        else:
            partial += 1
        row["value_labels"] = value_labels
        row["value_label_status"] = (
            f"official wave-specific Codebook response categories transcribed without frequencies; {coverage}; "
            "ordered frequency categories are not equally spaced; preserve parent/spouse route and indexed roster; "
            "special missing and nonresponse semantics remain release-specific"
        )
        row["value_label_source"] = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        row["value_semantics"] = (
            "Ordered parent-contact frequency response. This is not perceived emotional support or a measured "
            "caregiving outcome. Preserve wave-specific kinship definition and the source parent/roster index; "
            "do not treat category scores as equally spaced or infer unlisted categories from other fields."
        )
        row["mapping_status"] = (
            f"official {wave} Codebook value categories located; field-level categories are {coverage}; "
            "candidate only pending release-level special-code, routing, and eligible-denominator QA"
        )
        row["caveat"] = (
            "Parent definitions and source slots differ across waves: 2011 uses parent indices; 2013 includes "
            "father/mother/in-law items; 2015 distinguishes biological, step, and adopted parent slots for the "
            "respondent and spouse; 2018 uses indexed XConParName roster fields. Preserve the original wave and "
            "slot; do not collapse parent types or infer nonresponse from an empty roster slot."
        )
        crosswalk.loc[idx, row.index] = row
        parent.loc[idx, row.index] = row
    crosswalk.to_csv(MAPPING, index=False, encoding="utf-8-sig")

    # The main field catalogue is generated downstream from source crosswalks.
    # When present, carry these labels and their field-specific completeness
    # status into the review table before the site shards are regenerated.
    catalog_path = AUDIT / "charls_atlas_candidate_fields_v0.csv"
    if catalog_path.exists():
        catalog = pd.read_csv(catalog_path, dtype=str, encoding="utf-8-sig").fillna("")
        for row in parent.to_dict("records"):
            selected = (
                catalog["Source.Wave"].astype(str).eq(str(row["wave"]))
                & catalog["Variable.Name"].astype(str).str.lower().eq(str(row["code"]).lower())
            )
            if not selected.any():
                raise SystemExit(f"Parent-visit field missing from candidate catalogue: {row['wave']}/{row['code']}")
            catalog.loc[selected, "Value.Labels"] = row["value_labels"]
            catalog.loc[selected, "Value.Label.Source"] = row["value_label_source"]
            catalog.loc[selected, "Value.Label.Review"] = row["value_label_status"]
            catalog.loc[selected, "Harmonization.Status"] = row["mapping_status"]
        catalog.to_csv(catalog_path, index=False, encoding="utf-8-sig")

    # Downstream review scripts update the master site JSON after the CSV is
    # built. Patch that final source immediately before role shards are made.
    master_site_path = ROOT / "site-prototype" / "dist" / "catalog.json"
    if master_site_path.exists():
        records = json.loads(master_site_path.read_text(encoding="utf-8"))
        for row in parent.to_dict("records"):
            matched = [item for item in records
                       if str(item.get("Source.Wave", "")) == str(row["wave"])
                       and str(item.get("Variable.Name", "")).lower() == str(row["code"]).lower()]
            if not matched:
                raise SystemExit(f"Parent-visit field missing from master site catalog: {row['wave']}/{row['code']}")
            for item in matched:
                item["Value.Labels"] = row["value_labels"]
                item["Value.Label.Source"] = row["value_label_source"]
                item["Value.Label.Review"] = row["value_label_status"]
                item["Harmonization.Status"] = row["mapping_status"]
                item["value_labels"] = row["value_labels"]
                item["value_label_source"] = row["value_label_source"]
                item["value_label_review"] = row["value_label_status"]
                item["harmonization_status"] = row["mapping_status"]
        master_site_path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Keep the focused topic JSON synchronized with the audited source rows.
    site_path = ROOT / "site-prototype" / "dist" / "social_exposures_v1.json"
    topics = json.loads(site_path.read_text(encoding="utf-8"))
    topic = next((item for item in topics if item.get("concept_id") == "parent_visits"), None)
    if topic is None:
        raise SystemExit("parent_visits topic not found in social-exposures JSON")
    source_rows = parent.set_index(["wave", "code"]).to_dict("index")
    for field in topic["source_fields"]:
        item = source_rows.get((str(field.get("wave", "")), str(field.get("code", "")).lower()))
        if item:
            field["value_labels"] = item["value_labels"]
            field["note"] = item["mapping_status"]
            field["value_semantics"] = item["value_semantics"]
            field["value_label_source"] = item["value_label_source"]
    site_path.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"parent visit field labels: {len(parent)}; complete categories={complete}; partial Codebook sets={partial}; candidate catalogue propagated={catalog_path.exists()}; master site catalog propagated={master_site_path.exists()}; no frequencies copied")


if __name__ == "__main__":
    main()
