"""Build a questionnaire-grounded, wave-aware CHARLS cognition item crosswalk.

Only public variable metadata and official questionnaire text are read. No respondent records are loaded.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


CONCEPTS = [
    ("cog_subjective_memory", "自评记忆", "主观认知", {"2011": [r"dc004"], "2013": [r"dc004"], "2015": [r"dc004"], "2018": [r"dc004"], "2020": [r"dc006"]}, "自评记忆题；应按各波响应选项统一方向后再比较。"),
    ("cog_orientation_time", "时间定向", "定向能力", {"2011": [r"dc001s[123]", r"dc002", r"dc003"], "2013": [r"dc001s[123]", r"dc002", r"dc003"], "2015": [r"dc001s[123]", r"dc002", r"dc003"], "2018": [r"dc00[1256]_w4"], "2020": [r"dc00[1-5]"]}, "按问卷分别记录年/月/日/星期/季节的题目；各波覆盖项目不同，勿直接汇总为相同总分。"),
    ("cog_orientation_place", "地点/个人信息定向", "定向能力", {"2018": [r"dc00[789]_w4", r"dc010_w4", r"dc012_w4"]}, "2018扩展认知模块独有的省市、乡镇、楼层及地址/个人信息题；须按年龄适用规则处理。"),
    ("cog_serial7", "连续减 7", "注意/计算", {"2011": [r"dc0(19|20|21|22|23|24)"], "2013": [r"dc0(19|20|21|22|23|24)"], "2015": [r"dc0(19|20|21|22|23|24)"], "2018": [r"dc014_w4(_[1-5](_1)?)?", r"dc024"], "2020": [r"dc007_[1-5](_1)?", r"dc008"]}, "题目回答字段与访员记录的辅助工具字段分开保留；按正确答案规则派生分数前需核对值标签。"),
    ("cog_figure_copy", "相交五边形临摹", "视空间能力", {"2011": [r"dc025"], "2013": [r"dc025"], "2015": [r"dc025"], "2018": [r"dc024_w4"], "2020": [r"dc009"]}, "相同任务语义的候选映射；核对评分规则、影像/纸笔记录及未评估代码后才能跨波合并。"),
    ("cog_word_immediate", "词语即时回忆", "情景记忆", {"2011": [r"dc006s\d+"], "2013": [r"dc006_[123]_s\d+"], "2015": [r"dc006s\d+"], "2018": [r"dc028_w4_s\d+", r"dc029_w4_s\d+", r"dc030_w4_s\d+"], "2020": [r"dc012_s\d+", r"dc013_s\d+", r"dc014_s\d+"]}, "2011/2013/2015与2020为多词即时学习/回忆；2013有重复呈现轮次，2018有三轮词语回忆，2020有三种词表。字段级项目不等于总分；代码本未明确的未选择存储码保持未知。"),
    ("cog_wordlist_repetition_count", "词表提示重复次数", "认知测验过程", {"2013": [r"dc006_cnt"]}, "2013代码本确认DC006_CNT取值类别1/2/3，标签为词表重复次数；问卷允许受访者未回忆出词时重复提示，最多3次。它是受施测流程影响的辅助认知表现候选，不是标准即时回忆得分；初次呈现是否计入及与逐词回忆答案的关系仍需核实。"),
    ("cog_word_delayed", "词语延迟回忆", "情景记忆", {"2011": [r"dc027s\d+"], "2013": [r"dc027s\d+"], "2015": [r"dc027s\d+"], "2018": [r"dc047_w4_s\d+"], "2020": [r"dc028_s\d+"]}, "延迟回忆题；2018为扩展十词表延迟回忆，2020 DC028为延迟回忆；2020 DC029访员观察不是认知结局。各波词表/编码结构需分别解释。"),
    ("cog_word_recognition", "词语辨识记忆", "情景记忆", {"2018": [r"dc0(4[8-9]|5[0-9]|6[0-7])_w4"]}, "2018 WRE词语辨识任务的20个词卡条目；每项询问是否在先前词表中见过，保留逐词响应，不合成为未经验证的总分。题目适用路由依赖WR101_INTRO和DC028_W4s12；拒答/未进入任务不编码为辨识错误。"),
    ("cog_word_recall_administration", "词语回忆施测情况", "认知测验条件", {"2018": [r"dc028_w4_1", r"dc031_w4_s\d+"]}, "2018拒绝/无法完成的原因及词语回忆施测时的访员观察/中断/阅读困难；属于测验条件，不作回忆得分。"),
    ("cog_animal_fluency", "动物命名流畅性", "语言/执行功能", {"2018": [r"dc03[2-9]_w4"]}, "2018限时60秒动物命名，按时间段记录总数与正确数；不要与词语回忆合并。"),
    ("cog_csid_items", "简明社区痴呆筛查认知条目", "认知筛查", {"2018": [r"dc04[2-5]_w4"]}, "2018 CSI-D受访者认知部分的四项单题表现；按原题正确/错误/不能回答分别处理，不合成为量表分。"),
    ("cog_object_learning", "三物品学习/注册", "情景记忆", {"2018": [r"dc013_w4_[1-5]_s\d+"]}, "2018扩展模块三物品重复学习记录，存在最多五轮及提前停止路由；勿与10词学习字段直接等同。"),
    ("cog_object_delayed", "三物品延迟回忆", "情景记忆", {"2018": [r"dc015_w4_s\d+"]}, "2018三物品延迟回忆，任务不同于其他波的10词延迟回忆。"),
    ("cog_naming", "物品命名", "语言能力", {"2018": [r"dc016_w4", r"dc017_w4"]}, "2018扩展认知任务：手表和铅笔命名。"),
    ("cog_repetition", "句子重复", "语言能力", {"2018": [r"dc018_w4"]}, "2018扩展认知任务；按原题正确性选项核验。"),
    ("cog_reading_comprehension", "阅读理解/执行指令", "语言与执行功能", {"2018": [r"dc019_w4", r"dc020_w4", r"dc021_w4", r"dc022_w4"]}, "2018扩展认知任务的阅读及多步骤指令题，保留单题级字段。"),
    ("cog_sentence_writing", "书写句子", "语言/执行功能", {"2018": [r"dc023_w4"]}, "2018扩展认知模块独有。"),
    ("cog_semantic_knowledge_item", "语义知识单题：仙人掌命名", "一般知识/认知筛查", {"2018": [r"dc026_w4", r"dc026_w4_revised"]}, "2018 HRS-TICS仙人掌命名单题。官方Data Alert提示其正确性可能受文化熟悉度和教育影响；dc026_w4_revised是Codebook中的替代评分字段，具体修订规则需官方发行定义，不能当作独立认知任务或与原始字段同时计入。"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--catalog", type=Path, default=root / "audit/raw_variable_catalog_v1.csv")
    ap.add_argument("--out-csv", type=Path, default=root / "audit/cognition_item_variable_mapping_v1.csv")
    ap.add_argument("--out-json", type=Path, default=root / "site-prototype/dist/cognition_items_v1.json")
    args = ap.parse_args()
    src = pd.read_csv(args.catalog, dtype=str, encoding="utf-8-sig").fillna("")
    codebook_labels: dict[tuple[str, str], str] = {}
    for wave, filename in [
        ("2011", "CHARLS_2011_Codebook_extracted.txt"),
        ("2013", "CHARLS_2013_Codebook_extracted.txt"),
        ("2015", "CHARLS_2015_Codebook_extracted.txt"),
        ("2018", "CHARLS_2018_Codebook_extracted.txt"),
        ("2020", "CHARLS_2020_Codebook_extracted.txt"),
    ]:
        path = root / "sources_official" / filename
        if not path.exists():
            path = root / "audit" / filename
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                match = re.match(r"^\s*[•·]?\s*(dc[0-9a-z_]+)\s*:\s*(.+?)\s*$", line, flags=re.I)
                if match:
                    codebook_labels[(wave, match.group(1).lower())] = match.group(2).strip()
    rows, concepts = [], []
    for cid, label, domain, wave_patterns, caveat in CONCEPTS:
        fields = []
        for wave, patterns in wave_patterns.items():
            frame = src[src.wave.eq(wave)]
            chosen = frame[frame.variable.apply(lambda v: any(re.fullmatch(p, v, flags=re.I) for p in patterns))]
            for _, rec in chosen.sort_values("variable").iterrows():
                code = rec.variable
                # Field descriptions here are transcribed/condensed from CHARLS questionnaire prompts.
                field = {"wave": wave, "code": code, "source_label": codebook_labels.get((wave, code.lower()), ""), "module": rec.module,
                         "note": f"问卷语义映射候选；{caveat}"}
                fields.append(field)
                rows.append({"concept_id": cid, "concept_label": label, "domain": domain, **field,
                             "mapping_status": "按波次模块及官方问卷题意映射；需检查值标签/路由"})
        concepts.append({"concept_id": cid, "label": label, "domain": domain, "source_fields": fields,
                         "status": "问卷题意候选映射；未派生分数", "caveat": caveat})
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out_csv, index=False, encoding="utf-8-sig")
    args.out_json.write_text(json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Mapped {len(rows)} metadata fields across {sum(bool(x['source_fields']) for x in concepts)} concepts; no respondent data read.")


if __name__ == "__main__":
    main()
