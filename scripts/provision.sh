#!/usr/bin/env bash
set -euo pipefail

TIMING_FILE=/vagrant/vagrant_setup_time.json

echo "Recording start timestamp"
START_TS=$(python3 - <<PY
import time
print(time.time())
PY
)

echo "Updating APT and installing dependencies..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip sqlite3 build-essential git curl sysstat

echo "Setting up python virtualenv and installing requirements"
python3 -m venv /home/vagrant/.venv
source /home/vagrant/.venv/bin/activate
pip install --upgrade pip
if [ -f /vagrant/requirements.txt ]; then
  pip install -r /vagrant/requirements.txt || true
fi


echo "Initializing database (if present)"
if [ -f /vagrant/init_db.py ]; then
  # run init_db.py with project root as cwd so relative files like schema.sql are found
  (cd /vagrant && python3 init_db.py) || true
fi

echo "Optionally running tests (if pytest installed)"
if command -v pytest >/dev/null 2>&1; then
  # run pytest from project root so test discovery works with relative imports/templates
  (cd /vagrant && pytest -q) || true
fi

# Collect memory and CPU metrics inside VM
echo "Collecting in-VM memory and CPU metrics"
# used memory (human readable)
USED_MEM_H=$(free -h | awk '/Mem:/ {print $3"/"$2}') || USED_MEM_H=""

# CPU usage via sar: sample for 20 seconds then compute avg idle and cpu usage
CPU_USAGE=""
if command -v sar >/dev/null 2>&1; then
  # run sar for 20 seconds (1s interval)
  SAR_OUT=$(sar -u 1 20 2>/dev/null || true)
  # try to extract the Average line's idle column (last column)
  AVG_IDLE=$(echo "$SAR_OUT" | awk 'tolower($0) ~ /average/ {print $NF; exit}')
  if [ -z "$AVG_IDLE" ]; then
    # try last line fallback
    AVG_IDLE=$(echo "$SAR_OUT" | tail -n 1 | awk '{print $NF}')
  fi
  if [ -n "$AVG_IDLE" ]; then
    # compute cpu usage = 100 - idle
    CPU_USAGE=$(python3 - <<PY
try:
    idle=float("$AVG_IDLE")
    print(max(0.0, 100.0 - idle))
except Exception:
    print("")
PY
)
  fi
fi

END_TS=$(python3 - <<PY
import time
print(time.time())
PY
)

DURATION=$(python3 - <<PY
start=${START_TS}
end=${END_TS}
print(end-start)
PY
)

# Append entry to timing file (as an array). Preserve existing entries.
python3 - <<PY
import json, os
f='${TIMING_FILE}'
entry={'start': ${START_TS}, 'end': ${END_TS}, 'duration': ${DURATION}, 'used_memory': '${USED_MEM_H}', 'cpu_usage_percent': '${CPU_USAGE}'}
data=[]
if os.path.exists(f):
    try:
        data=json.load(open(f))
        if not isinstance(data, list):
            data=[data]
    except Exception:
        data=[]
data.append(entry)
open(f,'w').write(json.dumps(data))
print('appended timing entry')
PY

echo "Provisioning complete"
