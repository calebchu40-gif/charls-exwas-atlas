"""Build a reviewed, wave-specific pension response-label crosswalk.

Labels are transcribed from the CHARLS wave codebooks. Positive-only checkbox
categories are explicitly marked; this script never infers unselected values.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
rows = []

def add(wave, code, labels, note):
    rows.append({
        "wave": str(wave), "code": code.lower(), "value_labels": labels,
        "value_label_status": "official codebook response labels reviewed",
        "value_label_source": f"sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        "questionnaire_note": note,
    })

checkbox_note = "Official codebook lists the positive selected-category code only; unselected storage and missing codes are not inferred."
add(2011, "fn001", "1=Yes; 2=No", "Currently receiving at least one kind of pension.")
for i, label in enumerate([
    "Supplemental pension insurance of the firm", "Commercial pension",
    "Rural pension", "Residents pension", "Urban residents pension",
    "Pension subsidy to the oldest old", "Other",
], 1):
    add(2011, f"fn002s{i}", f"{i}={label} (selected category)", checkbox_note)

wave2_categories = [
    "Pension Program of The Government and Institutions",
    "Pension Insurance of The Firms", "Supplemental Pension Insurance of The Firm",
    "Commercial Pension", "Life Insurance", "Rural Pension", "Residents' Pension",
    "Urban Residents' Pension", "New Rural Social Pension Insurance",
    "Land Requisition Insurance", "Pension Subsidy to The Oldest Old", "Other", "None",
]
for i, label in enumerate(wave2_categories, 1):
    add(2013, f"fn001_w2s{i}", f"{i}={label} (selected category)", checkbox_note)
for i, label in enumerate([
    "Pension Program of The Government", "Pension Program of Staffing of Government Affiliated Institutions",
    "Pension Insurance of The Firms", "None of above",
], 1):
    add(2013, f"fn002_w2s{i}", f"{i}={label} (selected category)", checkbox_note)
add(2013, "fn006_w2", "1=Yes, Pension Program of The Government and Institutions; 2=Yes, Basic Pension Insurance of The Firms; 3=Yes, Both of Them; 4=No", "Enrollment in government/institution or firm basic pension program.")

add(2015, "fn002_w3", "1=Receive; 2=Participate, Not Receive; 3=Not Participate", "Combined government, institution, and firm pension participation/receipt status.")
for i, label in enumerate([
    "Pension Program of The Government", "Pension Program of Staffing of Government Affiliated Institutions",
    "Pension Insurance of The Firms",
], 1):
    add(2015, f"fn002_w2s{i}", f"{i}={label} (selected category)", checkbox_note)
add(2015, "fn006_w2", "1=Yes, Pension Program of The Government and Institutions; 2=Yes, Basic Pension Insurance of The Firms; 3=Yes, Both of Them; 4=No", "Enrollment in government/institution or firm basic pension program.")

add(2018, "fn002_w4", "1=Yes; 2=No", "Receive/participate in government, institution, or firm pension.")
for code, val, label in [
    ("fn002_w4_a_s1", 1, "Government Pension"),
    ("fn002_w4_a_s2", 2, "Institutions Pension"),
    ("fn002_w4_a_s3", 3, "Firm Pension"),
    ("fn002_w4_a_s4", 4, "Don't Know the Type"),
]:
    add(2018, code, f"0=No; {val}={label}", "Pension type checkbox; codebook explicitly reports 0=No and the selected category code.")
for i, label in enumerate(["Government Pension", "Institutions Pension", "Firm Pension", "Government/Institutions/Firm Pension"], 1):
    add(2018, f"fn002_w4_b_{i}_", f"1=Yes; 2=No", f"Whether respondent receives {label}; asked conditionally by pension type.")

raw = pd.read_csv(ROOT / "audit/raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
keys = set(zip(raw.wave.astype(str), raw.variable.str.lower()))
missing = [(r["wave"], r["code"]) for r in rows if (r["wave"], r["code"]) not in keys]
if missing:
    raise SystemExit(f"Codebook-reviewed field(s) absent from official raw catalog: {missing}")
out = pd.DataFrame(rows)
if out.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate wave-code entries in reviewed label map")
out.to_csv(ROOT / "audit/pension_value_label_review_v1.csv", index=False, encoding="utf-8-sig")
print(f"Wrote {len(out)} reviewed wave-field labels across {out.wave.nunique()} waves")
