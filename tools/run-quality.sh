#!/usr/bin/env bash
# tools/run_reports.sh
# HomeMatch — Executa ferramentas de análise estática e salva relatórios organizados
#
# Funcionalidades:
#  - opções: --sprint/-s, --tools/-t, --fail-on, --scheme, --src, --reports, --dry-run, --black-mode
#  - esquema de saída: simple ou nested (padrão: nested)
#  - código de saída configurável via --fail-on (any | none | lista separada por vírgula)
#  - summary.txt gerado em cada diretório de sprint com timestamps e códigos de saída
#  - usa set -euo pipefail e traps

# --------------------
# Cores & logging
# --------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'

log() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${CYAN}[%s]${NC} %s\n" "$timestamp" "$*"
}

log_sucesso() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${GREEN}✓ [%s]${NC} %s\n" "$timestamp" "$*"
}

log_erro() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${RED}✗ [%s]${NC} %s\n" "$timestamp" "$*" >&2
}

log_aviso() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${YELLOW}⚠ [%s]${NC} %s\n" "$timestamp" "$*"
}

log_info() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${BLUE}ℹ [%s]${NC} %s\n" "$timestamp" "$*"
}

exibir_cabecalho() {
    echo
    printf "${PURPLE}${BOLD}"
    printf "╔══════════════════════════════════════════════════════════════════════════════╗\n"
    printf "║                        🔍 ANÁLISE DE QUALIDADE DE CÓDIGO 🔍                 ║\n"
    printf "║                      HomeMatch — Sprint: %-3s | Esquema: %-8s           ║\n" "$sprint" "$scheme"
    printf "╚══════════════════════════════════════════════════════════════════════════════╝\n"
    printf "${NC}"
    echo
    printf "${WHITE}📁 Diretório fonte:${NC} %s\n" "$SRC_DIR"
    printf "${WHITE}📊 Diretório de relatórios:${NC} %s\n" "$REPORTS_DIR"
    printf "${WHITE}🛠️  Ferramentas a executar:${NC} %s\n" "${TOOLS_TO_RUN[*]}"
    printf "${WHITE}⚙️  Política de falha:${NC} %s\n" "$fail_on"
    echo
}

set -euo pipefail

# --------------------
# Configurações padrão
# --------------------
SRC_DIR="${SRC_DIR:-apps/}"
REPORTS_DIR="${REPORTS_DIR:-tools/reports}"
DEFAULT_SPRINT=1
sprint="${DEFAULT_SPRINT}"
scheme="nested"
DRY_RUN=0
black_mode="check"

# --------------------
# Registro de ferramentas
# --------------------
declare -A TOOL_CMD

TOOL_CMD[pylint]="pylint apps/ --disable=C0114,C0115,C0116 --ignore=migrations"
TOOL_CMD[flake8]="flake8 --max-line-length=88 --exclude=migrations,venv,node_modules apps/"
TOOL_CMD[vulture]="vulture apps/ --exclude 'migrations|settings.py'"
TOOL_CMD[black]="black --${black_mode} apps/"
TOOL_CMD[bandit]="bandit -r apps/ --exclude apps/ai_analysis/migrations,apps/properties/migrations,apps/search/migrations,apps/users/migrations"
TOOL_CMD[radon-mi]="radon mi -s apps/"
TOOL_CMD[radon-cc]="radon cc -a -s apps/"
TOOL_CMD[radon-raw]="radon raw apps/"

DEFAULT_TOOLS=(pylint flake8 vulture black bandit radon-mi radon-cc radon-raw)

# --------------------
# Estado interno
# --------------------
declare -a TOOLS_TO_RUN=()
declare -A TOOL_EXIT
declare -A TOOL_REPORT_PATH
declare -A TOOL_CMD_EXPANDED
start_time="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
fail_on="any"

# --------------------
# Ajuda
# --------------------
uso() {
  cat <<EOF
Uso: $(basename "$0") [opções]

Opções:
    -s, --sprint N           Número do sprint (padrão: ${DEFAULT_SPRINT})
    -t, --tools a,b,c        Ferramentas a executar separadas por vírgula.
                             Disponíveis: ${DEFAULT_TOOLS[*]}
    --src CAMINHO            Diretório fonte (padrão: ${SRC_DIR})
    --reports CAMINHO        Diretório de relatórios (padrão: ${REPORTS_DIR})
    --scheme simple|nested   Esquema de nomes dos relatórios (padrão: nested)
    --fail-on LISTA          'any'|'none'|lista de ferramentas (padrão: ${fail_on})
    --dry-run                Exibe os comandos sem executá-los
    --black-mode check|format Modo do black: verificar ou formatar (padrão: check)
    -h, --help               Exibe esta ajuda

Exemplos:
    $(basename "$0") --sprint 1
    $(basename "$0") -t pylint,flake8,bandit
    $(basename "$0") -t black --black-mode format
    $(basename "$0") --dry-run
EOF
}

# --------------------
# Funções auxiliares
# --------------------
verificar_comando() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

caminho_relatorio() {
  local tool="$1"
  if [[ "$scheme" == "simple" ]]; then
    echo "${REPORTS_DIR}/${tool}-relatorio${sprint}.txt"
  else
    echo "${SPRINT_DIR}/${tool}-sprint${sprint}.txt"
  fi
}

executar_ferramenta() {
  local tool="$1"
  local raw_cmd="${TOOL_CMD[$tool]}"
  TOOL_CMD_EXPANDED[$tool]="$raw_cmd"
  local out_file
  out_file="$(caminho_relatorio "$tool")"
  TOOL_REPORT_PATH[$tool]="$out_file"

  printf "${PURPLE}${BOLD}┌─────────────────────────────────────────────────────────────────────────────┐${NC}\n"
  printf "${PURPLE}${BOLD}│${NC} ${WHITE}🔧 Executando: %-20s${NC} ${PURPLE}${BOLD}│${NC}\n" "$tool"
  printf "${PURPLE}${BOLD}└─────────────────────────────────────────────────────────────────────────────┘${NC}\n"
  log_info "Comando: ${TOOL_CMD_EXPANDED[$tool]}"

  local t_start t_end elapsed
  t_start="$(date +%s)"

  if [[ "${DRY_RUN:-0}" -eq 1 ]]; then
    printf "${YELLOW}[DRY-RUN]${NC} Comando para ${BOLD}${tool}${NC}: ${TOOL_CMD_EXPANDED[$tool]}\n"
    TOOL_EXIT[$tool]=0
  else
    mkdir -p "$(dirname "$out_file")"
    printf "${CYAN}⏳ Executando...${NC}\n"
    if bash -c "${TOOL_CMD_EXPANDED[$tool]}" >"${out_file}" 2>&1; then
      TOOL_EXIT[$tool]=0
    else
      TOOL_EXIT[$tool]=$?
    fi
  fi

  t_end="$(date +%s)"
  elapsed=$((t_end - t_start))

  if [[ "${TOOL_EXIT[$tool]}" -eq 0 ]]; then
    log_sucesso "${tool} concluído com sucesso em ${elapsed}s"
    printf "${GREEN}📄 Relatório salvo: ${out_file}${NC}\n"
  else
    log_erro "${tool} falhou com código ${TOOL_EXIT[$tool]} após ${elapsed}s"
    printf "${RED}📄 Relatório de erro salvo: ${out_file}${NC}\n"
  fi
  echo

  if [[ "${DRY_RUN:-0}" -eq 0 ]]; then
    {
      printf "\n\n# --- metadados ---\n"
      printf "ferramenta: %s\n" "$tool"
      printf "comando: %s\n" "${TOOL_CMD_EXPANDED[$tool]}"
      printf "codigo_saida: %s\n" "${TOOL_EXIT[$tool]}"
      printf "tempo_execucao_segundos: %s\n" "${elapsed}"
      printf "caminho_relatorio: %s\n" "${out_file}"
    } >>"${out_file}"
  fi
}

# --------------------
# Parsing de argumentos
# --------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--sprint)
      sprint="$2"
      shift 2
      ;;
    -t|--tools)
      IFS=',' read -r -a TOOLS_TO_RUN <<<"$2"
      shift 2
      ;;
    --src)
      SRC_DIR="$2"
      shift 2
      ;;
    --reports)
      REPORTS_DIR="$2"
      shift 2
      ;;
    --scheme)
      scheme="$2"
      shift 2
      ;;
    --fail-on)
      fail_on="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --black-mode)
      black_mode="$2"
      shift 2
      ;;
    -h|--help)
      uso
      exit 0
      ;;
    *)
      echo "Opção desconhecida: $1" >&2
      uso
      exit 2
      ;;
  esac
done

if [[ ${#TOOLS_TO_RUN[@]} -eq 0 ]]; then
  TOOLS_TO_RUN=("${DEFAULT_TOOLS[@]}")
fi

TOOL_CMD[black]="black --${black_mode} apps/"

# --------------------
# Conjunto fail-on
# --------------------
declare -A FAIL_ON_HASH
if [[ "${fail_on}" == "any" ]]; then
  for t in "${TOOLS_TO_RUN[@]}"; do FAIL_ON_HASH["$t"]=1; done
elif [[ "${fail_on}" == "none" ]]; then
  true
else
  IFS=',' read -r -a tmp <<<"${fail_on}"
  for t in "${tmp[@]}"; do FAIL_ON_HASH["$t"]=1; done
fi

# --------------------
# Diretório do sprint
# --------------------
if [[ "$scheme" == "nested" ]]; then
  SPRINT_DIR="${REPORTS_DIR}/sprint${sprint}"
  mkdir -p "${SPRINT_DIR}"
else
  SPRINT_DIR="${REPORTS_DIR}"
  mkdir -p "${SPRINT_DIR}"
fi

SUMMARY_FILE="${SPRINT_DIR}/summary.txt"
mkdir -p "${REPORTS_DIR}"

# --------------------
# Trap: sumário ao sair
# --------------------
ao_sair() {
  local final_exit=$?
  end_time="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
  {
    printf "inicio: %s\n" "${start_time}"
    printf "fim:    %s\n" "${end_time}"
    printf "src:    %s\n" "${SRC_DIR}"
    printf "relatorios: %s\n" "${REPORTS_DIR}"
    printf "sprint: %s\n" "${sprint}"
    printf "esquema: %s\n" "${scheme}"
    printf "dry_run: %s\n" "${DRY_RUN}"
    printf "\n# ferramentas executadas:\n"
    for t in "${TOOLS_TO_RUN[@]}"; do
      local code="${TOOL_EXIT[$t]:-nao-executado}"
      local path="${TOOL_REPORT_PATH[$t]:-N/A}"
      printf "%s: saida=%s caminho=%s cmd=%s\n" "$t" "$code" "$path" "${TOOL_CMD_EXPANDED[$t]:-N/A}"
    done
    printf "\n# saida_final: %s\n" "${final_exit}"
  } >"${SUMMARY_FILE}.tmp" || true

  mv "${SUMMARY_FILE}.tmp" "${SUMMARY_FILE}" 2>/dev/null || true

  echo
  printf "${PURPLE}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}\n"
  printf "${PURPLE}${BOLD}║                            📊 RESUMO DA EXECUÇÃO 📊                          ║${NC}\n"
  printf "${PURPLE}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"

  local success_count=0
  local fail_count=0

  for t in "${TOOLS_TO_RUN[@]}"; do
    local code="${TOOL_EXIT[$t]:-0}"
    if [[ "$code" -eq 0 ]]; then
      success_count=$((success_count + 1))
      printf "${GREEN}✓${NC} %-15s ${GREEN}PASSOU${NC}\n" "$t"
    else
      fail_count=$((fail_count + 1))
      printf "${RED}✗${NC} %-15s ${RED}FALHOU (código: $code)${NC}\n" "$t"
    fi
  done

  echo
  printf "${WHITE}📈 Resultado: ${GREEN}$success_count passaram${NC}, ${RED}$fail_count falharam${NC}\n"
  printf "${WHITE}📄 Arquivo de resumo: ${CYAN}${SUMMARY_FILE}${NC}\n"
  echo

  if [[ "${fail_on}" == "none" ]]; then
    exit 0
  fi
  if [[ "${fail_on}" == "any" ]]; then
    for t in "${TOOLS_TO_RUN[@]}"; do
      local code="${TOOL_EXIT[$t]:-0}"
      if [[ "$code" -ne 0 ]]; then
        printf "${RED}${BOLD}💥 PIPELINE FALHOU!${NC}\n"
        log_erro "Ferramenta ${t} retornou ${code} e --fail-on any está ativo"
        exit 2
      fi
    done
    exit 0
  fi
  for t in "${!FAIL_ON_HASH[@]}"; do
    local code="${TOOL_EXIT[$t]:-0}"
    if [[ "$code" -ne 0 ]]; then
      printf "${RED}${BOLD}💥 PIPELINE FALHOU!${NC}\n"
      log_erro "Ferramenta ${t} retornou ${code} e está na lista --fail-on"
      exit 2
    fi
  done
  exit 0
}
trap ao_sair EXIT

# --------------------
# Início da execução
# --------------------
exibir_cabecalho

ferramentas_ausentes=()
for t in "${TOOLS_TO_RUN[@]}"; do
  case "$t" in
    pylint) bin="pylint" ;;
    flake8) bin="flake8" ;;
    vulture) bin="vulture" ;;
    black) bin="black" ;;
    bandit) bin="bandit" ;;
    radon-mi|radon-cc|radon-raw) bin="radon" ;;
    *) bin="$t" ;;
  esac
  if ! verificar_comando "$bin"; then
    ferramentas_ausentes+=("$bin")
    log "AVISO: comando '$bin' (para ferramenta '$t') não encontrado no PATH"
  fi
done

if [[ "${#ferramentas_ausentes[@]}" -gt 0 ]]; then
  echo
  printf "${RED}${BOLD}❌ ERRO: Ferramentas necessárias não encontradas!${NC}\n"
  printf "${RED}🚫 Ausentes: ${ferramentas_ausentes[*]}${NC}\n"
  echo
  printf "${YELLOW}💡 Instale com:${NC}\n"
  printf "${WHITE}   pip install pylint flake8 vulture black bandit radon${NC}\n"
  echo
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    log_aviso "Continuando em dry-run apesar das ferramentas ausentes"
  else
    exit 3
  fi
fi

for t in "${TOOLS_TO_RUN[@]}"; do
  if [[ -z "${TOOL_CMD[$t]-}" ]]; then
    log "Ferramenta desconhecida: $t — ignorando"
    TOOL_EXIT[$t]=127
    continue
  fi
  executar_ferramenta "$t"
done