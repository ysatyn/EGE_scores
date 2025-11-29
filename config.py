import dotenv
import os

dotenv.load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")