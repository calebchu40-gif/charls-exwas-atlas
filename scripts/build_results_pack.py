#!/usr/bin/env python3
"""Assemble the public aggregate modules into a paper-ready results pack.

Reads the published JSON modules and writes:

* ``audit/results_table_pack_2026-11-02.md`` — one table per analysis;
* ``audit/results_table_pack_2026-11-02.csv`` — long format for reuse.

No respondent data is involved; every number also appears on the public site.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"
AUDIT = ROOT / "audit"
MD = AUDIT / "results_table_pack_2026-11-02.md"
CSV_OUT = AUDIT / "results_table_pack_2026-11-02.csv"


def load(name):
    path = SITE / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def plain(value, digits=3):
    if value is None or value == "":
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number != 0 and abs(number) < 0.001:
        return "<0.001"
    return f"{number:.{digits}f}"


def fmt(value, digits=3):
    if value is None or value == "":
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number != 0 and abs(number) < 0.001:
        return "<0.001"
    return f"{number:+.{digits}f}"


def main() -> int:
    rows: list[dict] = []
    sections: list[str] = ["# 结果表打包（2026-11-02）\n",
                           "所有数字均来自公开聚合模块，探索性、未经独立方法审阅。\n"]

    def add(analysis, exposure, outcome, estimate, low, high, p, q, n, note=""):
        rows.append({"analysis": analysis, "exposure": exposure, "outcome": outcome,
                     "estimate": estimate, "ci_lower": low, "ci_upper": high,
                     "p": p, "q": q, "n": n, "note": note})

    # 1. fuel gradient
    data = load("fuel_gradient_v1.json")
    if data:
        sections.append("\n## 1. 燃料清洁度梯度（尿酸等 15 项）\n")
        sections.append("| 结局 | 每等级 β | 95% CI | q | n |")
        sections.append("|---|---|---|---|---|")
        for row in data["results"]:
            sections.append(f"| {row['phenotype_concept_id']} | {fmt(row['estimate'])} | "
                            f"{fmt(row['ci_lower'])} – {fmt(row['ci_upper'])} | "
                            f"{plain(row['q'])} | {row['n']} |")
            add("fuel_gradient", "cooking_fuel_rank", row["phenotype_concept_id"],
                row["estimate"], row["ci_lower"], row["ci_upper"], row["p"], row["q"], row["n"])

    # 2. joint model
    data = load("joint_household_model_v1.json")
    if data:
        sections.append("\n## 2. 七暴露联合模型（q<0.05 项）\n")
        sections.append("| 结局 | 暴露项 | β | 95% CI | q | n |")
        sections.append("|---|---|---|---|---|---|")
        for row in [r for r in data["results"] if r["q_value_by"] < 0.05]:
            sections.append(f"| {row['phenotype_concept_id']} | {row['term']} | "
                            f"{fmt(row['estimate'])} | {fmt(row['ci_lower'])} – "
                            f"{fmt(row['ci_upper'])} | {plain(row['q_value_by'])} | {row['n_model']} |")
            add("joint_model", row["term"], row["phenotype_concept_id"], row["estimate"],
                row["ci_lower"], row["ci_upper"], row["p_value"], row["q_value_by"], row["n_model"])

    # 3. solid fuel
    data = load("solid_fuel_blood_v1.json")
    if data:
        sections.append("\n## 3. 固体燃料 vs 清洁燃料（血检 15 项）\n")
        sections.append("| 结局 | β | 95% CI | q | n |")
        sections.append("|---|---|---|---|---|")
        for row in data["results"]:
            sections.append(f"| {row['phenotype_concept_id']} | {fmt(row['estimate'])} | "
                            f"{fmt(row['ci_lower'])} – {fmt(row['ci_upper'])} | "
                            f"{plain(row['q'])} | {row['n']} |")
            add("solid_fuel", "solid_vs_clean", row["phenotype_concept_id"], row["estimate"],
                row["ci_lower"], row["ci_upper"], row["p"], row["q"], row["n"])

    # 4. age gradient
    data = load("age_gradient_v1.json")
    if data:
        sections.append("\n## 4. 尿酸—燃料关联的年龄梯度\n")
        sections.append("| 对照 | 年龄组 | β | 95% CI | p | n |")
        sections.append("|---|---|---|---|---|---|")
        for row in data["results"]:
            sections.append(f"| {row['term']} | {row['band']} | {fmt(row['estimate'])} | "
                            f"{fmt(row['ci_lower'])} – {fmt(row['ci_upper'])} | "
                            f"{fmt(row['p_value'])} | {row['n_model']} |")
            add("age_gradient", row["term"], "blood_uric_acid", row["estimate"],
                row["ci_lower"], row["ci_upper"], row["p_value"], "", row["n_model"],
                note=row["band"])

    # 5. lifestyle restricted
    data = load("lifestyle_restricted_v1.json")
    if data:
        sections.append("\n## 5. 生活方式限制（从不吸烟 + 不饮酒）\n")
        sections.append("| 对照 | β | 95% CI | p | n |")
        sections.append("|---|---|---|---|---|")
        for row in data["results"]:
            sections.append(f"| {row['term']} | {fmt(row['estimate'])} | "
                            f"{fmt(row['ci_lower'])} – {fmt(row['ci_upper'])} | "
                            f"{fmt(row['p_value'])} | {row['n_model']} |")
            add("lifestyle_restricted", row["term"], "blood_uric_acid", row["estimate"],
                row["ci_lower"], row["ci_upper"], row["p_value"], "", row["n_model"])

    # 6. 2013 anthropometry
    data = load("wave2013_solid_fuel_v1.json")
    if data:
        sections.append("\n## 6. 2013 体测复现（固体燃料）\n")
        sections.append("| 结局 | β | 95% CI | p | n |")
        sections.append("|---|---|---|---|---|")
        for row in data["results"]:
            sections.append(f"| {row['outcome']} | {fmt(row['estimate'])} | "
                            f"{fmt(row['ci_lower'])} – {fmt(row['ci_upper'])} | "
                            f"{fmt(row['p_value'])} | {row['n_model']} |")
            add("wave2013_anthropometry", "solid_vs_clean", row["outcome"], row["estimate"],
                row["ci_lower"], row["ci_upper"], row["p_value"], "", row["n_model"])

    # 7. health index
    data = load("health_index_v1.json")
    if data:
        sections.append("\n## 7. 健康指数与家庭暴露\n")
        sections.append("| 暴露项 | β（指数 SD） | 95% CI | p | n |")
        sections.append("|---|---|---|---|---|")
        for row in data["associations"]:
            sections.append(f"| {row['term']} | {fmt(row['estimate'])} | "
                            f"{fmt(row['ci_lower'])} – {fmt(row['ci_upper'])} | "
                            f"{fmt(row['p'])} | {data['index']['n']} |")
            add("health_index", row["term"], "health_index", row["estimate"],
                row["ci_lower"], row["ci_upper"], row["p"], "", data["index"]["n"])

    # 8. replication summary
    data = load("replication_v1.json")
    if data:
        sections.append("\n## 8. 2015 复现记分卡\n")
        sections.append(f"- 可匹配 {data['pairs_available']} 项，同向 {data['same_sign']} 项"
                        f"（{data['same_sign_fraction'] * 100:.1f}%），效应量相关 r={data['pearson_r']}，"
                        f"两波均 q<0.05 的有 {data['q_both_below_05']} 项。")

    # 9. network stability
    data = load("network_stability_v1.json")
    if data:
        sections.append("\n## 9. 暴露网络跨波稳定性\n")
        sections.append(f"- {data['edges_in_multiple_waves']} 条边出现在 ≥2 波，"
                        f"{data['edges_in_all_waves']} 条三波都有，方向一致率 "
                        f"{data['sign_consistent_fraction'] * 100:.0f}%。")

    # 10. trajectories
    data = load("trajectories_v1.json")
    if data:
        sections.append("\n## 10. 纵向轨迹（2011–2015）\n")
        sections.append("| 波次 | 年龄组 | 自评健康 | 自评记忆 | BMI | n |")
        sections.append("|---|---|---|---|---|---|")
        for row in data["by_wave"]:
            bmi = "—" if row.get("bmi") is None else f"{row['bmi']:.1f}"
            srh = "—" if row["srh"] is None else f"{row['srh']:.2f}"
            memory = "—" if row["memory"] is None else f"{row['memory']:.2f}"
            sections.append(f"| {row['wave']} | {row['band']} | {srh} | {memory} | {bmi} | {row['n']} |")

    MD.write_text("\n".join(sections) + "\n", encoding="utf-8")
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["analysis", "exposure", "outcome", "estimate",
                                                    "ci_lower", "ci_upper", "p", "q", "n", "note"])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"markdown": str(MD.relative_to(ROOT)), "rows": len(rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
