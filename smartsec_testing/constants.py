import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# TODO разделить файлы констант между фласком и bot_testing
TELEGRAM_BOT_TOKEN = os.getenv('TESTING_BOT_KEY')
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = os.environ.get('PG_PORT')
PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASSWORD')
PG_DBNAME = os.environ.get('PG_DBNAME')
MY_ID = os.environ.get('MY_ID')
MY_NAME = os.environ.get('MY_NAME')
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

TESTING_QUESTION_COUNT = 3
