"""
Módulo de exportação / importação CSV (backup).
"""
import csv
import os
from datetime import datetime
from .database import get_connection

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


def _ensure_exports_dir() -> None:
    os.makedirs(EXPORTS_DIR, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ──────────────────────────────────────────────
# EXPORTAÇÃO
# ──────────────────────────────────────────────

def export_test_cases(project_id: int) -> str:
    _ensure_exports_dir()
    path = os.path.join(EXPORTS_DIR, f"test_cases_proj{project_id}_{_timestamp()}.csv")
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT tc.id, ts.name AS suite, tc.title, tc.description,
                      tc.preconditions, tc.steps, tc.expected,
                      tc.priority, tc.status, tc.executed_at, tc.created_at
               FROM test_cases tc
               JOIN test_suites ts ON tc.suite_id = ts.id
               WHERE ts.project_id = ?
               ORDER BY tc.id""",
            (project_id,)
        ).fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id","suite","title","description","preconditions",
            "steps","expected","priority","status","executed_at","created_at"
        ])
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    return path


def export_bugs(project_id: int) -> str:
    _ensure_exports_dir()
    path = os.path.join(EXPORTS_DIR, f"bugs_proj{project_id}_{_timestamp()}.csv")
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, title, description, steps_repro, severity,
                      status, environment, reported_by, created_at, updated_at
               FROM bugs WHERE project_id = ? ORDER BY id""",
            (project_id,)
        ).fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id","title","description","steps_repro","severity",
            "status","environment","reported_by","created_at","updated_at"
        ])
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    return path


def export_scenarios(project_id: int) -> str:
    _ensure_exports_dir()
    path = os.path.join(EXPORTS_DIR, f"scenarios_proj{project_id}_{_timestamp()}.csv")
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, given, when_, then_, tags, status, created_at FROM scenarios WHERE project_id = ? ORDER BY id",
            (project_id,)
        ).fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id","title","given","when_","then_","tags","status","created_at"
        ])
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    return path


def export_all(project_id: int) -> dict:
    return {
        "test_cases": export_test_cases(project_id),
        "bugs": export_bugs(project_id),
        "scenarios": export_scenarios(project_id),
    }


# ──────────────────────────────────────────────
# IMPORTAÇÃO
# ──────────────────────────────────────────────

def import_test_cases(project_id: int, csv_path: str, suite_id: int) -> int:
    """Importa casos de teste de um arquivo CSV para uma suite específica."""
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with get_connection() as conn:
            from .database import now_iso
            for row in reader:
                conn.execute(
                    """INSERT OR IGNORE INTO test_cases
                       (suite_id, title, description, preconditions, steps, expected, priority, status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (suite_id, row.get("title",""), row.get("description",""),
                     row.get("preconditions",""), row.get("steps",""),
                     row.get("expected",""), row.get("priority","MÉDIA"),
                     row.get("status","NÃO EXECUTADO"), now_iso())
                )
                count += 1
    return count


def import_bugs(project_id: int, csv_path: str) -> int:
    """Importa bugs de um arquivo CSV."""
    count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with get_connection() as conn:
            from .database import now_iso
            for row in reader:
                ts = now_iso()
                conn.execute(
                    """INSERT OR IGNORE INTO bugs
                       (project_id, title, description, steps_repro, severity, status,
                        environment, reported_by, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (project_id, row.get("title",""), row.get("description",""),
                     row.get("steps_repro",""), row.get("severity","MÉDIA"),
                     row.get("status","ABERTO"), row.get("environment",""),
                     row.get("reported_by",""), ts, ts)
                )
                count += 1
    return count
