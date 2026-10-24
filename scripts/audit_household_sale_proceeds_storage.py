"""Private aggregate-only QA for CHARLS 2013/2015 property-sale allocation fields.

Reads only the target household fields from protected prepared tables, never IDs.
Writes a field-level aggregate report only beneath the configured private QA path.
Raw values, response examples, and small-cell category counts are never exported.
"""
from __future__ import annotations

import re

import pandas as pd
import pyreadstat

from project_paths import QA_OUTPUT_DIR, WAVE_DATA_DIR, require_private_path

WAVES = ("2013", "2015")
SLOTS = ("1", "2", "25")
OPTIONS = {
    "a": "s1", "b": "s2", "c": "s3", "d": "s4", "e": "s5",
    "f": "s6", "g": "s7", "h": "s8", "j": "s9",
}


def planned_columns() -> dict[str, list[str]]:
    return {
        wave: [
            *[f"ha026_w2_1_{slot}_" for slot in SLOTS],
            *[f"ha026_w2_5{letter}_{slot}_" for slot in SLOTS for letter in OPTIONS],
            *[f"ha026_w2_5_{slot}_{option}" for slot in SLOTS for option in OPTIONS.values()],
        ]
        for wave in WAVES
    }


def summarize_response(amount: pd.Series, selector: pd.Series, status: pd.Series) -> dict[str, int]:
    """Summarize one matching amount/selector/property status without exporting values."""
    amount_text = amount.astype("string").str.strip()
    selector_text = selector.astype("string").str.strip()
    status_text = status.astype("string").str.strip()
    amount_present = amount_text.notna() & amount_text.ne("")
    selector_present = selector_text.notna() & selector_text.ne("")
    numeric = pd.to_numeric(amount_text.where(amount_present), errors="coerce")
    numeric_present = numeric.notna()
    sold = status_text.eq("3")
    status_present = status_text.notna() & status_text.ne("")
    return {
        "amount_present": bool(amount_present.any()),
        "all_nonblank_amounts_numeric": bool((~amount_present | numeric_present).all()),
        "numeric_amount_observed": bool(numeric_present.any()),
        "all_numeric_amounts_within_0_100": bool(
            (~numeric_present | (numeric.ge(0) & numeric.le(100))).all()
        ),
        "selector_present": bool(selector_present.any()),
        "selector_without_amount_observed": bool((selector_present & ~amount_present).any()),
        "amount_without_selector_observed": bool((amount_present & ~selector_present).any()),
        "selector_amount_linkage_consistent": bool(
            not ((selector_present & ~amount_present) | (amount_present & ~selector_present)).any()
        ),
        "sold_status_present": bool(sold.any()),
        "amount_only_when_status_sold": bool(
            not (amount_present & status_present & ~sold).any()
            and not (amount_present & ~status_present).any()
        ),
    }


def main() -> None:
    outputs = []
    plan = planned_columns()
    for wave, requested in plan.items():
        path = require_private_path(WAVE_DATA_DIR / f"CHARLS_wave{wave}_person_analytic.dta")
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        present = {name.lower(): name for name in meta.column_names}
        missing = sorted(name for name in requested if name.lower() not in present)
        if missing:
            raise SystemExit(f"{wave}: required sale-proceeds fields missing from prepared table ({len(missing)} fields)")
        selected = [present[name.lower()] for name in requested]
        data, _ = pyreadstat.read_dta(str(path), usecols=selected)
        labels = dict(zip(meta.column_names, meta.column_labels or [""] * len(meta.column_names)))
        types = meta.readstat_variable_types or {}
        for slot in SLOTS:
            status_code = present[f"ha026_w2_1_{slot}_"]
            for letter, option in OPTIONS.items():
                amount_code = present[f"ha026_w2_5{letter}_{slot}_"]
                selector_code = present[f"ha026_w2_5_{slot}_{option}"]
                metrics = summarize_response(data[amount_code], data[selector_code], data[status_code])
                outputs.append({
                    "wave": wave, "property_slot": slot, "use_category_code": letter,
                    "amount_code": amount_code, "amount_source_label": labels.get(amount_code, ""),
                    "amount_storage_type": types.get(amount_code, ""),
                    "selector_code": selector_code, "selector_source_label": labels.get(selector_code, ""),
                    "selector_storage_type": types.get(selector_code, ""),
                    "property_status_code": status_code, "property_status_source_label": labels.get(status_code, ""),
                    **metrics,
                    "interpretation": "aggregate QA on prepared person table only; household-level values may be repeated; not a valid analytic denominator; no response values exported",
                })
    out_path = require_private_path(QA_OUTPUT_DIR / "house_sale_proceeds_storage_qa_v1.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(outputs).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(outputs)} field-level aggregate QA rows to protected local output: {out_path}")
    print("No respondent IDs or raw response values were read into the output file.")


if __name__ == "__main__":
    main()
