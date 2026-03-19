# tools/run-quality.sh — HomeMatch

Script local de análise estática de código para o projeto HomeMatch.
Complementa o CI do GitHub Actions rodando análises mais detalhadas
na máquina do desenvolvedor antes de abrir um PR.

---

## Relação com o GitHub Actions

| | `run-quality.sh` | GitHub Actions |
|---|---|---|
| **Quando roda** | Manual, antes do commit/PR | Automático a cada push/PR |
| **Onde roda** | Máquina local | Nuvem (ubuntu-latest) |
| **Objetivo** | Análise detalhada + relatórios por sprint | Validação rápida do pipeline |
| **Relatórios** | Salvos em `tools/reports/` | Visível na aba Actions do GitHub |

---

## Ferramentas executadas

| Ferramenta | O que faz |
|---|---|
| `pylint` | Análise estática profunda, detecta erros e má práticas |
| `flake8` | Linting rápido, verifica estilo PEP8 |
| `black` | Formatação automática de código |
| `vulture` | Detecta código morto (funções/variáveis não usadas) |
| `bandit` | Analisa vulnerabilidades de segurança |
| `radon-mi` | Índice de manutenibilidade do código |
| `radon-cc` | Complexidade ciclomática por função |
| `radon-raw` | Métricas brutas (linhas de código, comentários etc) |

---

## Pré-requisitos
```bash
pip install pylint flake8 black vulture bandit radon
chmod +x tools/run-quality.sh
```

---

## Uso

### Análise completa
```bash
./tools/run-quality.sh
```

### Ferramentas específicas
```bash
# Só linting e formatação
./tools/run-quality.sh -t flake8,black

# Só segurança
./tools/run-quality.sh -t bandit

# Só métricas de complexidade
./tools/run-quality.sh -t radon-cc,radon-mi
```

### Por sprint
```bash
# Gera relatórios em tools/reports/sprint1/
./tools/run-quality.sh --sprint 1

# Sprint 2
./tools/run-quality.sh --sprint 2
```

### Formatar código automaticamente
```bash
./tools/run-quality.sh -t black --black-mode format
```

### Dry run — ver comandos sem executar
```bash
./tools/run-quality.sh --dry-run
```

---

## Padrões do projeto HomeMatch

| Configuração | Valor |
|---|---|
| **Diretório fonte** | `apps/` |
| **Diretório de relatórios** | `tools/reports/` |
| **Sprint padrão** | `1` |
| **Esquema de relatórios** | `nested` (por sprint) |
| **Modo black** | `check` (não formata automaticamente) |
| **Política de falha** | `any` (falha se qualquer ferramenta falhar) |

---

## Saída

Relatórios salvos em `tools/reports/sprintN/`:
- Um arquivo por ferramenta com output completo e metadados
- `summary.txt` com resumo geral da execução

---

## Códigos de saída

| Código | Significado |
|---|---|
| `0` | Todas as ferramentas passaram |
| `2` | Uma ou mais ferramentas falharam |
| `3` | Dependências não instaladas |

---

## Fluxo recomendado antes de abrir um PR
```bash
# 1. Formatar o código
./tools/run-quality.sh -t black --black-mode format

# 2. Rodar análise completa
./tools/run-quality.sh --sprint 1

# 3. Se tudo passar, commitar e abrir o PR
# O GitHub Actions vai validar automaticamente
```