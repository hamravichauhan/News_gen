import os
import sys
import json
import re
import shutil
import glob
from datetime import datetime, timedelta
from config import DATA_DIR, PAGE_HANDLE, POSTS_DIR, DOWNLOAD_DIR
from scraper import fetch_news_by_genre
from visual_harvester import get_high_value_visual_stories
from trend_engine import get_live_search_keywords, get_reddit_trending_posts
from classifier import verify_and_tag
from scorer import calculate_virality_score
from generator import build_cover_card, build_carousel_slide
# from telegram_bot import send_carousel_album  # DISABLED for local testing

# ============================================================
#  LOCAL TEST MODE FLAG
#  Set environment variable LOCAL_TEST_MODE=true for local tests.
#  Defaults to False (production behavior: Telegram + Instagram).
# ============================================================
LOCAL_TEST_MODE = os.getenv("LOCAL_TEST_MODE", "false").lower() in ("true", "1")

HISTORY_FILE = os.path.join(DATA_DIR, "posted_history.json")


def load_posted_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return list(data.values())
            elif isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def save_posted_history(history_data):
    os.makedirs(DATA_DIR, exist_ok=True)
    cutoff = (datetime.now() - timedelta(hours=48)).isoformat()
    cleaned = []
    for item in history_data:
        if isinstance(item, dict):
            if item.get("timestamp", "") > cutoff:
                cleaned.append(item)
        elif isinstance(item, str):
            cleaned.append({"title": item, "timestamp": datetime.now().isoformat()})

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)


def get_token_set(text):
    if not text or not isinstance(text, str):
        return set()
    words = re.sub(r"[^\w\s]", "", text.lower()).split()
    return {w for w in words if len(w) > 3}


def is_fuzzy_duplicate(new_title, history_data):
    new_tokens = get_token_set(str(new_title))
    if not new_tokens:
        return False

    for item in history_data:
        if isinstance(item, dict):
            past_title = item.get("title", "")
        elif isinstance(item, str):
            past_title = item
        else:
            continue

        past_tokens = get_token_set(past_title)
        intersection = new_tokens.intersection(past_tokens)
        if len(intersection) >= 3:
            similarity = len(intersection) / float(min(len(new_tokens), len(past_tokens)))
            if similarity > 0.45:
                return True
    return False


def get_selected_genre():
    if "--genre" in sys.argv:
        try:
            idx = sys.argv.index("--genre") + 1
            return sys.argv[idx].strip().upper()
        except IndexError:
            pass
    return "ALL"


def has_valid_image(story):
    img_path = story.get("image_path")
    if img_path and isinstance(img_path, str) and os.path.exists(img_path):
        try:
            return os.path.getsize(img_path) > 3000
        except OSError:
            return False
    return False


def purge_local_storage(carousel_folder):
    """Deletes temporary downloads and generated carousel slides after dispatch."""
    print("[*] Cleaning up temporary storage...")

    # 1. Delete generated carousel folder
    if os.path.exists(carousel_folder):
        try:
            shutil.rmtree(carousel_folder)
            print(f"    🗑️ Deleted generated post folder: {os.path.basename(carousel_folder)}")
        except Exception as e:
            print(f"    [-] Notice deleting carousel folder: {e}")

    # 2. Delete downloaded raw images
    if os.path.exists(DOWNLOAD_DIR):
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
            try:
                os.remove(f)
            except Exception:
                pass
        print("    🗑️ Cleared temporary media cache in downloads/")


def run(target_genre=None):
    genre = (target_genre or get_selected_genre()).upper()
    date_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_display = datetime.now().strftime("%d %b %Y").upper()

    carousel_folder = os.path.join(POSTS_DIR, f"carousel_{genre}_{date_tag}")
    os.makedirs(carousel_folder, exist_ok=True)

    print(f"\n🚀 RUNNING PIPELINE FOR GENRE: [{genre}]")
    if LOCAL_TEST_MODE:
        print("🧪 MODE: LOCAL TEST (no Telegram dispatch, no history save, no purge)")

    history = load_posted_history()

    # 1. Targeted Feed & API Ingestion
    news_stories = fetch_news_by_genre(genre)
    visual_stories = get_high_value_visual_stories() if genre in ["ALL", "AI_TECH", "GADGETS_HARDWARE", "SPACE_DEEPTECH"] else []
    reddit_stories = get_reddit_trending_posts(genre)

    combined = visual_stories + news_stories + reddit_stories
    if not combined:
        print(f"[-] No stories harvested for {genre}.")
        if not LOCAL_TEST_MODE:
            purge_local_storage(carousel_folder)
        return

    # 2. Tagging & Virality Scoring
    tagged = verify_and_tag(combined)
    trends = get_live_search_keywords()
    scored = [calculate_virality_score(s, trends) for s in tagged]
    ranked = sorted(scored, key=lambda x: x.get("virality_score", 0), reverse=True)

    # 3. Deduplication and Image Verification
    top_10 = []
    for story in ranked:
        if is_fuzzy_duplicate(story.get("title", ""), history):
            continue
        if has_valid_image(story):
            top_10.append(story)
        if len(top_10) == 10:
            break

    if len(top_10) < 10:
        for story in ranked:
            if story not in top_10 and not is_fuzzy_duplicate(story.get("title", ""), history):
                top_10.append(story)
            if len(top_10) == 10:
                break

    if not top_10:
        print("[-] No qualifying stories found.")
        if not LOCAL_TEST_MODE:
            purge_local_storage(carousel_folder)
        return

    # 4. Render 11 Carousel Slides (1 cover + 10 ranked)
    cover_path = os.path.join(carousel_folder, "slide_01_cover.jpg")
    build_cover_card(top_10, date_display, cover_path)

    for idx, story in enumerate(top_10, start=1):
        slide_path = os.path.join(carousel_folder, f"slide_{idx+1:02d}_rank_{idx:02d}.jpg")
        build_carousel_slide(story, slide_index=idx, total_slides=len(top_10), output_path=slide_path)

        # Only record to history when NOT in local test mode
        if not LOCAL_TEST_MODE:
            history.append({
                "title": story.get("title", ""),
                "genre": genre,
                "timestamp": datetime.now().isoformat()
            })

    # Only persist history when NOT in local test mode
    if not LOCAL_TEST_MODE:
        save_posted_history(history)

    # 5. Master Caption
    caption_lines = [
        f"🚨 {genre.replace('_', ' ')} BRIEFING — {date_display}",
        "",
        f"Top 10 ranked developments in {genre.replace('_', ' ').title()}:",
        ""
    ]
    for idx, s in enumerate(top_10[:10], start=1):
        caption_lines.append(f"{idx:02d}. {s['title']}")

    caption_lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━",
        "Which story are you tracking? Drop your take below. 👇",
        "",
        f"Follow {PAGE_HANDLE} for daily briefings, tech models, and intelligence digests.",
        "",
        ".",
        "#extrovernerd #TechNews #DailyBrief #Top10"
    ])
    caption = "\n".join(caption_lines)

    caption_file = os.path.join(carousel_folder, "carousel_caption.txt")
    with open(caption_file, "w", encoding="utf-8") as f:
        f.write(caption)

    # 6. Dispatch (Telegram) OR Local Save
    if LOCAL_TEST_MODE:
        print("\n💾 LOCAL TEST MODE — nothing sent to Telegram.")
        print(f"📁 Carousel folder : {carousel_folder}")
        print(f"📝 Caption file    : {caption_file}")
        try:
            slide_files = sorted(
                f for f in os.listdir(carousel_folder)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            )
            print(f"🖼️  Slides generated: {len(slide_files)}")
            for f in slide_files:
                print(f"     - {f}")
        except Exception as e:
            print(f"    [-] Could not list slides: {e}")
        print("\n✅ Local run complete. Inspect the folder above.")
        return

    # ---- Production path (only reached when LOCAL_TEST_MODE = False) ----
    from telegram_bot import send_carousel_album  # lazy import
    dispatch_success = send_carousel_album(carousel_folder, caption_text=caption)
    print(f"✅ Delivered 11-slide [{genre}] carousel directly to Telegram.")

    # 7. Automatic Instagram Dispatch & Dynamic Bio Update
    try:
        from instagram_uploader import upload_carousel_and_update_bio
        print(f"[*] Dispatching [{genre}] carousel & updating bio on Instagram @extrovertnerd...")
        ig_success = upload_carousel_and_update_bio(
            carousel_folder=carousel_folder,
            caption=caption,
            genre=genre,
            max_slides=10,
        )
        if ig_success:
            print("✅ Successfully published to Instagram & updated bio!")
    except Exception as ig_err:
        print(f"[-] Instagram dispatch notice: {ig_err}")

    # 8. Automatic Local Storage Purge (production only)
    if dispatch_success:
        purge_local_storage(carousel_folder)


if __name__ == "__main__":
    run()