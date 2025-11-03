# Fitness Aplikace

Aplikace pro sledování fitness tréninků s webovým rozhraním a desktop aplikací.

## Struktura projektu

- `backend/` - Flask API server
- `fitness_app/` - Kivy desktop aplikace
- `web/` - Webové rozhraní

## Instalace a spuštění

### Backend (API server)

1. Vytvořte virtuální prostředí a aktivujte ho:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

3. Nastavte proměnné prostředí:
```bash
# Windows
set FLASK_ENV=development
set DB_PASSWORD=vase_heslo_k_db

# Linux/Mac
export FLASK_ENV=development
export DB_PASSWORD=vase_heslo_k_db
```

4. Spusťte server:
```bash
python app.py
```

### Desktop aplikace

1. Vytvořte virtuální prostředí:
```bash
cd fitness_app
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

3. Spusťte aplikaci:
```bash
python main.py
```

### Webové rozhraní

1. Umístěte soubory z adresáře `web/` na váš webový server nebo spusťte lokální server:
```bash
cd web
python -m http.server 5000
```

## Konfigurace

### Backend

- Upravte `backend/config.py` pro nastavení databáze a dalších parametrů
- V produkci nastavte proměnné prostředí:
  - `FLASK_ENV=production`
  - `DB_PASSWORD=vase_heslo`
  - `SECRET_KEY=vas_tajny_klic`
  - `FRONTEND_URL=https://vase-domena.cz`

### Desktop aplikace

- Upravte `API_URL` v `fitness_app/api.py` pokud backend běží na jiné adrese než `http://localhost:5000`

## Databáze

1. Nainstalujte MySQL server
2. Spusťte inicializační skript:
```bash
mysql -u root -p < backend/schema.sql
```

## Vývoj

### Přidání nových funkcí

1. Backend:
   - Přidejte nové endpointy do `app.py`
   - Aktualizujte databázové schéma v `schema.sql`

2. Desktop aplikace:
   - Přidejte nové API volání do `api.py`
   - Aktualizujte UI v `fitness.kv`
   - Přidejte novou logiku do `main.py`

### Testování

- Backend testy: TODO
- Desktop aplikace testy: TODO

## Známé problémy

- Offline režim není implementován
- Chybí obnovení zapomenutého hesla
- Chybí export dat