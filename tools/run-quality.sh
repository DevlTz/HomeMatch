#!/usr/bin/env bash
# tools/run_reports.sh
# Run static analysis tools and save organized reports in refactoring/reports/
#
# Features:
#  - options: --sprint/-s, --tools/-t, --fail-on, --scheme, --src, --reports, --dry-run, --black-mode
#  - output scheme: simple or nested (default nested)
#  - configurable exit code via --fail-on (any | none | comma-list)
#  - summary.txt generated in each sprint dir with timestamps and exit codes
#  - uses set -euo pipefail and traps

# --------------------
# Colors & logging
# --------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

log() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${CYAN}[%s]${NC} %s\n" "$timestamp" "$*"
}

log_success() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${GREEN}✓ [%s]${NC} %s\n" "$timestamp" "$*"
}

log_error() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${RED}✗ [%s]${NC} %s\n" "$timestamp" "$*" >&2
}

log_warning() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${YELLOW}⚠ [%s]${NC} %s\n" "$timestamp" "$*"
}

log_info() {
    local timestamp
    timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf "${BLUE}ℹ [%s]${NC} %s\n" "$timestamp" "$*"
}

print_header() {
    echo
    printf "${PURPLE}${BOLD}"
    printf "╔══════════════════════════════════════════════════════════════════════════════╗\n"
    printf "║                          🔍 CODE QUALITY ANALYSIS 🔍                        ║\n"
    printf "║                              Sprint: %-3s | Scheme: %-8s                ║\n" "$sprint" "$scheme"
    printf "╚══════════════════════════════════════════════════════════════════════════════╝\n"
    printf "${NC}"
    echo
    printf "${WHITE}📁 Source Directory:${NC} %s\n" "$SRC_DIR"
    printf "${WHITE}📊 Reports Directory:${NC} %s\n" "$REPORTS_DIR"
    printf "${WHITE}🛠️  Tools to run:${NC} %s\n" "${TOOLS_TO_RUN[*]}"
    printf "${WHITE}⚙️  Fail policy:${NC} %s\n" "$fail_on"
    echo
}

set -euo pipefail

# --------------------
# Defaults / Configuration
# --------------------
SRC_DIR="${SRC_DIR:-../src/djangoproject/}"
REPORTS_DIR="${REPORTS_DIR:-../refactoring/reports}"
DEFAULT_SPRINT=1
sprint="${DEFAULT_SPRINT}"
scheme="nested" # 'nested' or 'simple'
DRY_RUN=0
black_mode="check" # 'check' or 'format'

# Tools registration: keys and default commands (will be partially recomputed later)
declare -A TOOL_CMD
# Run pylint from inside the SRC_DIR so package modules resolve correctly.
# Assumes package root is 'djangoproject' inside SRC_DIR (adjust if different).
TOOL_CMD[pylint]="(cd \"${SRC_DIR}\" && pylint djangoproject users posts reviews)"
# Keep Black's default line length (88) consistent with Flake8 to avoid conflicts.
# Exclude common generated folders (migrations, venv, node_modules).
TOOL_CMD[flake8]="flake8 --max-line-length=88 --exclude=migrations,venv,node_modules \"${SRC_DIR}\""
# Vulture tends to report false positives for Django settings and migrations; exclude them.
TOOL_CMD[vulture]="vulture \"${SRC_DIR}\" --exclude 'migrations|settings.py'"
TOOL_CMD[black]="black --${black_mode} \"${SRC_DIR}\""
TOOL_CMD[radon-mi]="radon mi -s \"${SRC_DIR}\""
TOOL_CMD[radon-cc]="radon cc -a -s \"${SRC_DIR}\""
TOOL_CMD[radon-raw]="radon raw \"${SRC_DIR}\""

# Default order
DEFAULT_TOOLS=(pylint flake8 vulture black radon-mi radon-cc radon-raw)

# Internal state
declare -a TOOLS_TO_RUN=()
declare -A TOOL_EXIT
declare -A TOOL_REPORT_PATH
declare -A TOOL_CMD_EXPANDED
start_time="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Fail-on default
fail_on="any"

# --------------------
# Usage
# --------------------
usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Options:
    -s, --sprint N           Sprint number (default: ${DEFAULT_SPRINT})
    -t, --tools a,b,c        Comma-separated subset of tools to run (by key).
                             Available keys: ${DEFAULT_TOOLS[*]}
    --src PATH               Source dir (default: ${SRC_DIR})
    --reports PATH           Reports root dir (default: ${REPORTS_DIR})
    --scheme simple|nested   Output filename scheme (default: nested)
    --fail-on LIST           'any'|'none'|comma-list of tools to cause non-zero exit.
                             (default: ${fail_on})
    --dry-run                Print commands instead of executing them.
    --black-mode check|format Run black in check or format mode (default: check)
    -h, --help               Show this help
Examples:
    $(basename "$0") --sprint 2
    $(basename "$0") -s 3 -t pylint,flake8 --scheme simple
    $(basename "$0") --dry-run --black-mode format
EOF
}

# --------------------
# Helpers
# --------------------
check_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

report_path_for() {
  local tool="$1"
  if [[ "$scheme" == "simple" ]]; then
    echo "${REPORTS_DIR}/${tool}-report${sprint}.txt"
  else
    echo "${SPRINT_DIR}/${tool}-sprint${sprint}.txt"
  fi
}

run_tool() {
  local tool="$1"
  local raw_cmd="${TOOL_CMD[$tool]}"
  TOOL_CMD_EXPANDED[$tool]="$raw_cmd"
  local out_file
  out_file="$(report_path_for "$tool")"
  TOOL_REPORT_PATH[$tool]="$out_file"

  printf "${PURPLE}${BOLD}┌─────────────────────────────────────────────────────────────────────────────┐${NC}\n"
  printf "${PURPLE}${BOLD}│${NC} ${WHITE}🔧 Running: %-20s${NC} ${PURPLE}${BOLD}│${NC}\n" "$tool"
  printf "${PURPLE}${BOLD}└─────────────────────────────────────────────────────────────────────────────┘${NC}\n"
  log_info "Command: ${TOOL_CMD_EXPANDED[$tool]}"

  local t_start t_end elapsed
  t_start="$(date +%s)"

  if [[ "${DRY_RUN:-0}" -eq 1 ]]; then
    printf "${YELLOW}[DRY-RUN]${NC} Command for ${BOLD}${tool}${NC}: ${TOOL_CMD_EXPANDED[$tool]}\n"
    TOOL_EXIT[$tool]=0
  else
    mkdir -p "$(dirname "$out_file")"
    printf "${CYAN}⏳ Executing...${NC}\n"
    if bash -c "${TOOL_CMD_EXPANDED[$tool]}" >"${out_file}" 2>&1; then
      TOOL_EXIT[$tool]=0
    else
      TOOL_EXIT[$tool]=$?
    fi
  fi

  t_end="$(date +%s)"
  elapsed=$((t_end - t_start))

  if [[ "${TOOL_EXIT[$tool]}" -eq 0 ]]; then
    log_success "${tool} completed successfully in ${elapsed}s"
    printf "${GREEN}📄 Report saved: ${out_file}${NC}\n"
  else
    log_error "${tool} failed with exit code ${TOOL_EXIT[$tool]} after ${elapsed}s"
    printf "${RED}📄 Error report saved: ${out_file}${NC}\n"
  fi
  echo

  if [[ "${DRY_RUN:-0}" -eq 0 ]]; then
    {
      printf "\n\n# --- metadata ---\n"
      printf "tool: %s\n" "$tool"
      printf "command: %s\n" "${TOOL_CMD_EXPANDED[$tool]}"
      printf "exit_code: %s\n" "${TOOL_EXIT[$tool]}"
      printf "runtime_seconds: %s\n" "${elapsed}"
      printf "report_path: %s\n" "${out_file}"
    } >>"${out_file}"
  fi
}

# --------------------
# Arg parsing
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
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

# If tools not provided, use defaults
if [[ ${#TOOLS_TO_RUN[@]} -eq 0 ]]; then
  TOOLS_TO_RUN=("${DEFAULT_TOOLS[@]}")
fi

# Recompute black cmd if black_mode set by args
TOOL_CMD[black]="black --${black_mode} \"${SRC_DIR}\""

# --------------------
# Compose fail_on set (after tools list is known)
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
# Determine sprint dir and filenames AFTER args parsing
# --------------------
if [[ "$scheme" == "nested" ]]; then
  SPRINT_DIR="${REPORTS_DIR}/sprint${sprint}"
  mkdir -p "${SPRINT_DIR}"
else
  SPRINT_DIR="${REPORTS_DIR}"
  mkdir -p "${SPRINT_DIR}"
fi

SUMMARY_FILE="${SPRINT_DIR}/summary.txt"

# Ensure reports dir exists (in case REPORTS_DIR was overridden)
mkdir -p "${REPORTS_DIR}"

# --------------------
# Trap: write summary on exit
# --------------------
on_exit() {
  local final_exit=$?
  end_time="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
  {
    printf "start_time: %s\n" "${start_time}"
    printf "end_time:   %s\n" "${end_time}"
    printf "src_dir:    %s\n" "${SRC_DIR}"
    printf "reports_dir:%s\n" "${REPORTS_DIR}"
    printf "sprint:     %s\n" "${sprint}"
    printf "scheme:     %s\n" "${scheme}"
    printf "dry_run:    %s\n" "${DRY_RUN}"
    printf "\n# tools executed:\n"
    for t in "${TOOLS_TO_RUN[@]}"; do
      local code="${TOOL_EXIT[$t]:-not-run}"
      local path="${TOOL_REPORT_PATH[$t]:-N/A}"
      printf "%s: exit=%s path=%s cmd=%s\n" "$t" "$code" "$path" "${TOOL_CMD_EXPANDED[$t]:-N/A}"
    done
    printf "\n# final_exit: %s\n" "${final_exit}"
  } >"${SUMMARY_FILE}.tmp" || true

  mv "${SUMMARY_FILE}.tmp" "${SUMMARY_FILE}" 2>/dev/null || true

  echo
  printf "${PURPLE}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}\n"
  printf "${PURPLE}${BOLD}║                            📊 EXECUTION SUMMARY 📊                           ║${NC}\n"
  printf "${PURPLE}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"

  local success_count=0
  local fail_count=0

  for t in "${TOOLS_TO_RUN[@]}"; do
    local code="${TOOL_EXIT[$t]:-0}"
    if [[ "$code" -eq 0 ]]; then
      success_count=$((success_count + 1))
      printf "${GREEN}✓${NC} %-15s ${GREEN}PASSED${NC}\n" "$t"
    else
      fail_count=$((fail_count + 1))
      printf "${RED}✗${NC} %-15s ${RED}FAILED (exit: $code)${NC}\n" "$t"
    fi
  done

  echo
  printf "${WHITE}📈 Results: ${GREEN}$success_count passed${NC}, ${RED}$fail_count failed${NC}\n"
  printf "${WHITE}📄 Summary file: ${CYAN}${SUMMARY_FILE}${NC}\n"
  echo

  # Determine final exit based on fail_on config and tool exits
  if [[ "${fail_on}" == "none" ]]; then
    exit 0
  fi
  if [[ "${fail_on}" == "any" ]]; then
    for t in "${TOOLS_TO_RUN[@]}"; do
      local code="${TOOL_EXIT[$t]:-0}"
      if [[ "$code" -ne 0 ]]; then
        printf "${RED}${BOLD}💥 PIPELINE FAILED!${NC}\n"
        log_error "Tool ${t} returned ${code} and --fail-on any is set"
        exit 2
      fi
    done
    exit 0
  fi
  for t in "${!FAIL_ON_HASH[@]}"; do
    local code="${TOOL_EXIT[$t]:-0}"
    if [[ "$code" -ne 0 ]]; then
      printf "${RED}${BOLD}💥 PIPELINE FAILED!${NC}\n"
      log_error "Tool ${t} returned ${code} and is in --fail-on list"
      exit 2
    fi
  done
  exit 0
}
trap on_exit EXIT

# --------------------
# Start execution
# --------------------
print_header

# Validate presence of tools (report missing ones, continue or error as appropriate)
missing_tools=()
for t in "${TOOLS_TO_RUN[@]}"; do
  case "$t" in
    pylint) bin="pylint" ;;
    flake8) bin="flake8" ;;
    vulture) bin="vulture" ;;
    black) bin="black" ;;
    radon-mi|radon-cc|radon-raw) bin="radon" ;;
    *) bin="$t" ;;
  esac
  if ! check_command "$bin"; then
    missing_tools+=("$bin")
    log "WARNING: required command '$bin' (for tool '$t') not found in PATH"
  fi
done

if [[ "${#missing_tools[@]}" -gt 0 ]]; then
  echo
  printf "${RED}${BOLD}❌ ERROR: Missing required tools!${NC}\n"
  printf "${RED}🚫 Missing commands: ${missing_tools[*]}${NC}\n"
  echo
  printf "${YELLOW}💡 Install them with:${NC}\n"
  printf "${WHITE}   pip install pylint flake8 vulture black radon${NC}\n"
  echo
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    log_warning "Continuing in dry-run despite missing tools"
  else
    exit 3
  fi
fi

# Run tools
for t in "${TOOLS_TO_RUN[@]}"; do
  if [[ -z "${TOOL_CMD[$t]-}" ]]; then
    log "Unknown tool key: $t — skipping"
    TOOL_EXIT[$t]=127
    continue
  fi
  run_tool "$t"
done