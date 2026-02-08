import requests
import json
import time
from bs4 import BeautifulSoup
from telegram import Bot

# ---------------- CONFIG ----------------
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

URL = "https://www.sheinindia.in/c/sverse-5939-37961"
CHECK_INTERVAL = 30  # seconds
DATA_FILE = "products.json"
# ----------------------------------------

bot = Bot(token=TOKEN)


def fetch_products():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    products = {}

    for item in soup.select("section.product-card"):
        link = item.find("a")
        if not link:
            continue

        product_url = "https://www.sheinindia.in" + link["href"]
        product_id = link["href"].split("/")[-1]

        name = item.select_one(".goods-title")
        img = item.find("img")

        products[product_id] = {
            "name": name.text.strip() if name else "SHEIN Product",
            "url": product_url,
            "image": img["src"] if img else ""
        }

    return products


def load_old_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def send_message(text, img=None):
    if img:
        bot.send_photo(chat_id=CHAT_ID, photo=img, caption=text)
    else:
        bot.send_message(chat_id=CHAT_ID, text=text)


def send_summary(products):
    msg = f"📦 *Current SHEIN Verse Stock*\n\nTotal Products: {len(products)}"
    send_message(msg)


def check_updates():
    old = load_old_data()
    current = fetch_products()

    old_ids = set(old.keys())
    new_ids = set(current.keys())

    # NEW PRODUCTS
    added = new_ids - old_ids
    for pid in added:
        p = current[pid]
        send_message(
            f"🆕 *New Stock Added*\n\n{p['name']}\n🔗 {p['url']}",
            p["image"]
        )

    # RESTOCK (Product removed earlier but back)
    restored = old_ids - new_ids
    if restored:
        print("Some products removed")

    save_data(current)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("Bot Started...")
    products = fetch_products()
    save_data(products)

    send_summary(products)

    while True:
        try:
            check_updates()
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print("Error:", e)
            time.sleep(10)
