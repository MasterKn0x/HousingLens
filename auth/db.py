"""
HousingLens – auth/db.py
--------------------------
Lightweight SQLite-based user store with bcrypt password hashing.
Tables:
    users(id, username, password_hash, role, created_at)

Roles:
    'admin'  – full access including Admin Control Panel
    'user'   – standard access (prediction tools only)
"""

import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime

# ── Database location ──────────────────────────────────────────────────────────
_DB_DIR  = Path(__file__).parent.parent / "data"
_DB_PATH = _DB_DIR / "users.db"

# Default admin credentials – change these after first login!
_DEFAULT_ADMIN_USERNAME = "admin"
_DEFAULT_ADMIN_PASSWORD = "housingadmin2025"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _connect() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ── Public API ────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create the users table and seed the default admin if it doesn't exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL DEFAULT 'user'
                                      CHECK(role IN ('admin', 'user')),
                created_at    TEXT    NOT NULL
            )
        """)
        conn.commit()

        # Seed default admin only if no admin exists yet
        existing = conn.execute(
            "SELECT id FROM users WHERE role='admin' LIMIT 1"
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?,?,?,?)",
                (
                    _DEFAULT_ADMIN_USERNAME,
                    _hash(_DEFAULT_ADMIN_PASSWORD),
                    "admin",
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()


def verify_login(username: str, password: str) -> dict | None:
    """
    Verify credentials.
    Returns user dict {id, username, role} on success, None on failure.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username=? COLLATE NOCASE",
            (username.strip(),),
        ).fetchone()

    if row and _check(password, row["password_hash"]):
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None


def register_user(username: str, password: str, role: str = "user") -> tuple[bool, str]:
    """
    Register a new user. Returns (success: bool, message: str).
    Admin can only be created through this function directly (not via public form).
    """
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?,?,?,?)",
                (username.strip(), _hash(password), role, datetime.utcnow().isoformat()),
            )
            conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already taken. Please choose another."


def list_users() -> list[dict]:
    """Return all users (admin view). Excludes password hashes."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, username, role, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_user(user_id: int) -> None:
    """Delete a user by ID. Will not delete the last admin."""
    with _connect() as conn:
        conn.execute("DELETE FROM users WHERE id=? AND role != 'admin'", (user_id,))
        conn.commit()


def promote_user(user_id: int) -> None:
    """Promote a standard user to admin."""
    with _connect() as conn:
        conn.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
        conn.commit()


# Initialise on import
init_db()
