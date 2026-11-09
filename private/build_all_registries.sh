#!/bin/bash
set -u
BASE="/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas"
PY="$BASE/env/venv/bin/python"
for w in 2011 2013 2015 2018 2020; do
  "$PY" /tmp/build_full_registry_wave.py "$w" 2>&1 | tail -n 1
done
