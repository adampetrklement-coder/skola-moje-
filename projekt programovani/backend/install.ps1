# Aktivace společného virtuálního prostředí (v kořeni projektu)
if (Test-Path ..\.venv\Scripts\Activate.ps1) {
	& ..\.venv\Scripts\Activate.ps1
} else {
	python -m venv ..\.venv
	& ..\.venv\Scripts\Activate.ps1
}

# Instalace závislostí
pip install -r requirements.txt

# Nastavení proměnných prostředí (volitelné pro Flask)
$env:FLASK_ENV = "development"

Write-Host "Backend instalace dokončena!"