#!/usr/bin/env sh
set -euo pipefail

DB_PATH="${AUTH_DB_PATH:-${DATABASE_PATH:-/data/auth.db}}"
SCHEMA_PATH="${AUTH_SCHEMA_PATH:-/app/schema.sql}"
export DB_PATH SCHEMA_PATH

mkdir -p "$(dirname "$DB_PATH")"

if [ ! -f "$DB_PATH" ]; then
  echo "Initializing auth database at $DB_PATH"
  if [ -f "$SCHEMA_PATH" ]; then
    python - <<PY
import sqlite3, os
db_path = os.environ.get("DB_PATH")
schema_path = os.environ.get("SCHEMA_PATH")
conn = sqlite3.connect(db_path)
with open(schema_path, "r") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("Database initialized")
PY
  else
    echo "Schema not found at $SCHEMA_PATH; skipping DB init"
  fi
fi

exec "$@"
