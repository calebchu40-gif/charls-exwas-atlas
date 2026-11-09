#!/bin/bash
set -u
BASE="/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas"
PY="$BASE/env/venv/bin/python"
mkdir -p "$BASE/private/logs"
pids=()
for w in 2011 2013 2015 2018 2020; do
  nohup "$PY" /tmp/run_wave_full.py "$w" > "$BASE/private/logs/full_$w.log" 2>&1 &
  pids+=($!)
  echo "started $w pid $!"
done
for pid in "${pids[@]}"; do
  wait "$pid" || echo "pid $pid failed"
done
for f in "$BASE/private/logs"/full_*.log; do
  echo "== $f"
  tail -n 2 "$f"
done
