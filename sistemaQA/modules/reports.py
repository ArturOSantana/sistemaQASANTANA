"""
Módulo de relatórios e estatísticas do Sistema QA.
Gera dados agregados para exibição no dashboard e exportação.
"""
from .database import get_connection


def get_project_summary(project_id: int) -> dict:
    with get_connection() as conn:
        # ── Casos de teste ──────────────────────────────────────────────
        total_cases = conn.execute(
            """SELECT COUNT(*) FROM test_cases tc
               JOIN test_suites ts ON tc.suite_id = ts.id
               WHERE ts.project_id = ?""",
            (project_id,)
        ).fetchone()[0]

        cases_by_status = conn.execute(
            """SELECT tc.status, COUNT(*) AS cnt
               FROM test_cases tc
               JOIN test_suites ts ON tc.suite_id = ts.id
               WHERE ts.project_id = ?
               GROUP BY tc.status""",
            (project_id,)
        ).fetchall()

        # ── Bugs ────────────────────────────────────────────────────────
        total_bugs = conn.execute(
            "SELECT COUNT(*) FROM bugs WHERE project_id = ?",
            (project_id,)
        ).fetchone()[0]

        bugs_by_severity = conn.execute(
            "SELECT severity, COUNT(*) AS cnt FROM bugs WHERE project_id = ? GROUP BY severity",
            (project_id,)
        ).fetchall()

        bugs_by_status = conn.execute(
            "SELECT status, COUNT(*) AS cnt FROM bugs WHERE project_id = ? GROUP BY status",
            (project_id,)
        ).fetchall()

        # ── Cenários ────────────────────────────────────────────────────
        total_scenarios = conn.execute(
            "SELECT COUNT(*) FROM scenarios WHERE project_id = ?",
            (project_id,)
        ).fetchone()[0]

        scenarios_by_status = conn.execute(
            "SELECT status, COUNT(*) AS cnt FROM scenarios WHERE project_id = ? GROUP BY status",
            (project_id,)
        ).fetchall()

    # ── Cobertura ───────────────────────────────────────────────────────
    status_map = {r["status"]: r["cnt"] for r in cases_by_status}
    executed = sum(v for k, v in status_map.items() if k != "NÃO EXECUTADO")
    passed   = status_map.get("PASSOU", 0)
    failed   = status_map.get("FALHOU", 0)
    blocked  = status_map.get("BLOQUEADO", 0)
    skipped  = status_map.get("IGNORADO", 0)
    not_run  = status_map.get("NÃO EXECUTADO", 0)
    coverage = round((executed / total_cases * 100), 1) if total_cases else 0.0
    pass_rate = round((passed / executed * 100), 1) if executed else 0.0

    return {
        "total_cases": total_cases,
        "executed": executed,
        "passed": passed,
        "failed": failed,
        "blocked": blocked,
        "skipped": skipped,
        "not_run": not_run,
        "coverage": coverage,
        "pass_rate": pass_rate,
        "cases_by_status": dict(status_map),
        "total_bugs": total_bugs,
        "bugs_by_severity": {r["severity"]: r["cnt"] for r in bugs_by_severity},
        "bugs_by_status": {r["status"]: r["cnt"] for r in bugs_by_status},
        "total_scenarios": total_scenarios,
        "scenarios_by_status": {r["status"]: r["cnt"] for r in scenarios_by_status},
    }


def get_global_summary() -> dict:
    with get_connection() as conn:
        total_projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        total_cases = conn.execute("SELECT COUNT(*) FROM test_cases").fetchone()[0]
        total_bugs = conn.execute("SELECT COUNT(*) FROM bugs").fetchone()[0]
        total_scenarios = conn.execute("SELECT COUNT(*) FROM scenarios").fetchone()[0]

        open_bugs = conn.execute(
            "SELECT COUNT(*) FROM bugs WHERE status IN ('ABERTO', 'EM ANÁLISE', 'REABERTO')"
        ).fetchone()[0]

        passed = conn.execute(
            "SELECT COUNT(*) FROM test_cases WHERE status = 'PASSOU'"
        ).fetchone()[0]

        executed = conn.execute(
            "SELECT COUNT(*) FROM test_cases WHERE status != 'NÃO EXECUTADO'"
        ).fetchone()[0]

    return {
        "total_projects": total_projects,
        "total_cases": total_cases,
        "total_bugs": total_bugs,
        "total_scenarios": total_scenarios,
        "open_bugs": open_bugs,
        "passed": passed,
        "executed": executed,
        "global_pass_rate": round((passed / executed * 100), 1) if executed else 0.0,
        "global_coverage": round((executed / total_cases * 100), 1) if total_cases else 0.0,
    }


def get_bugs_timeline(project_id: int) -> list:
    """Retorna bugs agrupados por data de criação para gráfico de linha."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS cnt
               FROM bugs WHERE project_id = ?
               GROUP BY day ORDER BY day""",
            (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_cases_history(project_id: int) -> list:
    """Retorna evolução de execução por data."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT substr(executed_at, 1, 10) AS day,
                      SUM(CASE WHEN status='PASSOU' THEN 1 ELSE 0 END)  AS passed,
                      SUM(CASE WHEN status='FALHOU' THEN 1 ELSE 0 END)  AS failed
               FROM test_cases tc
               JOIN test_suites ts ON tc.suite_id = ts.id
               WHERE ts.project_id = ? AND executed_at IS NOT NULL
               GROUP BY day ORDER BY day""",
            (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]
