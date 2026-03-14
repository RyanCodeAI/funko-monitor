import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime
from flask import Flask
import threading
import sys

URL = "https://shop.forbiddenplanet.co.uk/collections/funko"
STORAGE_FILE = "seen_funko_products.json"

# ←←← YOUR TELEGRAM DETAILS ←←←
TELEGRAM_BOT_TOKEN = "8617739074:AAHhHJdGaN11XQB24nOs7jJ4XDdxghvQrvI"      # ← paste your token here
TELEGRAM_CHAT_ID = "1232067059"        # ← paste your chat ID here

app = Flask(__name__)

def load_seen_products():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_seen_products(seen):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, indent=2)

def get_current_product_urls():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(URL, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select('a[href^="/products/"]')
        base = "https://shop.forbiddenplanet.co.uk"
        return {base + link.get("href").split("?")[0].split("#")[0] for link in links if link.get("href")}
    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")
        sys.stdout.flush()
        return set()

def send_telegram_notification(new_products):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"\n🚨 {len(new_products)} NEW FUNKO(S) FOUND! (Telegram not set up)")
        for p in list(new_products)[:5]:
            print(f"→ {p}")
        sys.stdout.flush()
        return

    message = f"🚨 <b>{len(new_products)} NEW FUNKO(S)</b> on Forbidden Planet International!\n\n"
    message += "\n".join([f"• {p}" for p in list(new_products)[:10]])

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        )
        print(f"[{datetime.now()}] ✅ Telegram notification sent!")
        sys.stdout.flush()
    except Exception as e:
        print(f"[{datetime.now()}] Telegram failed: {e}")
        sys.stdout.flush()

def monitor_loop():
    print("🛍️ Funko Monitor STARTED 24/7 with TELEGRAM alerts!")
    sys.stdout.flush()
    seen = load_seen_products()
    while True:
        current = get_current_product_urls()
        new = current - seen
        if new:
            print(f"[{datetime.now()}] 🎉 {len(new)} NEW PRODUCTS!")
            sys.stdout.flush()
            send_telegram_notification(new)
            seen.update(new)
            save_seen_products(seen)
        else:
            print(f"[{datetime.now()}] ✅ No new Funko")
            sys.stdout.flush()
        time.sleep(60)

@app.route("/")
def home():
    return "✅ Funko Monitor is running 24/7 with TELEGRAM! (ping OK)"

if __name__ == "__main__":
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
