"""
Módulo de Casos de Teste e Suites de Teste.
"""
from .database import get_connection, now_iso


# ──────────────────────────────────────────────
# SUITES
# ──────────────────────────────────────────────

def create_suite(project_id: int, name: str, description: str = "") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO test_suites (project_id, name, description, created_at) VALUES (?, ?, ?, ?)",
            (project_id, name, description, now_iso())
        )
        return cur.lastrowid


def list_suites(project_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM test_suites WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_suite(suite_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM test_suites WHERE id = ?", (suite_id,))


# ──────────────────────────────────────────────
# CASOS DE TESTE
# ──────────────────────────────────────────────

def create_test_case(
    suite_id: int,
    title: str,
    description: str = "",
    preconditions: str = "",
    steps: str = "",
    expected: str = "",
    priority: str = "MÉDIA"
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO test_cases
               (suite_id, title, description, preconditions, steps, expected, priority, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (suite_id, title, description, preconditions, steps, expected, priority, now_iso())
        )
        return cur.lastrowid


def list_test_cases(suite_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM test_cases WHERE suite_id = ? ORDER BY created_at DESC",
            (suite_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def list_all_test_cases(project_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT tc.*, ts.name AS suite_name
               FROM test_cases tc
               JOIN test_suites ts ON tc.suite_id = ts.id
               WHERE ts.project_id = ?
               ORDER BY tc.created_at DESC""",
            (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def update_test_case_status(case_id: int, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE test_cases SET status = ?, executed_at = ? WHERE id = ?",
            (status, now_iso(), case_id)
        )


def update_test_case(case_id: int, **fields) -> None:
    allowed = {"title", "description", "preconditions", "steps", "expected", "priority", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [case_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE test_cases SET {set_clause} WHERE id = ?", values)


def delete_test_case(case_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM test_cases WHERE id = ?", (case_id,))


def get_test_case(case_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM test_cases WHERE id = ?", (case_id,)).fetchone()
        return dict(row) if row else None
