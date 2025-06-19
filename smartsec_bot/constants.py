import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TELEGRAM_BOT_TOKEN = os.getenv('HELP_BOT_KEY')
MISTRAL_API_KEY = os.getenv('API_KEY')
DOMAINREPUTATION_API_KEY = os.getenv('DOMAINREPUTATION_API_KEY')
