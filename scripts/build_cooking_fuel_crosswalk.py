"""Build a codebook-verified, wave-specific cooking-fuel category crosswalk."""
from pathlib import Path
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
WAVE_CODES = {
    2011: ("i022", {1: ("coal", "Coal"), 2: ("natural_gas", "Natural gas"),
        3: ("marsh_gas", "Marsh gas"), 4: ("lpg", "Liquefied petroleum gas"),
        5: ("electricity", "Electric"), 6: ("crop_residue_wood", "Crop residue/wood burning"),
        7: ("other", "Other")}),
    2013: ("i022", {1: ("coal", "Coal"), 2: ("natural_gas", "Natural gas"),
        3: ("marsh_gas", "Marsh gas"), 4: ("lpg", "Liquefied petroleum gas"),
        5: ("electricity", "Electric"), 6: ("crop_residue_wood", "Crop residue/wood burning"),
        7: ("other", "Other")}),
    2015: ("i022", {1: ("coal", "Coal"), 2: ("natural_gas", "Natural gas"),
        3: ("marsh_gas", "Marsh gas"), 4: ("lpg", "Liquefied petroleum gas"),
        5: ("electricity", "Electric"), 6: ("crop_residue_wood", "Crop residue/wood burning"),
        7: ("other", "Other")}),
    2018: ("i022_w4", {1: ("coal", "Coal"), 2: ("natural_gas", "Natural gas"),
        3: ("marsh_gas", "Marsh gas"), 4: ("lpg", "Liquefied petroleum gas"),
        5: ("electricity", "Electric"), 6: ("crop_residue_wood", "Crop residue/wood burning"),
        7: ("other", "Other"), 8: ("no_cooking", "Do not cook")}),
    2020: ("i021", {1: ("coal", "Coal"), 2: ("natural_gas", "Natural gas"),
        3: ("marsh_gas", "Marsh gas"), 4: ("lpg", "Liquefied petroleum gas"),
        5: ("electricity", "Electric"), 6: ("crop_residue_wood", "Crop residue/wood burning"),
        7: ("solar_energy", "Solar energy"), 8: ("other", "Other"), 9: ("no_cooking", "Do not cook")}),
}


def main():
    counts = pd.read_csv(PROJECT / "audit" / "core_exposure_value_counts_v1.csv")
    counts = counts[counts.concept_id.eq("cooking_fuel_main")].copy()
    rows = []
    for wave, (variable, categories) in WAVE_CODES.items():
        observed = counts[counts.wave.eq(wave)]
        observed_codes = {int(float(v)) for v in observed.raw_value if pd.notna(v)}
        if observed_codes - set(categories):
            raise ValueError(f"Unmapped valid/raw fuel codes in {wave}: {observed_codes - set(categories)}")
        for code, (semantic, label) in categories.items():
            match = observed[pd.to_numeric(observed.raw_value, errors="coerce").eq(code)]
            n = int(match.n.sum()) if len(match) else 0
            valid = bool(match.valid_under_current_rule.any()) if len(match) else False
            rows.append({"wave": wave, "raw_variable": variable, "raw_code": code,
                "codebook_label": label, "canonical_category": semantic,
                "respondent_rows_raw_count": n, "observed_in_prepared_table": bool(len(match)),
                "valid_under_current_rule": valid,
                "harmonization_note": "Nominal primary fuel category; raw numeric codes are wave-specific and must not be treated as ordered dose."})
    out = pd.DataFrame(rows)
    path = PROJECT / "audit" / "cooking_fuel_crosswalk_v1.csv"
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"crosswalk rows={len(out)}; common semantic categories={out.groupby('canonical_category').wave.nunique().ge(5).sum()}")


if __name__ == "__main__":
    main()
