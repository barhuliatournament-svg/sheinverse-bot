import asyncio
from aiogram import Bot, Dispatcher, executor, types
from config import *
from stock_api import fetch_stock
from storage import load_stock, save_stock

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

ADMIN_ID = None

def detect_changes(old, new):
    added = {}
    for cat, items in new.items():
        old_items = set(old.get(cat, []))
        diff = set(items) - old_items
        if diff:
            added[cat] = list(diff)
    return added

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    global ADMIN_ID
    if ADMIN_ID is None:
        ADMIN_ID = msg.from_user.id

    stock = load_stock()
    text = "🛍️ *Shein Verse – Current Stock*\n\n"

    if not stock:
        text += "_No stock data yet_"
    else:
        for cat, items in stock.items():
            text += f"• {cat}: {len(items)} items\n"

    await msg.reply(text, parse_mode="Markdown")

@dp.message_handler(commands=['forcecheck'])
async def forcecheck(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    await msg.reply("🔄 Checking stock now…")
    await check_and_notify()

async def check_and_notify():
    new_stock = fetch_stock()
    if not new_stock:
        return

    old_stock = load_stock()
    changes = detect_changes(old_stock, new_stock)

    if changes:
        for cat, items in changes.items():
            msg = f"🆕 *New / Restored Stock*\n\n📦 {cat}\n\n"
            msg += "\n".join(items)
            await bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")

        save_stock(new_stock)

async def monitor():
    while True:
        try:
            await check_and_notify()
        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(CHECK_INTERVAL)

async def on_startup(dp):
    asyncio.create_task(monitor())

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
