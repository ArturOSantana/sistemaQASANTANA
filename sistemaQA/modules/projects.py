"""
Módulo de gerenciamento de Projetos.
"""
from .database import get_connection, now_iso


def create_project(name: str, description: str = "") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?)",
            (name, description, now_iso())
        )
        return cur.lastrowid


def list_projects() -> list:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_project(project_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return dict(row) if row else None


def update_project(project_id: int, name: str, description: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE projects SET name = ?, description = ? WHERE id = ?",
            (name, description, project_id)
        )


def delete_project(project_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
