# Aktivace společného virtuálního prostředí a spuštění procesů

# Spuštění backendu s root .venv
Start-Process powershell -ArgumentList "-NoExit -Command `". .\\.venv\\Scripts\\Activate.ps1; python backend\\app.py`""

# Spuštění desktop aplikace s root .venv
Start-Process powershell -ArgumentList "-NoExit -Command `". .\\.venv\\Scripts\\Activate.ps1; python fitness_app\\main.py`""

# Spuštění webového serveru
Start-Process powershell -ArgumentList "-NoExit -Command `". .\\.venv\\Scripts\\Activate.ps1; cd web; python -m http.server 5000`""