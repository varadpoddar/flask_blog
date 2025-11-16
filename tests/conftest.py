import importlib
import sqlite3
import sys
from pathlib import Path

import pytest


@pytest.fixture
def client(tmp_path):
    """Create a Flask test client backed by a temporary SQLite database.

    This fixture does not change the working directory or run project scripts.
    Instead it:
    - creates a fresh `database.db` inside `tmp_path`
    - executes `schema.sql` from the project root into that DB
    - seeds the DB with two initial posts (matching `init_db.py`)
    - imports the project's `app` module and patches its
      `get_db_connection` function to return connections to the temp DB
    - yields a Flask test client configured for testing
    """
    project_root = Path(__file__).resolve().parent.parent

    tmp_db = tmp_path / 'database.db'

    # Create and initialize the temporary database
    conn = sqlite3.connect(str(tmp_db))
    with open(project_root / 'schema.sql', 'r') as f:
        conn.executescript(f.read())

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

    # Ensure project root is on sys.path so `import app` works regardless of CWD
    sys.path.insert(0, str(project_root))

    # Import and reload the app module so we can patch its DB connector
    import app as blog_app
    importlib.reload(blog_app)

    # Patch the app's get_db_connection to use our temp DB
    def get_db_connection():
        c = sqlite3.connect(str(tmp_db))
        c.row_factory = sqlite3.Row
        return c

    blog_app.get_db_connection = get_db_connection
    blog_app.app.config['TESTING'] = True

    with blog_app.app.test_client() as client:
        yield client
