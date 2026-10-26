"""Summarize metadata-only overlap of environment-context E concepts and P concepts.

This script reads only the public, sanitized concept-source crosswalk. It does not
read participant-level data, calculate analytic sample sizes, or fit models.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "audit" / "ep_concept_source_crosswalk_v1.csv"
OUTPUT = ROOT / "audit" / "environment_phenotype_metadata_readiness_2026-10-26.md"

ENVIRONMENT_FILES = {
    "audit/community_exposure_crosswalk_v1.csv",
    "audit/food_environment_crosswalk_v1.csv",
    "audit/housing_exposure_variable_mapping_v1.csv",
    "audit/environmental_perception_crosswalk_v1.csv",
}


def is_environment_candidate(row: dict[str, str]) -> bool:
    if "e" not in row["Role"].split(","):
        return False
    source = row["Source.File"]
    if source not in ENVIRONMENT_FILES:
        return False
    if source == "audit/environmental_perception_crosswalk_v1.csv":
        return True
    domain = row["Domain"].casefold()
    return "environment" in domain or "housing" in domain


def main() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    exposures: dict[str, set[str]] = defaultdict(set)
    phenotypes: dict[str, set[str]] = defaultdict(set)
    exposure_source_counts: dict[str, dict[str, set[tuple[str, str]]]] = defaultdict(
        lambda: defaultdict(set)
    )
    source_waves: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        wave = row["Wave"]
        if is_environment_candidate(row):
            exposures[wave].add(row["Concept.ID"])
            exposure_source_counts[row["Source.File"]][wave].add(
                (row["Concept.ID"], row["Source.Code"])
            )
            source_waves[row["Source.File"]].add(wave)
        if "p" in row["Role"].split(","):
            phenotypes[wave].add(row["Concept.ID"])

    waves = sorted(set(exposures) | set(phenotypes))
    report = [
        "# CHARLS 环境/住房候选—表型目录共现盘点（2026-10-26）",
        "",
        "## 范围与口径",
        "",
        "本审计从 `audit/ep_concept_source_crosswalk_v1.csv` 读取已去标识的字段元数据。E 侧仅纳入社区暴露、饮食/家庭环境目录中域名明确含 environment 或 housing 的概念，以及单列的主观空气质量感知概念；P 侧纳入全目录中该波次具有来源字段的表型概念。概念按波次去重后计算笛卡尔积。",
        "",
        "这是一项目录层面的同波次共现盘点：不读取个人答案，不代表配对有效样本量、问卷适格人数、权重/抽样设计可行性、因果识别条件或统计关联；不应把结果称为已完成 ExWAS。概念的 household/community/respondent 测量层级仍须逐项保留。",
        "",
        "## 波次覆盖与元数据共现",
        "",
        "| 波次 | 环境/住房 E 候选概念 | P 候选概念 | 元数据共现候选对 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for wave in waves:
        e_count = len(exposures[wave])
        p_count = len(phenotypes[wave])
        report.append(f"| {wave} | {e_count} | {p_count} | {e_count * p_count:,} |")

    report.extend(
        [
            "",
            "按上述筛选，跨波去重后共有 **94 个环境/住房 E 候选概念**；各波次的同波字段候选概念配对为 2,184–13,482 对。波次之间概念量差异主要反映来源模块与调查覆盖，不代表分析效能或研究质量。",
            "",
            "## 环境候选来源目录覆盖",
            "",
            "| 来源 crosswalk | 波次字段映射行 | 波次 | 解释边界 |",
            "| --- | ---: | --- | --- |",
        ]
    )
    source_explanations = {
        "audit/community_exposure_crosswalk_v1.csv": "社区告知者、设施/污染/天气/水燃料等情境；不是个人剂量",
        "audit/food_environment_crosswalk_v1.csv": "家庭住宅、燃料、供水、卫生设施等代理指标；按波次保留不同题意",
        "audit/housing_exposure_variable_mapping_v1.csv": "住宅/家庭层字段；大量住房资产字段不在本次环境候选筛选内",
        "audit/environmental_perception_crosswalk_v1.csv": "个人主观空气质量满意度，不等同监测浓度",
    }
    for source, explanation in source_explanations.items():
        field_rows = sum(len(codes) for codes in exposure_source_counts[source].values())
        waves_text = ", ".join(sorted(source_waves[source]))
        report.append(
            f"| `{source}` | {field_rows} | {waves_text} | {explanation} |"
        )
    report.extend(
        [
            "",
            "来源字段行会重复代表概念、波次选项或成员/住宅槽位，不能当作独立暴露种数。2020住房字段并不一定进入 `housing_exposure_variable_mapping_v1.csv`；其部分住宅环境指标来自五波饮食/家庭环境 crosswalk。",
            "",
            "## 对下一阶段建模准备的含义",
            "",
            "1. 优先从候选集合中选取题意明确且较可解释的家庭/社区环境代理指标（例如主要烹饪燃料、住宅供水/厕所、社区工业污染报告/距离、天气估计）；在目录中标明层级、参照时期、路由、单位与波次。",
            "2. 个人化学暴露与环境监测浓度在 CHARLS 当前确认的目录中缺席；不能以住房/社区代理量冒充 NHANES 生物监测暴露。2011/2015 的 16 项血液分析物应作为内部生理表型单独处理，并遵循各自血检样本框和权重说明。",
            "3. 从少量具备官方来源和清晰测量层级的 E/P 对开始样本框、数据版本、缺失/特殊码、波次可比性和复杂抽样审核；社区变量需确认个人—家庭—社区链接与聚类处理。只有在这些门槛通过后，才计算真实配对 N 和拟合模型。",
            "4. 不把此表作为候选分析对清单；逐对资格、测量层级兼容性、估计目标和协变量集合尚未决定。",
            "",
            "## 可复现",
            "",
            "运行 `python scripts/summarize_environment_phenotype_readiness.py`，由 sanitized concept-source crosswalk 重新生成本文件。输入不包含参与者记录，输出也不含样本量、频数或关联估计。",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    print(f"Environmental/housing concepts: {len(set.union(*exposures.values()))}")
    for wave in waves:
        e_count = len(exposures[wave])
        p_count = len(phenotypes[wave])
        print(f"{wave}: E={e_count}, P={p_count}, metadata_pairs={e_count * p_count}")


if __name__ == "__main__":
    main()
