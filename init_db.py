import os
import sqlite3
import sys


def find_schema_file(provided_path=None):
    """Return path to schema.sql. Try provided_path, cwd, then script dir."""
    candidates = []
    if provided_path:
        candidates.append(provided_path)

    # look in current working directory
    candidates.append(os.path.join(os.getcwd(), 'schema.sql'))

    # look next to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(script_dir, 'schema.sql'))

    for p in candidates:
        if p and os.path.exists(p):
            return os.path.abspath(p)

    raise FileNotFoundError(f"schema.sql not found. Checked: {candidates}")


def default_db_path(schema_path=None):
    """Pick a sensible default DB path: same dir as schema if available, else cwd."""
    if schema_path:
        return os.path.join(os.path.dirname(schema_path), 'database.db')
    return os.path.join(os.getcwd(), 'database.db')


def init_db(schema_file=None, db_file=None, seed=True):
    schema_path = find_schema_file(schema_file or os.getenv('SCHEMA_FILE'))
    db_path = db_file or os.getenv('DATABASE_FILE') or default_db_path(schema_path)

    print(f"Initializing database at: {db_path}")
    print(f"Using schema file: {schema_path}")

    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())

    if seed:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post'),
        )
        cur.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post'),
        )
        conn.commit()

    conn.close()
    print("Database initialized successfully.")


if __name__ == '__main__':
    # Allow optional CLI args: schema-file and db-file
    schema_arg = sys.argv[1] if len(sys.argv) > 1 else None
    db_arg = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        init_db(schema_file=schema_arg, db_file=db_arg, seed=True)
    except Exception:
        print("Error while initializing database:")
        raise

