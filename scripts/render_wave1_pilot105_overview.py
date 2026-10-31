#!/usr/bin/env python3
"""Render a private overview of the pilot-105 scan.

Draws a two-panel Manhattan-style figure (community PSUs on top, county PSUs
below) plus an HTML table of the most extreme coefficients, from the protected
result tables. Output is written next to the results and is **private**: it
contains coefficients and must not be committed or published.
"""
from __future__ import annotations

import argparse
import csv
import html
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from project_paths import PRIVATE_ROOT, require_private_path  # noqa: E402

RESULT_DIR = PRIVATE_ROOT / "results"
PANELS = (("community PSU (450 clusters)", "wave1_pilot105_main_v1.csv"),
          ("county PSU (150 clusters)", "wave1_pilot105_county_psu_v1.csv"))
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
SHORT = {
    "running_water_at_residence": "water",
    "cooking_fuel_coal": "coal",
    "cooking_fuel_natural_gas": "gas",
    "cooking_fuel_marsh_gas": "marsh",
    "cooking_fuel_LPG": "LPG",
    "cooking_fuel_crop_residue_or_wood": "wood",
    "cooking_fuel_other": "other",
}
PHENO_SHORT = {
    "blood_wbc": "WBC", "blood_hemoglobin": "Hb", "blood_hematocrit": "Hct",
    "blood_mcv": "MCV", "blood_platelets": "PLT", "blood_crp": "CRP",
    "blood_hba1c": "HbA1c", "blood_total_cholesterol": "TC", "blood_hdl": "HDL",
    "blood_ldl": "LDL", "blood_triglycerides": "TG", "blood_bun": "BUN",
    "blood_creatinine": "Cr", "blood_glucose": "Glu", "blood_uric_acid": "UA",
}


def load(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["p"] = float(row["p_value"]) if row.get("p_value") else 1.0
        row["q"] = float(row["q_value_by"]) if row.get("q_value_by") else 1.0
        row["beta"] = float(row["estimate"]) if row.get("estimate") else 0.0
    return rows


def order(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: (r["exposure_concept_id"], r["phenotype_concept_id"]))


def panel(rows: list[dict], top: int, title: str, height: int = 260) -> str:
    width, left, right = 1180, 70, 20
    plot_w = width - left - right
    y_max = max(6.0, max(-math.log10(max(r["p"], 1e-300)) for r in rows) + 0.6)
    parts = [f'<text x="{left}" y="{top - 10}" font-family="Segoe UI,Arial" font-size="15" '
             f'font-weight="600">{html.escape(title)}</text>']
    parts.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{height}" fill="#fafafa" '
                 f'stroke="#dddddd"/>')
    # thresholds
    for p, label, color in ((0.05, "p=0.05", "#bbbbbb"), (0.05 / len(rows), "Bonferroni", "#e06666")):
        y = top + height * (1 - (-math.log10(p) / y_max))
        if top <= y <= top + height:
            parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" '
                         f'stroke="{color}" stroke-dasharray="4 4"/>')
            parts.append(f'<text x="{left + plot_w - 4}" y="{y - 4:.1f}" text-anchor="end" '
                         f'font-family="Segoe UI,Arial" font-size="11" fill="{color}">{label}</text>')
    step = plot_w / max(len(rows), 1)
    for index, row in enumerate(rows):
        x = left + step * (index + 0.5)
        y = top + height * (1 - (-math.log10(max(row["p"], 1e-300)) / y_max))
        color = COLORS[hash(row["exposure_concept_id"]) % len(COLORS)]
        radius = 4.5 if row["q"] < 0.05 else 3.0
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{color}" '
                     f'fill-opacity="0.85"/>')
    # axis labels
    parts.append(f'<text x="18" y="{top + height / 2}" transform="rotate(-90 18 {top + height / 2})" '
                 f'text-anchor="middle" font-family="Segoe UI,Arial" font-size="12">-log10(p)</text>')
    parts.append(f'<text x="{left}" y="{top + height + 18}" font-family="Segoe UI,Arial" '
                 f'font-size="11" fill="#666">7 exposure contrasts × 15 blood phenotypes, ordered '
                 f'by exposure then phenotype</text>')
    return "\n".join(parts)


def render(rows: list[dict], panels: list[tuple[str, list[dict]]]) -> str:
    height = 680
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" '
            f'viewBox="0 0 1200 {height}">',
            '<rect width="1200" height="680" fill="white"/>']
    for index, (title, subset) in enumerate(panels):
        body.append(panel(order(subset), 60 + index * 320, title))
    body.append("</svg>")
    return "\n".join(body)


def table(rows: list[dict], limit: int = 25) -> str:
    top = sorted(rows, key=lambda r: r["p"])[:limit]
    lines = ["<table><thead><tr><th>exposure</th><th>phenotype</th><th>β (per SD)</th>"
             "<th>p</th><th>q (BY, K=105)</th><th>n</th></tr></thead><tbody>"]
    for row in top:
        css = ' style="background:#fff3cd"' if row["q"] < 0.05 else ""
        lines.append(
            f"<tr{css}><td>{html.escape(SHORT.get(row['exposure_concept_id'], row['exposure_concept_id']))}</td>"
            f"<td>{html.escape(PHENO_SHORT.get(row['phenotype_concept_id'], row['phenotype_concept_id']))}</td>"
            f"<td>{row['beta']:+.3f}</td><td>{row['p']:.2e}</td><td>{row['q']:.3f}</td>"
            f"<td>{row['n_model']}</td></tr>")
    lines.append("</tbody></table>")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="read the protected result tables")
    parser.add_argument("--outdir", type=Path, default=PRIVATE_ROOT / "results")
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required to read the protected result tables")

    panels = []
    main_rows: list[dict] = []
    for title, filename in PANELS:
        path = RESULT_DIR / filename
        if not path.is_file():
            parser.error(f"missing result table: {filename}")
        rows = load(path)
        panels.append((title, rows))
        if not main_rows:
            main_rows = rows
    svg = render(main_rows, panels)
    outdir = require_private_path(args.outdir)
    if not outdir.is_relative_to(PRIVATE_ROOT.resolve()):
        parser.error(f"output must stay under {PRIVATE_ROOT}")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "wave1_pilot105_overview.svg").write_text(svg, encoding="utf-8")
    page = ("<!doctype html><meta charset='utf-8'><title>Wave 1 pilot-105 (private, exploratory)</title>"
            "<style>body{font-family:Segoe UI,Arial;margin:24px;color:#222}"
            "table{border-collapse:collapse;margin-top:18px;font-size:13px}"
            "th,td{border:1px solid #ddd;padding:5px 9px;text-align:right}"
            "th{background:#f2f2f2}td:first-child,td:nth-child(2){text-align:left}"
            ".warn{background:#fff3cd;padding:10px 14px;border-left:4px solid #e0a800;margin:12px 0}"
            "</style>"
            "<h2>Wave 1 pilot-105 — private exploratory view</h2>"
            "<div class='warn'>Exploratory, PI-delegated, not independently reviewed. "
            "Do not publish or cite. Variance is an approximation.</div>"
            + svg + table(main_rows))
    (outdir / "wave1_pilot105_overview.html").write_text(page, encoding="utf-8")
    print(str(outdir / "wave1_pilot105_overview.html"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
