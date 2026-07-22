import os
import logging
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'arun123')

if not TELEGRAM_BOT_TOKEN:
    logging.warning("⚠️ TELEGRAM_BOT_TOKEN environment variable is not set.")

if not OPENAI_API_KEY:
    logging.warning("⚠️ OPENAI_API_KEY environment variable is not set.")
