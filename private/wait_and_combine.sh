#!/bin/bash
set -u
BASE="/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas"
PY="$BASE/env/venv/bin/python"
for i in $(seq 1 240); do
  if ! pgrep -f run_wave_full >/dev/null; then break; fi
  sleep 15
done
for f in "$BASE/private/logs"/full_*.log; do
  echo "== $(basename "$f")"
  tail -n 1 "$f"
done
"$PY" /tmp/combine_meta.py
