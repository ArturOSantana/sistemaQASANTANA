"""
Módulo de Cenários de Teste (formato Gherkin: Given / When / Then).
"""
from .database import get_connection, now_iso


def create_scenario(
    project_id: int,
    title: str,
    given: str = "",
    when_: str = "",
    then_: str = "",
    tags: str = ""
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO scenarios (project_id, title, given, when_, then_, tags, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, title, given, when_, then_, tags, now_iso())
        )
        return cur.lastrowid


def list_scenarios(project_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM scenarios WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def update_scenario_status(scenario_id: int, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE scenarios SET status = ? WHERE id = ?",
            (status, scenario_id)
        )


def update_scenario(scenario_id: int, **fields) -> None:
    allowed = {"title", "given", "when_", "then_", "tags", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [scenario_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE scenarios SET {set_clause} WHERE id = ?", values)


def delete_scenario(scenario_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))


def get_scenario(scenario_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,)).fetchone()
        return dict(row) if row else None
