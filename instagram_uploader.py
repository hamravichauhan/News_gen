"""
Instagram Auto-Uploader & Dynamic Bio Manager for News_gen Pipeline.
Designed for both local execution and automated cloud runs via GitHub Actions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger("InstagramUploader")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path(__file__).resolve().parent
SESSION_FILE = BASE_DIR / "ig_session.json"


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


def upload_carousel_and_update_bio(
    carousel_folder: str | Path,
    caption: str,
    genre: Optional[str] = None,
    max_slides: int = 10,
) -> bool:
    """
    Uploads the generated carousel deck to Instagram and updates the profile bio.
    Does not crash the pipeline if Instagram encounters a transient issue.
    """
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

    # Instagram album limit is 10 items
    upload_paths = [Path(s) for s in slides[:max_slides]]
    logger.info(f"Uploading {len(upload_paths)} slides to Instagram @extrovertnerd...")

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
