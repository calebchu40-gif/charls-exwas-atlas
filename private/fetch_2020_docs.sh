#!/bin/bash
set -u
BASE="/storage/home/tmu2301/nhanes分析/CHARLS_ExWAS_Atlas"
OUT="$BASE/private/source_documents"
declare -a URLS=(
"https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_User_Guide_English.pdf"
"https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/Codebook2020.pdf"
"https://charls.charlsdata.com/Public/ashelf/public/uploads/document/2020-charls-wave5/application/CHARLS_2020_Codebook.pdf"
)
for url in "${URLS[@]}"; do
  name=$(basename "$url")
  code=$(curl -sS -L --max-time 120 -o "/tmp/$name" -w "%{http_code}" "$url" 2>/dev/null || echo "000")
  echo "$name -> $code $(stat -c%s "/tmp/$name" 2>/dev/null || echo 0)"
  if [ "$code" = "200" ]; then
    cp "/tmp/$name" "$OUT/$name" && chmod 600 "$OUT/$name"
  fi
done
ls -1 "$OUT" | wc -l
