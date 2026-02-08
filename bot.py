import requests
import json
import time
import random
from bs4 import BeautifulSoup
from telegram import Bot
from fake_useragent import UserAgent

# ================= CONFIG =================
TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

CATEGORIES = {
    "MEN": "https://www.sheinindia.in/c/sverse-5939-37961",
    "WOMEN": "https://www.sheinindia.in/c/sverse-5939-37962"
}

DATA_FILE = "data.json"
MIN_DELAY = 180   # 3 minutes
MAX_DELAY = 300   # 5 minutes
# =========================================

bot = Bot(token=TOKEN)
ua = UserAgent()
session = requests.Session()


def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.sheinindia.in/"
    }


def fetch_products(url):
    r = session.get(url, headers=get_headers(), timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    products = {}

    for a in soup.select("a[href*='/goods/']"):
        pid = a["href"].split("/")[-1]
        img = a.find("img")

        products[pid] = {
            "name": img.get("alt", "SHEIN Product") if img else "SHEIN Product",
            "url": "https://www.sheinindia.in" + a["href"],
            "image": img.get("src", "") if img else ""
        }

    return products


def load_old():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def send_message(text, image=None):
    if image:
        bot.send_photo(chat_id=CHAT_ID, photo=image, caption=text)
    else:
        bot.send_message(chat_id=CHAT_ID, text=text)


def send_start_summary(data):
    msg = "📦 SHEIN VERSE CURRENT STOCK\n\n"
    for cat in data:
        msg += f"• {cat}: {len(data[cat])} products\n"
    send_message(msg)


def check_updates():
    old_data = load_old()
    current_data = {}

    for cat, url in CATEGORIES.items():
        current_data[cat] = fetch_products(url)
        time.sleep(random.uniform(4, 7))

    if not old_data:
        save_data(current_data)
        send_start_summary(current_data)
        return

    for cat in current_data:
        old_ids = set(old_data.get(cat, {}).keys())
        new_ids = set(current_data[cat].keys())

        added = new_ids - old_ids

        for pid in added:
            p = current_data[cat][pid]
            send_message(
                f"🆕 NEW / RESTOCK ({cat})\n\n{p['name']}\n🔗 {p['url']}",
                p["image"]
            )

    save_data(current_data)


# ================= MAIN =================
if __name__ == "__main__":
    send_message("✅ SHEIN Verse Bot Started Successfully")

    while True:
        try:
            check_updates()
            sleep_time = random.randint(MIN_DELAY, MAX_DELAY)
            time.sleep(sleep_time)
        except Exception as e:
            print("Error:", e)
            time.sleep(60)
