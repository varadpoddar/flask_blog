#!/usr/bin/env sh
set -euo pipefail

DB_PATH="${BLOG_DB_PATH:-${DATABASE_PATH:-/data/blog.db}}"
SCHEMA_PATH="${BLOG_SCHEMA_PATH:-/app/schema.sql}"
export DB_PATH SCHEMA_PATH

mkdir -p "$(dirname "$DB_PATH")"

if [ ! -f "$DB_PATH" ]; then
  echo "Initializing blog database at $DB_PATH"
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
