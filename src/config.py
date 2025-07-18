import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PROXY_URL = os.getenv("PROXY_URL")
# Опционально, для заголовка X-Title
SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "AI Telegram Bot")

if not BOT_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Необходимо задать BOT_TOKEN и OPENROUTER_API_KEY в файле .env")

# Новый URL и название модели
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Ваша модель. Вынесем в конфиг, чтобы легко менять.
MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free" # "deepseek/deepseek-coder" "google/gemma-2-9b-it:free" #"deepseek/deepseek-r1-0528-qwen3-8b:free"