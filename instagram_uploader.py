"""
Instagram Auto-Uploader & Dynamic Bio Manager for News_gen Pipeline.
Designed for both local execution and automated cloud runs via GitHub Actions.
"""

import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger("InstagramUploader")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path(__file__).resolve().parent
SESSION_FILE = BASE_DIR / "ig_session.json"

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "").strip()
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "17841430226354207").strip()


def get_authenticated_client():
    """Restores an authenticated instagrapi Client from environment or session file."""
    from instagrapi import Client

    cl = Client()

    # 1. Check for proxy if configured
    proxy = os.getenv("IG_PROXY", "").strip()
    if proxy:
        logger.info(f"Using proxy: {proxy}")
        cl.set_proxy(proxy)

    # 2. Restore session from GitHub Secret (IG_SESSION_JSON) if in cloud runner
    session_json_env = os.getenv("IG_SESSION_JSON", "").strip()
    if session_json_env:
        try:
            logger.info("Restoring Instagram session from IG_SESSION_JSON environment secret...")
            session_data = json.loads(session_json_env)
            cl.set_settings(session_data)
            acc = cl.account_info()
            cl.username = acc.username
            logger.info(f"Session restored and validated for @{cl.username} from environment!")
            return cl
        except Exception as e:
            logger.warning(f"Could not restore from IG_SESSION_JSON secret: {e}")

    # 3. Restore session from local file
    if SESSION_FILE.exists():
        try:
            logger.info(f"Loading Instagram session from {SESSION_FILE}...")
            cl.load_settings(SESSION_FILE)
            acc = cl.account_info()
            cl.username = acc.username
            logger.info(f"Session restored and validated for @{cl.username} from local file!")
            return cl
        except Exception as e:
            logger.warning(f"Failed to validate saved session file: {e}")

    # 4. Fallback to password login
    username = os.getenv("IG_USERNAME", "extrovertnerd").strip()
    password = os.getenv("IG_PASSWORD", "").strip()
    if username and password:
        logger.info(f"Attempting fresh password login as @{username}...")
        cl.login(username, password)
        cl.dump_settings(SESSION_FILE)
        logger.info("Login successful and session persisted.")
        return cl

    raise ValueError(
        "No valid Instagram session found. Please provide IG_SESSION_JSON or credentials in your environment."
    )


def build_dynamic_bio(genre: Optional[str] = None) -> str:
    """Builds a punchy, clean profile bio within Instagram's 150-character limit."""
    genre_display = (genre or "Daily").replace("_", " ").title()
    date_display = datetime.now().strftime("%d %b")

    # Keep strictly under 150 characters
    bio_lines = [
        "⚡ The Daily Brief in 10 Slides",
        "🧠 Deep Tech, AI & Nerd Culture",
        f"🚨 {genre_display} Briefing ({date_display}) 👇",
    ]
    bio = "\n".join(bio_lines)
    return bio[:150]


def upload_carousel_via_meta_graph(
    image_urls: List[str],
    caption: str,
    access_token: Optional[str] = None,
    ig_account_id: Optional[str] = None,
    max_slides: int = 20,
) -> Optional[str]:
    """
    Publishes an 11-slide carousel using official Meta Graph API v21.0.
    100% compliant with Meta terms, zero session expiry issues.
    """
    token = (access_token or os.getenv("META_ACCESS_TOKEN", "")).strip()
    ig_id = (ig_account_id or os.getenv("INSTAGRAM_ACCOUNT_ID", "17841430226354207")).strip()

    if not token or not ig_id:
        logger.warning("Meta Graph API credentials missing. Cannot dispatch via official API.")
        return None

    urls = image_urls[:max_slides]
    if not urls:
        logger.error("No image URLs provided for Meta Graph API carousel.")
        return None

    logger.info(f"🚀 [Meta Graph API] Initiating carousel upload ({len(urls)} slides) to account {ig_id}...")

    # Step 1: Create child item containers
    child_ids = []
    for idx, url in enumerate(urls, start=1):
        try:
            res = requests.post(
                f"{GRAPH_API_BASE}/{ig_id}/media",
                data={
                    "image_url": url,
                    "is_carousel_item": "true",
                    "access_token": token,
                },
                timeout=30,
            ).json()
            cid = res.get("id")
            if cid:
                child_ids.append(cid)
                logger.info(f"  [{idx}/{len(urls)}] Slide container created: {cid}")
            else:
                logger.error(f"  [-] Failed container for slide {idx}: {res}")
        except Exception as e:
            logger.error(f"  [-] Exception creating container for slide {idx}: {e}")
        time.sleep(1)

    if len(child_ids) < len(urls):
        logger.warning(f"Only {len(child_ids)}/{len(urls)} child containers created.")
        if not child_ids:
            return None

    # Step 2: Create parent carousel container
    logger.info(f"Creating parent carousel container for {len(child_ids)} slides...")
    try:
        parent_res = requests.post(
            f"{GRAPH_API_BASE}/{ig_id}/media",
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(child_ids),
                "caption": caption,
                "access_token": token,
            },
            timeout=30,
        ).json()
        carousel_container_id = parent_res.get("id")
        if not carousel_container_id:
            logger.error(f"Failed to create parent carousel container: {parent_res}")
            return None
        logger.info(f"✅ Parent carousel container created: {carousel_container_id}")
    except Exception as e:
        logger.error(f"Exception creating parent carousel: {e}")
        return None

    # Step 3: Wait for Meta crawler processing
    time.sleep(6)

    # Step 4: Publish carousel
    logger.info(f"Publishing carousel container {carousel_container_id}...")
    try:
        pub_res = requests.post(
            f"{GRAPH_API_BASE}/{ig_id}/media_publish",
            data={
                "creation_id": carousel_container_id,
                "access_token": token,
            },
            timeout=30,
        ).json()
        post_id = pub_res.get("id")
        if post_id:
            logger.info(f"🎉 Meta Graph API Publish SUCCESS! Post ID: {post_id}")
            return post_id
        else:
            logger.error(f"Failed to publish carousel: {pub_res}")
            return None
    except Exception as e:
        logger.error(f"Exception publishing carousel: {e}")
        return None


def upload_carousel_and_update_bio(
    carousel_folder: str | Path,
    caption: str,
    genre: Optional[str] = None,
    max_slides: int = 20,
    image_urls: Optional[List[str]] = None,
) -> bool:
    """
    Uploads the generated carousel deck to Instagram and updates profile bio.
    Priority 1: Official Meta Graph API v21.0 (using image_urls if provided)
    Priority 2: Fallback to instagrapi if session is available
    """
    # 1. Primary: Official Meta Graph API v21.0
    meta_token = os.getenv("META_ACCESS_TOKEN", "").strip()
    if meta_token and image_urls:
        logger.info(f"Using Official Meta Graph API v21.0 with {len(image_urls)} slide URLs...")
        post_id = upload_carousel_via_meta_graph(
            image_urls=image_urls,
            caption=caption,
            access_token=meta_token,
            max_slides=max_slides,
        )
        if post_id:
            logger.info(f"🎉 Successfully published via official Meta Graph API: {post_id}")
            return True
        logger.warning("Meta Graph API dispatch failed. Attempting instagrapi fallback...")

    # 2. Fallback: instagrapi private API
    folder = Path(carousel_folder)
    if not folder.is_dir():
        logger.error(f"Carousel directory does not exist: {folder}")
        return False

    # Find image slides
    image_exts = (".jpg", ".jpeg", ".png")
    slides = sorted([
        f for f in folder.iterdir()
        if f.suffix.lower() in image_exts and f.name.lower().startswith("slide_")
    ])

    if not slides:
        slides = sorted([f for f in folder.iterdir() if f.suffix.lower() in image_exts])

    if not slides:
        logger.error(f"No image slides found in {folder}")
        return False

    upload_paths = [Path(s) for s in slides[:max_slides]]
    logger.info(f"Uploading {len(upload_paths)} slides to Instagram @extrovertnerd via instagrapi...")

    try:
        cl = get_authenticated_client()

        # 1. Upload Carousel Album
        media = cl.album_upload(
            paths=upload_paths,
            caption=caption,
        )
        logger.info(f"🎉 Successfully published carousel to Instagram! Media ID: {media.pk}")

        # 2. Update Profile Bio
        try:
            new_bio = build_dynamic_bio(genre)
            logger.info(f"Updating profile bio to:\n{new_bio}")
            cl.account_set_biography(new_bio)
            logger.info("✅ Instagram biography updated successfully.")
        except Exception as bio_err:
            logger.warning(f"Could not update bio (non-fatal): {bio_err}")

        return True

    except Exception as e:
        logger.error(f"❌ Instagram upload failed: {e}")
        return False
