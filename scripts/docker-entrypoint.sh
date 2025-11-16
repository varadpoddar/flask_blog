#!/usr/bin/env sh
set -euo pipefail

# Initialize the SQLite database using Python if it doesn't exist.
DB_FILE=/app/database.db
SCHEMA_FILE=/app/schema.sql

if [ ! -f "$DB_FILE" ]; then
  echo "Initializing database at $DB_FILE"
  if [ -f "$SCHEMA_FILE" ]; then
    # Use Python's sqlite3 module to execute the schema and seed data.
    python - <<'PY'
import sqlite3
db = sqlite3.connect('/app/database.db')
cur = db.cursor()
with open('/app/schema.sql', 'r') as f:
    db.executescript(f.read())
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", ('First Post','Content for the first post'))
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", ('Second Post','Content for the second post'))
db.commit()
db.close()
print('Database initialized')
PY
  else
    echo "schema.sql not found at $SCHEMA_FILE; skipping DB initialization"
  fi
fi

exec "$@"
