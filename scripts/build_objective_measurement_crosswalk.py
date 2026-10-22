from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    ("systolic_bp", "收缩压", "血压/循环", "qa003;qa007;qa011", "三次读数；保留原始读数并按分析方案定义均值。"),
    ("diastolic_bp", "舒张压", "血压/循环", "qa004;qa008;qa012", "三次读数；保留原始读数并按分析方案定义均值。"),
    ("pulse_rate", "脉搏", "血压/循环", "qa005;qa009;qa013", "伴随血压测量的重复读数；确认单位/异常值规则。"),
    ("peak_flow", "呼气峰流速", "肺功能", "qb002;qb003;qb004", "最多三次测量，问卷以呼吸测量模块记录；不是完整肺量计肺功能。"),
    ("grip_strength", "握力", "肌力/功能", "qc003;qc004;qc005;qc006", "左右手各两次；保留原侧别和重复次序，汇总值需预先定义。"),
    ("balance_semi_tandem", "半串联站立平衡", "平衡/功能", "qd002;qd003;qd004", "完成状态、持续时间、代偿动作；不能把未完成路由一律编码为0秒。"),
    ("balance_full_tandem", "全串联站立平衡", "平衡/功能", "qe002;qe003;qe004", "完成状态、持续时间、代偿动作；按问卷资格解释缺失。"),
    ("balance_side_by_side", "并排站立平衡", "平衡/功能", "qf002;qf003;qf004", "是否坚持满10秒、持续时间、代偿动作；分别保留。"),
    ("walking_speed", "步行速度/计时步行", "移动/功能", "qg002;qg003", "两次步行计时；具体速度需按问卷测距与单位推导，不能直接把时间叫速度。"),
    ("repeated_chair_stand", "重复椅子起立表现", "下肢功能", "qh002;qh003;qh004;qh005", "站立能力、重复测时/间隔及次数依问卷定义；2015 qh006为座椅信息而非身高。"),
    ("standing_height", "身高", "人体测量", "qi002", "现场身高读数；与qh006等椅子测试字段区分。"),
    ("arm_length", "上臂长度", "人体测量", "qj002", "记录值并保留测量侧别qj003。"),
    ("knee_height", "膝高", "人体测量", "qk002", "记录值并保留测量侧别/腿别qk003。"),
    ("body_weight", "体重", "人体测量", "ql002", "部分波次含测量资格、鞋履/地面等质量字段；原始读数与质量标记分开。"),
    ("waist_circumference", "腰围", "人体测量/脂肪分布", "qm002", "注意厚重衣物、测量完成状态及波次问卷的路由。"),
]

rows=[]
for concept,label,domain,codes,note in FIELDS:
    for wave,module in [("2011","biomarkers"),("2013","Biomarker"),("2015","Biomarker")]:
        rows.append({"concept_id":concept,"concept_label":label,"domain":domain,"wave":wave,
                     "variables":codes,"module":module,"value_semantics":note,
                     "source_status":"原始字段目录与对应波次体检问卷已定位；概念对应候选，字段路由/单位需逐波复核",
                     "source_document":"CHARLS 2011 Baseline User Guide; CHARLS 2013/2015 Biomarker Questionnaire"})

out=ROOT/"audit"/"objective_measurement_crosswalk_v1.csv"
with out.open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(ROOT/"site-prototype"/"dist"/"objective_measurements_v1.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"wrote {len(rows)} mappings across {len(FIELDS)} concepts")
