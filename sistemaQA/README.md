# Sistema QA — Gestão de Testes

Sistema de Quality Assurance para registro de casos de teste, cenários Gherkin, bugs e geração de relatórios.
Disponível em duas interfaces: **Web (Flask)** e **CLI**.

## Estrutura

```
sistemaQA/
├── main.py              ← Ponto de entrada (CLI)
├── seed_demo.py         ← Dados de exemplo
├── data/
│   └── qa_system.db     ← Banco SQLite (criado automaticamente)
├── exports/             ← Arquivos CSV exportados
├── reports/             ← Dashboards HTML gerados
├── modules/             ← Lógica de negócio (compartilhada entre web e CLI)
│   ├── database.py
│   ├── projects.py
│   ├── test_cases.py
│   ├── scenarios.py
│   ├── bugs.py
│   ├── reports.py
│   ├── html_report.py
│   └── csv_io.py
└── web/                 ← Interface Web (Flask)
    ├── app.py           ← Servidor web — todas as rotas
    ├── requirements.txt ← flask>=3.1
    └── templates/       ← Templates Jinja2
        ├── base.html
        ├── index.html
        ├── projetos.html
        ├── projeto_form.html
        ├── projeto_detalhe.html
        ├── suites.html
        ├── casos.html
        ├── caso_form.html
        ├── cenarios.html
        ├── bugs.html
        └── bug_form.html
```

## Requisitos

- Python 3.10+
- **Interface web**: `flask>=3.1` (única dependência externa)
- **CLI**: nenhuma dependência — usa apenas stdlib

## Como usar — Interface Web (recomendado)

### 1. Criar ambiente virtual e instalar dependências

```bash
cd sistemaQA/web
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 2. Carregar dados de demonstração (opcional)

```bash
cd ..   # volta para sistemaQA/
python seed_demo.py
cd web
```

### 3. Iniciar o servidor

```bash
python app.py
```

Acesse **http://127.0.0.1:5000** no navegador.

## Como usar — CLI

```bash
cd sistemaQA
python main.py
```

## Funcionalidades

### Projetos
- Criar, listar e excluir projetos
- Cada projeto agrupa suites, casos, cenários e bugs

### Suites de Teste
- Agrupam casos de teste por área funcional

### Casos de Teste
- Campos: título, descrição, pré-condições, passos, resultado esperado, prioridade
- Prioridades: BAIXA | MÉDIA | ALTA | CRÍTICA
- Status: NÃO EXECUTADO | PASSOU | FALHOU | BLOQUEADO | IGNORADO
- Registro de data/hora de execução

### Cenários Gherkin
- Formato: **Dado que** / **Quando** / **Então**
- Status: PENDENTE | APROVADO | REPROVADO
- Suporte a tags para organização

### Bugs
- Campos: título, descrição, passos de reprodução, severidade, ambiente, reportado por
- Severidades: BAIXA | MÉDIA | ALTA | CRÍTICA
- Status: ABERTO | EM ANÁLISE | CORRIGIDO | FECHADO | REABERTO
- Vinculação opcional ao caso de teste que originou o bug

### Relatórios
- **Resumo no terminal**: métricas de cobertura, pass rate, bugs por status/severidade
- **Dashboard HTML**: gráficos de pizza, barras e linhas com cobertura e histórico
- **Exportação CSV**: backup separado por casos de teste, bugs e cenários
- **Importação CSV**: restauração de dados a partir de backup

## Métricas calculadas

| Métrica | Descrição |
|---|---|
| Cobertura | % de casos executados em relação ao total |
| Taxa de Aprovação | % de casos que passaram dentre os executados |
| Bugs por severidade | Distribuição BAIXA / MÉDIA / ALTA / CRÍTICA |
| Evolução temporal | Bugs registrados por dia, testes executados por dia |

## Dashboard HTML

O dashboard gerado contém:
- KPIs: total de casos, passaram, falharam, bloqueados, bugs, cenários
- Gauge de cobertura e taxa de aprovação
- Gráfico de pizza: status dos casos de teste
- Gráfico de pizza: bugs por severidade
- Gráfico de barras: bugs por status
- Gráfico de linha: bugs registrados por dia
- Gráfico de linha: histórico de execução (passou/falhou por dia)

## Backup CSV

Os arquivos são salvos em `exports/` com timestamp no nome:
- `test_cases_proj{id}_{timestamp}.csv`
- `bugs_proj{id}_{timestamp}.csv`
- `scenarios_proj{id}_{timestamp}.csv`
