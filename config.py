import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# Shein Configuration
SHEIN_URL = "https://www.sheinindia.in/c/sverse-5939-37961"
PROXY = os.getenv("PROXY")  # Optional: if needed

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shein_stock.db")

# Monitoring Settings
CHECK_INTERVAL = 1800  # 30 minutes in seconds
IMMEDIATE_CHECK_INTERVAL = 300  # 5 minutes for rapid checks
