"""
Módulo responsável por gerar o dashboard HTML do Sistema QA.
"""
import json
import os
from datetime import datetime

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def generate_dashboard(summary: dict, project_name: str, bugs_timeline: list,
                       cases_history: list, output_path: str | None = None) -> str:
    """Gera o HTML do dashboard e salva em reports/. Retorna o caminho do arquivo."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_path is None:
        safe_name = project_name.replace(" ", "_").lower()
        output_path = os.path.join(REPORTS_DIR, f"dashboard_{safe_name}_{ts}.html")

    # ── dados para os gráficos ────────────────────────────────────────
    cases_labels  = list(summary["cases_by_status"].keys())
    cases_values  = list(summary["cases_by_status"].values())
    cases_colors  = ["#10b981","#ef4444","#f59e0b","#6b7280","#3b82f6"]

    bug_sev_labels  = list(summary["bugs_by_severity"].keys())
    bug_sev_values  = list(summary["bugs_by_severity"].values())
    bug_sev_colors  = ["#6b7280","#f59e0b","#ef4444","#7c3aed"]

    bug_st_labels = list(summary["bugs_by_status"].keys())
    bug_st_values = list(summary["bugs_by_status"].values())

    # ── gráfico de linha: bugs por dia ────────────────────────────────
    timeline_dates  = [r["day"] for r in bugs_timeline] or ["Sem dados"]
    timeline_counts = [r["cnt"] for r in bugs_timeline] or [0]

    # ── gráfico de linha: testes executados por dia ───────────────────
    hist_dates  = [r["day"] for r in cases_history] or ["Sem dados"]
    hist_passed = [r["passed"] for r in cases_history] or [0]
    hist_failed = [r["failed"] for r in cases_history] or [0]

    coverage   = summary["coverage"]
    pass_rate  = summary["pass_rate"]
    gauge_cov_stroke  = 283 - (283 * coverage / 100)
    gauge_pass_stroke = 283 - (283 * pass_rate / 100)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QA Dashboard — {project_name}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system,"Segoe UI",system-ui,sans-serif; background:#f0f4f8; color:#1f2328; font-size:14px; }}
  header {{ background:#1e3a5f; color:#fff; padding:18px 32px; display:flex; align-items:center; gap:16px; }}
  header h1 {{ font-size:20px; font-weight:700; letter-spacing:.5px; }}
  header span {{ font-size:12px; opacity:.7; margin-left:auto; }}
  .container {{ max-width:1280px; margin:0 auto; padding:24px 16px; }}
  h2 {{ font-size:15px; font-weight:700; color:#1e3a5f; margin-bottom:14px; border-left:4px solid #3b82d4; padding-left:10px; }}
  .kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:28px; }}
  .kpi {{ background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:18px 14px; text-align:center; }}
  .kpi .value {{ font-size:32px; font-weight:800; color:#1e3a5f; line-height:1; }}
  .kpi .label {{ font-size:11px; color:#57606a; margin-top:6px; text-transform:uppercase; letter-spacing:.4px; }}
  .kpi.green  .value {{ color:#10b981; }}
  .kpi.red    .value {{ color:#ef4444; }}
  .kpi.orange .value {{ color:#f59e0b; }}
  .kpi.purple .value {{ color:#7c5cd8; }}
  .charts-row {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; margin-bottom:28px; }}
  .card {{ background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:20px; }}
  .gauge-wrap {{ display:flex; gap:32px; justify-content:center; align-items:center; flex-wrap:wrap; padding:8px 0; }}
  .gauge {{ text-align:center; }}
  .gauge svg {{ width:110px; height:110px; }}
  circle.track {{ fill:none; stroke:#e5e7eb; stroke-width:14; }}
  circle.fill-cov  {{ fill:none; stroke:#3b82d4; stroke-width:14; stroke-linecap:round; transition:stroke-dashoffset .6s ease;
                      stroke-dasharray:283; stroke-dashoffset:{gauge_cov_stroke:.1f};
                      transform:rotate(-90deg); transform-origin:50% 50%; }}
  circle.fill-pass {{ fill:none; stroke:#10b981; stroke-width:14; stroke-linecap:round; transition:stroke-dashoffset .6s ease;
                      stroke-dasharray:283; stroke-dashoffset:{gauge_pass_stroke:.1f};
                      transform:rotate(-90deg); transform-origin:50% 50%; }}
  .gauge-val {{ font-size:20px; font-weight:800; }}
  .gauge-lbl {{ font-size:11px; color:#57606a; margin-top:4px; }}
  .chart-wrap {{ position:relative; height:220px; }}
  .section-title {{ font-size:15px; font-weight:700; color:#1e3a5f; margin:28px 0 14px; border-left:4px solid #3b82d4; padding-left:10px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ background:#f7f8fa; text-align:left; padding:9px 12px; font-weight:600; border-bottom:2px solid #e5e7eb; white-space:nowrap; }}
  td {{ padding:8px 12px; border-bottom:1px solid #f0f4f8; vertical-align:top; }}
  tr:last-child td {{ border-bottom:none; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }}
  .b-passou      {{ background:#d1fae5; color:#065f46; }}
  .b-falhou      {{ background:#fee2e2; color:#991b1b; }}
  .b-bloqueado   {{ background:#fef3c7; color:#92400e; }}
  .b-ignorado    {{ background:#f3f4f6; color:#374151; }}
  .b-nao         {{ background:#e0e7ff; color:#3730a3; }}
  .b-aberto      {{ background:#fee2e2; color:#991b1b; }}
  .b-analise     {{ background:#fef3c7; color:#92400e; }}
  .b-corrigido   {{ background:#d1fae5; color:#065f46; }}
  .b-fechado     {{ background:#f3f4f6; color:#374151; }}
  .b-reaberto    {{ background:#ede9fe; color:#5b21b6; }}
  .b-baixa       {{ background:#f3f4f6; color:#374151; }}
  .b-media       {{ background:#fef3c7; color:#92400e; }}
  .b-alta        {{ background:#fee2e2; color:#991b1b; }}
  .b-critica     {{ background:#7c3aed; color:#fff; }}
  .b-pendente    {{ background:#e0e7ff; color:#3730a3; }}
  .b-aprovado    {{ background:#d1fae5; color:#065f46; }}
  .b-reprovado   {{ background:#fee2e2; color:#991b1b; }}
  footer {{ text-align:center; padding:24px 0 16px; color:#57606a; font-size:11px; border-top:1px solid #e5e7eb; margin-top:32px; }}
</style>
</head>
<body>
<header>
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
  </svg>
  <h1>QA Dashboard — {project_name}</h1>
  <span>Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</span>
</header>

<div class="container">

  <!-- KPIs principais -->
  <h2>Visão Geral</h2>
  <div class="kpi-grid">
    <div class="kpi"><div class="value">{summary['total_cases']}</div><div class="label">Casos de Teste</div></div>
    <div class="kpi green"><div class="value">{summary['passed']}</div><div class="label">Passaram</div></div>
    <div class="kpi red"><div class="value">{summary['failed']}</div><div class="label">Falharam</div></div>
    <div class="kpi orange"><div class="value">{summary['blocked']}</div><div class="label">Bloqueados</div></div>
    <div class="kpi"><div class="value">{summary['not_run']}</div><div class="label">Não Executados</div></div>
    <div class="kpi red"><div class="value">{summary['total_bugs']}</div><div class="label">Bugs Registrados</div></div>
    <div class="kpi purple"><div class="value">{summary['total_scenarios']}</div><div class="label">Cenários</div></div>
  </div>

  <!-- Gauges de cobertura -->
  <div class="charts-row">
    <div class="card">
      <h2>Cobertura &amp; Taxa de Aprovação</h2>
      <div class="gauge-wrap">
        <div class="gauge">
          <svg viewBox="0 0 100 100">
            <circle class="track"    cx="50" cy="50" r="45"/>
            <circle class="fill-cov" cx="50" cy="50" r="45"/>
            <text x="50" y="54" text-anchor="middle" font-size="18" font-weight="800" fill="#3b82d4">{coverage}%</text>
          </svg>
          <div class="gauge-lbl">Cobertura</div>
        </div>
        <div class="gauge">
          <svg viewBox="0 0 100 100">
            <circle class="track"     cx="50" cy="50" r="45"/>
            <circle class="fill-pass" cx="50" cy="50" r="45"/>
            <text x="50" y="54" text-anchor="middle" font-size="18" font-weight="800" fill="#10b981">{pass_rate}%</text>
          </svg>
          <div class="gauge-lbl">Taxa de Aprovação</div>
        </div>
      </div>
    </div>

    <!-- Donut: status dos testes -->
    <div class="card">
      <h2>Status dos Casos de Teste</h2>
      <div class="chart-wrap"><canvas id="chartCases"></canvas></div>
    </div>

    <!-- Donut: bugs por severidade -->
    <div class="card">
      <h2>Bugs por Severidade</h2>
      <div class="chart-wrap"><canvas id="chartBugSev"></canvas></div>
    </div>
  </div>

  <!-- Linha: bugs por dia e histórico de execução -->
  <div class="charts-row">
    <div class="card">
      <h2>Bugs Registrados por Dia</h2>
      <div class="chart-wrap"><canvas id="chartTimeline"></canvas></div>
    </div>
    <div class="card">
      <h2>Histórico de Execução de Testes</h2>
      <div class="chart-wrap"><canvas id="chartHistory"></canvas></div>
    </div>
    <div class="card">
      <h2>Bugs por Status</h2>
      <div class="chart-wrap"><canvas id="chartBugSt"></canvas></div>
    </div>
  </div>

</div>

<footer>
  Sistema QA — Relatório gerado automaticamente &nbsp;|&nbsp; <strong>Made with IBM Bob</strong>
</footer>

<script>
const casesLabels  = {_json(cases_labels)};
const casesValues  = {_json(cases_values)};
const casesColors  = {_json(cases_colors)};
const bugSevLabels = {_json(bug_sev_labels)};
const bugSevValues = {_json(bug_sev_values)};
const bugSevColors = {_json(bug_sev_colors)};
const bugStLabels  = {_json(bug_st_labels)};
const bugStValues  = {_json(bug_st_values)};
const tlDates      = {_json(timeline_dates)};
const tlCounts     = {_json(timeline_counts)};
const histDates    = {_json(hist_dates)};
const histPassed   = {_json(hist_passed)};
const histFailed   = {_json(hist_failed)};

const opts = {{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{position:'bottom',labels:{{boxWidth:12,font:{{size:11}}}}}}}}}};

new Chart(document.getElementById('chartCases'), {{
  type:'doughnut', data:{{labels:casesLabels, datasets:[{{data:casesValues, backgroundColor:casesColors, borderWidth:2}}]}},
  options:{{...opts}}
}});

new Chart(document.getElementById('chartBugSev'), {{
  type:'doughnut', data:{{labels:bugSevLabels, datasets:[{{data:bugSevValues, backgroundColor:bugSevColors, borderWidth:2}}]}},
  options:{{...opts}}
}});

new Chart(document.getElementById('chartBugSt'), {{
  type:'bar',
  data:{{labels:bugStLabels, datasets:[{{label:'Bugs', data:bugStValues, backgroundColor:'#3b82d4', borderRadius:4}}]}},
  options:{{...opts, plugins:{{legend:{{display:false}}}}, scales:{{y:{{beginAtZero:true, ticks:{{precision:0}}}}}}}}
}});

new Chart(document.getElementById('chartTimeline'), {{
  type:'line',
  data:{{labels:tlDates, datasets:[{{label:'Bugs', data:tlCounts, borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,.1)', tension:.3, fill:true, pointRadius:3}}]}},
  options:{{...opts, plugins:{{legend:{{display:false}}}}, scales:{{y:{{beginAtZero:true, ticks:{{precision:0}}}}}}}}
}});

new Chart(document.getElementById('chartHistory'), {{
  type:'line',
  data:{{labels:histDates, datasets:[
    {{label:'Passou', data:histPassed, borderColor:'#10b981', backgroundColor:'rgba(16,185,129,.1)', tension:.3, fill:true, pointRadius:3}},
    {{label:'Falhou', data:histFailed, borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,.08)', tension:.3, fill:true, pointRadius:3}}
  ]}},
  options:{{...opts, scales:{{y:{{beginAtZero:true, ticks:{{precision:0}}}}}}}}
}});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def generate_bug_cards(bugs: list, project_name: str, output_path: str | None = None) -> str:
    """Gera um HTML com cartões visuais de bugs organizados por severidade.
    Ideal para imprimir ou compartilhar. Retorna o caminho do arquivo."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_path is None:
        safe_name = project_name.replace(" ", "_").lower()
        output_path = os.path.join(REPORTS_DIR, f"bug_cards_{safe_name}_{ts}.html")

    SEV_ORDER = ["CRÍTICA", "ALTA", "MÉDIA", "BAIXA"]
    SEV_STYLE = {
        "CRÍTICA": ("sev-critica", "#7c3aed", "#fff"),
        "ALTA":    ("sev-alta",    "#ef4444", "#fff"),
        "MÉDIA":   ("sev-media",   "#f59e0b", "#1f2328"),
        "BAIXA":   ("sev-baixa",   "#6b7280", "#fff"),
    }
    STATUS_CLASS = {
        "ABERTO":      "st-aberto",
        "EM ANÁLISE":  "st-analise",
        "CORRIGIDO":   "st-corrigido",
        "FECHADO":     "st-fechado",
        "REABERTO":    "st-reaberto",
    }

    # Agrupa bugs por severidade
    grouped: dict[str, list] = {sev: [] for sev in SEV_ORDER}
    for b in bugs:
        sev = b.get("severity", "BAIXA").upper()
        if sev not in grouped:
            sev = "BAIXA"
        grouped[sev].append(b)

    # Gera seções HTML
    sections_html = ""
    total = len(bugs)
    for sev in SEV_ORDER:
        group = grouped[sev]
        if not group:
            continue
        _, header_bg, header_fg = SEV_STYLE.get(sev, ("", "#6b7280", "#fff"))
        cards_html = ""
        for b in group:
            bid      = b.get("id", "—")
            title    = b.get("title", "Sem título")
            desc     = b.get("description", "") or ""
            steps    = b.get("steps_repro", "") or ""
            env      = b.get("environment", "") or ""
            who      = b.get("reported_by", "") or ""
            status   = b.get("status", "ABERTO")
            created  = (b.get("created_at") or "")[:10]
            st_cls   = STATUS_CLASS.get(status, "st-aberto")
            desc_row  = f'<div class="field"><span class="flabel">Descrição</span><span class="fval">{desc}</span></div>' if desc else ""
            steps_row = f'<div class="field"><span class="flabel">Passos p/ reproduzir</span><span class="fval steps">{steps}</span></div>' if steps else ""
            env_row   = f'<div class="field"><span class="flabel">Ambiente</span><span class="fval">{env}</span></div>' if env else ""
            who_row   = f'<div class="field"><span class="flabel">Reportado por</span><span class="fval">{who}</span></div>' if who else ""
            cards_html += f"""
      <div class="bug-card">
        <div class="card-header" style="background:{header_bg};color:{header_fg};">
          <span class="bug-id">#{bid}</span>
          <span class="bug-title">{title}</span>
          <span class="bug-status {st_cls}">{status}</span>
        </div>
        <div class="card-body">
          {desc_row}
          {steps_row}
          {env_row}
          {who_row}
          <div class="field meta"><span class="flabel">Criado em</span><span class="fval">{created}</span></div>
        </div>
      </div>"""

        sections_html += f"""
  <div class="sev-section">
    <div class="sev-title" style="background:{header_bg};color:{header_fg};">
      {sev} &nbsp;<span class="sev-count">{len(group)} bug{'s' if len(group)>1 else ''}</span>
    </div>
    <div class="cards-grid">
      {cards_html}
    </div>
  </div>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cartões de Bug — {project_name}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system,"Segoe UI",system-ui,sans-serif; background:#f0f4f8; color:#1f2328; font-size:14px; }}
  header {{ background:#1e3a5f; color:#fff; padding:16px 32px; display:flex; align-items:center; gap:12px; }}
  header h1 {{ font-size:18px; font-weight:700; }}
  header .meta {{ font-size:12px; opacity:.7; margin-left:auto; }}
  .container {{ max-width:1200px; margin:0 auto; padding:24px 16px; }}
  .summary {{ background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:14px 20px;
              margin-bottom:24px; display:flex; gap:20px; align-items:center; flex-wrap:wrap; font-size:13px; }}
  .summary strong {{ font-size:22px; font-weight:800; color:#1e3a5f; margin-right:4px; }}
  .sev-section {{ margin-bottom:32px; }}
  .sev-title {{ padding:10px 18px; font-size:14px; font-weight:700; border-radius:8px 8px 0 0;
                letter-spacing:.4px; text-transform:uppercase; display:flex; align-items:center; gap:10px; }}
  .sev-count {{ font-size:12px; font-weight:600; opacity:.85; }}
  .cards-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; padding:14px 0; }}
  .bug-card {{ background:#fff; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden;
               break-inside:avoid; }}
  .card-header {{ padding:10px 14px; display:flex; align-items:center; gap:10px; }}
  .bug-id {{ font-size:12px; font-weight:700; opacity:.85; white-space:nowrap; }}
  .bug-title {{ font-weight:700; font-size:13px; flex:1; line-height:1.3; }}
  .bug-status {{ font-size:11px; font-weight:600; padding:2px 8px; border-radius:20px; white-space:nowrap; }}
  .st-aberto    {{ background:rgba(255,255,255,.25); }}
  .st-analise   {{ background:rgba(255,255,255,.25); }}
  .st-corrigido {{ background:rgba(16,185,129,.25); color:#065f46 !important; }}
  .st-fechado   {{ background:rgba(0,0,0,.15); }}
  .st-reaberto  {{ background:rgba(124,92,216,.25); color:#4c1d95 !important; }}
  .card-body {{ padding:12px 14px; display:flex; flex-direction:column; gap:8px; }}
  .field {{ display:flex; flex-direction:column; gap:2px; }}
  .flabel {{ font-size:10px; font-weight:700; text-transform:uppercase; color:#57606a; letter-spacing:.4px; }}
  .fval {{ font-size:12px; color:#1f2328; line-height:1.5; }}
  .fval.steps {{ white-space:pre-wrap; font-family:monospace; font-size:11px; background:#f7f8fa;
                 border:1px solid #e5e7eb; border-radius:4px; padding:6px 8px; }}
  .meta .fval {{ color:#57606a; }}
  @media print {{
    body {{ background:#fff; }}
    header {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    .sev-title {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    .card-header {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    .bug-card {{ border:1px solid #ccc; page-break-inside:avoid; }}
  }}
  footer {{ text-align:center; padding:24px 0 16px; color:#57606a; font-size:11px;
            border-top:1px solid #e5e7eb; margin-top:32px; }}
</style>
</head>
<body>
<header>
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
  <h1>Cartões de Bug — {project_name}</h1>
  <span class="meta">Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</span>
</header>

<div class="container">
  <div class="summary">
    <div><strong>{total}</strong> bug{'s' if total != 1 else ''} no total</div>
    {''.join(f'<div><strong style="color:{SEV_STYLE[s][1]}">{len(grouped[s])}</strong> {s.lower()}</div>' for s in SEV_ORDER if grouped[s])}
  </div>
  {sections_html}
</div>

<footer>Sistema QA — Cartões de Bug &nbsp;|&nbsp; <strong>Made with IBM Bob</strong></footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
