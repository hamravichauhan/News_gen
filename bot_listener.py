import os
import time
import threading
import requests
from dotenv import load_dotenv

# 1. Environment & Configuration Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Lock to prevent simultaneous overlapping runs
IS_PROCESSING = False
PROCESSING_LOCK = threading.Lock()

# Pretty labels for category display
GENRE_LABELS = {
    "AI_TECH": "🤖 AI & Frontier Tech",
    "DEV_SECURITY": "💻 Dev & Cybersecurity",
    "SPACE_DEEPTECH": "🚀 Space & Deep Tech",
    "INDIA_POLICY": "🇮🇳 National & Policy",
    "GEOPOLITICS": "🌍 Global Geopolitics",
    "BUSINESS_STARTUPS": "🦄 Startups & Business",
    "CRYPTO_WEB3": "⚡ Crypto & Web3",
    "GADGETS_HARDWARE": "📱 Gadgets & Hardware",
    "GAMING_ESPORTS": "🎮 Gaming & Esports",
    "INTERNET_CULTURE": "🔥 Internet Culture",
    "ALL": "🌐 Top 10 All-Round Digest"
}


def send_message(chat_id, text, reply_markup=None):
    """Sends a formatted Markdown message to Telegram."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        res = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=15)
        return res.json()
    except Exception as e:
        print(f"[-] Send error: {e}")
        return None


def send_main_dashboard(chat_id, header_text=None):
    """Sends the clean 2-column interactive control deck."""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🤖 AI & Frontier", "callback_data": "GENRE_AI_TECH"},
                {"text": "💻 Dev & Security", "callback_data": "GENRE_DEV_SECURITY"}
            ],
            [
                {"text": "🚀 Space & DeepTech", "callback_data": "GENRE_SPACE_DEEPTECH"},
                {"text": "🇮🇳 National & Policy", "callback_data": "GENRE_INDIA_POLICY"}
            ],
            [
                {"text": "🌍 Geopolitics", "callback_data": "GENRE_GEOPOLITICS"},
                {"text": "🦄 Startups & Business", "callback_data": "GENRE_BUSINESS_STARTUPS"}
            ],
            [
                {"text": "⚡ Crypto & Web3", "callback_data": "GENRE_CRYPTO_WEB3"},
                {"text": "📱 Gadgets & Hardware", "callback_data": "GENRE_GADGETS_HARDWARE"}
            ],
            [
                {"text": "🎮 Gaming & Esports", "callback_data": "GENRE_GAMING_ESPORTS"},
                {"text": "🔥 Internet Culture", "callback_data": "GENRE_INTERNET_CULTURE"}
            ],
            [
                {"text": "🌐 Top 10 Universal Briefing", "callback_data": "GENRE_ALL"}
            ]
        ]
    }

    prompt = header_text or (
        "👑 *EXTROVERNERD CAROUSEL STUDIO*\n\n"
        "Select a topic below to harvest fresh stories, run 48-hour deduplication, "
        "and generate an **11-slide HD editorial deck** with caption ready for Instagram:\n"
    )
    send_message(chat_id, prompt, reply_markup=keyboard)


def execute_pipeline_task(selected_genre, chat_id):
    """Background worker executing scraping, rendering, and auto-cleanup."""
    global IS_PROCESSING
    from pipeline import run

    genre_name = GENRE_LABELS.get(selected_genre, selected_genre)

    try:
        # Step 1: Notify start
        send_message(
            chat_id,
            f"⚡ *Building Deck:* `{genre_name}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"1️⃣ Scanning high-signal RSS feeds & APIs...\n"
            f"2️⃣ Filtering out past 48h duplicates...\n"
            f"3️⃣ Formatting executive summaries & HD typography...\n\n"
            f"⏱️ _Delivery in ~45 seconds._"
        )

        # Step 2: Run pipeline
        run(target_genre=selected_genre)

        # Step 3: Success Confirmation
        send_message(
            chat_id,
            f"✅ *All slides delivered successfully!*\n"
            f"Temporary storage has been cleared."
        )

        # Step 4: Automatically re-render menu for the next run
        time.sleep(1)
        send_main_dashboard(
            chat_id, 
            header_text="🔄 *Ready for the next deck!*\nSelect another category below whenever you want to generate a new post:"
        )

    except Exception as e:
        print(f"[-] Pipeline execution failure: {e}")
        send_message(
            chat_id,
            f"❌ *Build Error Occurred:*\n`{str(e)[:200]}`\n\nPlease try again in a few moments."
        )
        time.sleep(1)
        send_main_dashboard(chat_id)

    finally:
        with PROCESSING_LOCK:
            IS_PROCESSING = False


def poll_updates():
    global IS_PROCESSING
    offset = 0

    print("🤖 Extrovernerd Studio Assistant is active...")

    while True:
        try:
            resp = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": 25}, timeout=30)
            if resp.status_code != 200:
                time.sleep(2)
                continue

            updates = resp.json().get("result", [])
            for u in updates:
                offset = u["update_id"] + 1

                # 1. Text Commands (/start, /menu, /help)
                if "message" in u and "text" in u["message"]:
                    chat_id = u["message"]["chat"]["id"]
                    text = u["message"]["text"].strip().lower()

                    if text in ["/start", "/menu", "start", "menu", "hi", "news"]:
                        send_main_dashboard(chat_id)
                    elif text in ["/help", "help"]:
                        help_text = (
                            "ℹ️ *How to use Extrovernerd Studio:*\n\n"
                            "• Tap `/start` or `/menu` to open the genre dashboard.\n"
                            "• Pick any category to generate 11 luxury carousel slides.\n"
                            "• Stories covered in the last 48h are automatically skipped.\n"
                            "• Disk space is automatically cleared after delivery."
                        )
                        send_message(chat_id, help_text)

                # 2. Interactive Button Taps
                elif "callback_query" in u:
                    cq = u["callback_query"]
                    cq_id = cq["id"]
                    chat_id = cq["message"]["chat"]["id"]
                    data = cq.get("data", "")

                    # Acknowledge button press immediately to dismiss loading wheel
                    requests.post(f"{BASE_URL}/answerCallbackQuery", json={"callback_query_id": cq_id})

                    if data.startswith("GENRE_"):
                        selected_genre = data.replace("GENRE_", "")

                        # Prevent overlapping double-triggers
                        with PROCESSING_LOCK:
                            if IS_PROCESSING:
                                send_message(
                                    chat_id,
                                    "⚠️ *A deck is currently rendering!* Please wait for the current delivery to finish before starting another."
                                )
                                continue
                            IS_PROCESSING = True

                        # Spawn detached background task
                        worker = threading.Thread(
                            target=execute_pipeline_task,
                            args=(selected_genre, chat_id),
                            daemon=True
                        )
                        worker.start()

        except Exception as e:
            time.sleep(2)


if __name__ == "__main__":
    poll_updates()