import os
import time
from dotenv import load_dotenv

# Ожидаем пока контейнер webhook_url_extractor запишет URL в volume
time.sleep(5)
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

volume_path = os.path.join(os.path.dirname(__file__), '/shared/webhook_url.txt')
if os.path.exists(volume_path):
    with open(volume_path, "r") as f:
        print(f"f = ")
        WEBHOOK_URL = f.read().strip() + "/webhook"
else:
    WEBHOOK_URL = None

TELEGRAM_BOT_TOKEN = os.getenv('TESTING_BOT_KEY')
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = os.environ.get('PG_PORT')
PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASSWORD')
PG_DBNAME = os.environ.get('PG_DBNAME')
WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT')
CLOUDPUB_TOKEN = os.environ.get('CLOUDPUB_TOKEN')
TG_WEBHOOK_INFO_URL = os.environ.get('TG_WEBHOOK_INFO_URL').format(cloudpub_token=CLOUDPUB_TOKEN)

REGULAR_QUESTIONS_PERIOD = 2*24*60*60
REGULAR_COMPLETE_RESULT = 0.6

ANSWER_TO_TESTING_QUESTION_TIME = 10
TESTING_COMPLETE_RESULT = 0.8
TESTING_QUESTION_COUNT = 4
