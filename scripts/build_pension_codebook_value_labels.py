"""Review pension response labels in wave-specific official CHARLS codebooks."""
from pathlib import Path
import re
import sys
from difflib import SequenceMatcher
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_work_exposure_value_labels import read_codebook  # shared, frequency-free parser

AUDIT = ROOT / "audit"
BOOKS = {
    "2011": ROOT / "sources_official" / "CHARLS_2011_Codebook_extracted.txt",
    "2013": ROOT / "sources_official" / "CHARLS_2013_Codebook_extracted.txt",
    "2015": ROOT / "sources_official" / "CHARLS_2015_Codebook_extracted.txt",
    "2018": ROOT / "sources_official" / "CHARLS_2018_Codebook_extracted.txt",
}


def norm(x):
    return re.sub(r"[^a-z0-9]+", " ", str(x).lower()).strip()


def main():
    fields = pd.read_csv(AUDIT / "pension_exposure_variable_mapping_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    books = {w: read_codebook(p) for w, p in BOOKS.items() if p.exists()}
    rows = []
    for r in fields.itertuples(index=False):
        options = books.get(str(r.wave), {}).get(str(r.code).lower(), [])
        target = norm(r.source_label)
        ranked = sorted(options, key=lambda x: SequenceMatcher(None, target, norm(x[0])).ratio(), reverse=True)
        entry = ranked[0] if ranked else None
        similarity = SequenceMatcher(None, target, norm(entry[0])).ratio() if entry else 0
        if entry is None or similarity < 0.48:
            labels, status, source = "", "official response label not located or title match insufficient", ""
        else:
            labels = "; ".join(f"{value}={label}" for value, label in entry[1])
            source = BOOKS[str(r.wave)].relative_to(ROOT).as_posix()
            if labels and re.search(r"s\d+$", str(r.code), re.I):
                status = "official selected-option label; checkbox slot, unselected is not a negative response"
                labels += " [selected option only; unselected storage is not inferred]"
            elif labels:
                status = "official codebook response labels reviewed; frequencies omitted"
            else:
                status = "official codebook field located; continuous/count or no categorical labels"
        # The 2018 questionnaire explicitly permits -1 for unknown answers on
        # both 4050 insurance subsidy items; preserve this even when the
        # codebook treats the response as continuous and lists no categories.
        if str(r.wave) == "2018" and str(r.code).lower() in {"fn106_w4_1", "fn106_w4_2", "fn107_w4_1", "fn107_w4_2"}:
            labels = (labels + "; " if labels else "") + "-1=Unknown (per questionnaire)"
            status = "2018 questionnaire unknown-response code and scale/unit reviewed; frequencies omitted"
            source = "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt"
        rows.append({"wave": str(r.wave), "code": str(r.code), "concept_id": str(r.concept_id),
                     "source_label": str(r.source_label), "value_labels": labels,
                     "value_label_status": status, "value_label_source": source,
                     "questionnaire_note": str(r.construct)})
    reviewed = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
    # A few extracted Codebook tables leak frequency columns into category text.
    # Replace those with the full questionnaire menus before they reach the atlas.
    bracket_label_status = "official codebook response labels reviewed; only listed categories transcribed; unlisted categories not inferred; frequencies omitted"
    bracket_label_source = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
    repairs = {
        ("2011", "fn064_1"): ("1=Less than 250 yuan; 2=About 250 yuan; 3=More than 250 yuan", bracket_label_status),
        ("2011", "fn064_2"): ("1=Less than 500 yuan; 2=About 500 yuan; 3=More than 500 yuan", bracket_label_status),
        ("2011", "fn064_3"): ("1=Less than 1,000 yuan; 2=About 1,000 yuan; 3=More than 1,000 yuan", bracket_label_status),
        ("2011", "fn064_4"): ("1=Less than 2,000 yuan", bracket_label_status),
        ("2011", "fn070_1"): ("2=About 250 yuan", bracket_label_status),
        ("2011", "fn070_2"): ("1=Less than 500 yuan; 3=More than 500 yuan", bracket_label_status),
        ("2011", "fn070_3"): ("1=Less than 1,000 yuan; 3=More than 1,000 yuan", bracket_label_status),
        ("2011", "fn070_4"): ("1=Less than 2,000 yuan; 3=More than 2,000 yuan", bracket_label_status),
        ("2015", "fn057_w3_6_3_"): ("1=No Money; 2=Not Satisfaction of Pension; 3=Not Helpful to Life; 4=Inconvenience of Application or Payment; 5=Unreasonably Designed Payment; 6=No Local Hukou; 7=Already Have Other Pension; 8=Others", "official codebook response labels reviewed; frequency columns removed after questionnaire identity check"),
        ("2015", "fn076_w3_2_s1"): ("1=Myself [selected option only; unselected storage is not inferred]", "official codebook response labels reviewed; selected-option frequency columns removed; checkbox slot"),
        ("2015", "fn047_w2"): ("1=Annual Payment; 2=Lump-sum Amount", "official codebook response labels reviewed; frequency columns removed after questionnaire identity check"),
    }
    for idx, r in reviewed.iterrows():
        key = (str(r["wave"]), str(r["code"]).lower())
        if key in repairs:
            reviewed.at[idx, "value_labels"] = repairs[key][0]
            reviewed.at[idx, "value_label_status"] = repairs[key][1]
            reviewed.at[idx, "value_label_source"] = (bracket_label_source if key[0] == "2011" else "sources_official/CHARLS_2015_Codebook_extracted.txt; sources_official/CHARLS_2015_Questionnaire_extracted.txt")
    reviewed.to_csv(AUDIT / "pension_codebook_value_labels_v1.csv", index=False, encoding="utf-8-sig")

    label_by_key = {}
    for r in reviewed.itertuples(index=False):
        if r.value_labels:
            label_by_key[(str(r.wave), str(r.code).lower())] = r
    fields["value_labels"] = [getattr(label_by_key.get((str(r.wave), str(r.code).lower())), "value_labels", "") for r in fields.itertuples(index=False)]
    fields["value_label_status"] = [getattr(label_by_key.get((str(r.wave), str(r.code).lower())), "value_label_status", "official response label not located; review required") for r in fields.itertuples(index=False)]
    fields["value_label_source"] = [getattr(label_by_key.get((str(r.wave), str(r.code).lower())), "value_label_source", "") for r in fields.itertuples(index=False)]
    fields.to_csv(AUDIT / "pension_exposure_variable_mapping_v1.csv", index=False, encoding="utf-8-sig")

    # Preserve existing manually reviewed rows; append only new, positively
    # matched official labels. Conflicts are retained in the audit file for review.
    path = AUDIT / "pension_value_label_review_v1.csv"
    existing = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    existing_keys = set(zip(existing.wave.astype(str), existing.code.str.lower()))
    append = reviewed[(reviewed.value_labels.ne("")) &
                      (~reviewed.apply(lambda x: (str(x.wave), str(x.code).lower()) in existing_keys, axis=1))].copy()
    append = append[["wave", "code", "value_labels", "value_label_status", "value_label_source", "questionnaire_note"]]
    merged = pd.concat([existing, append], ignore_index=True).drop_duplicates(["wave", "code"], keep="first")
    selection_keys = set(zip(
        reviewed.loc[reviewed.value_label_status.str.contains("checkbox slot", na=False), "wave"].astype(str),
        reviewed.loc[reviewed.value_label_status.str.contains("checkbox slot", na=False), "code"].str.lower(),
    ))
    for idx, row in merged.iterrows():
        key = (str(row["wave"]), str(row["code"]).lower())
        if key in selection_keys and "selected option only" not in row["value_labels"]:
            merged.at[idx, "value_labels"] = row["value_labels"].rstrip() + " [selected option only; unselected storage is not inferred]"
    for idx, row in merged.iterrows():
        key = (str(row["wave"]), str(row["code"]).lower())
        if key in repairs:
            merged.at[idx, "value_labels"] = repairs[key][0]
            merged.at[idx, "value_label_status"] = repairs[key][1]
            merged.at[idx, "value_label_source"] = (bracket_label_source if key[0] == "2011" else "sources_official/CHARLS_2015_Codebook_extracted.txt; sources_official/CHARLS_2015_Questionnaire_extracted.txt")
    merged.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"pension value-label mappings={len(reviewed)}; with extracted categories={reviewed.value_labels.ne('').sum()}; newly appended to atlas labels={len(append)}")


if __name__ == "__main__":
    main()
