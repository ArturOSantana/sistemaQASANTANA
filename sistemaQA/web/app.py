#!/usr/bin/env python3
"""
Sistema QA — Interface Web (Flask)
Uso: python web/app.py
"""
import sys
import os
import json

# garante que os módulos do projeto sejam encontrados
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file

from modules.database import init_db
from modules import (
    projects as proj_mod,
    test_cases as tc_mod,
    scenarios as sc_mod,
    bugs as bug_mod,
    reports as rep_mod,
    csv_io,
    html_report,
)

app = Flask(__name__)
app.secret_key = os.environ.get("QA_SECRET_KEY", os.urandom(32))

# ── constantes de domínio ────────────────────────────────────────────────────
STATUS_TC  = ["NÃO EXECUTADO", "PASSOU", "FALHOU", "BLOQUEADO", "IGNORADO"]
PRIORITY   = ["BAIXA", "MÉDIA", "ALTA", "CRÍTICA"]
STATUS_SC  = ["PENDENTE", "APROVADO", "REPROVADO"]
STATUS_BUG = ["ABERTO", "EM ANÁLISE", "CORRIGIDO", "FECHADO", "REABERTO"]
SEVERITY   = ["BAIXA", "MÉDIA", "ALTA", "CRÍTICA"]


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    summary = rep_mod.get_global_summary()
    projects = proj_mod.list_projects()
    return render_template("index.html", summary=summary, projects=projects)


# ══════════════════════════════════════════════════════════════════════════════
# PROJETOS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/projetos")
def projetos():
    projects = proj_mod.list_projects()
    return render_template("projetos.html", projects=projects)


@app.route("/projetos/novo", methods=["GET", "POST"])
def projeto_novo():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        desc = request.form.get("description", "").strip()
        if not name:
            flash("Nome do projeto é obrigatório.", "error")
            return render_template("projeto_form.html", projeto=None)
        try:
            pid = proj_mod.create_project(name, desc)
            flash(f"Projeto '{name}' criado com sucesso.", "success")
            return redirect(url_for("projeto_detalhe", project_id=pid))
        except Exception:
            flash("Já existe um projeto com esse nome.", "error")
    return render_template("projeto_form.html", projeto=None)


@app.route("/projetos/<int:project_id>")
def projeto_detalhe(project_id):
    projeto = proj_mod.get_project(project_id)
    if not projeto:
        flash("Projeto não encontrado.", "error")
        return redirect(url_for("projetos"))
    summary  = rep_mod.get_project_summary(project_id)
    timeline = rep_mod.get_bugs_timeline(project_id)
    history  = rep_mod.get_cases_history(project_id)
    return render_template(
        "projeto_detalhe.html",
        projeto=projeto,
        summary=summary,
        timeline_json=json.dumps(timeline),
        history_json=json.dumps(history),
    )


@app.route("/projetos/<int:project_id>/editar", methods=["GET", "POST"])
def projeto_editar(project_id):
    projeto = proj_mod.get_project(project_id)
    if not projeto:
        flash("Projeto não encontrado.", "error")
        return redirect(url_for("projetos"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        desc = request.form.get("description", "").strip()
        if not name:
            flash("Nome é obrigatório.", "error")
        else:
            proj_mod.update_project(project_id, name, desc)
            flash("Projeto atualizado.", "success")
            return redirect(url_for("projeto_detalhe", project_id=project_id))
    return render_template("projeto_form.html", projeto=projeto)


@app.route("/projetos/<int:project_id>/excluir", methods=["POST"])
def projeto_excluir(project_id):
    proj_mod.delete_project(project_id)
    flash("Projeto excluído.", "success")
    return redirect(url_for("projetos"))


# ══════════════════════════════════════════════════════════════════════════════
# SUITES DE TESTE
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/projetos/<int:project_id>/suites")
def suites(project_id):
    projeto = proj_mod.get_project(project_id)
    suites  = tc_mod.list_suites(project_id)
    return render_template("suites.html", projeto=projeto, suites=suites)


@app.route("/projetos/<int:project_id>/suites/nova", methods=["POST"])
def suite_nova(project_id):
    name = request.form.get("name", "").strip()
    desc = request.form.get("description", "").strip()
    if not name:
        flash("Nome da suite é obrigatório.", "error")
    else:
        tc_mod.create_suite(project_id, name, desc)
        flash(f"Suite '{name}' criada.", "success")
    return redirect(url_for("suites", project_id=project_id))


@app.route("/suites/<int:suite_id>/excluir", methods=["POST"])
def suite_excluir(suite_id):
    # descobre o project_id para redirecionar
    import sqlite3
    from modules.database import get_connection
    with get_connection() as conn:
        row = conn.execute("SELECT project_id FROM test_suites WHERE id=?", (suite_id,)).fetchone()
    pid = row["project_id"] if row else None
    tc_mod.delete_suite(suite_id)
    flash("Suite excluída.", "success")
    return redirect(url_for("suites", project_id=pid) if pid else url_for("projetos"))


# ══════════════════════════════════════════════════════════════════════════════
# CASOS DE TESTE
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/projetos/<int:project_id>/casos")
def casos(project_id):
    projeto = proj_mod.get_project(project_id)
    cases   = tc_mod.list_all_test_cases(project_id)
    suites  = tc_mod.list_suites(project_id)
    return render_template(
        "casos.html",
        projeto=projeto,
        cases=cases,
        suites=suites,
        STATUS_TC=STATUS_TC,
        PRIORITY=PRIORITY,
    )


@app.route("/projetos/<int:project_id>/casos/novo", methods=["POST"])
def caso_novo(project_id):
    suite_id     = request.form.get("suite_id", type=int)
    title        = request.form.get("title", "").strip()
    description  = request.form.get("description", "").strip()
    preconditions= request.form.get("preconditions", "").strip()
    steps        = request.form.get("steps", "").strip()
    expected     = request.form.get("expected", "").strip()
    priority     = request.form.get("priority", "MÉDIA")
    if not title or not suite_id:
        flash("Título e suite são obrigatórios.", "error")
    else:
        tc_mod.create_test_case(suite_id, title, description, preconditions, steps, expected, priority)
        flash(f"Caso '{title}' criado.", "success")
    return redirect(url_for("casos", project_id=project_id))


@app.route("/casos/<int:case_id>/status", methods=["POST"])
def caso_status(case_id):
    status = request.form.get("status")
    tc_mod.update_test_case_status(case_id, status)
    flash("Status atualizado.", "success")
    pid = request.form.get("project_id", type=int)
    return redirect(url_for("casos", project_id=pid))


@app.route("/casos/<int:case_id>/editar", methods=["GET", "POST"])
def caso_editar(case_id):
    case    = tc_mod.get_test_case(case_id)
    if not case:
        flash("Caso não encontrado.", "error")
        return redirect(url_for("projetos"))
    from modules.database import get_connection
    with get_connection() as conn:
        suite_row = conn.execute(
            "SELECT ts.project_id FROM test_suites ts WHERE ts.id = ?", (case["suite_id"],)
        ).fetchone()
    project_id = suite_row["project_id"] if suite_row else None
    suites     = tc_mod.list_suites(project_id) if project_id else []
    if request.method == "POST":
        tc_mod.update_test_case(
            case_id,
            title        = request.form.get("title", "").strip(),
            description  = request.form.get("description", "").strip(),
            preconditions= request.form.get("preconditions", "").strip(),
            steps        = request.form.get("steps", "").strip(),
            expected     = request.form.get("expected", "").strip(),
            priority     = request.form.get("priority", "MÉDIA"),
        )
        flash("Caso atualizado.", "success")
        return redirect(url_for("casos", project_id=project_id))
    return render_template(
        "caso_form.html",
        case=case,
        suites=suites,
        project_id=project_id,
        PRIORITY=PRIORITY,
        STATUS_TC=STATUS_TC,
    )


@app.route("/casos/<int:case_id>/excluir", methods=["POST"])
def caso_excluir(case_id):
    pid = request.form.get("project_id", type=int)
    tc_mod.delete_test_case(case_id)
    flash("Caso excluído.", "success")
    return redirect(url_for("casos", project_id=pid))


# ══════════════════════════════════════════════════════════════════════════════
# CENÁRIOS GHERKIN
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/projetos/<int:project_id>/cenarios")
def cenarios(project_id):
    projeto   = proj_mod.get_project(project_id)
    scenarios = sc_mod.list_scenarios(project_id)
    return render_template(
        "cenarios.html",
        projeto=projeto,
        scenarios=scenarios,
        STATUS_SC=STATUS_SC,
    )


@app.route("/projetos/<int:project_id>/cenarios/novo", methods=["POST"])
def cenario_novo(project_id):
    title = request.form.get("title", "").strip()
    if not title:
        flash("Título é obrigatório.", "error")
    else:
        sc_mod.create_scenario(
            project_id,
            title,
            given = request.form.get("given", "").strip(),
            when_ = request.form.get("when_", "").strip(),
            then_ = request.form.get("then_", "").strip(),
            tags  = request.form.get("tags",  "").strip(),
        )
        flash(f"Cenário '{title}' criado.", "success")
    return redirect(url_for("cenarios", project_id=project_id))


@app.route("/cenarios/<int:scenario_id>/status", methods=["POST"])
def cenario_status(scenario_id):
    sc_mod.update_scenario_status(scenario_id, request.form.get("status"))
    flash("Status do cenário atualizado.", "success")
    pid = request.form.get("project_id", type=int)
    return redirect(url_for("cenarios", project_id=pid))


@app.route("/cenarios/<int:scenario_id>/excluir", methods=["POST"])
def cenario_excluir(scenario_id):
    pid = request.form.get("project_id", type=int)
    sc_mod.delete_scenario(scenario_id)
    flash("Cenário excluído.", "success")
    return redirect(url_for("cenarios", project_id=pid))


# ══════════════════════════════════════════════════════════════════════════════
# BUGS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/projetos/<int:project_id>/bugs")
def bugs(project_id):
    projeto  = proj_mod.get_project(project_id)
    bug_list = bug_mod.list_bugs(project_id)
    return render_template(
        "bugs.html",
        projeto=projeto,
        bugs=bug_list,
        STATUS_BUG=STATUS_BUG,
        SEVERITY=SEVERITY,
    )


@app.route("/projetos/<int:project_id>/bugs/novo", methods=["POST"])
def bug_novo(project_id):
    title = request.form.get("title", "").strip()
    if not title:
        flash("Título é obrigatório.", "error")
    else:
        bug_mod.create_bug(
            project_id,
            title,
            description = request.form.get("description", "").strip(),
            steps_repro = request.form.get("steps_repro", "").strip(),
            severity    = request.form.get("severity", "MÉDIA"),
            environment = request.form.get("environment", "").strip(),
            reported_by = request.form.get("reported_by", "").strip(),
        )
        flash(f"Bug '{title}' registrado.", "success")
    return redirect(url_for("bugs", project_id=project_id))


@app.route("/bugs/<int:bug_id>/status", methods=["POST"])
def bug_status(bug_id):
    bug_mod.update_bug_status(bug_id, request.form.get("status"))
    flash("Status do bug atualizado.", "success")
    pid = request.form.get("project_id", type=int)
    return redirect(url_for("bugs", project_id=pid))


@app.route("/bugs/<int:bug_id>/editar", methods=["GET", "POST"])
def bug_editar(bug_id):
    bug = bug_mod.get_bug(bug_id)
    if not bug:
        flash("Bug não encontrado.", "error")
        return redirect(url_for("projetos"))
    if request.method == "POST":
        bug_mod.update_bug(
            bug_id,
            title       = request.form.get("title", "").strip(),
            description = request.form.get("description", "").strip(),
            steps_repro = request.form.get("steps_repro", "").strip(),
            severity    = request.form.get("severity", "MÉDIA"),
            environment = request.form.get("environment", "").strip(),
            reported_by = request.form.get("reported_by", "").strip(),
        )
        flash("Bug atualizado.", "success")
        return redirect(url_for("bugs", project_id=bug["project_id"]))
    return render_template(
        "bug_form.html",
        bug=bug,
        SEVERITY=SEVERITY,
        STATUS_BUG=STATUS_BUG,
    )


@app.route("/bugs/<int:bug_id>/excluir", methods=["POST"])
def bug_excluir(bug_id):
    pid = request.form.get("project_id", type=int)
    bug_mod.delete_bug(bug_id)
    flash("Bug excluído.", "success")
    return redirect(url_for("bugs", project_id=pid))


# ══════════════════════════════════════════════════════════════════════════════
# RELATÓRIOS / EXPORTAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/projetos/<int:project_id>/relatorio")
def relatorio(project_id):
    projeto  = proj_mod.get_project(project_id)
    summary  = rep_mod.get_project_summary(project_id)
    timeline = rep_mod.get_bugs_timeline(project_id)
    history  = rep_mod.get_cases_history(project_id)
    path     = html_report.generate_dashboard(summary, projeto["name"], timeline, history)
    flash(f"Dashboard HTML gerado: {path}", "success")
    return redirect(url_for("projeto_detalhe", project_id=project_id))


@app.route("/projetos/<int:project_id>/exportar-csv")
def exportar_csv(project_id):
    paths = csv_io.export_all(project_id)
    flash("CSVs exportados: " + " | ".join(f"{k}: {v}" for k, v in paths.items()), "success")
    return redirect(url_for("projeto_detalhe", project_id=project_id))


# ══════════════════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
