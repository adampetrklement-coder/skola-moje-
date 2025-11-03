# Inicializace prostředí na cizím PC (bez aktivace venv)
param(
    [switch]$NoDesktop
)

Write-Host "[SETUP] Kontrola Pythonu..." -ForegroundColor Cyan

$pythonCmd = $null
try {
    $ver = & py -3 --version 2>$null
    if ($LASTEXITCODE -eq 0) { $pythonCmd = 'py -3' }
} catch {}

if (-not $pythonCmd) {
    try {
        $ver = & python --version 2>$null
        if ($LASTEXITCODE -eq 0) { $pythonCmd = 'python' }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "[SETUP] Python nebyl nalezen. Na školním PC nainstaluj Python 3.11+ do profilu uživatele (bez admin) a spusť skript znovu." -ForegroundColor Yellow
    exit 1
}

Write-Host "[SETUP] Python: $pythonCmd" -ForegroundColor Green

if (-not (Test-Path ".\.venv")) {
    Write-Host "[SETUP] Vytvářím virtuální prostředí .venv" -ForegroundColor Cyan
    iex "$pythonCmd -m venv .venv"
    if ($LASTEXITCODE -ne 0) { Write-Host "[SETUP] Vytvoření venv selhalo" -ForegroundColor Red; exit 1 }
}

$venvPy = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) { Write-Host "[SETUP] Nenalezen python v .venv" -ForegroundColor Red; exit 1 }

Write-Host "[SETUP] Aktualizuji pip" -ForegroundColor Cyan
& $venvPy -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { Write-Host "[SETUP] Upgrade pip selhal" -ForegroundColor Yellow }

Write-Host "[SETUP] Instaluji backend závislosti" -ForegroundColor Cyan
& $venvPy -m pip install -r "backend\requirements.txt"
if ($LASTEXITCODE -ne 0) { Write-Host "[SETUP] Instalace backend závislostí selhala" -ForegroundColor Red; exit 1 }

if (-not $NoDesktop) {
    Write-Host "[SETUP] Instaluji desktop (Kivy) závislosti" -ForegroundColor Cyan
    & $venvPy -m pip install -r "fitness_app\requirements.txt"
    if ($LASTEXITCODE -ne 0) { Write-Host "[SETUP] Instalace desktop závislostí selhala" -ForegroundColor Yellow }
}

Write-Host "[SETUP] Hotovo. Můžeš spustit 'Spustit_Aplikaci.bat' nebo web server přes 'run_web.ps1'." -ForegroundColor Green
