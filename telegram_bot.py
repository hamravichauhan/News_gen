import os
import time
import requests
from dotenv import load_dotenv

# Automatically load from project root .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def send_message(text):
    """Sends raw text/captions to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Telegram credentials missing (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID).")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        return res.status_code == 200
    except Exception as e:
        print(f"[-] Telegram message error: {e}")
        return False


def send_carousel_album(carousel_folder, caption_text="", return_urls: bool = False):
    """
    Sends the ready-to-copy Master Caption first, 
    then uploads all slide images in sequential order.
    Returns (success, slide_urls) if return_urls is True, else success.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Telegram credentials not set. Skipping mobile dispatch.")
        return (False, []) if return_urls else False

    if not os.path.exists(carousel_folder):
        print(f"[-] Carousel folder not found: {carousel_folder}")
        return (False, []) if return_urls else False

    # Get all .jpg slides sorted in exact order (slide_01, slide_02, ...)
    images = sorted([f for f in os.listdir(carousel_folder) if f.lower().endswith(".jpg")])
    if not images:
        print(f"[-] No JPG images found in {carousel_folder}")
        return (False, []) if return_urls else False

    print(f"[*] Dispatching master caption and {len(images)} slides to Telegram...")

    # Step 1: Send the formatted caption
    if caption_text:
        send_message(caption_text)
        time.sleep(1)

    # Step 2: Upload each slide sequentially
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    success_count = 0
    slide_urls = []

    for idx, img_name in enumerate(images, start=1):
        img_path = os.path.join(carousel_folder, img_name)
        try:
            with open(img_path, "rb") as photo:
                files = {"photo": photo}
                data = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": f"📸 Slide {idx:02d}/{len(images):02d} — {img_name}"
                }
                res = requests.post(url, data=data, files=files, timeout=30)
                if res.status_code == 200:
                    success_count += 1
                    try:
                        data_json = res.json()
                        photo_sizes = data_json.get("result", {}).get("photo", [])
                        if photo_sizes:
                            file_id = photo_sizes[-1].get("file_id")
                            if file_id:
                                f_res = requests.get(
                                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}",
                                    timeout=15,
                                )
                                if f_res.status_code == 200:
                                    file_path = f_res.json().get("result", {}).get("file_path")
                                    if file_path:
                                        cdn_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
                                        slide_urls.append(cdn_url)
                    except Exception as cdn_err:
                        print(f"[-] Could not resolve Telegram CDN URL for {img_name}: {cdn_err}")
                else:
                    print(f"[-] Failed to upload {img_name}: {res.text}")
            time.sleep(0.5)  # Prevents Telegram API rate limiting
        except Exception as e:
            print(f"[-] Error uploading {img_name}: {e}")

    print(f"✅ Delivered {success_count}/{len(images)} slides to Telegram ({len(slide_urls)} CDN URLs ready).")
    is_success = (success_count == len(images))
    if return_urls:
        return is_success, slide_urls
    return is_success


if __name__ == "__main__":
    # Standalone verification test
    print(f"[*] Testing connection with Bot Token: {TELEGRAM_BOT_TOKEN[:6]}... and Chat ID: {TELEGRAM_CHAT_ID}")
    test_msg = "🚀 Telegram Bot connected successfully for @extrovernerd pipeline!"
    if send_message(test_msg):
        print("[+] Test ping sent successfully to your Telegram chat.")
    else:
        print("[-] Test failed. Please check your .env credentials.")