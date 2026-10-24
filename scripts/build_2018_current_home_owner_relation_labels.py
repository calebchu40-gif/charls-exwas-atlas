"""Review 2018 current-home owner-relation labels without copying frequencies."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "sources_official/CHARLS_2018_Codebook_extracted.txt"
LABEL_PATTERN = re.compile(r"(?m)^\s*(\d+)\s+(Do Not Own|Own)\s*$")
REVIEW_STATUS = "official Codebook listed ownership labels transcribed; frequencies omitted; unlisted categories not inferred"


def build_rows(mapping: pd.DataFrame, codebook: str) -> list[dict[str, str]]:
    rows = mapping.loc[
        mapping["wave"].astype(str).eq("2018")
        & mapping["concept_id"].eq("current_home_owner_relation"), ["wave", "code"]
    ].drop_duplicates()
    if len(rows) != 9:
        raise ValueError(f"Expected nine mapped 2018 owner-relation fields; found {len(rows)}")
    headers = list(re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9_]*):[^\n]*", codebook))
    block_by_code: dict[str, str] = {}
    for index, match in enumerate(headers):
        code = match.group(1).casefold()
        stop = headers[index + 1].start() if index + 1 < len(headers) else len(codebook)
        block_by_code[code] = codebook[match.end():stop]

    output = []
    for item in rows.itertuples(index=False):
        code = str(item.code)
        block = block_by_code.get(code.casefold())
        if block is None:
            raise ValueError(f"Official Codebook block not found for {code}")
        labels = {value: label for value, label in LABEL_PATTERN.findall(block)}
        label_text = "; ".join(f"{value}={labels[value]}" for value in sorted(labels, key=int))
        output.append({
            "wave": "2018", "code": code,
            "value_labels": label_text,
            "value_label_status": REVIEW_STATUS,
            "value_label_source": SOURCE,
        })
    if len(output) != 9 or any(not row["value_labels"] for row in output):
        raise ValueError("Expected listed Codebook categories for all nine fields")
    expected = {f"i000_w4_4_s{index}": f"0=Do Not Own; {index}=Own" for index in range(1, 10)}
    if {row["code"].lower(): row["value_labels"] for row in output} != expected:
        raise ValueError("Unexpected current-home relation codes; review the official source blocks before writing")
    return output


def main() -> None:
    mapping = pd.read_csv(ROOT / "audit/housing_exposure_variable_mapping_v1.csv", dtype=str,
                          encoding="utf-8-sig").fillna("")
    source = (ROOT / SOURCE).read_text(encoding="utf-8", errors="ignore")
    output = pd.DataFrame(build_rows(mapping, source))
    output.to_csv(ROOT / "audit/housing_current_owner_relation_labels_2018_v1.csv",
                  index=False, encoding="utf-8-sig")
    labeled = int(output["value_labels"].ne("").sum())
    print(f"2018 current-home owner relation fields={len(output)}; fields with listed labels={labeled}; frequencies omitted; unlisted categories not inferred")


if __name__ == "__main__":
    main()
