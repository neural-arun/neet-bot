import os
import logging
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 3 Subject Telegram Bot Tokens
BIOLOGY_BOT_TOKEN = os.getenv('BIOLOGY_TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', ''))
TELEGRAM_BOT_TOKEN = BIOLOGY_BOT_TOKEN
PHYSICS_BOT_TOKEN = os.getenv('PHYSICS_TELEGRAM_BOT_TOKEN', '')
CHEMISTRY_BOT_TOKEN = os.getenv('CHEMISTRY_TELEGRAM_BOT_TOKEN', '')

# OpenAI Config
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# Admin Password
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'arun123')

if not BIOLOGY_BOT_TOKEN:
    logging.warning("⚠️ BIOLOGY_TELEGRAM_BOT_TOKEN environment variable is not set.")

if not PHYSICS_BOT_TOKEN:
    logging.warning("⚠️ PHYSICS_TELEGRAM_BOT_TOKEN environment variable is not set.")

if not CHEMISTRY_BOT_TOKEN:
    logging.warning("⚠️ CHEMISTRY_TELEGRAM_BOT_TOKEN environment variable is not set.")
