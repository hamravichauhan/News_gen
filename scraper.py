import os
import re
import requests
import feedparser
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from config import GENRE_FEEDS, DOWNLOAD_DIR

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


def clean_summary_text(raw_html, max_words=32):
    """
    Strips raw HTML tags, tracking pixels, and extracts the first 1-2 
    complete factual sentences to provide a full briefing takeaway.
    """
    if not raw_html or not isinstance(raw_html, str):
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    # Remove script, style, and anchor artifacts
    for tag in soup(["script", "style", "a", "form"]):
        tag.decompose()

    text = soup.get_text(separator=" ").strip()
    text = " ".join(text.split())

    # Extract clean, complete sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    extracted = []
    word_count = 0

    for s in sentences:
        s_clean = s.strip()
        if not s_clean or "read more" in s_clean.lower() or "appeared first on" in s_clean.lower():
            continue
        words = s_clean.split()
        if word_count + len(words) <= max_words:
            extracted.append(s_clean)
            word_count += len(words)
        else:
            if not extracted:
                # If first sentence is longer than word limit, truncate cleanly
                extracted.append(" ".join(words[:max_words]) + "...")
            break

    brief = " ".join(extracted).strip()
    return brief


def extract_best_image_url(entry):
    """Extracts high-resolution images from RSS metadata or summary HTML."""
    # 1. Media Content / Enclosure
    if "media_content" in entry and len(entry.media_content) > 0:
        url = entry.media_content[0].get("url")
        if url and not url.lower().endswith(".gif"):
            return url

    # 2. Media Thumbnail
    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        url = entry.media_thumbnail[0].get("url")
        if url and not url.lower().endswith(".gif"):
            return url

    # 3. Direct Image Links
    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image/") or link.get("rel") == "enclosure":
                href = link.get("href")
                if href and not href.lower().endswith(".gif"):
                    return href

    # 4. Parse <img> tag from HTML summary or content
    summary_html = entry.get("summary", "") or entry.get("description", "")
    if "content" in entry and len(entry.content) > 0:
        summary_html += " " + entry.content[0].get("value", "")

    if summary_html:
        soup = BeautifulSoup(summary_html, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            src = img.get("src")
            if not src.lower().endswith((".gif", ".svg")) and not "1x1" in src:
                return src

    return None


def download_media_file(image_url, unique_id):
    """Downloads and verifies image integrity (>4KB)."""
    if not image_url or not isinstance(image_url, str):
        return None
    try:
        res = requests.get(image_url, headers=HEADERS, timeout=6)
        if res.status_code == 200 and len(res.content) > 4000:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            local_path = os.path.join(DOWNLOAD_DIR, f"feed_{unique_id}.jpg")
            with open(local_path, "wb") as f:
                f.write(res.content)
            return local_path
    except Exception:
        pass
    return None


def fetch_single_feed(url):
    """Parses a single RSS feed endpoint and extracts structured story cards."""
    results = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            feed = feedparser.parse(resp.content)
            source_raw = feed.feed.get("title", "Global Media")
            source_name = source_raw.replace(" - Latest", "").replace(" RSS Feed", "").split(" | ")[0].strip()

            for entry in feed.entries[:8]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                summary_raw = entry.get("summary", "") or entry.get("description", "")
                
                # Extract clean, complete factual briefing summary
                summary = clean_summary_text(summary_raw)

                # Skip empty titles or low-effort stubs
                if not title or len(title) < 15:
                    continue

                raw_img = extract_best_image_url(entry)
                uid = str(abs(hash(title)))
                local_img = download_media_file(raw_img, uid)

                results.append({
                    "id": f"rss_{uid}",
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "source": source_name if source_name else "Verified Source",
                    "image_url": raw_img,
                    "image_path": local_img,
                    "score": 90
                })
    except Exception:
        pass
    return results


def fetch_api_sources(genre_key):
    """Fetches real-time structured API endpoints for Dev/Tech/Startups."""
    api_stories = []

    if genre_key in ["DEV_SECURITY", "AI_TECH", "ALL"]:
        # Dev.to Top Articles
        try:
            res = requests.get("https://dev.to/api/articles?top=1", headers=HEADERS, timeout=5)
            if res.status_code == 200:
                for item in res.json()[:4]:
                    uid = str(item.get("id"))
                    img_url = item.get("cover_image")
                    local_img = download_media_file(img_url, uid)
                    api_stories.append({
                        "id": f"devto_{uid}",
                        "title": item.get("title", "").strip(),
                        "summary": clean_summary_text(item.get("description", "")),
                        "link": item.get("url", ""),
                        "source": "Dev.to",
                        "image_url": img_url,
                        "image_path": local_img,
                        "score": 95
                    })
        except Exception:
            pass

        # Lobste.rs Trending
        try:
            res = requests.get("https://lobste.rs/hottest.json", headers=HEADERS, timeout=5)
            if res.status_code == 200:
                for item in res.json()[:3]:
                    api_stories.append({
                        "id": f"lobsters_{item.get('short_id')}",
                        "title": item.get("title", "").strip(),
                        "summary": clean_summary_text(item.get("description", "")),
                        "link": item.get("url", ""),
                        "source": "Lobste.rs",
                        "image_url": None,
                        "image_path": None,
                        "score": 85
                    })
        except Exception:
            pass

    return api_stories


def fetch_news_by_genre(genre_key="ALL"):
    """Fetches all target category feeds in parallel using ThreadPoolExecutor."""
    target_urls = GENRE_FEEDS.get(genre_key, [])
    if not target_urls or genre_key == "ALL":
        target_urls = []
        for feeds in GENRE_FEEDS.values():
            target_urls.extend(feeds[:2])

    all_stories = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        feed_results = executor.map(fetch_single_feed, target_urls)
        for res in feed_results:
            all_stories.extend(res)

    # Combine with developer APIs when applicable
    api_stories = fetch_api_sources(genre_key)
    all_stories.extend(api_stories)

    return all_stories