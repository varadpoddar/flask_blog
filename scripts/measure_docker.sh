#!/usr/bin/env bash
set -euo pipefail

# Measure docker container startup time and capture a single snapshot of docker stats.
# Usage: ./scripts/measure_docker.sh [N] [image] [output.csv]
# Defaults: N=3, image=flask_blog:latest, output=measurements/docker_durations.csv

N=${1:-3}
IMAGE=${2:-flask_blog:latest}
OUT=${3:-measurements/docker_durations.csv}

mkdir -p $(dirname "$OUT")
echo "run,duration_seconds,mem_usage,cpu_percent" > "$OUT"

for i in $(seq 1 "$N"); do
  echo "--- docker run $i/$N ---"

  # Run container detached on a random host port to avoid conflicts
  HOST_PORT=$((5000 + i))
  CONTAINER_NAME=measure_container_$i
  docker run -d --name "$CONTAINER_NAME" -p ${HOST_PORT}:5000 "$IMAGE" >/dev/null

  # Wait for first successful HTTP 200 on / (timeout 60s)
  START_TS=$(python3 - <<PY
import time
print(time.time())
PY
)
  SUCCESS=0
  for attempt in $(seq 1 60); do
    if curl -s -o /dev/null -w '%{http_code}' "http://localhost:${HOST_PORT}/" | grep -q '^2'; then
      SUCCESS=1
      break
    fi
    sleep 1
  done
  END_TS=$(python3 - <<PY
import time
print(time.time())
PY
)

  if [ "$SUCCESS" -eq 0 ]; then
    DURATION=""
  else
    DURATION=$(python3 - <<PY
start=${START_TS}
end=${END_TS}
print(end-start)
PY
)
  fi

  # Capture docker stats snapshot
  STATS=$(docker stats --no-stream --format "{{.MemUsage}},{{.CPUPerc}}" "$CONTAINER_NAME" 2>/dev/null || true)
  MEM_USAGE=""
  CPU_PERC=""
  if [ -n "$STATS" ]; then
    MEM_USAGE=$(echo "$STATS" | cut -d',' -f1)
    CPU_PERC=$(echo "$STATS" | cut -d',' -f2)
  fi

  echo "$i,$DURATION,$MEM_USAGE,$CPU_PERC" >> "$OUT"

  # Stop and remove container
  docker rm -f "$CONTAINER_NAME" >/dev/null

  sleep 1
done

echo "Docker measurements written to $OUT"
