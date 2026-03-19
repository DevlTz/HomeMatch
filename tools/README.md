# run-quality.sh — Documentation (English / Português)

---

## English —  Guide

### Overview

/run-quality.sh` is a comprehensive static analysis automation script for Django and Python projects. It orchestrates multiple code quality, manages reports, and provides metadata for CI/CD and local workflows.

**Main Features:**
- Runs: `pylint`, `flake8`, `vulture`, `black`, `radon` (mi, cc, raw)
- Flexible tool selection and configuration
- Sprint-based and flat report organization
- CI/CD friendly: exit codes, dry-run, environment overrides
- Detailed summary and per-tool metadata
- Handles missing dependencies and errors gracefully

### Prerequisites

- **System:** Bash shell (Linux/macOS/WSL), Python 3.6+ with pip
- **Install:**
    ```bash
    pip install pylint flake8 vulture black radon
    ```
- **Make script executable:**
    ```bash
    chmod +x/run-quality.sh
    ```

### Usage

#### Basic

```bash
./run-quality.sh
./run-quality.sh --help
```

#### Tool Selection

```bash
./run-quality.sh -t pylint,flake8
./run-quality.sh - black,vulture
./run-quality.sh -t radon-cc,radon-mi
```

#### Sprint/Report Organization

```bash
./run-quality.sh --sprint 2
./run-quality.sh --scheme nested   # Default: reports/sprintN/tool-sprintN.txt
./run-quality.sh --scheme simple   # reports/tool-reportN.txt
```

#### Directory Configuration

```bash
./run-quality.sh --src path/to/code --reports path/to/reports
```

#### Black Formatter

```bash
./run-quality.sh --black-mode check   # Default: check only
./run-quality.sh --black-mode format  # Actually formats files
```

#### Failure Policy

```bash
./run-quality.sh --fail-on any        # Default: fail if any tool fails
./run-quality.sh --fail-on none       # Never fail
./run-quality.sh --fail-on pylint,black
```

#### Dry Run & Debug

```bash
./run-quality.sh --dry-run
./run-quality.sh --dry-run -t black,flake8
```

#### Environment Variable Overrides

```bash
export SRC_DIR="src/"
export REPORTS_DIR="refactoring/reports"
./run-quality.sh
SRC_DIR=custom SRC_DIR=custom ./run-quality.sh
```

### Defaults

- **Source dir:** `../src/djangoproject/`
- **Reports dir:** `../refactoring/reports`
- **Sprint:** `1`
- **Scheme:** `nested`
- *:** `pylint,flake8,vulture,black,radon-mi,radon-cc,radon-raw`
- **Black mode:** `check`
- **Fail policy:** `any`
- **Dry run:** `0`

### Output

- **Reports:** Per-tool, per-sprint or flat, with tool output and metadata
- **Summary:** `summary.txt` with execution info, tool results, exit codes

### Exit Codes

- `0`: All passed (or `--fail-on none`)
- `2`: One or more in `--fail-on` failed
- `3`: Missing dependencies

### Examples

```bash
# Full analysis, default settings
./run-quality.sh

# Only flake8 and black, format code
./run-quality.sh -t flake8,black --black-mode format

# CI: strict, custom sprint
./run-quality.sh --sprint $BUILD_NUMBER --fail-on any

# Dry run, custom paths
./run-quality.sh --dry-run --src src --reports reports
```

---

## Português — Guia 

### Visão Geral

/run-quality.sh` é um script completo de automação de análise estática para projetos Django/Python. Ele executa várias ferramentas de qualidade, organiza relatórios e fornece metadados para CI/CD e uso local.

**Principais Recursos:**
- Executa: `pylint`, `flake8`, `vulture`, `black`, `radon` (mi, cc, raw)
- Seleção e configuração flexível de ferramentas
- Organização de relatórios por sprint ou plana
- Pronto para CI/CD: códigos de saída, dry-run, variáveis de ambiente
- Sumário detalhado e metadados por ferramenta
- Lida com dependências ausentes e erros

### Pré-requisitos

- **Sistema:** Bash (Linux/macOS/WSL), Python 3.6+ com pip
- **Instalar ferramentas:**
    ```bash
    pip install pylint flake8 vulture black radon
    ```
- **Tornar executável:**
    ```bash
    chmod +x/run-quality.sh
    ```

### Uso

#### Básico

```bash
./run-quality.sh
./run-quality.sh --help
```

#### Seleção de Ferramentas

```bash
./run-quality.sh -t pylint,flake8
./run-quality.sh - black,vulture
./run-quality.sh -t radon-cc,radon-mi
```

#### Organização de Relatórios

```bash
./run-quality.sh --sprint 2
./run-quality.sh --scheme nested   # Padrão: reports/sprintN/tool-sprintN.txt
./run-quality.sh --scheme simple   # reports/tool-reportN.txt
```

#### Configuração de Diretórios

```bash
./run-quality.sh --src caminho/codigo --reports caminho/relatorios
```

#### Black Formatter

```bash
./run-quality.sh --black-mode check   # Padrão: só verifica
./run-quality.sh --black-mode format  # Formata arquivos
```

#### Política de Falha

```bash
./run-quality.sh --fail-on any        # Padrão: falha se qualquer ferramenta falhar
./run-quality.sh --fail-on none       # Nunca falha
./run-quality.sh --fail-on pylint,black
```

#### Dry Run & Debug

```bash
./run-quality.sh --dry-run
./run-quality.sh --dry-run -t black,flake8
```

#### Variáveis de Ambiente

```bash
export SRC_DIR="src/"
export REPORTS_DIR="refactoring/reports"
./run-quality.sh
SRC_DIR=custom SRC_DIR=custom ./run-quality.sh
```

### Padrões

- **Diretório fonte:** `../src/djangoproject/`
- **Diretório de relatórios:** `../refactoring/reports`
- **Sprint:** `1`
- **Esquema:** `nested`
- **Ferramentas:** `pylint,flake8,vulture,black,radon-mi,radon-cc,radon-raw`
- **Modo black:** `check`
- **Política de falha:** `any`
- **Dry run:** `0`

### Saída

- **Relatórios:** Por ferramenta, por sprint ou plano, com saída e metadados
- **Sumário:** `summary.txt` com informações de execução, resultados e códigos de saída

### Códigos de Saída

- `0`: Todas as ferramentas passaram (ou `--fail-on none`)
- `2`: Uma ou mais ferramentas em `--fail-on` falharam
- `3`: Dependências ausentes

### Exemplos

```bash
# Análise completa, padrões
./run-quality.sh

# Apenas flake8 e black, formatar código
./run-quality.sh -t flake8,black --black-mode format

# CI: rigoroso, sprint customizado
./run-quality.sh --sprint $BUILD_NUMBER --fail-on any

# Dry run, caminhos customizados
./run-quality.sh --dry-run --src src --reports reports
```

---
