"""Build wave-specific reviewed response labels for common dwelling fields."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
raw = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

rows = []
# Wave-specific response categories for building and dwelling context. The
# source strings below intentionally contain category labels only: Codebook
# frequency and percentage columns describe the released sample and must not
# be presented as atlas data or used as analysis denominators.
HOUSING_CATEGORIES = {
    "2011": {
        "i004": "1=Concrete and steel; 2=Bricks and wood; 3=Mixed structure; 4=Wood, bamboo, grass; 5=Woolen felt; 6=Sheet iron; 7=Cave dwelling; 8=Tent; 9=Adobe; 10=Other",
        "i005_1": "1=0-5 years; 2=5-10 years; 3=10-20 years; 4=20-30 years; 5=30-40 years; 6=Above 40 years",
        "i006": "1=One-story building; 2=Multi-story building",
        "i007": "1=Independent story; 2=Compound",
        "i009": "1=Yes; 2=No",
        "i010": "1=Yes; 2=No",
        "i011": "1=1-5 steps; 2=6-15 steps; 3=16-25 steps; 4=More than 25 steps",
        "i023": "1=Yes; 2=No",
        "i024": "1=Yes; 2=No",
        "i003": "1=Yes; 2=No",
        "i025": "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor",
        "i026": "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold",
        "i021": "1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied petroleum gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        "i015": "1=Yes; 2=No",
        "i016": "1=Yes; 2=No",
        "i017": "1=Yes; 2=No",
        "i018": "1=Hot water provided; 2=Water heater installed by the household; 3=No",
        "i019": "1=Yes; 2=No",
        "i020": "1=Yes; 2=No",
    },
    "2013": {
        # Code 8 is not listed in the official 2013 Codebook category table;
        # do not carry the 2011 Tent category forward by assumption.
        "i004": "1=Concrete and steel; 2=Bricks and wood; 3=Mixed structure; 4=Wood, bamboo, grass; 5=Woolen felt; 6=Sheet iron; 7=Cave dwelling; 9=Adobe; 10=Other",
        "i005_1": "1=0-5 years; 2=5-10 years; 3=10-20 years; 4=20-30 years; 5=30-40 years; 6=Above 40 years",
        "i006": "1=One-story building; 2=Multi-story building",
        "i007": "1=Independent story; 2=Compound",
        "i009": "1=Yes; 2=No",
        "i010": "1=Yes; 2=No",
        "i011": "1=1-5 steps; 2=6-15 steps; 3=16-25 steps; 4=More than 25 steps",
        "i023": "1=Yes; 2=No",
        "i024": "1=Yes; 2=No",
        "i003": "1=Yes; 2=No",
        "i025": "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
        "i026": "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
        "i021": "1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied petroleum gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        "i015": "1=Yes; 2=No",
        "i016": "1=Yes; 2=No",
        "i017": "1=Yes; 2=No",
        "i018": "1=Hot water provided; 2=Water heater installed by the household; 3=No",
        "i019": "1=Yes; 2=No",
        "i020": "1=Yes; 2=No",
    },
    "2015": {
        "i004": "1=Concrete and steel/Bricks and wood; 2=Adobe; 3=Wood/Thatched; 4=Cave dwelling; 5=Mongolian yurt/Woolen felt/Tend (Codebook spelling); 6=Stone; 7=Other",
        "i005_1": "1=0-5 years; 2=5-10 years; 3=10-20 years; 4=20-30 years; 5=30-40 years; 6=Above 40 years",
        "i006": "1=One-story building; 2=Common multi-story building; 3=Self-contained multi-story building",
        "i007": "1=Independent; 2=Compound",
        "i009": "1=Yes; 2=No",
        "i010": "1=Yes; 2=No",
        "i011": "1=0 steps; 2=1-5 steps; 3=6-15 steps; 4=16-25 steps; 5=More than 25 steps",
        "i023": "1=Yes; 2=No",
        "i024": "1=Yes; 2=No",
        "i027_w3": "1=Yes; 2=No",
        "i003": "1=Yes; 2=No",
        "i025": "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
        "i026": "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
        "i021": "1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied petroleum gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        "i020": "1=Yes; 2=No",
        "i015": "1=Yes; 2=No",
        "i017": "1=Yes; 2=No",
        "i018": "1=Hot water provided; 2=Water heater installed by the household; 3=No",
        "i019": "1=Yes; 2=No",
    },
    "2018": {
        "i004": "1=Concrete and steel/Bricks and wood; 2=Adobe; 3=Wood/Thatched; 4=Cave dwelling; 5=Mongolian yurt/Woolen felt/Tent; 6=Stone; 7=Other",
        "i005_1": "1=0-5 years; 2=5-10 years; 3=10-20 years; 4=20-30 years; 5=30-40 years; 6=More than 40 years",
        "i006": "1=One-story building; 2=Common multi-story building; 3=Self-contained multi-story building",
        "i007": "1=Independent storey; 2=Compound",
        "i009": "1=Yes; 2=No",
        "i010_w4": "1=Yes; 2=No; 3=Do not need",
        "i011": "1=0 step; 2=1-5 steps; 3=6-15 steps; 4=16-25 steps; 5=More than 25 steps",
        "i023": "1=Yes; 2=No",
        "i024": "1=Yes; 2=No",
        "i027_w3": "1=Yes; 2=No",
        "i003": "1=Yes; 2=No",
        "i000_w4_2": "1=City/Town central area; 2=Rural-urban fringe; 3=Rural; 4=Special zone",
        "i000_w4_3": "1=Unit building; 2=Detached house; 3=Attached house; 4=Siheyuan; 5=Compound occupied by many households; 6=Work shed; 7=Haphazard building; 8=Other",
        "i025": "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
        "i026": "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
        "i021_w4": "1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied petroleum gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other; 8=Heating provided",
        "i020": "1=Yes; 2=No",
        "i015": "1=Yes; 2=No",
        "i016": "1=Yes; 2=No",
        "i017": "1=Yes; 2=No",
        "i018": "1=Hot water provided; 2=Water heater installed by the household; 3=No",
        "i019": "1=Yes; 2=No",
    },
    "2020": {
        "i001": "1=Concrete and steel/Bricks and wood; 2=Adobe; 3=Wood/Thatched; 4=Cave dwelling; 5=Mongolian yurt/Woolen felt/Tent; 6=Stone; 7=Other",
        "i003": "1=0-5 years; 2=5-10 years; 3=10-20 years; 4=20-30 years; 5=30-40 years; 6=More than 40 years",
        "i004": "1=One-storey building; 2=Common multi-storey building; 3=Self-contained multi-storey building",
        "i005": "1=Independent storey; 2=Compound",
        "i007": "1=Yes; 2=No",
        "i009": "1=Yes; 2=No; 3=Do not need",
        "i022": "1=Yes; 2=No",
        "i023": "1=Yes; 2=No",
        "i024": "1=Yes; 2=No",
        "i027": "1=Flat covered; 2=Flat concrete; 3=Uneven",
        "i016": "1=Yes; 2=No",
        "i029": "1=Yes; 2=No; 997=Do not know",
        "i025": "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
        "i026": "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
        "i020": "1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied petroleum gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other; 8=Do not heating",
        "i019": "1=Yes; 2=No",
        "i014": "1=Yes; 2=No",
        "i015": "1=Yes; 2=No",
        "i017": "1=Unified hot water supply; 2=Water heater; 3=No",
        "i018": "1=Yes; 2=No",
        # i010 is a continuous number of steps in 2020, so it has no category map.
    },
}
for wave, fields in HOUSING_CATEGORIES.items():
    for code, labels in fields.items():
        found = raw[(raw.wave == wave) & (raw.variable.str.lower() == code.lower())]
        if found.empty:
            raise SystemExit(f"Official variable catalog has no {wave} {code}; check mapping.")
        rows.append({
            "wave": wave, "code": code, "value_labels": labels,
            "value_label_status": "Official Codebook response categories reviewed; frequencies and percentages omitted; preserve wave-specific coding",
            "value_label_source": f"sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        })
out = pd.DataFrame(rows)
out.to_csv(ROOT / "audit/housing_value_label_review_v1.csv", index=False, encoding="utf-8-sig")
print(f"reviewed housing value labels={len(out)}; distinct fields={out.code.nunique()}; waves={out.wave.nunique()}")
