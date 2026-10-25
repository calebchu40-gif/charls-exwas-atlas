"""Extract 2011 community-item answer labels without frequency summaries."""
from pathlib import Path
import json
import re
import unicodedata
from difflib import SequenceMatcher
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
BOOK = AUDIT / "CHARLS_2011_Codebook_extracted.txt"
HEADING = re.compile(r"^\s*[•●]\s*(.*?)\s*:\s*(.*?)\s*$", re.M)
VALUE = re.compile(r"^\s*(\d+)\s+(.+?)\s*$")
FREQUENCY_TAIL = re.compile(r"\s+[\d,]+\s+[\d.]+%?\s*$")


def norm_code(x):
    return "".join(re.findall(r"[a-z0-9]+", str(x).lower()))


def main():
    text = BOOK.read_text(encoding="utf-8", errors="replace")
    hits = list(HEADING.finditer(text))
    book = {}
    for i, h in enumerate(hits):
        prefix = h.group(1).strip()
        code = norm_code(prefix)
        if not code.startswith(("ja", "jb", "jc", "jf", "jg", "jh", "ji", "jj", "jk")):
            continue
        block = text[h.end():hits[i + 1].start() if i + 1 < len(hits) else len(text)]
        vals = []
        for line in block.splitlines():
            m = VALUE.match(line)
            if not m:
                continue
            label = unicodedata.normalize("NFKC", FREQUENCY_TAIL.sub("", m.group(2).strip()).strip())
            label = re.sub(r"\s+", " ", label)
            if label and label[0].isalpha() and label.lower() not in {"total", "obs"}:
                vals.append((m.group(1), label))
        book.setdefault(code, []).append((h.group(2).strip(), vals))

    fields = pd.read_csv(AUDIT / "community_exposure_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    rows = []
    for r in fields.itertuples(index=False):
        entries = book.get(norm_code(r.code), [])
        target = re.sub(r"[^a-z0-9]+", " ", r.source_label.lower()).strip()
        ranked = sorted(entries, key=lambda x: SequenceMatcher(None, target, re.sub(r"[^a-z0-9]+", " ", x[0].lower()).strip()).ratio(), reverse=True)
        entry = ranked[0] if ranked else None
        score = SequenceMatcher(None, target, re.sub(r"[^a-z0-9]+", " ", entry[0].lower()).strip()).ratio() if entry else 0
        labels = "; ".join(f"{v}={label}" for v, label in entry[1]) if entry and score >= 0.48 else ""
        if str(r.code).lower().startswith(("jf012_", "jf015_")):
            # The questionnaire explicitly asks for year-indexed household
            # participation counts. These are numeric measures, not answer
            # categories; retain each source year and omit Codebook summaries.
            labels = ""
            status = "official questionnaire identifies a continuous household count; year-indexed source item retained; no categorical answer labels; frequencies omitted"
            source = "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt"
        elif labels:
            status = "official codebook response labels; frequencies omitted"
            source = "sources_official/CHARLS_2011_Codebook_extracted.txt"
        elif entry and score >= 0.48:
            status = "official codebook field located; continuous/count response, no category labels"
            source = "sources_official/CHARLS_2011_Codebook_extracted.txt"
        else:
            status = "official category labels not located or field-title match insufficient"
            source = ""
        rows.append({"wave": r.wave, "code": r.code, "concept_id": r.concept_id,
                     "source_label": r.source_label, "value_labels": labels,
                     "value_label_status": status, "value_label_source": source})
    out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
    override_path = AUDIT / "community_questionnaire_label_overrides_v1.csv"
    if override_path.exists():
        overrides = pd.read_csv(override_path, dtype=str, encoding="utf-8-sig").fillna("")
        for item in overrides.itertuples(index=False):
            selected = out["wave"].eq(str(item.wave)) & out["code"].str.lower().eq(str(item.code).lower())
            out.loc[selected, "value_labels"] = item.value_labels
            out.loc[selected, "value_label_status"] = item.value_label_status
            out.loc[selected, "value_label_source"] = item.value_label_source
    out.to_csv(AUDIT / "community_exposure_value_labels_v1.csv", index=False, encoding="utf-8-sig")
    path = ROOT / "site-prototype" / "dist" / "community_exposures_v1.json"
    items = json.loads(path.read_text(encoding="utf-8"))
    lookup = {(r.wave, r.code, r.concept_id): r for r in out.itertuples(index=False)}
    for concept in items:
        for field in concept["source_fields"]:
            r = lookup[(field["wave"], field["code"], concept["concept_id"])]
            field.update(value_labels=r.value_labels, value_label_status=r.value_label_status, value_label_source=r.value_label_source)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"community value-label mappings={len(out)}; with category labels={out.value_labels.ne('').sum()}")


if __name__ == "__main__":
    main()
