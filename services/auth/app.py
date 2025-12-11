import os
import sqlite3
from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

DEFAULT_DB_PATH = os.getenv("AUTH_DB_PATH") or os.getenv("DATABASE_PATH") or "auth.db"
DEFAULT_SCHEMA_PATH = os.getenv("AUTH_SCHEMA_PATH") or os.path.join(os.path.dirname(__file__), "schema.sql")
DEFAULT_JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
DEFAULT_JWT_ALGO = os.getenv("JWT_ALGORITHM", "HS256")
DEFAULT_JWT_EXP_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

app.config.update(
    DATABASE_PATH=DEFAULT_DB_PATH,
    SCHEMA_PATH=DEFAULT_SCHEMA_PATH,
    JWT_SECRET=DEFAULT_JWT_SECRET,
    JWT_ALGORITHM=DEFAULT_JWT_ALGO,
    JWT_EXPIRES_MINUTES=DEFAULT_JWT_EXP_MINUTES,
)


def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


def row_to_user(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "created": row["created"],
    }


def issue_token(user):
    exp = datetime.now(timezone.utc) + timedelta(minutes=app.config["JWT_EXPIRES_MINUTES"])
    payload = {
        "sub": user["id"],
        "username": user["username"],
        "exp": exp,
    }
    token = jwt.encode(payload, app.config["JWT_SECRET"], algorithm=app.config["JWT_ALGORITHM"])
    # PyJWT<2 returns bytes; normalize to str so headers are correct.
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def parse_token(token):
    try:
        return jwt.decode(token, app.config["JWT_SECRET"], algorithms=[app.config["JWT_ALGORITHM"]])
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    payload = parse_token(token)
    if not payload:
        return None
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (payload.get("sub"),)).fetchone()
    conn.close()
    if not user:
        return None
    return row_to_user(user)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


def validate_credentials(data):
    if not isinstance(data, dict):
        return False, "Invalid JSON payload"
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username:
        return False, "Username is required"
    if not password:
        return False, "Password is required"
    return True, {"username": username, "password": password}


@app.route("/signup", methods=["POST"])
def signup():
    ok, payload = validate_credentials(request.get_json(silent=True))
    if not ok:
        return jsonify({"error": payload}), 400

    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM users WHERE username = ?", (payload["username"],)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Username already exists"}), 409

    hashed = generate_password_hash(payload["password"])
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, created) VALUES (?, ?, ?)",
        (payload["username"], hashed, datetime.utcnow()),
    )
    conn.commit()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    user_data = row_to_user(user)
    token = issue_token(user_data)
    return jsonify({"token": token, "user": user_data}), 201


@app.route("/login", methods=["POST"])
def login():
    ok, payload = validate_credentials(request.get_json(silent=True))
    if not ok:
        return jsonify({"error": payload}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (payload["username"],)).fetchone()
    conn.close()
    if not user or not check_password_hash(user["password_hash"], payload["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    user_data = row_to_user(user)
    token = issue_token(user_data)
    return jsonify({"token": token, "user": user_data}), 200


@app.route("/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(user), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5002"))
    app.run(host="0.0.0.0", port=port)
