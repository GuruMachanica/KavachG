# VajraNetra 1-Click Launch Script (Windows PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  VAJRANETRA - INDUSTRIAL AI COMMAND CENTER       " -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Cyan

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT_DIR

# 1. Virtual Environment Setup
$VENV_DIR = Join-Path $ROOT_DIR ".venv"
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "[*] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv $VENV_DIR
}

$PYTHON = Join-Path $VENV_DIR "Scripts\python.exe"

Write-Host "[*] Installing & verifying backend requirements..." -ForegroundColor Yellow
& $PYTHON -m pip install -q -r "$ROOT_DIR\Backend\requirements.txt"

# 2. Environment Configuration
$ENV_FILE = Join-Path $ROOT_DIR "Backend\.env"
$ENV_EXAMPLE = Join-Path $ROOT_DIR "Backend\.env.example"
if (-not (Test-Path $ENV_FILE) -and (Test-Path $ENV_EXAMPLE)) {
    Write-Host "[*] Initializing Backend\.env from template..." -ForegroundColor Yellow
    Copy-Item $ENV_EXAMPLE $ENV_FILE
}

# 3. Create Admin User if missing
Write-Host "[*] Verifying admin user credentials..." -ForegroundColor Yellow
Push-Location "$ROOT_DIR\Backend"
& $PYTHON create_admin_user.py
Pop-Location

# 4. Launch Backend & Frontend Servers
Write-Host "[+] Launching FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
$backendJob = Start-Process -FilePath $PYTHON -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -WorkingDirectory "$ROOT_DIR\Backend" -PassThru

Write-Host "[+] Launching Command Center Frontend on http://127.0.0.1:5500..." -ForegroundColor Green
$frontendJob = Start-Process -FilePath $PYTHON -ArgumentList "-m", "http.server", "5500" -WorkingDirectory "$ROOT_DIR\Frontend" -PassThru

Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:5500/landing.html"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "VajraNetra Command Center is live!" -ForegroundColor Green
Write-Host "Landing:  http://127.0.0.1:5500/landing.html" -ForegroundColor White
Write-Host "Console:  http://127.0.0.1:5500/index.html" -ForegroundColor White
Write-Host "Backend:  http://127.0.0.1:8000 (Swagger: /docs)" -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Cyan
