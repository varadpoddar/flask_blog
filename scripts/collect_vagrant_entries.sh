#!/usr/bin/env bash
set -euo pipefail

# Run Vagrant up/provision N times and ensure /vagrant/vagrant_setup_time.json
# contains N appended entries. The provisioning script (scripts/provision.sh)
# appends an entry to that file on each run.
#
# Usage:
#   ./scripts/collect_vagrant_entries.sh [N]
# Default: N=3

N=${1:-3}
TIMING_FILE=vagrant_setup_time.json

echo "Collecting $N vagrant timing entries into $TIMING_FILE"

for i in $(seq 1 $N); do
  echo "=== run $i/$N ==="

  # Ensure clean state
  vagrant destroy -f >/dev/null 2>&1 || true

  # Count existing entries (0 if missing or invalid)
  PRE_COUNT=$(python3 - <<PY || true
import json,sys,os
f='${TIMING_FILE}'
if not os.path.exists(f):
    print(0); sys.exit(0)
try:
    d=json.load(open(f))
    if isinstance(d, list):
        print(len(d))
    else:
        print(1)
except Exception:
    print(0)
PY
)

  echo "existing entries before run: $PRE_COUNT"

  # Bring VM up and provision. Show minimal output to track progress.
  if ! vagrant up --provision; then
    echo "vagrant up failed for run $i (continuing to next)" >&2
  fi

  # Wait for timing file to have one more entry (with timeout)
  TIMEOUT=30
  SLEEP=2
  waited=0
  TARGET=$((PRE_COUNT+1))
  echo -n "waiting for timing file to contain >= $TARGET entries"
  while [ $waited -lt $TIMEOUT ]; do
    CUR_COUNT=$(python3 - <<PY || true
import json,sys,os
f='${TIMING_FILE}'
if not os.path.exists(f):
    print(0); sys.exit(0)
try:
    d=json.load(open(f))
    if isinstance(d, list):
        print(len(d))
    else:
        print(1)
except Exception:
    print(0)
PY
)
    if [ -n "$CUR_COUNT" ] && [ "$CUR_COUNT" -ge "$TARGET" ]; then
      echo " -> done (entries=$CUR_COUNT)"
      break
    fi
    sleep $SLEEP
    waited=$((waited+SLEEP))
    echo -n "."
  done
  if [ $waited -ge $TIMEOUT ]; then
    echo "\nTimed out waiting for timing file to update (run $i)" >&2
  fi

  # Show last appended entry (if present)
  echo "Last entry (if available):"
  python3 - <<PY || true
import json,sys,os
f='${TIMING_FILE}'
if not os.path.exists(f):
    print('no timing file')
    sys.exit(0)
try:
    d=json.load(open(f))
    if isinstance(d, list) and len(d)>0:
        import pprint
        pprint.pprint(d[-1])
    elif d:
        import pprint
        pprint.pprint(d)
    else:
        print('timing file empty')
except Exception as e:
    print('error reading timing file:', e)
PY

  # Halt and destroy to reset for next run
  vagrant halt >/dev/null 2>&1 || true
  vagrant destroy -f >/dev/null 2>&1 || true

  # small pause
  sleep 2
done

echo "Done. Final timing file contents:"
python3 - <<PY
import json,sys,os
f='${TIMING_FILE}'
if not os.path.exists(f):
    print('no timing file')
    sys.exit(0)
print(json.dumps(json.load(open(f)), indent=2))
PY
