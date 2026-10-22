from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "audit" / "ep_concept_source_crosswalk_v1.csv"
OUTPUT = ROOT / "site-prototype" / "dist" / "candidate_pair_explorer_v1.json"
WAVES = ("2011", "2013", "2015", "2018", "2020")

groups: dict[tuple[str, str], dict] = {}
with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        roles = {part.strip().lower() for part in row.get("Role", "").split(",")}
        if not roles.intersection({"e", "p"}):
            continue
        wave = row.get("Wave", "").strip()
        if wave not in WAVES:
            continue
        key = (row.get("Concept.ID", "").strip(), wave)
        if not key[0]:
            continue
        item = groups.setdefault(key, {
            "concept_id": key[0], "label": row.get("Concept.Label", "").strip(),
            "domain": row.get("Domain", "").strip(), "wave": wave,
            "roles": set(), "source_fields": {},
        })
        item["roles"].update(roles.intersection({"e", "p"}))
        field = {
            "code": row.get("Source.Code", "").strip(),
            "label": row.get("Source.Label", "").strip(),
            "module": row.get("Module", "").strip(),
            "unit": row.get("Unit", "").strip(),
            "value_labels": row.get("Value.Labels", "").strip(),
            "value_semantics": row.get("Value.Semantics", "").strip(),
            "mapping_status": row.get("Mapping.Status", "").strip(),
            "caveat": row.get("Caveat", "").strip(),
        }
        field_key = (field["code"], field["module"], field["label"])
        item["source_fields"][field_key] = field

by_wave = {}
for wave in WAVES:
    concepts = []
    for item in groups.values():
        if item["wave"] != wave:
            continue
        concepts.append({
            "concept_id": item["concept_id"], "label": item["label"], "domain": item["domain"],
            "roles": sorted(item["roles"]),
            "source_fields": sorted(item["source_fields"].values(), key=lambda f: (f["code"], f["module"], f["label"])),
        })
    concepts.sort(key=lambda x: (x["label"].casefold(), x["concept_id"]))
    exposure_ids = {x["concept_id"] for x in concepts if "e" in x["roles"]}
    phenotype_ids = {x["concept_id"] for x in concepts if "p" in x["roles"]}
    candidate_pairs = len(exposure_ids) * len(phenotype_ids) - len(exposure_ids & phenotype_ids)
    by_wave[wave] = {
        "exposure_count": len(exposure_ids), "phenotype_count": len(phenotype_ids),
        "candidate_pair_count": candidate_pairs,
        "exposures": [x for x in concepts if "e" in x["roles"]],
        "phenotypes": [x for x in concepts if "p" in x["roles"]],
    }

OUTPUT.write_text(json.dumps({
    "status": "metadata_candidate_pairs_only",
    "wave_order": list(WAVES),
    "waves": by_wave,
    "limitations": [
        "Counts are distinct concept combinations present in the wave-level source crosswalk, not people, eligible samples, complete-case pairs, or fitted associations.",
        "Source fields, route, survey eligibility, weights, variance design, value storage, missingness, and analysis readiness require separate review.",
        "No CHARLS respondent-level data or association estimates are included.",
    ],
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {OUTPUT}; " + ", ".join(f"{w}: {d['exposure_count']} E × {d['phenotype_count']} P, {d['candidate_pair_count']} distinct non-self metadata pairs" for w, d in by_wave.items()))
