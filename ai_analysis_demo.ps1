# =============================================================================
# HomeMatch - Demo Script
# Creates 3 distinct properties and uploads all photos from their respective
# folders, triggering automatic LLM Vision analysis on each photo.
#
# Folder structure expected at project root:
#   property_examples/
#     property_1/   <- haunted house photos    (.jpg, .jpeg, .png)
#     property_2/   <- normal condo apartment  (.jpg, .jpeg, .png)
#     property_3/   <- futuristic sci-fi house (.jpg, .jpeg, .png)
#
# Usage:
#   .\demo.ps1
#   .\demo.ps1 -DbUser "postgres" -DbName "homematch_db"
# =============================================================================

param(
    [string]$BaseUrl  = "http://localhost:8000",
    [string]$Email    = "demo@test.com",
    [string]$Password = "demo1234!",
    [string]$DbUser   = "postgres",
    [string]$DbName   = "homematch_db"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

function Write-Step([string]$msg) {
    Write-Host "`n===> $msg" -ForegroundColor Cyan
}

function Write-OK([string]$msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}

function Write-Warn([string]$msg) {
    Write-Host "  [WARN] $msg" -ForegroundColor Yellow
}

function Write-Fail([string]$msg) {
    Write-Host "  [FAIL] $msg" -ForegroundColor Red
    exit 1
}

function Invoke-Api {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = "",
        [string]$ContentType = "application/json"
    )
    try {
        $params = @{
            Method      = $Method
            Uri         = $Url
            Headers     = $Headers
            ErrorAction = "Stop"
        }
        if ($Body) {
            $params.Body        = $Body
            $params.ContentType = $ContentType
        }
        return Invoke-RestMethod @params
    }
    catch {
        $status = $_.Exception.Response.StatusCode.value__
        $detail = $_.ErrorDetails.Message
        Write-Fail "HTTP $status on $Method $Url - $detail"
    }
}

function Upload-Photo {
    param(
        [string]$PropertyId,
        [string]$Path,
        [int]$Order
    )
    $filename = Split-Path $Path -Leaf
    Write-Host "    Uploading photo $Order - $filename" -ForegroundColor Gray

    $result = & curl.exe -s -X POST "$BaseUrl/api/properties/$PropertyId/photos/" `
        -H "Authorization: Bearer $TOKEN" `
        -F "image=@$Path" `
        -F "order=$Order"

    try {
        $parsed = $result | ConvertFrom-Json
        Write-Host "    Photo id=$($parsed.id) uploaded. Waiting for AI analysis..." -ForegroundColor Gray
    }
    catch {
        Write-Warn "Could not parse upload response for $filename - $result"
    }

    Start-Sleep -Seconds 5
}

function Upload-FolderPhotos {
    param(
        [string]$PropertyId,
        [string]$FolderPath
    )
    $photos = @(
        Get-ChildItem -Path $FolderPath -File |
        Where-Object { $_.Extension -match '\.(jpg|jpeg|png)$' } |
        Sort-Object Name
    )

    if ($photos.Count -eq 0) {
        Write-Warn "No photos found in $FolderPath - skipping."
        return
    }

    Write-OK "$($photos.Count) photo(s) found"
    $order = 1
    foreach ($photo in $photos) {
        Upload-Photo -PropertyId $PropertyId -Path $photo.FullName -Order $order
        $order++
    }
}

function Show-DbAttributes {
    param(
        [string]$PropertyId,
        [string]$Label
    )
    Write-Step "DB check - $Label (property id=$PropertyId)"

    Write-Host "  PhotoSubjectiveAttribute (per photo):" -ForegroundColor Gray
    docker compose exec db psql -U $DbUser -d $DbName -c "SELECT attribute_token, ROUND(strength::numeric, 3) AS strength FROM ai_analysis_photosubjectiveattribute WHERE property_id = $PropertyId ORDER BY strength DESC LIMIT 10;"

    Write-Host "  PropertySubjectiveAttribute (aggregated):" -ForegroundColor Gray
    docker compose exec db psql -U $DbUser -d $DbName -c "SELECT attribute_token, ROUND(strength_mean::numeric, 3) AS mean FROM ai_analysis_propertysubjectiveattribute WHERE property_id = $PropertyId ORDER BY mean DESC;"
}

# -----------------------------------------------------------------------------
# Validate photo folders
# -----------------------------------------------------------------------------

Write-Step "Validating photo folders"

$examplesRoot = Join-Path $PSScriptRoot "property_examples"
$folder1 = Join-Path $examplesRoot "property_1"
$folder2 = Join-Path $examplesRoot "property_2"
$folder3 = Join-Path $examplesRoot "property_3"

foreach ($folder in @($folder1, $folder2, $folder3)) {
    if (-not (Test-Path $folder)) {
        Write-Fail "Folder not found: $folder`n  Create it and add photos before running."
    }
    $count = @(
        Get-ChildItem -Path $folder -File |
        Where-Object { $_.Extension -match '\.(jpg|jpeg|png)$' }
    ).Count
    if ($count -eq 0) {
        Write-Fail "Folder is empty: $folder`n  Add at least one .jpg / .jpeg / .png photo."
    }
    Write-OK "$folder - $count photo(s) ready"
}

# -----------------------------------------------------------------------------
# Step 1: Register advertiser
# -----------------------------------------------------------------------------

Write-Step "Registering advertiser ($Email)"

$registerBody = @{
    name      = "Demo User"
    email     = $Email
    password  = $Password
    user_type = "A"
} | ConvertTo-Json

try {
    $register = Invoke-Api -Method POST -Url "$BaseUrl/api/users/register/" -Body $registerBody
    Write-OK "Registered - user id=$($register.id)"
}
catch {
    Write-Warn "User may already exist, continuing..."
}

# -----------------------------------------------------------------------------
# Step 2: Login
# -----------------------------------------------------------------------------

Write-Step "Logging in"

$loginBody = @{
    email    = $Email
    password = $Password
} | ConvertTo-Json

$login = Invoke-Api -Method POST -Url "$BaseUrl/api/users/login/" -Body $loginBody
$script:TOKEN = $login.access
Write-OK "Token obtained"

$authHeaders = @{ Authorization = "Bearer $TOKEN" }

# -----------------------------------------------------------------------------
# Step 3: Create property 1 - Haunted House
# -----------------------------------------------------------------------------

Write-Step "Creating Property 1 - The Haunted House"

$prop1Body = @{
    property_purpose = "S"
    type             = "H"
    area             = 340
    floors           = 3
    price            = "185000.00"
    address          = "Rua das Almas Perdidas, 13"
    neighborhood     = "Vila Sombria"
    city             = "Natal"
    description      = "Mansao de 1887 com historia perturbadora. Paredes originais, madeiras rangentes, porao selado e jardim de vegetacao densa. Relatorios de atividade inexplicavel pelos ultimos tres proprietarios. Vende-se no estado."
    rooms            = @{ bedrooms = 6; bathrooms = 3; parking_spots = 2 }
    rooms_extras     = @{ living_room = $true; kitchen = $true; garden = $true; office = $true }
    embedding        = "[]"
} | ConvertTo-Json -Depth 5

$prop1 = Invoke-Api -Method POST -Url "$BaseUrl/api/properties/" -Headers $authHeaders -Body $prop1Body
$prop1Id = $prop1.id
Write-OK "Property 1 created - id=$prop1Id"

# -----------------------------------------------------------------------------
# Step 4: Create property 2 - Condo Apartment
# -----------------------------------------------------------------------------

Write-Step "Creating Property 2 - Condo Apartment"

$prop2Body = @{
    property_purpose = "R"
    type             = "A"
    area             = 72
    floors           = 12
    floor_number     = 8
    price            = "2800.00"
    address          = "Avenida das Dunas, 850"
    neighborhood     = "Ponta Negra"
    city             = "Natal"
    description      = "Apartamento moderno em condominio fechado com infraestrutura completa. Acabamento padrao medio-alto, sala integrada a varanda, cozinha americana. Condominio com piscina, academia e salao de festas."
    rooms            = @{ bedrooms = 2; bathrooms = 2; parking_spots = 1 }
    rooms_extras     = @{ living_room = $true; kitchen = $true; laundry_room = $true }
    condo            = @{
        name         = "Residencial Dunas"
        address      = "Avenida das Dunas, 850 - Ponta Negra, Natal"
        gym          = $true
        pool         = $true
        party_spaces = $true
        concierge    = $true
        court        = $false
        parks        = $false
    }
    embedding        = "[]"
} | ConvertTo-Json -Depth 5

$prop2 = Invoke-Api -Method POST -Url "$BaseUrl/api/properties/" -Headers $authHeaders -Body $prop2Body
$prop2Id = $prop2.id
Write-OK "Property 2 created - id=$prop2Id"

# -----------------------------------------------------------------------------
# Step 5: Create property 3 - Futuristic Sci-Fi House
# -----------------------------------------------------------------------------

Write-Step "Creating Property 3 - Futuristic Sci-Fi House"

$prop3Body = @{
    property_purpose = "S"
    type             = "H"
    area             = 520
    floors           = 2
    price            = "4200000.00"
    address          = "Rua da Singularidade, 2077"
    neighborhood     = "Neopolis"
    city             = "Natal"
    description      = "Residencia de alto padrao com arquitetura bionica e tecnologia integrada. Fachada em vidro inteligente com opacidade controlavel, automacao total por IA, paineis solares de ultima geracao, piscina com borda infinita e laboratorio pessoal. Design inspirado em naves espaciais."
    rooms            = @{ bedrooms = 4; bathrooms = 4; parking_spots = 4 }
    rooms_extras     = @{ living_room = $true; kitchen = $true; office = $true; pool = $true; laundry_room = $true }
    embedding        = "[]"
} | ConvertTo-Json -Depth 5

$prop3 = Invoke-Api -Method POST -Url "$BaseUrl/api/properties/" -Headers $authHeaders -Body $prop3Body
$prop3Id = $prop3.id
Write-OK "Property 3 created - id=$prop3Id"

# -----------------------------------------------------------------------------
# Step 6: Upload photos (triggers AI signal on each)
# -----------------------------------------------------------------------------

Write-Step "Uploading photos for Property 1 - Haunted House (id=$prop1Id)"
Upload-FolderPhotos -PropertyId $prop1Id -FolderPath $folder1

Write-Step "Uploading photos for Property 2 - Condo Apartment (id=$prop2Id)"
Upload-FolderPhotos -PropertyId $prop2Id -FolderPath $folder2

Write-Step "Uploading photos for Property 3 - Sci-Fi House (id=$prop3Id)"
Upload-FolderPhotos -PropertyId $prop3Id -FolderPath $folder3

# -----------------------------------------------------------------------------
# Step 7: Confirm AI attributes in DB
# -----------------------------------------------------------------------------

Show-DbAttributes -PropertyId $prop1Id -Label "Haunted House"
Show-DbAttributes -PropertyId $prop2Id -Label "Condo Apartment"
Show-DbAttributes -PropertyId $prop3Id -Label "Sci-Fi House"

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Demo complete!" -ForegroundColor Cyan
Write-Host "  Admin:      $BaseUrl/admin" -ForegroundColor Cyan
Write-Host "  All props:  $BaseUrl/api/properties/" -ForegroundColor Cyan
Write-Host "  Property 1 (Haunted House):   $BaseUrl/api/properties/$prop1Id/" -ForegroundColor Cyan
Write-Host "  Property 2 (Condo Apartment): $BaseUrl/api/properties/$prop2Id/" -ForegroundColor Cyan
Write-Host "  Property 3 (Sci-Fi House):    $BaseUrl/api/properties/$prop3Id/" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan