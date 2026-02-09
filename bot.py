import os
import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time
import threading
from datetime import datetime
from flask import Flask

# ============================================
# 1. CONFIGURATION - CHANGE THIS!
# ============================================
# REPLACE THIS WITH YOUR ACTUAL BOT TOKEN FROM STEP 1
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # ← CHANGE THIS!
SHEIN_URL = "https://www.sheinindia.in/c/sverse-5939-37961"
# ============================================

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Store active users
active_users = set()

# Flask app for Railway
app = Flask(__name__)

def get_shein_stock():
    """Fetch stock from Shein Verse"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print("🔍 Fetching Shein stock...")
        response = requests.get(SHEIN_URL, headers=headers, timeout=30)
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all product items (UPDATE THESE SELECTORS IF NEEDED)
        products = []
        
        # Try different selectors
        product_selectors = [
            'div.S-product-item',
            'section.product-list',
            'div[data-qa="product-card"]',
            'div.c-product-item'
        ]
        
        for selector in product_selectors:
            products = soup.select(selector)
            if products:
                break
        
        # Prepare summary
        total_items = len(products)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            'success': True,
            'total_items': total_items,
            'last_checked': current_time,
            'url': SHEIN_URL,
            'message': f"Found {total_items} items in Shein Verse"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'last_checked': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def send_stock_update(chat_id):
    """Send update to user"""
    stock_data = get_shein_stock()
    
    if stock_data['success']:
        message = f"""
🛍️ *SHEIN VERSE STOCK UPDATE*

⏰ *Time:* {stock_data['last_checked']}
📦 *Total Items:* {stock_data['total_items']}
🔗 *Link:* [Click Here]({SHEIN_URL})

_Checking every hour automatically_
        """
    else:
        message = f"""
❌ *ERROR CHECKING STOCK*

⚠️ *Error:* {stock_data['error']}
🕒 *Time:* {stock_data['last_checked']}

_Trying again in next check_
        """
    
    try:
        bot.send_message(chat_id, message, parse_mode='Markdown')
        print(f"✅ Update sent to {chat_id}")
    except Exception as e:
        print(f"❌ Failed to send to {chat_id}: {e}")

# ============================================
# 2. TELEGRAM COMMANDS
# ============================================

@bot.message_handler(commands=['start'])
def start_command(message):
    """When user sends /start"""
    chat_id = message.chat.id
    active_users.add(chat_id)
    
    welcome_msg = """
🤖 *Welcome to Shein Verse Stock Tracker!*

I will monitor Shein Verse section 24/7.

*Commands:*
/start - Start bot
/check - Check stock NOW
/stop - Stop updates
/status - Check status

✅ You will get automatic updates every hour!
"""
    
    bot.send_message(chat_id, welcome_msg, parse_mode='Markdown')
    
    # Send immediate first check
    bot.send_message(chat_id, "🔄 Getting initial stock data...")
    send_stock_update(chat_id)

@bot.message_handler(commands=['check'])
def check_command(message):
    """When user sends /check"""
    chat_id = message.chat.id
    bot.send_message(chat_id, "🔍 Checking current stock...")
    send_stock_update(chat_id)

@bot.message_handler(commands=['stop'])
def stop_command(message):
    """When user sends /stop"""
    chat_id = message.chat.id
    if chat_id in active_users:
        active_users.remove(chat_id)
    bot.send_message(chat_id, "⏸️ Updates stopped. Use /start to resume.")

@bot.message_handler(commands=['status'])
def status_command(message):
    """When user sends /status"""
    chat_id = message.chat.id
    status = "✅ ACTIVE" if chat_id in active_users else "⏸️ INACTIVE"
    
    status_msg = f"""
📊 *BOT STATUS*

Your Status: {status}
Active Users: {len(active_users)}
Last Check: {datetime.now().strftime("%H:%M:%S")}
Shein URL: {SHEIN_URL}
"""
    bot.send_message(chat_id, status_msg, parse_mode='Markdown')

# ============================================
# 3. SCHEDULER - AUTO CHECK EVERY HOUR
# ============================================

def auto_check_job():
    """Run every hour to check stock"""
    print(f"\n⏰ Auto-check at {datetime.now().strftime('%H:%M:%S')}")
    print(f"👥 Active users: {len(active_users)}")
    
    for user_id in list(active_users):
        try:
            send_stock_update(user_id)
        except:
            continue

def run_scheduler():
    """Background scheduler thread"""
    # Check every hour
    schedule.every(1).hours.do(auto_check_job)
    
    # Also check every 30 minutes
    schedule.every(30).minutes.do(lambda: auto_check_job() if active_users else None)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ============================================
# 4. FLASK APP FOR RAILWAY
# ============================================

@app.route('/')
def home():
    return "Shein Verse Bot is running!"

@app.route('/health')
def health():
    return {
        "status": "online",
        "active_users": len(active_users),
        "last_check": datetime.now().isoformat()
    }

# ============================================
# 5. MAIN FUNCTION
# ============================================

def main():
    print("="*50)
    print("🤖 SHEIN VERSE STOCK TRACKER BOT")
    print("="*50)
    
    # Start scheduler in background
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("✅ Scheduler started (checks every hour)")
    
    # Start Flask (for Railway)
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()
    print("✅ Flask server started")
    
    # Start bot
    print("✅ Bot starting...")
    print("📱 Open Telegram and send /start to your bot")
    print("="*50)
    
    bot.infinity_polling(timeout=30, long_polling_timeout=30)

if __name__ == "__main__":
    main()
