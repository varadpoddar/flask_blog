import importlib
import sqlite3
import sys
from pathlib import Path

import pytest


@pytest.fixture
def client(tmp_path):
    """Create a Flask test client for the blog API backed by a temp SQLite DB."""
    service_root = Path(__file__).resolve().parents[1]
    db_path = tmp_path / "blog.db"

    conn = sqlite3.connect(db_path)
    with open(service_root / "schema.sql", "r") as f:
        conn.executescript(f.read())
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        ("First Post", "First content"),
    )
    cur.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        ("Second Post", "Second content"),
    )
    conn.commit()
    conn.close()

    sys.path.insert(0, str(service_root))

    import app as blog_app

    importlib.reload(blog_app)
    blog_app.app.config.update(
        TESTING=True,
        DATABASE_PATH=str(db_path),
    )

    with blog_app.app.test_client() as client:
        yield client
