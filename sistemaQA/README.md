# Sistema QA — Gestão de Testes

Sistema de Quality Assurance para registro de casos de teste, cenários Gherkin, bugs e geração de relatórios.
Disponível em duas interfaces: **Web (Flask)** e **CLI**.

---

## Índice

- [Estrutura do projeto](#estrutura-do-projeto)
- [Requisitos](#requisitos)
- [Instalação e execução — Web](#instalação-e-execução--interface-web-recomendado)
- [Instalação e execução — CLI](#instalação-e-execução--cli)
- [Funcionalidades](#funcionalidades)
- [Rotas da aplicação web](#rotas-da-aplicação-web)
- [Métricas calculadas](#métricas-calculadas)
- [Exportações](#exportações)

---

## Estrutura do projeto

```
sistemaQA/
├── main.py              ← Ponto de entrada da CLI
├── seed_demo.py         ← Popula o banco com dados de demonstração
├── data/
│   └── qa_system.db     ← Banco SQLite (criado automaticamente)
├── exports/             ← Arquivos CSV gerados pelo sistema
├── reports/             ← Dashboards HTML gerados pelo sistema
├── modules/             ← Lógica de negócio — compartilhada entre Web e CLI
│   ├── database.py      ← Conexão SQLite e criação de tabelas
│   ├── projects.py      ← CRUD de projetos
│   ├── test_cases.py    ← CRUD de suites e casos de teste
│   ├── scenarios.py     ← CRUD de cenários Gherkin
│   ├── bugs.py          ← CRUD de bugs
│   ├── reports.py       ← Agregações e métricas
│   ├── html_report.py   ← Geração de dashboard HTML estático
│   └── csv_io.py        ← Exportação e importação CSV
└── web/                 ← Interface Web (Flask)
    ├── app.py           ← Servidor Flask — 25 rotas HTTP
    ├── requirements.txt ← Dependências Python da interface web
    └── templates/       ← Templates Jinja2
        ├── base.html          ← Layout base (nav, flash, CSS)
        ├── index.html         ← Dashboard global
        ├── projetos.html      ← Listagem de projetos
        ├── projeto_form.html  ← Formulário criar/editar projeto
        ├── projeto_detalhe.html ← KPIs e gráficos por projeto
        ├── suites.html        ← Gerenciamento de suites
        ├── casos.html         ← Casos de teste com status inline
        ├── caso_form.html     ← Formulário edição de caso
        ├── cenarios.html      ← Cenários Gherkin
        ├── bugs.html          ← Listagem e registro de bugs
        └── bug_form.html      ← Formulário edição de bug
```

---

## Requisitos

| Interface | Python | Dependências externas |
|-----------|--------|-----------------------|
| Web       | 3.10+  | `flask >= 3.1`        |
| CLI       | 3.10+  | nenhuma (stdlib only) |

---

## Instalação e execução — Interface Web (recomendado)

### 1. Clonar / acessar o diretório

```bash
cd sistemaQA/web
```

### 2. Criar ambiente virtual

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. (Opcional) Carregar dados de demonstração

```bash
cd ..                 # volta para sistemaQA/
python seed_demo.py
cd web
```

### 5. Iniciar o servidor

```bash
python app.py
```

Acesse **http://127.0.0.1:5000** no navegador.

> **Variável de ambiente opcional**
> Por padrão a `secret_key` do Flask é gerada aleatoriamente a cada inicialização.
> Para sessões persistentes entre reinicializações, defina:
> ```bash
> export QA_SECRET_KEY="sua-chave-segura-aqui"   # Linux/macOS
> set QA_SECRET_KEY=sua-chave-segura-aqui         # Windows CMD
> ```

---

## Instalação e execução — CLI

```bash
cd sistemaQA

# (opcional) dados de demonstração
python seed_demo.py

# iniciar a interface interativa
python main.py
```

> A CLI não requer nenhuma instalação adicional além do Python 3.10+.

---

## Funcionalidades

### Projetos
- Criar, listar, editar e excluir projetos
- Cada projeto agrupa suites, casos, cenários e bugs de forma independente

### Suites de Teste
- Agrupam casos de teste por área funcional (ex.: Autenticação, Checkout)
- Exclusão em cascata remove todos os casos vinculados

### Casos de Teste
| Campo | Descrição |
|-------|-----------|
| Título | Identificação do caso |
| Descrição | Detalhamento do objetivo |
| Pré-condições | Estado necessário antes da execução |
| Passos | Sequência de ações (separadas por `\|`) |
| Resultado esperado | Comportamento correto do sistema |
| Prioridade | `BAIXA` / `MÉDIA` / `ALTA` / `CRÍTICA` |
| Status | `NÃO EXECUTADO` / `PASSOU` / `FALHOU` / `BLOQUEADO` / `IGNORADO` |

### Cenários Gherkin
- Formato **Dado que / Quando / Então**
- Status: `PENDENTE` / `APROVADO` / `REPROVADO`
- Suporte a tags para organização e filtragem

### Bugs
| Campo | Descrição |
|-------|-----------|
| Título | Identificação do bug |
| Descrição | O que foi observado |
| Passos para reproduzir | Como replicar o problema |
| Severidade | `BAIXA` / `MÉDIA` / `ALTA` / `CRÍTICA` |
| Ambiente | Ex.: produção, homolog, iOS 17, Chrome 124 |
| Reportado por | Nome do analista / QA |
| Status | `ABERTO` / `EM ANÁLISE` / `CORRIGIDO` / `FECHADO` / `REABERTO` |

### Relatórios e exportações
- **Dashboard HTML estático** — gerado em `reports/` com gráficos de cobertura, pass rate e histórico
- **Exportação CSV** — backup por projeto salvo em `exports/` com timestamp
- **Importação CSV** — restauração de casos de teste e bugs a partir de arquivos exportados

---

## Rotas da aplicação web

| Método | Rota | Função |
|--------|------|--------|
| GET | `/` | Dashboard global |
| GET | `/projetos` | Listar projetos |
| GET / POST | `/projetos/novo` | Criar projeto |
| GET | `/projetos/<id>` | Detalhe + KPIs |
| GET / POST | `/projetos/<id>/editar` | Editar projeto |
| POST | `/projetos/<id>/excluir` | Excluir projeto |
| GET | `/projetos/<id>/suites` | Listar suites |
| POST | `/projetos/<id>/suites/nova` | Criar suite |
| POST | `/suites/<id>/excluir` | Excluir suite |
| GET | `/projetos/<id>/casos` | Listar casos de teste |
| POST | `/projetos/<id>/casos/novo` | Criar caso |
| POST | `/casos/<id>/status` | Atualizar status |
| GET / POST | `/casos/<id>/editar` | Editar caso |
| POST | `/casos/<id>/excluir` | Excluir caso |
| GET | `/projetos/<id>/cenarios` | Listar cenários |
| POST | `/projetos/<id>/cenarios/novo` | Criar cenário |
| POST | `/cenarios/<id>/status` | Atualizar status |
| POST | `/cenarios/<id>/excluir` | Excluir cenário |
| GET | `/projetos/<id>/bugs` | Listar bugs |
| POST | `/projetos/<id>/bugs/novo` | Registrar bug |
| POST | `/bugs/<id>/status` | Atualizar status |
| GET / POST | `/bugs/<id>/editar` | Editar bug |
| POST | `/bugs/<id>/excluir` | Excluir bug |
| GET | `/projetos/<id>/relatorio` | Gerar dashboard HTML |
| GET | `/projetos/<id>/exportar-csv` | Exportar CSVs |

---

## Métricas calculadas

| Métrica | Fórmula |
|---------|---------|
| Cobertura | `casos executados / total de casos × 100` |
| Taxa de aprovação | `casos que passaram / casos executados × 100` |
| Bugs por severidade | Contagem agrupada por `BAIXA / MÉDIA / ALTA / CRÍTICA` |
| Bugs por status | Contagem agrupada por status |
| Evolução temporal | Bugs registrados por dia e execuções por dia |

---

## Exportações

Os arquivos são salvos em `exports/` com timestamp:

```
exports/
├── test_cases_proj{id}_{YYYYMMDD_HHMMSS}.csv
├── bugs_proj{id}_{YYYYMMDD_HHMMSS}.csv
└── scenarios_proj{id}_{YYYYMMDD_HHMMSS}.csv
```
