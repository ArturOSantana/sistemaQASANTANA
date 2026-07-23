"""
Módulo de banco de dados — SQLite local para persistência de dados do Sistema QA.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "qa_system.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Cria todas as tabelas necessárias se não existirem."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                description TEXT,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS test_suites (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                name        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS test_cases (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                suite_id      INTEGER NOT NULL REFERENCES test_suites(id) ON DELETE CASCADE,
                title         TEXT    NOT NULL,
                description   TEXT,
                preconditions TEXT,
                steps         TEXT,
                expected      TEXT,
                priority      TEXT    DEFAULT 'MÉDIA'  CHECK(priority IN ('BAIXA','MÉDIA','ALTA','CRÍTICA')),
                status        TEXT    DEFAULT 'NÃO EXECUTADO'
                                      CHECK(status IN ('NÃO EXECUTADO','PASSOU','FALHOU','BLOQUEADO','IGNORADO')),
                executed_at   TEXT,
                created_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scenarios (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title       TEXT    NOT NULL,
                given       TEXT,
                when_       TEXT,
                then_       TEXT,
                tags        TEXT,
                status      TEXT    DEFAULT 'PENDENTE'
                                    CHECK(status IN ('PENDENTE','APROVADO','REPROVADO')),
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS bugs (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                test_case_id INTEGER REFERENCES test_cases(id),
                title        TEXT    NOT NULL,
                description  TEXT,
                steps_repro  TEXT,
                severity     TEXT    DEFAULT 'MÉDIA'
                                     CHECK(severity IN ('BAIXA','MÉDIA','ALTA','CRÍTICA')),
                status       TEXT    DEFAULT 'ABERTO'
                                     CHECK(status IN ('ABERTO','EM ANÁLISE','CORRIGIDO','FECHADO','REABERTO')),
                environment  TEXT,
                reported_by  TEXT,
                created_at   TEXT    NOT NULL,
                updated_at   TEXT    NOT NULL
            );
        """)


def now_iso() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")
