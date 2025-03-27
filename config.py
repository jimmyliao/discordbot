import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not DISCORD_BOT_TOKEN:
    raise ValueError("Discord Bot Token 未設定")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key 未設定")