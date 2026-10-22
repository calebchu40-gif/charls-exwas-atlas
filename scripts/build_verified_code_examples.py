"""Build a small, explicitly reviewed CHARLS code-to-measure lookup.

Uses public variable metadata only. It does not read respondent values or
derive analysis indicators from repeated measurements.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


CONCEPTS = {
    "qa003": "收缩压·第1次", "qa007": "收缩压·第2次", "qa011": "收缩压·第3次",
    "qa004": "舒张压·第1次", "qa008": "舒张压·第2次", "qa012": "舒张压·第3次",
    "qa005": "脉搏·第1次", "qa009": "脉搏·第2次", "qa013": "脉搏·第3次",
    "qc003": "握力·左手第1次", "qc004": "握力·右手第1次",
    "qc005": "握力·左手第2次", "qc006": "握力·右手第2次",
    "qb002": "呼吸测试读数·第1次", "qb003": "呼吸测试读数·第2次", "qb004": "呼吸测试读数·第3次",
    "qd002": "半串联站立·完成情况", "qd003": "半串联站立·持续时间",
    "qe002": "全串联站立·完成情况", "qe003": "全串联站立·持续时间",
    "qf002": "并排站立·完成情况", "qf003": "并排站立·持续时间",
    "qg002": "步速测试·第1次用时", "qg003": "步速测试·第2次用时",
    "qh003": "重复坐站·第1段用时", "qh004": "重复坐站·第2段用时", "qh005": "重复坐站次数",
    "qi002": "身高测量", "ql002": "体重测量", "qm002": "腰围测量", "qk002": "膝高测量",
    "qj002": "上臂长度测量",
    "qc1_va003": "空腹状态", "qc1_vb002": "白细胞", "qc1_vb004": "血红蛋白",
    "qc1_vb005": "红细胞压积", "qc1_vb006": "平均红细胞体积", "qc1_vb009": "血小板",
    "newbun": "尿素氮", "newglu": "葡萄糖", "newcrea": "肌酐", "newcho": "总胆固醇",
    "newtg": "甘油三酯", "newhdl": "HDL胆固醇", "newldl": "LDL胆固醇",
    "newcrp": "C反应蛋白", "newhba1c": "糖化血红蛋白", "newua": "尿酸", "cystatinc": "胱抑素C",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "audit/raw_variable_catalog_v1.csv")
    parser.add_argument("--audit-out", type=Path, default=Path(__file__).resolve().parents[1] / "audit/verified_code_examples_v1.csv")
    parser.add_argument("--site-out", type=Path, default=Path(__file__).resolve().parents[1] / "site-prototype/dist/verified_code_examples_v1.json")
    args = parser.parse_args()

    source = pd.read_csv(args.catalog, dtype=str, encoding="utf-8-sig").fillna("")
    rows: list[dict[str, str]] = []
    for code, concept in CONCEPTS.items():
        matched = source[(source.variable.str.lower() == code.lower()) & source.module.str.contains("biomarker|Blood_Assays", case=False, regex=True)]
        if matched.empty:
            continue
        waves = sorted(set(matched.wave), key=int)
        labels = [f"{r.wave}: {r.variable_label}" for r in matched[["wave", "variable_label"]].drop_duplicates().itertuples(index=False)]
        repeated_measure = code.startswith(("qa", "qc", "qg", "qi", "ql", "qm", "qk"))
        rows.append({
            "code": code,
            "concept": concept,
            "waves": ",".join(waves),
            "modules": ",".join(sorted(set(matched.module))),
            "source_labels": " | ".join(labels),
            "source_layer": "CHARLS原始字段",
            "mapping_status": "字段标签已由官方变量目录核对；派生规则待定",
            "note": "重复读数/测量完成资格须按官方问卷和设计文件处理。" if repeated_measure else "仅确认2011官方检验字段存在；不可推断其他波次也有该检验。",
        })
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    args.site_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.audit_out, index=False, encoding="utf-8-sig")
    args.site_out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} metadata-only code mappings; no respondent data read.")


if __name__ == "__main__":
    main()
