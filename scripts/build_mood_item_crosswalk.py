"""Build an item-level crosswalk for CHARLS mood/depressive symptom questions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ITEMS = [
    ("mood_bothered", "因小事烦恼", r"bothered by things"),
    ("mood_concentration", "难以集中注意", r"trouble keeping mind"),
    ("mood_depressed", "情绪低落", r"felt depressed"),
    ("mood_effort", "做事费力", r"everything i did was an effort"),
    ("mood_hopeful", "对未来有希望", r"hopeful about the future"),
    ("mood_fearful", "感到害怕", r"felt fearful"),
    ("mood_restless_sleep", "睡眠不安稳", r"sleep was restless"),
    ("mood_happy", "感到快乐", r"i was happy|^happy$"),
    ("mood_lonely", "感到孤独", r"felt lonely"),
    ("mood_could_not_get_going", "提不起劲", r"could not get"),
]


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--catalog',type=Path,default=Path(__file__).resolve().parents[1]/'audit/raw_variable_catalog_v1.csv')
    ap.add_argument('--out-csv',type=Path,default=Path(__file__).resolve().parents[1]/'audit/mood_item_variable_mapping_v1.csv')
    ap.add_argument('--out-json',type=Path,default=Path(__file__).resolve().parents[1]/'site-prototype/dist/mood_items_v1.json')
    args=ap.parse_args()
    src=pd.read_csv(args.catalog,dtype=str,encoding='utf-8-sig').fillna('')
    src=src[src.variable.str.match(r'(?i)^dc\d{3}$') & src.module.str.contains('health_status_and_functioning|cognition',case=False,regex=True)]
    rows=[]; concepts=[]
    for cid,label,pattern in ITEMS:
        found=src[src.variable_label.str.contains(pattern,case=False,regex=True,na=False)]
        fields=[]
        for _,r in found.sort_values(['wave','variable']).iterrows():
            note='条目级候选映射；响应选项、参照期、反向计分和跳题仍需逐波核验。'
            if r.wave=='2020': note='2020条目编码改为dc016–dc025序列；不可套用2011–2018题号。'+note
            field={'wave':r.wave,'code':r.variable,'source_label':r.variable_label,'module':r.module,'note':note}
            fields.append(field)
            rows.append({'concept_id':cid,'concept_label':label,**field,'mapping_status':'按CHARLS原字段标签匹配；量表计分未定义'})
        concepts.append({'concept_id':cid,'label':label,'source_fields':fields,'status':'独立条目候选，不是已计分量表','caveat':'不能直接当作一个总分；响应类别、计分方向、时间窗、缺失题处理及跨波可比性需逐波审定。'})
    args.out_csv.parent.mkdir(parents=True,exist_ok=True);args.out_json.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out_csv,index=False,encoding='utf-8-sig')
    args.out_json.write_text(json.dumps(concepts,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Mapped {len(rows)} item-wave fields across {len(concepts)} concepts; no respondent data read.')


if __name__=='__main__': main()
