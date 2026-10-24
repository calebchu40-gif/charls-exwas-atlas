"""Keep Wave-3 marriage-date fields as C metadata pending release QA.

The 2015 questionnaire defines a routed item, but its public Codebook lists
No Observations for both components. Do not infer that the authorized release
contains no values, and do not publish a Wave-3 exposure mapping from that
Codebook summary alone.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUTPUT = AUDIT / "marriage_date_2015_no_observation_review_v1.csv"
TARGETS = ("be009_1", "be009_2")
Q = "sources_official/CHARLS_2015_Questionnaire_extracted.txt"
CB = "sources_official/CHARLS_2015_Codebook_extracted.txt"
STATUS = "official questionnaire route reviewed; 2015 Codebook lists No Observations; authorized-release availability not verified"
NOTE = (
    "The 2015 questionnaire asks BE009 only when BE003_W2_1 > 0, but the public 2015 Codebook lists No Observations for this field. "
    "Keep as source-availability metadata pending authorized-release QA; do not assume the released data contain no values, do not infer categories, "
    "and do not include a 2015 exposure mapping until the official release is checked."
)


def validate_sources() -> None:
    qtext = (ROOT / Q).read_text(encoding="utf-8", errors="replace").replace("\x00", "").lower()
    cbtext = (ROOT / CB).read_text(encoding="utf-8", errors="replace").replace("\x00", "").lower()
    if "if be003_w2_1 > 0, ask be009" not in qtext:
        raise SystemExit("2015 questionnaire route for BE009 was not confirmed")
    for code in TARGETS:
        if code not in qtext or code not in cbtext:
            raise SystemExit(f"2015 official sources do not contain {code}")
        start = cbtext.find(code)
        if "no observations" not in cbtext[start:start + 160]:
            raise SystemExit(f"2015 Codebook does not state No Observations for {code}")


def propagate() -> None:
    validate_sources()
    entries = []
    catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
    for code in TARGETS:
        matches = [r for r in catalog if r.get("Source.Wave") == "2015" and r.get("Variable.Name", "").lower() == code and r.get("Data.File.Name") == "Demographic_Background" and r.get("epcf", "").lower() == "c"]
        if len(matches) != 1:
            raise SystemExit(f"Expected one 2015 C record for {code}; found {len(matches)}")
        entries.append({"wave": "2015", "code": code, "module": "Demographic_Background", "official_sources": f"{Q}; {CB}", "review_status": STATUS, "review_note": NOTE})
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists():
            continue
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            count = 0
            for item in entries:
                mask = df["Source.Wave"].eq(item["wave"]) & df["Variable.Name"].str.lower().eq(item["code"]) & df["Data.File.Name"].eq(item["module"]) & df["epcf"].str.lower().eq("c")
                if mask.any():
                    df.loc[mask, "category"] = "measurement metadata"
                    df.loc[mask, "subcategory"] = "marriage-history source availability and route metadata"
                    df.loc[mask, "Candidate.Status"] = STATUS
                    df.loc[mask, "Harmonization.Status"] = NOTE
                    df.loc[mask, "Review.Flag"] = "C metadata only; exclude from E/P association mapping until authorized-release source QA"
                    df.loc[mask, "Value.Labels"] = ""
                    df.loc[mask, "Value.Label.Source"] = item["official_sources"]
                    df.loc[mask, "Value.Label.Review"] = item["review_status"]
                    count += int(mask.sum())
            if count != 2: raise SystemExit(f"Expected 2 C rows in {rel}; updated {count}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8")); count = 0
            for row in data:
                for item in entries:
                    key = row.get("Source.Wave") == item["wave"] and row.get("Variable.Name", "").lower() == item["code"] and row.get("Data.File.Name") == item["module"] and row.get("epcf", "").lower() == "c"
                    if key:
                        row.update({"category": "measurement metadata", "subcategory": "marriage-history source availability and route metadata", "Candidate.Status": STATUS, "Harmonization.Status": NOTE, "Review.Flag": "C metadata only; exclude from E/P association mapping until authorized-release source QA", "Value.Labels": "", "Value.Label.Source": item["official_sources"], "Value.Label.Review": item["review_status"]})
                        count += 1
            if count != 2: raise SystemExit(f"Expected 2 C rows in {rel}; updated {count}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(entries[0])); writer.writeheader(); writer.writerows(entries)
    print("Reviewed 2 Wave-3 marriage-date C rows; retained route and Codebook No Observations caveat, no E mapping inferred.")


if __name__ == "__main__":
    propagate()
