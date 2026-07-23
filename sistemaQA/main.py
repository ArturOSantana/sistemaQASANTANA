#!/usr/bin/env python3
"""
Sistema QA — Interface de Linha de Comando (CLI)
Uso: python main.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

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


# ══════════════════════════════════════════════════════════════
# Utilitários de UI
# ══════════════════════════════════════════════════════════════

BLUE   = "\033[94m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def c(text, color): return f"{color}{text}{RESET}"
def header(title): print(f"\n{BOLD}{BLUE}{'═'*55}{RESET}\n{BOLD}  {title}{RESET}\n{BOLD}{BLUE}{'═'*55}{RESET}")
def sep():          print(f"{BLUE}{'─'*55}{RESET}")
def ok(msg):        print(f"{GREEN}✔  {msg}{RESET}")
def err(msg):       print(f"{RED}✖  {msg}{RESET}")
def warn(msg):      print(f"{YELLOW}⚠  {msg}{RESET}")
def info(msg):      print(f"{CYAN}ℹ  {msg}{RESET}")

def ask(prompt, default="") -> str:
    val = input(f"  {prompt}{f' [{default}]' if default else ''}: ").strip()
    return val if val else default

def ask_choice(prompt, options: list) -> str:
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        v = input(f"  {prompt} [1-{len(options)}]: ").strip()
        if v.isdigit() and 1 <= int(v) <= len(options):
            return options[int(v) - 1]
        warn("Opção inválida.")

def pick_project() -> dict | None:
    projects = proj_mod.list_projects()
    if not projects:
        warn("Nenhum projeto cadastrado.")
        return None
    header("Selecionar Projeto")
    for i, p in enumerate(projects, 1):
        print(f"  {i}. {c(p['name'], BOLD)}  (id={p['id']})")
    while True:
        v = input(f"  Escolha [1-{len(projects)}] ou 0 para cancelar: ").strip()
        if v == "0": return None
        if v.isdigit() and 1 <= int(v) <= len(projects):
            return projects[int(v) - 1]
        warn("Opção inválida.")


# ══════════════════════════════════════════════════════════════
# PROJETOS
# ══════════════════════════════════════════════════════════════

def menu_projects():
    while True:
        header("Projetos")
        print("  1. Listar projetos")
        print("  2. Criar projeto")
        print("  3. Excluir projeto")
        print("  0. Voltar")
        sep()
        opt = input("  Opção: ").strip()
        if opt == "0":
            break
        elif opt == "1":
            projects = proj_mod.list_projects()
            if not projects:
                warn("Nenhum projeto cadastrado.")
            else:
                sep()
                for p in projects:
                    print(f"  [{p['id']}] {c(p['name'], BOLD)} — {p['description'] or 'sem descrição'}")
        elif opt == "2":
            name = ask("Nome do projeto")
            if not name:
                warn("Nome obrigatório.")
                continue
            desc = ask("Descrição (opcional)")
            pid = proj_mod.create_project(name, desc)
            ok(f"Projeto '{name}' criado com id={pid}")
        elif opt == "3":
            p = pick_project()
            if p:
                confirm = ask(f"Confirma exclusão do projeto '{p['name']}'? (s/n)", "n")
                if confirm.lower() == "s":
                    proj_mod.delete_project(p["id"])
                    ok("Projeto excluído.")


# ══════════════════════════════════════════════════════════════
# SUITES DE TESTE
# ══════════════════════════════════════════════════════════════

def menu_suites():
    p = pick_project()
    if not p:
        return
    while True:
        header(f"Suites de Teste — {p['name']}")
        suites = tc_mod.list_suites(p["id"])
        print("  1. Listar suites")
        print("  2. Criar suite")
        print("  3. Excluir suite")
        print("  0. Voltar")
        sep()
        opt = input("  Opção: ").strip()
        if opt == "0":
            break
        elif opt == "1":
            if not suites:
                warn("Nenhuma suite cadastrada.")
            else:
                for s in suites:
                    print(f"  [{s['id']}] {c(s['name'], BOLD)} — {s['description'] or 'sem descrição'}")
        elif opt == "2":
            name = ask("Nome da suite")
            if not name:
                warn("Nome obrigatório.")
                continue
            desc = ask("Descrição (opcional)")
            sid = tc_mod.create_suite(p["id"], name, desc)
            ok(f"Suite '{name}' criada com id={sid}")
        elif opt == "3":
            suites = tc_mod.list_suites(p["id"])
            if not suites:
                warn("Nenhuma suite cadastrada.")
                continue
            for i, s in enumerate(suites, 1):
                print(f"  {i}. [{s['id']}] {s['name']}")
            idx = input("  Número da suite para excluir (0=cancelar): ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(suites):
                tc_mod.delete_suite(suites[int(idx)-1]["id"])
                ok("Suite excluída.")


# ══════════════════════════════════════════════════════════════
# CASOS DE TESTE
# ══════════════════════════════════════════════════════════════

STATUS_TC  = ["NÃO EXECUTADO", "PASSOU", "FALHOU", "BLOQUEADO", "IGNORADO"]
PRIORITY   = ["BAIXA", "MÉDIA", "ALTA", "CRÍTICA"]

def badge_tc(status):
    colors = {"PASSOU": GREEN, "FALHOU": RED, "BLOQUEADO": YELLOW, "IGNORADO": CYAN, "NÃO EXECUTADO": BLUE}
    return c(f"[{status}]", colors.get(status, RESET))

def menu_test_cases():
    p = pick_project()
    if not p:
        return
    suites = tc_mod.list_suites(p["id"])
    if not suites:
        warn("Crie uma suite de teste primeiro.")
        return

    while True:
        header(f"Casos de Teste — {p['name']}")
        print("  1. Listar todos os casos")
        print("  2. Adicionar caso de teste")
        print("  3. Registrar execução (atualizar status)")
        print("  4. Editar caso de teste")
        print("  5. Excluir caso de teste")
        print("  0. Voltar")
        sep()
        opt = input("  Opção: ").strip()
        if opt == "0":
            break
        elif opt == "1":
            cases = tc_mod.list_all_test_cases(p["id"])
            if not cases:
                warn("Nenhum caso de teste cadastrado.")
            else:
                sep()
                for tc in cases:
                    print(f"  [{tc['id']}] {c(tc['title'], BOLD)}  {badge_tc(tc['status'])}  "
                          f"prioridade={tc['priority']}  suite={tc['suite_name']}")
                    if tc["description"]:
                        print(f"       {tc['description'][:80]}")
        elif opt == "2":
            print("\n  Suites disponíveis:")
            for i, s in enumerate(suites, 1):
                print(f"    {i}. {s['name']}")
            idx = input("  Suite [número]: ").strip()
            if not idx.isdigit() or not (1 <= int(idx) <= len(suites)):
                warn("Suite inválida.")
                continue
            suite = suites[int(idx)-1]
            title = ask("Título do caso")
            if not title: warn("Título obrigatório."); continue
            desc         = ask("Descrição")
            preconditions = ask("Pré-condições")
            steps        = ask("Passos (separe por | )")
            expected     = ask("Resultado esperado")
            priority     = ask_choice("Prioridade", PRIORITY)
            cid = tc_mod.create_test_case(suite["id"], title, desc, preconditions, steps, expected, priority)
            ok(f"Caso '{title}' criado com id={cid}")
        elif opt == "3":
            cases = tc_mod.list_all_test_cases(p["id"])
            if not cases:
                warn("Nenhum caso cadastrado."); continue
            sep()
            for i, tc in enumerate(cases, 1):
                print(f"  {i}. [{tc['id']}] {tc['title']}  {badge_tc(tc['status'])}")
            idx = input("  Número do caso [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(cases):
                tc = cases[int(idx)-1]
                new_status = ask_choice("Novo status", STATUS_TC)
                tc_mod.update_test_case_status(tc["id"], new_status)
                ok(f"Status atualizado para '{new_status}'")
        elif opt == "4":
            cases = tc_mod.list_all_test_cases(p["id"])
            if not cases:
                warn("Nenhum caso cadastrado."); continue
            for i, tc in enumerate(cases, 1):
                print(f"  {i}. [{tc['id']}] {tc['title']}")
            idx = input("  Número do caso [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(cases):
                tc = cases[int(idx)-1]
                info(f"Deixe em branco para manter o valor atual.")
                title = ask(f"Título", tc["title"])
                desc  = ask(f"Descrição", tc["description"] or "")
                prec  = ask(f"Pré-condições", tc["preconditions"] or "")
                steps = ask(f"Passos", tc["steps"] or "")
                exp   = ask(f"Resultado esperado", tc["expected"] or "")
                priority = ask_choice("Prioridade", PRIORITY)
                tc_mod.update_test_case(tc["id"], title=title, description=desc,
                                        preconditions=prec, steps=steps,
                                        expected=exp, priority=priority)
                ok("Caso atualizado.")
        elif opt == "5":
            cases = tc_mod.list_all_test_cases(p["id"])
            if not cases:
                warn("Nenhum caso cadastrado."); continue
            for i, tc in enumerate(cases, 1):
                print(f"  {i}. [{tc['id']}] {tc['title']}")
            idx = input("  Número do caso [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(cases):
                tc_mod.delete_test_case(cases[int(idx)-1]["id"])
                ok("Caso excluído.")


# ══════════════════════════════════════════════════════════════
# CENÁRIOS
# ══════════════════════════════════════════════════════════════

STATUS_SC = ["PENDENTE", "APROVADO", "REPROVADO"]

def menu_scenarios():
    p = pick_project()
    if not p: return
    while True:
        header(f"Cenários de Teste — {p['name']}")
        print("  1. Listar cenários")
        print("  2. Criar cenário (Gherkin)")
        print("  3. Atualizar status do cenário")
        print("  4. Excluir cenário")
        print("  0. Voltar")
        sep()
        opt = input("  Opção: ").strip()
        if opt == "0": break
        elif opt == "1":
            scenarios = sc_mod.list_scenarios(p["id"])
            if not scenarios:
                warn("Nenhum cenário cadastrado.")
            else:
                sep()
                for sc in scenarios:
                    st_color = GREEN if sc["status"]=="APROVADO" else (RED if sc["status"]=="REPROVADO" else YELLOW)
                    print(f"\n  [{sc['id']}] {c(sc['title'], BOLD)} — {c(sc['status'], st_color)}")
                    if sc["given"]:  print(f"    {c('Dado que', CYAN)}: {sc['given']}")
                    if sc["when_"]:  print(f"    {c('Quando',   CYAN)}: {sc['when_']}")
                    if sc["then_"]:  print(f"    {c('Então',    CYAN)}: {sc['then_']}")
                    if sc["tags"]:   print(f"    Tags: {sc['tags']}")
        elif opt == "2":
            title = ask("Título do cenário")
            if not title: warn("Obrigatório."); continue
            given  = ask("Dado que (Given)")
            when_  = ask("Quando (When)")
            then_  = ask("Então (Then)")
            tags   = ask("Tags (separadas por vírgula)")
            sid = sc_mod.create_scenario(p["id"], title, given, when_, then_, tags)
            ok(f"Cenário '{title}' criado com id={sid}")
        elif opt == "3":
            scenarios = sc_mod.list_scenarios(p["id"])
            if not scenarios:
                warn("Nenhum cenário cadastrado."); continue
            for i, sc in enumerate(scenarios, 1):
                print(f"  {i}. [{sc['id']}] {sc['title']}")
            idx = input("  Número [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(scenarios):
                new_status = ask_choice("Novo status", STATUS_SC)
                sc_mod.update_scenario_status(scenarios[int(idx)-1]["id"], new_status)
                ok(f"Cenário atualizado para '{new_status}'")
        elif opt == "4":
            scenarios = sc_mod.list_scenarios(p["id"])
            if not scenarios:
                warn("Nenhum cenário."); continue
            for i, sc in enumerate(scenarios, 1):
                print(f"  {i}. [{sc['id']}] {sc['title']}")
            idx = input("  Número [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(scenarios):
                sc_mod.delete_scenario(scenarios[int(idx)-1]["id"])
                ok("Cenário excluído.")


# ══════════════════════════════════════════════════════════════
# BUGS
# ══════════════════════════════════════════════════════════════

SEV_OPTS    = ["BAIXA", "MÉDIA", "ALTA", "CRÍTICA"]
STATUS_BUG  = ["ABERTO", "EM ANÁLISE", "CORRIGIDO", "FECHADO", "REABERTO"]

def badge_bug(severity):
    colors = {"BAIXA": CYAN, "MÉDIA": YELLOW, "ALTA": RED, "CRÍTICA": "\033[35m"}
    return c(f"[{severity}]", colors.get(severity, RESET))

def menu_bugs():
    p = pick_project()
    if not p: return
    while True:
        header(f"Bugs — {p['name']}")
        print("  1. Listar bugs")
        print("  2. Registrar novo bug")
        print("  3. Atualizar status do bug")
        print("  4. Editar bug")
        print("  5. Excluir bug")
        print("  6. Exportar cartões de bugs (HTML)")
        print("  0. Voltar")
        sep()
        opt = input("  Opção: ").strip()
        if opt == "0": break
        elif opt == "1":
            bugs = bug_mod.list_bugs(p["id"])
            if not bugs:
                warn("Nenhum bug registrado.")
            else:
                sep()
                for b in bugs:
                    st_c = GREEN if b["status"] in ("CORRIGIDO","FECHADO") else RED
                    print(f"  [{b['id']}] {c(b['title'], BOLD)}  {badge_bug(b['severity'])}  {c(b['status'], st_c)}")
                    if b["description"]:
                        print(f"       {b['description'][:80]}")
                    if b["environment"]:
                        print(f"       Ambiente: {b['environment']}")
                    if b["reported_by"]:
                        print(f"       Reportado por: {b['reported_by']}")
        elif opt == "2":
            title = ask("Título do bug")
            if not title: warn("Obrigatório."); continue
            desc    = ask("Descrição do bug")
            steps   = ask("Passos para reproduzir")
            sev     = ask_choice("Severidade", SEV_OPTS)
            env     = ask("Ambiente (ex: produção, homolog, dev)")
            who     = ask("Reportado por")
            bid = bug_mod.create_bug(p["id"], title, desc, steps, sev, env, who)
            ok(f"Bug '{title}' registrado com id={bid}")
        elif opt == "3":
            bugs = bug_mod.list_bugs(p["id"])
            if not bugs:
                warn("Nenhum bug cadastrado."); continue
            for i, b in enumerate(bugs, 1):
                print(f"  {i}. [{b['id']}] {b['title']}  {badge_bug(b['severity'])}")
            idx = input("  Número [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(bugs):
                new_status = ask_choice("Novo status", STATUS_BUG)
                bug_mod.update_bug_status(bugs[int(idx)-1]["id"], new_status)
                ok(f"Status atualizado para '{new_status}'")
        elif opt == "4":
            bugs = bug_mod.list_bugs(p["id"])
            if not bugs:
                warn("Nenhum bug."); continue
            for i, b in enumerate(bugs, 1):
                print(f"  {i}. [{b['id']}] {b['title']}")
            idx = input("  Número [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(bugs):
                b = bugs[int(idx)-1]
                info("Deixe em branco para manter valor atual.")
                title  = ask("Título", b["title"])
                desc   = ask("Descrição", b["description"] or "")
                steps  = ask("Passos de reprodução", b["steps_repro"] or "")
                sev    = ask_choice("Severidade", SEV_OPTS)
                env    = ask("Ambiente", b["environment"] or "")
                who    = ask("Reportado por", b["reported_by"] or "")
                bug_mod.update_bug(b["id"], title=title, description=desc,
                                   steps_repro=steps, severity=sev,
                                   environment=env, reported_by=who)
                ok("Bug atualizado.")
        elif opt == "5":
            bugs = bug_mod.list_bugs(p["id"])
            if not bugs:
                warn("Nenhum bug."); continue
            for i, b in enumerate(bugs, 1):
                print(f"  {i}. [{b['id']}] {b['title']}")
            idx = input("  Número [0=cancelar]: ").strip()
            if not idx.isdigit() or int(idx) == 0: continue
            if 1 <= int(idx) <= len(bugs):
                bug_mod.delete_bug(bugs[int(idx)-1]["id"])
                ok("Bug excluído.")
        elif opt == "6":
            bugs = bug_mod.list_bugs(p["id"])
            if not bugs:
                warn("Nenhum bug registrado."); continue
            path = html_report.generate_bug_cards(bugs, p["name"])
            ok(f"Cartões gerados: {path}")
            info("Abra o arquivo no navegador e use Ctrl+P para imprimir / salvar como PDF.")


# ══════════════════════════════════════════════════════════════
# RELATÓRIOS
# ══════════════════════════════════════════════════════════════

def menu_reports():
    p = pick_project()
    if not p: return
    while True:
        header(f"Relatórios — {p['name']}")
        print("  1. Resumo no terminal")
        print("  2. Gerar dashboard HTML")
        print("  3. Exportar CSV (backup)")
        print("  4. Importar CSV")
        print("  0. Voltar")
        sep()
        opt = input("  Opção: ").strip()
        if opt == "0": break
        elif opt == "1":
            s = rep_mod.get_project_summary(p["id"])
            sep()
            print(f"\n  {c('CASOS DE TESTE', BOLD)}")
            print(f"  Total       : {s['total_cases']}")
            print(f"  Executados  : {s['executed']}  (cobertura: {c(str(s['coverage'])+'%', CYAN)})")
            print(f"  Passaram    : {c(str(s['passed']), GREEN)}")
            print(f"  Falharam    : {c(str(s['failed']), RED)}")
            print(f"  Bloqueados  : {c(str(s['blocked']), YELLOW)}")
            print(f"  Ignorados   : {s['skipped']}")
            print(f"  Não exec.   : {s['not_run']}")
            print(f"  Taxa aprovação : {c(str(s['pass_rate'])+'%', GREEN)}")
            print(f"\n  {c('BUGS', BOLD)}")
            print(f"  Total       : {c(str(s['total_bugs']), RED)}")
            for k, v in s["bugs_by_severity"].items():
                print(f"  {k:<12}: {v}")
            print(f"\n  {c('STATUS DOS BUGS', BOLD)}")
            for k, v in s["bugs_by_status"].items():
                print(f"  {k:<14}: {v}")
            print(f"\n  {c('CENÁRIOS', BOLD)}")
            print(f"  Total       : {s['total_scenarios']}")
            for k, v in s["scenarios_by_status"].items():
                print(f"  {k:<12}: {v}")
            sep()
        elif opt == "2":
            summary  = rep_mod.get_project_summary(p["id"])
            timeline = rep_mod.get_bugs_timeline(p["id"])
            history  = rep_mod.get_cases_history(p["id"])
            path = html_report.generate_dashboard(summary, p["name"], timeline, history)
            ok(f"Dashboard gerado: {path}")
            info("Abra o arquivo no navegador para visualizar.")
        elif opt == "3":
            paths = csv_io.export_all(p["id"])
            ok("Arquivos exportados:")
            for k, v in paths.items():
                print(f"  {k}: {v}")
        elif opt == "4":
            print("  1. Importar casos de teste")
            print("  2. Importar bugs")
            sub = input("  Opção: ").strip()
            if sub == "1":
                csv_path = ask("Caminho do arquivo CSV")
                if not os.path.exists(csv_path):
                    err("Arquivo não encontrado."); continue
                suites = tc_mod.list_suites(p["id"])
                if not suites:
                    warn("Crie uma suite primeiro."); continue
                for i, s in enumerate(suites, 1):
                    print(f"  {i}. {s['name']}")
                idx = input("  Suite destino [número]: ").strip()
                if not idx.isdigit() or not (1 <= int(idx) <= len(suites)): continue
                count = csv_io.import_test_cases(p["id"], csv_path, suites[int(idx)-1]["id"])
                ok(f"{count} casos importados.")
            elif sub == "2":
                csv_path = ask("Caminho do arquivo CSV de bugs")
                if not os.path.exists(csv_path):
                    err("Arquivo não encontrado."); continue
                count = csv_io.import_bugs(p["id"], csv_path)
                ok(f"{count} bugs importados.")


# ══════════════════════════════════════════════════════════════
# MENU PRINCIPAL
# ══════════════════════════════════════════════════════════════

def main():
    init_db()
    print(f"\n{BOLD}{BLUE}")
    print("  ╔══════════════════════════════════════════╗")
    print("  ║         SISTEMA QA — Gestão de Testes    ║")
    print("  ╚══════════════════════════════════════════╝")
    print(RESET)

    while True:
        glo = rep_mod.get_global_summary()
        info(f"Projetos: {glo['total_projects']}  |  "
             f"Casos: {glo['total_cases']}  |  "
             f"Bugs abertos: {c(str(glo['open_bugs']), RED)}  |  "
             f"Cobertura global: {c(str(glo['global_coverage'])+'%', CYAN)}")
        sep()
        print(f"\n  {BOLD}1.{RESET} Gerenciar Projetos")
        print(f"  {BOLD}2.{RESET} Suites de Teste")
        print(f"  {BOLD}3.{RESET} Casos de Teste")
        print(f"  {BOLD}4.{RESET} Cenários (Gherkin)")
        print(f"  {BOLD}5.{RESET} Bugs")
        print(f"  {BOLD}6.{RESET} Relatórios / Dashboard / Backup")
        print(f"  {BOLD}0.{RESET} Sair")
        sep()
        opt = input("  Opção: ").strip()

        if opt == "0":
            print(f"\n{GREEN}  Até logo!{RESET}\n")
            sys.exit(0)
        elif opt == "1": menu_projects()
        elif opt == "2": menu_suites()
        elif opt == "3": menu_test_cases()
        elif opt == "4": menu_scenarios()
        elif opt == "5": menu_bugs()
        elif opt == "6": menu_reports()
        else:
            warn("Opção inválida.")


if __name__ == "__main__":
    main()
