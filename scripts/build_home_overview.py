"""Build the homepage coverage overview payload.

The homepage describes what the atlas contains, not what it found: concept mix,
fields per wave, domain sizes, module flows and label-review progress. All values
come from the reviewed public catalogs; no association estimates are involved.

Output: site-prototype/dist/home_overview_v1.json
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"

CATEGORY_LABELS = {
    "social determinants": "社会决定因素",
    "social protection": "社会保障",
    "community context": "社区环境",
    "housing and built environment": "住房与建成环境",
    "behavior": "行为",
    "food and household environment": "饮食与家庭环境",
    "family and intergenerational context": "家庭与代际",
    "healthcare access": "医疗可及性",
    "early-life and family socioeconomic context": "早年与家庭社会经济",
    "environmental perception": "环境感知",
    "internal biomarker": "体内生物标志物",
    "life-course and reproductive history": "生命历程与生育史",
    "behavioral exposures": "行为暴露",
    "pandemic and public-health context": "疫情与公共卫生",
    "measurement metadata": "测量元数据",
    "chronic disease ancillary": "慢病辅助",
    "cognition": "认知",
    "psychological wellbeing": "心理与情绪",
    "physical function": "躯体功能",
    "health status and functioning": "健康与功能",
    "biomarker": "血液标志物",
    "chronic disease": "慢病",
    "health and symptoms": "健康与症状",
    "blood pressure": "血压",
    "mental health": "心理健康",
    "physical measurements": "体格测量",
    "blood biomarkers": "血液标志物",
}

MODULE_LABELS = [
    ("health_status_and_functioning", "健康与功能"),
    ("work_retirement", "工作与退休"),
    ("family_transfer", "家庭转移"),
    ("household_income", "家庭收入"),
    ("housing", "住房"),
    ("pension", "养老金"),
    ("community", "社区问卷"),
    ("biomarker", "血液检测"),
    ("anthropometr", "体测"),
    ("cognition", "认知测验"),
]


def module_label(raw: str) -> str | None:
    text = raw.lower()
    for key, label in MODULE_LABELS:
        if key in text:
            return label
    return None


def main() -> None:
    rows = json.loads((SITE / "catalog.json").read_text(encoding="utf-8"))

    # 1. Concept mix from the reviewed crosswalk.
    crosswalk = list(csv.DictReader((ROOT / "audit/ep_concept_source_crosswalk_v1.csv").open(encoding="utf-8-sig")))
    e_ids, p_ids = set(), set()
    for row in crosswalk:
        roles = {role.strip() for role in row["Role"].split(",")}
        if "e" in roles:
            e_ids.add(row["Concept.ID"])
        if "p" in roles:
            p_ids.add(row["Concept.ID"])
    concept_mix = {
        "exposure_only": len(e_ids - p_ids),
        "phenotype_only": len(p_ids - e_ids),
        "dual": len(e_ids & p_ids),
    }

    # 2. Fields per wave, split by role.
    wave_counts = {}
    for row in rows:
        roles = {role.strip() for role in str(row.get("epcf", "")).split(",") if role.strip()}
        for wave in str(row.get("waves", "")).split(","):
            wave = wave.strip()
            if not wave:
                continue
            bucket = wave_counts.setdefault(wave, {"wave": wave, "e": 0, "p": 0, "c": 0})
            for role in ("e", "p", "c"):
                if role in roles:
                    bucket[role] += 1
    waves = [wave_counts[key] for key in sorted(wave_counts)]

    # 3. Domain sizes.
    def top_categories(role: str, size: int = 8):
        counts = Counter(
            str(row.get("category"))
            for row in rows
            if role in {part.strip() for part in str(row.get("epcf", "")).split(",")}
        )
        return [
            {"label": CATEGORY_LABELS.get(name, name), "count": count}
            for name, count in counts.most_common(size)
        ]

    exposure_categories = top_categories("e")
    phenotype_categories = top_categories("p")

    # 4. Field flow from wave to questionnaire module.
    flow = Counter()
    for row in rows:
        module = None
        for candidate in str(row.get("source_modules", "")).replace(";", ",").split(","):
            module = module_label(candidate.strip())
            if module:
                break
        if not module:
            continue
        for wave in str(row.get("waves", "")).split(","):
            wave = wave.strip()
            if wave:
                flow[(wave, module)] += 1
    modules = [label for _, label in MODULE_LABELS]
    totals = Counter()
    for (_, module), count in flow.items():
        totals[module] += count
    keep = [module for module, _ in totals.most_common(6)]
    links = [{"wave": wave, "module": module, "count": count}
             for (wave, module), count in flow.items() if module in keep]
    module_flow = {"waves": [wave["wave"] for wave in waves], "modules": keep, "links": links}

    # 5. Label review progress.
    reviewed = pending = 0
    for row in rows:
        status = str(row.get("value_label_review") or row.get("Value.Label.Review") or "").lower()
        if "officially reviewed" in status or "official" in status:
            reviewed += 1
        elif status:
            pending += 1
    review = {"reviewed": reviewed, "pending": pending}

    payload = {
        "concept_mix": concept_mix,
        "waves": waves,
        "exposure_categories": exposure_categories,
        "phenotype_categories": phenotype_categories,
        "module_flow": module_flow,
        "review": review,
    }
    out = SITE / "home_overview_v1.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({
        "waves": len(waves),
        "exposure_categories": len(exposure_categories),
        "phenotype_categories": len(phenotype_categories),
        "modules": len(keep),
        "reviewed": reviewed,
        "pending": pending,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
