# Sistema QA — Gestão de Testes

Sistema de Quality Assurance para registro de casos de teste, cenários Gherkin, bugs e geração de relatórios com dashboard HTML interativo e backup CSV.

## Estrutura

```
sistemaQA/
├── main.py              ← Ponto de entrada (CLI interativa)
├── seed_demo.py         ← Dados de exemplo para demonstração
├── data/
│   └── qa_system.db     ← Banco SQLite (criado automaticamente)
├── exports/             ← Arquivos CSV exportados (backup)
├── reports/             ← Dashboards HTML gerados
└── modules/
    ├── database.py      ← Conexão e criação de tabelas
    ├── projects.py      ← Gerenciamento de projetos
    ├── test_cases.py    ← Suites e casos de teste
    ├── scenarios.py     ← Cenários Gherkin
    ├── bugs.py          ← Registro de bugs
    ├── reports.py       ← Cálculo de métricas e cobertura
    ├── html_report.py   ← Geração do dashboard HTML
    └── csv_io.py        ← Exportação/importação CSV
```

## Requisitos

- Python 3.10+ (sem dependências externas — usa apenas stdlib)

## Como usar

### 1. Iniciar o sistema

```bash
cd sistemaQA
python main.py
```

### 2. Carregar dados de demonstração (opcional)

```bash
cd sistemaQA
python seed_demo.py
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
