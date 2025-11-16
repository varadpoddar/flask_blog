#!/usr/bin/env bash
set -euo pipefail

# Convert vagrant_setup_time.json to measurements/vagrant_durations.csv
# Usage: ./scripts/convert_vagrant_json_to_csv.sh [json_file] [out_csv]

JSON=${1:-vagrant_setup_time.json}
OUT=${2:-measurements/vagrant_durations.csv}

if [ ! -f "$JSON" ]; then
  echo "JSON file $JSON not found" >&2
  exit 1
fi

mkdir -p $(dirname "$OUT")

echo "run,original_duration_seconds,adjusted_duration_seconds,mem_used,cpu_percent" > "$OUT"

python3 - <<PY >> "$OUT"
import json,csv,sys
f='$JSON'
with open(f) as fh:
    data=json.load(fh)
if not isinstance(data, list):
    data=[data]
writer=csv.writer(sys.stdout)
for i,entry in enumerate(data, start=1):
    dur=entry.get('duration','')
    adj=entry.get('adjusted_duration', dur)
    mem=entry.get('used_memory','')
    cpu=entry.get('cpu_usage_percent','')
    writer.writerow([i,dur,adj,mem,cpu])
PY

echo "Wrote $OUT"
