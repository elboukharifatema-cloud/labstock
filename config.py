import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Sur Render, le disque persistant est monté sur /data
# En local, on utilise le dossier database/
if os.path.exists('/data'):
    DATABASE = '/data/lab_stock.db'
else:
    DATABASE = os.path.join(BASE_DIR, 'database', 'lab_stock.db')

SECRET_KEY = os.environ.get('SECRET_KEY', 'lab-stock-secret-key-2024')
ITEMS_PER_PAGE = 20
LOW_STOCK_EXPIRY_DAYS = 30
