import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

PG_HOST = os.environ.get('PG_HOST')
PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASSWORD')
PG_DBNAME = os.environ.get('PG_DBNAME')
FLASK_ADMIN_PORT = os.environ.get('FLASK_ADMIN_PORT')
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
