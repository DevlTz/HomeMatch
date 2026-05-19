#!/usr/bin/env bash
# =============================================================================
# HomeMatch - Demo Script (Linux/Bash)
# Creates 3 demo properties and uploads all photos from their respective folders,
# triggering automatic LLM Vision analysis on each photo.
#
# Also supports re-uploading photos to existing properties, useful when local
# media files were deleted but the database still has the property records.
#
# Expected folder structure at project root:
#   property_examples/
#     property_1/   <- haunted house photos    (.jpg, .jpeg, .png)
#     property_2/   <- normal condo apartment  (.jpg, .jpeg, .png)
#     property_3/   <- futuristic sci-fi house (.jpg, .jpeg, .png)
#
# Usage:
#   chmod +x ai_analysis_demo.sh
#
#   # Create properties and upload photos:
#   ./ai_analysis_demo.sh
#
#   # Re-upload photos to existing property IDs:
#   ./ai_analysis_demo.sh --existing-ids 38,39,40
#
#   # Custom DB user/name:
#   ./ai_analysis_demo.sh --db-user admin --db-name homematch_db
#
# Requirements:
#   curl, python3, docker compose
# =============================================================================

set -Eeuo pipefail

BASE_URL="http://localhost:8000"
EMAIL="demo@test.com"
PASSWORD="demo1234!"
DB_USER="postgres"
DB_NAME="homematch_db"
EXISTING_IDS=""

# -----------------------------------------------------------------------------
# CLI args
# -----------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url)
      BASE_URL="$2"
      shift 2
      ;;
    --email)
      EMAIL="$2"
      shift 2
      ;;
    --password)
      PASSWORD="$2"
      shift 2
      ;;
    --db-user)
      DB_USER="$2"
      shift 2
      ;;
    --db-name)
      DB_NAME="$2"
      shift 2
      ;;
    --existing-ids)
      EXISTING_IDS="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '1,45p' "$0"
      exit 0
      ;;
    *)
      echo "[FAIL] Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

write_step() {
  echo
  echo "===> $1"
}

write_ok() {
  echo "  [OK] $1"
}

write_warn() {
  echo "  [WARN] $1"
}

write_fail() {
  echo "  [FAIL] $1" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || write_fail "Required command not found: $1"
}

json_get() {
  local json="$1"
  local expr="$2"

  python3 - "$expr" <<'PY' <<<"$json"
import json
import sys

expr = sys.argv[1]
data = json.load(sys.stdin)

cur = data
for part in expr.split("."):
    if isinstance(cur, dict):
        cur = cur.get(part)
    else:
        cur = None
        break

if cur is None:
    sys.exit(1)

print(cur)
PY
}

api_request() {
  local method="$1"
  local url="$2"
  local body="${3:-}"
  local auth="${4:-}"

  local tmp_body
  local tmp_status

  tmp_body="$(mktemp)"
  tmp_status="$(mktemp)"

  local args=(-sS -X "$method" "$url" -H "Content-Type: application/json" -o "$tmp_body" -w "%{http_code}")

  if [[ -n "$auth" ]]; then
    args+=(-H "Authorization: Bearer $auth")
  fi

  if [[ -n "$body" ]]; then
    args+=(-d "$body")
  fi

  local status
  status="$(curl "${args[@]}")"
  echo "$status" > "$tmp_status"

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "  [FAIL] HTTP $status on $method $url" >&2
    cat "$tmp_body" >&2
    echo >&2
    rm -f "$tmp_body" "$tmp_status"
    exit 1
  fi

  cat "$tmp_body"
  rm -f "$tmp_body" "$tmp_status"
}

upload_photo() {
  local property_id="$1"
  local path="$2"
  local order="$3"

  local filename
  filename="$(basename "$path")"

  echo "    Uploading photo $order - $filename"

  local tmp_body
  tmp_body="$(mktemp)"

  local status
  status="$(
    curl -sS -X POST "$BASE_URL/api/properties/$property_id/photos/" \
      -H "Authorization: Bearer $TOKEN" \
      -F "image=@$path" \
      -F "order=$order" \
      -o "$tmp_body" \
      -w "%{http_code}"
  )"

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "  [FAIL] HTTP $status uploading $filename to property $property_id" >&2
    cat "$tmp_body" >&2
    echo >&2
    rm -f "$tmp_body"
    exit 1
  fi

  local photo_id
  photo_id="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("id", "?"))' < "$tmp_body" 2>/dev/null || echo "?")"
  echo "    Photo id=$photo_id uploaded. Waiting for AI analysis..."

  rm -f "$tmp_body"

  sleep 5
}

upload_folder_photos() {
  local property_id="$1"
  local folder_path="$2"

  shopt -s nullglob
  local photos=("$folder_path"/*.jpg "$folder_path"/*.jpeg "$folder_path"/*.png "$folder_path"/*.JPG "$folder_path"/*.JPEG "$folder_path"/*.PNG)
  shopt -u nullglob

  if [[ "${#photos[@]}" -eq 0 ]]; then
    write_warn "No photos found in $folder_path - skipping."
    return
  fi

  IFS=$'\n' photos=($(printf "%s\n" "${photos[@]}" | sort))
  unset IFS

  write_ok "${#photos[@]} photo(s) found"

  local order=1
  local photo
  for photo in "${photos[@]}"; do
    upload_photo "$property_id" "$photo" "$order"
    order=$((order + 1))
  done
}

show_db_attributes() {
  local property_id="$1"
  local label="$2"

  write_step "DB check - $label (property id=$property_id)"

  echo "  PhotoSubjectiveAttribute (per photo):"
  docker compose exec db psql -U "$DB_USER" -d "$DB_NAME" -c \
    "SELECT attribute_token, ROUND(strength::numeric, 3) AS strength
     FROM ai_analysis_photosubjectiveattribute
     WHERE property_id = $property_id
     ORDER BY strength DESC
     LIMIT 10;"

  echo "  PropertySubjectiveAttribute (aggregated):"
  docker compose exec db psql -U "$DB_USER" -d "$DB_NAME" -c \
    "SELECT attribute_token, ROUND(strength_mean::numeric, 3) AS mean
     FROM ai_analysis_propertysubjectiveattribute
     WHERE property_id = $property_id
     ORDER BY mean DESC;"
}

make_json() {
  python3 - "$1" <<'PY'
import json
import sys

kind = sys.argv[1]

properties = {
    "property_1": {
        "property_purpose": "S",
        "type": "H",
        "area": 340,
        "floors": 3,
        "price": "185000.00",
        "address": "Rua das Almas Perdidas, 13",
        "neighborhood": "Vila Sombria",
        "city": "Natal",
        "description": "Mansao de 1887 com historia perturbadora. Paredes originais, madeiras rangentes, porao selado e jardim de vegetacao densa. Relatorios de atividade inexplicavel pelos ultimos tres proprietarios. Vende-se no estado.",
        "rooms": {"bedrooms": 6, "bathrooms": 3, "parking_spots": 2},
        "rooms_extras": {"living_room": True, "kitchen": True, "garden": True, "office": True},
        "embedding": "[]",
    },
    "property_2": {
        "property_purpose": "R",
        "type": "A",
        "area": 72,
        "floors": 12,
        "floor_number": 8,
        "price": "2800.00",
        "address": "Avenida das Dunas, 850",
        "neighborhood": "Ponta Negra",
        "city": "Natal",
        "description": "Apartamento moderno em condominio fechado com infraestrutura completa. Acabamento padrao medio-alto, sala integrada a varanda, cozinha americana. Condominio com piscina, academia e salao de festas.",
        "rooms": {"bedrooms": 2, "bathrooms": 2, "parking_spots": 1},
        "rooms_extras": {"living_room": True, "kitchen": True, "laundry_room": True},
        "condo": {
            "name": "Residencial Dunas",
            "address": "Avenida das Dunas, 850 - Ponta Negra, Natal",
            "gym": True,
            "pool": True,
            "party_spaces": True,
            "concierge": True,
            "court": False,
            "parks": False,
        },
        "embedding": "[]",
    },
    "property_3": {
        "property_purpose": "S",
        "type": "H",
        "area": 520,
        "floors": 2,
        "price": "4200000.00",
        "address": "Rua da Singularidade, 2077",
        "neighborhood": "Neopolis",
        "city": "Natal",
        "description": "Residencia de alto padrao com arquitetura bionica e tecnologia integrada. Fachada em vidro inteligente com opacidade controlavel, automacao total por IA, paineis solares de ultima geracao, piscina com borda infinita e laboratorio pessoal. Design inspirado em naves espaciais.",
        "rooms": {"bedrooms": 4, "bathrooms": 4, "parking_spots": 4},
        "rooms_extras": {"living_room": True, "kitchen": True, "office": True, "pool": True, "laundry_room": True},
        "embedding": "[]",
    },
}

print(json.dumps(properties[kind], ensure_ascii=False))
PY
}

# -----------------------------------------------------------------------------
# Requirements
# -----------------------------------------------------------------------------

require_cmd curl
require_cmd python3
require_cmd docker

# -----------------------------------------------------------------------------
# Validate photo folders
# -----------------------------------------------------------------------------

write_step "Validating photo folders"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLES_ROOT="$SCRIPT_DIR/property_examples"

FOLDER1="$EXAMPLES_ROOT/property_1"
FOLDER2="$EXAMPLES_ROOT/property_2"
FOLDER3="$EXAMPLES_ROOT/property_3"

for folder in "$FOLDER1" "$FOLDER2" "$FOLDER3"; do
  [[ -d "$folder" ]] || write_fail "Folder not found: $folder"$'\n'"  Create it and add photos before running."

  shopt -s nullglob
  files=("$folder"/*.jpg "$folder"/*.jpeg "$folder"/*.png "$folder"/*.JPG "$folder"/*.JPEG "$folder"/*.PNG)
  shopt -u nullglob

  if [[ "${#files[@]}" -eq 0 ]]; then
    write_fail "Folder is empty: $folder"$'\n'"  Add at least one .jpg / .jpeg / .png photo."
  fi

  write_ok "$folder - ${#files[@]} photo(s) ready"
done

# -----------------------------------------------------------------------------
# Register advertiser
# -----------------------------------------------------------------------------

write_step "Registering advertiser ($EMAIL)"

REGISTER_BODY="$(python3 - <<PY
import json
print(json.dumps({
    "name": "Demo User",
    "email": "$EMAIL",
    "password": "$PASSWORD",
    "user_type": "A",
}))
PY
)"

REGISTER_STATUS="$(
  curl -sS -X POST "$BASE_URL/api/users/register/" \
    -H "Content-Type: application/json" \
    -d "$REGISTER_BODY" \
    -o /tmp/homematch_register_response.json \
    -w "%{http_code}"
)"

if [[ "$REGISTER_STATUS" -ge 200 && "$REGISTER_STATUS" -lt 300 ]]; then
  USER_ID="$(python3 -c 'import json; print(json.load(open("/tmp/homematch_register_response.json")).get("id", "?"))' 2>/dev/null || echo "?")"
  write_ok "Registered - user id=$USER_ID"
else
  write_warn "User may already exist, continuing..."
fi

rm -f /tmp/homematch_register_response.json

# -----------------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------------

write_step "Logging in"

LOGIN_BODY="$(python3 - <<PY
import json
print(json.dumps({
    "email": "$EMAIL",
    "password": "$PASSWORD",
}))
PY
)"

LOGIN_RESPONSE="$(api_request POST "$BASE_URL/api/users/login/" "$LOGIN_BODY")"
TOKEN="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["access"])' <<<"$LOGIN_RESPONSE")"

write_ok "Token obtained"

# -----------------------------------------------------------------------------
# Create properties or use existing IDs
# -----------------------------------------------------------------------------

if [[ -n "$EXISTING_IDS" ]]; then
  write_step "Using existing properties"

  IFS=',' read -r PROP1_ID PROP2_ID PROP3_ID <<< "$EXISTING_IDS"

  [[ -n "${PROP1_ID:-}" && -n "${PROP2_ID:-}" && -n "${PROP3_ID:-}" ]] \
    || write_fail "--existing-ids must have exactly 3 ids, example: --existing-ids 38,39,40"

  write_ok "Property 1 id=$PROP1_ID"
  write_ok "Property 2 id=$PROP2_ID"
  write_ok "Property 3 id=$PROP3_ID"
else
  write_step "Creating Property 1 - The Haunted House"
  PROP1_RESPONSE="$(api_request POST "$BASE_URL/api/properties/" "$(make_json property_1)" "$TOKEN")"
  PROP1_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$PROP1_RESPONSE")"
  write_ok "Property 1 created - id=$PROP1_ID"

  write_step "Creating Property 2 - Condo Apartment"
  PROP2_RESPONSE="$(api_request POST "$BASE_URL/api/properties/" "$(make_json property_2)" "$TOKEN")"
  PROP2_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$PROP2_RESPONSE")"
  write_ok "Property 2 created - id=$PROP2_ID"

  write_step "Creating Property 3 - Futuristic Sci-Fi House"
  PROP3_RESPONSE="$(api_request POST "$BASE_URL/api/properties/" "$(make_json property_3)" "$TOKEN")"
  PROP3_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$PROP3_RESPONSE")"
  write_ok "Property 3 created - id=$PROP3_ID"
fi

# -----------------------------------------------------------------------------
# Upload photos
# -----------------------------------------------------------------------------

write_step "Uploading photos for Property 1 - Haunted House (id=$PROP1_ID)"
upload_folder_photos "$PROP1_ID" "$FOLDER1"

write_step "Uploading photos for Property 2 - Condo Apartment (id=$PROP2_ID)"
upload_folder_photos "$PROP2_ID" "$FOLDER2"

write_step "Uploading photos for Property 3 - Sci-Fi House (id=$PROP3_ID)"
upload_folder_photos "$PROP3_ID" "$FOLDER3"

# -----------------------------------------------------------------------------
# Confirm AI attributes in DB
# -----------------------------------------------------------------------------

show_db_attributes "$PROP1_ID" "Haunted House"
show_db_attributes "$PROP2_ID" "Condo Apartment"
show_db_attributes "$PROP3_ID" "Sci-Fi House"

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------

echo
echo "========================================"
echo "  Demo complete!"
echo "  Admin:      $BASE_URL/admin"
echo "  All props:  $BASE_URL/api/properties/"
echo "  Property 1 (Haunted House):   $BASE_URL/api/properties/$PROP1_ID/"
echo "  Property 2 (Condo Apartment): $BASE_URL/api/properties/$PROP2_ID/"
echo "  Property 3 (Sci-Fi House):    $BASE_URL/api/properties/$PROP3_ID/"
echo "========================================"
echo
