import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request
from sqlite3 import OperationalError

app = Flask(__name__)

# Configurable paths via env; defaults work for local/dev.
DEFAULT_DB_PATH = os.getenv("BLOG_DB_PATH") or os.getenv("DATABASE_PATH") or "database.db"
DEFAULT_SCHEMA_PATH = os.getenv("BLOG_SCHEMA_PATH") or os.path.join(os.path.dirname(__file__), "schema.sql")

app.config.setdefault("DATABASE_PATH", DEFAULT_DB_PATH)
app.config.setdefault("SCHEMA_PATH", DEFAULT_SCHEMA_PATH)


def get_db_connection():
    """Return a SQLite connection using the configured DB path."""
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


def row_to_post(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "created": row["created"],
    }


def ensure_schema():
    """Create schema if the posts table is missing (helps local/dev without entrypoint)."""
    conn = get_db_connection()
    try:
        conn.execute("SELECT 1 FROM posts LIMIT 1;")
    except OperationalError:
        with open(app.config["SCHEMA_PATH"], "r") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def get_post_or_404(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    if post is None:
        return None
    return row_to_post(post)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/posts", methods=["GET"])
def list_posts():
    ensure_schema()
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY created DESC").fetchall()
    conn.close()
    return jsonify([row_to_post(p) for p in posts]), 200


@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    ensure_schema()
    post = get_post_or_404(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post), 200


def validate_post_payload(data):
    if not isinstance(data, dict):
        return False, "Invalid JSON payload"
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    if not title:
        return False, "Title is required"
    if not content:
        return False, "Content is required"
    return True, {"title": title, "content": content}


@app.route("/posts", methods=["POST"])
def create_post():
    ensure_schema()
    ok, result = validate_post_payload(request.get_json(silent=True))
    if not ok:
        return jsonify({"error": result}), 400

    payload = result
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO posts (title, content, created) VALUES (?, ?, ?)",
        (payload["title"], payload["content"], datetime.utcnow()),
    )
    conn.commit()
    new_id = cur.lastrowid
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return jsonify(row_to_post(post)), 201


@app.route("/posts/<int:post_id>", methods=["PUT", "PATCH"])
def update_post(post_id):
    ensure_schema()
    existing = get_post_or_404(post_id)
    if not existing:
        return jsonify({"error": "Post not found"}), 404

    ok, result = validate_post_payload(request.get_json(silent=True))
    if not ok:
        return jsonify({"error": result}), 400

    payload = result
    conn = get_db_connection()
    conn.execute(
        "UPDATE posts SET title = ?, content = ? WHERE id = ?",
        (payload["title"], payload["content"], post_id),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return jsonify(row_to_post(updated)), 200


@app.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    ensure_schema()
    existing = get_post_or_404(post_id)
    if not existing:
        return jsonify({"error": "Post not found"}), 404

    conn = get_db_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f'Post "{existing["title"]}" deleted'}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
