"""
Módulo de registro e gerenciamento de Bugs.
"""
from .database import get_connection, now_iso


def create_bug(
    project_id: int,
    title: str,
    description: str = "",
    steps_repro: str = "",
    severity: str = "MÉDIA",
    environment: str = "",
    reported_by: str = "",
    test_case_id: int | None = None
) -> int:
    ts = now_iso()
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO bugs
               (project_id, test_case_id, title, description, steps_repro,
                severity, environment, reported_by, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, test_case_id, title, description, steps_repro,
             severity, environment, reported_by, ts, ts)
        )
        return cur.lastrowid


def list_bugs(project_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM bugs WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def list_all_bugs() -> list:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT b.*, p.name AS project_name
               FROM bugs b
               JOIN projects p ON b.project_id = p.id
               ORDER BY b.created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


def update_bug_status(bug_id: int, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE bugs SET status = ?, updated_at = ? WHERE id = ?",
            (status, now_iso(), bug_id)
        )


def update_bug(bug_id: int, **fields) -> None:
    allowed = {"title", "description", "steps_repro", "severity", "status", "environment", "reported_by"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    updates["updated_at"] = now_iso()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [bug_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE bugs SET {set_clause} WHERE id = ?", values)


def delete_bug(bug_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM bugs WHERE id = ?", (bug_id,))


def get_bug(bug_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM bugs WHERE id = ?", (bug_id,)).fetchone()
        return dict(row) if row else None
