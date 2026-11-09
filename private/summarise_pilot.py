"""Summarise the 2011 pilot output using the actual column names."""
from collections import Counter
from pathlib import Path

import polars as pl

OUT = Path("/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas/private/results/pilot_2011_core_continuous_v1.csv")
df = pl.read_csv(OUT, infer_schema_length=5000)
print("columns:", df.columns)
print("rows:", df.height)

status_col = "fit_status"
reason_col = "blocked_reason" if "blocked_reason" in df.columns else None
message_col = next((c for c in df.columns if "message" in c.lower()), None)

if reason_col:
    print("\nstatus:", Counter(df[status_col].to_list()))
    blocked = df.filter(pl.col(status_col) != "success")
    print("blocked reasons:", Counter(blocked[reason_col].to_list()).most_common(8))
    if message_col:
        print("\ntop messages:")
        for message, count in Counter(blocked[message_col].to_list()).most_common(8):
            print(f"  {count:5d}  {str(message)[:130]}")
    zero = blocked.filter(pl.col(reason_col) == "zero_exposure_variance")
    exposure_col = next((c for c in df.columns if c.startswith("exposure_var")), None)
    if exposure_col:
        print("\nzero-variance exposures:", Counter(zero[exposure_col].to_list()).most_common(12))
