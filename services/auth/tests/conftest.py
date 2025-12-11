import importlib
import sqlite3
import sys
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path):
    """Create a Flask test client for the auth service backed by a temp SQLite DB."""
    service_root = Path(__file__).resolve().parents[1]
    db_path = tmp_path / "auth.db"

    conn = sqlite3.connect(db_path)
    with open(service_root / "schema.sql", "r") as f:
        conn.executescript(f.read())
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("alice", generate_password_hash("password123")),
    )
    conn.commit()
    conn.close()

    sys.path.insert(0, str(service_root))

    import app as auth_app

    importlib.reload(auth_app)
    auth_app.app.config.update(
        TESTING=True,
        DATABASE_PATH=str(db_path),
        JWT_SECRET="test-secret",
        JWT_EXPIRES_MINUTES=30,
    )

    with auth_app.app.test_client() as client:
        yield client
