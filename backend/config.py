import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Gate.io
GATEIO_API_KEY = os.getenv("GATEIO_API_KEY")
GATEIO_API_SECRET = os.getenv("GATEIO_API_SECRET")
GATEIO_BASE_URL = "https://api.gateio.ws/api/v4"

# Backend URL untuk frontend (ganti dengan domain publik)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")