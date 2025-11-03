import os

# Základní konfigurace
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'fitness.db')
SECRET_KEY = 'tajny_klic_pro_tokeny'
CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
