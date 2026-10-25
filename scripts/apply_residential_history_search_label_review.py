"""Replace stale keyword-only labels on already source-reviewed C metadata rows."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TARGETS: dict[tuple[str, str], tuple[str, str]] = {
    ("2011", "ba004"): ("demographic background metadata", "respondent age field; source definition and derivation context"),
    ("2013", "ba004"): ("demographic background metadata", "respondent age field; source definition and derivation context"),
    ("2011", "bb007"): ("residential history metadata", "ever lived outside permanent county/city for over six months; wave-specific branch"),
    ("2013", "bb007"): ("residential history metadata", "ever lived outside permanent county/city/district for over six months; wave-specific branch"),
    ("2011", "bb008_1"): ("residential history metadata", "cumulative years outside permanent county/city after BB007 yes; keep separate from months"),
    ("2011", "bb008_2"): ("residential history metadata", "cumulative months outside permanent county/city after BB007 yes; keep separate from years"),
    ("2013", "bb008_1"): ("residential history metadata", "cumulative years outside permanent county/city after BB007 yes; keep separate from months"),
    ("2013", "bb008_2"): ("residential history metadata", "cumulative months outside permanent county/city after BB007 yes; keep separate from years"),
    ("2011", "bb009"): ("residential history metadata", "ever lived outside permanent county/city for over six months; alternate BB001 branch"),
    ("2013", "bb009"): ("residential history metadata", "ever lived outside permanent county/city/district for over six months; alternate BB001 branch"),
    ("2011", "bb010_1"): ("residential history metadata", "cumulative years outside permanent area after BB009 yes; keep separate from months"),
    ("2011", "bb010_2"): ("residential history metadata", "cumulative months outside permanent area after BB009 yes; keep separate from years"),
    ("2013", "bb010_1"): ("residential history metadata", "cumulative years outside permanent area after BB009 yes; keep separate from months"),
    ("2013", "bb010_2"): ("residential history metadata", "cumulative months outside permanent area after BB009 yes; keep separate from years"),
    ("2013", "bb003"): ("residential history metadata", "calendar year first lived in permanent county/city/district; distinct from village entry"),
    ("2015", "bb003"): ("residential history metadata", "calendar year first lived in permanent county/city/district; distinct from village entry"),
    ("2013", "bb005"): ("residential history metadata", "calendar year first lived in village/community; distinct from county entry"),
    ("2015", "bb005"): ("residential history metadata", "calendar year first lived in village/community; distinct from county entry"),
}
GENERIC = "keyword discovery only; not a reviewed covariate or adjustment recommendation"
SERIES_TARGETS: dict[str, tuple[str, str]] = {
    "ba004": ("demographic background metadata", "respondent age field; wave-specific source definition and derivation context"),
    "bb003": ("residential history metadata", "year of first residence in county/city/district; wave-specific source and route"),
    "bb005": ("residential history metadata", "year of first residence in village/community; distinct from county entry"),
    "bb007": ("residential history metadata", "prior residence outside permanent area; branch-specific yes/no item"),
    "bb008_1": ("residential history metadata", "duration outside permanent area in years after BB007 route; retain month component"),
    "bb008_2": ("residential history metadata", "duration outside permanent area in months after BB007 route; retain year component"),
    "bb009": ("residential history metadata", "alternate-branch prior residence outside permanent area; yes/no item"),
    "bb010_1": ("residential history metadata", "duration outside permanent area in years after BB009 route; retain month component"),
    "bb010_2": ("residential history metadata", "duration outside permanent area in months after BB009 route; retain year component"),
}


def update_row(row: dict[str, object]) -> bool:
    if str(row.get("epcf", "")).casefold() != "c":
        return False
    key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).casefold())
    if key not in TARGETS:
        return False
    source = str(row.get("Value.Label.Source", "") or row.get("value_label_source", ""))
    status = str(row.get("Candidate.Status", ""))
    if "Questionnaire" not in source or "Codebook" not in source or not status or status.startswith("automated keyword discovery only"):
        raise SystemExit(f"Refusing to relabel source-unverified C row {key}: source/status gate failed")
    category, subcategory = TARGETS[key]
    row["category"] = category
    row["subcategory"] = subcategory
    return True


def apply() -> None:
    expected = set(TARGETS)
    for rel in (
        "audit/charls_atlas_candidate_fields_v0.csv",
        "audit/charls_atlas_candidate_fields_v0.json",
        "site-prototype/dist/catalog.json",
        "site-prototype/dist/catalog_c.json",
    ):
        path = ROOT / rel
        if not path.is_file():
            continue
        if path.suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            accepted_subcategories = {GENERIC, *(sub for _, sub in TARGETS.values())}
            mask = frame["epcf"].str.casefold().eq("c") & frame["subcategory"].isin(accepted_subcategories) & frame["Source.Wave"].astype(str).isin({w for w, _ in expected})
            mask &= frame["Variable.Name"].str.casefold().isin({code for _, code in expected})
            selected = frame.loc[mask]
            found = {(str(r["Source.Wave"]), str(r["Variable.Name"]).casefold()) for r in selected.to_dict("records")}
            if found != expected or len(selected) != len(expected):
                raise SystemExit(f"Expected exactly {len(expected)} residential-history C rows in {rel}; found {len(selected)} keys={found}")
            for idx in selected.index:
                record = frame.loc[idx].to_dict()
                key = (str(record["Source.Wave"]), str(record["Variable.Name"]).casefold())
                wanted = TARGETS[key]
                if (record.get("category"), record.get("subcategory")) not in {
                    ("automated covariate search hit", GENERIC), wanted
                }:
                    raise SystemExit(f"Unexpected category/subcategory on {rel} row {key}")
                update_row(record)
                for column in ("category", "subcategory"):
                    frame.at[idx, column] = record[column]
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            rows = json.loads(path.read_text(encoding="utf-8"))
            accepted_subcategories = {GENERIC, *(sub for _, sub in TARGETS.values())}
            selected = [r for r in rows if str(r.get("epcf", "")).casefold() == "c" and r.get("subcategory") in accepted_subcategories and
                        (str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).casefold()) in expected]
            found = {(str(r.get("Source.Wave", "")), str(r.get("Variable.Name", "")).casefold()) for r in selected}
            if found != expected or len(selected) != len(expected):
                raise SystemExit(f"Expected exactly {len(expected)} residential-history C rows in {rel}; found {len(selected)} keys={found}")
            for row in selected:
                key = (str(row["Source.Wave"]), str(row["Variable.Name"]).casefold())
                wanted = TARGETS[key]
                if (row.get("category"), row.get("subcategory")) not in {
                    ("automated covariate search hit", GENERIC), wanted
                }:
                    raise SystemExit(f"Unexpected category/subcategory on {rel} row {key}")
                update_row(row)
            path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    series_expected = set(SERIES_TARGETS)
    for rel in ("audit/charls_atlas_candidate_series_v0.csv", "audit/charls_atlas_candidate_series_v0.json"):
        path = ROOT / rel
        if not path.is_file():
            continue
        if path.suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            accepted_subcategories = {GENERIC, *(sub for _, sub in SERIES_TARGETS.values())}
            mask = frame["epcf"].str.casefold().eq("c") & frame["subcategory"].isin(accepted_subcategories) & frame["Variable.Name"].str.casefold().isin(series_expected)
            selected = frame.loc[mask]
            found = set(selected["Variable.Name"].str.casefold())
            if found != series_expected or len(selected) != len(series_expected):
                raise SystemExit(f"Expected exactly {len(series_expected)} reviewed residential-history C series in {rel}; found {len(selected)}")
            for idx in selected.index:
                source = str(frame.at[idx, "value_label_source"] or "")
                code = str(frame.at[idx, "Variable.Name"]).casefold()
                wanted = SERIES_TARGETS[code]
                if "Questionnaire" not in source or "Codebook" not in source or frame.at[idx, "subcategory"] not in {GENERIC, wanted[1]}:
                    raise SystemExit(f"Refusing to relabel unverified or already-updated C series {frame.at[idx, 'Variable.Name']}")
                category, subcategory = SERIES_TARGETS[str(frame.at[idx, "Variable.Name"]).casefold()]
                frame.at[idx, "category"] = category
                frame.at[idx, "subcategory"] = subcategory
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            rows = json.loads(path.read_text(encoding="utf-8"))
            accepted_subcategories = {GENERIC, *(sub for _, sub in SERIES_TARGETS.values())}
            selected = [r for r in rows if str(r.get("epcf", "")).casefold() == "c" and r.get("subcategory") in accepted_subcategories and
                        str(r.get("Variable.Name", "")).casefold() in series_expected]
            found = {str(r.get("Variable.Name", "")).casefold() for r in selected}
            if found != series_expected or len(selected) != len(series_expected):
                raise SystemExit(f"Expected exactly {len(series_expected)} reviewed residential-history C series in {rel}; found {len(selected)}")
            for row in selected:
                source = str(row.get("value_label_source", ""))
                code = str(row["Variable.Name"]).casefold()
                wanted = SERIES_TARGETS[code]
                if "Questionnaire" not in source or "Codebook" not in source or row.get("subcategory") not in {GENERIC, wanted[1]}:
                    raise SystemExit(f"Refusing to relabel unverified or already-updated C series {row.get('Variable.Name')}")
                row["category"], row["subcategory"] = SERIES_TARGETS[str(row["Variable.Name"]).casefold()]
            path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Replaced stale generic search labels on {len(TARGETS)} already source-reviewed residential-history/age C rows; no analysis role inferred.")


if __name__ == "__main__":
    apply()
