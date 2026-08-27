import os
import re
import requests
import feedparser
from config import TRENDS_RSS_INDIA, DOWNLOAD_DIR

# Safe import for backward compatibility
try:
    from config import GENRE_SUBREDDITS
except ImportError:
    GENRE_SUBREDDITS = {
        "ALL": ["technology", "MachineLearning", "space", "gadgets", "science"]
    }

DEFAULT_TRENDING_KEYWORDS = {
    "india", "tech", "ai", "market", "isro", "space", "launch",
    "government", "economy", "crypto", "security", "record", "alert"
}


def get_live_search_keywords():
    """Extracts top trending search queries in India with safe fallback."""
    keywords = set()
    try:
        resp = requests.get(
            TRENDS_RSS_INDIA,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
            timeout=8
        )
        if resp.status_code == 200:
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:25]:
                words = [re.sub(r"[^\w]", "", w.lower()) for w in entry.title.split() if len(w) > 3]
                keywords.update([w for w in words if w])
    except Exception as e:
        print(f"[-] Google Trends fetch notice: {e}")

    if not keywords:
        return DEFAULT_TRENDING_KEYWORDS
    return keywords.union(DEFAULT_TRENDING_KEYWORDS)


def download_reddit_image(image_url, post_id):
    if not image_url or not any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        res = requests.get(image_url, headers=headers, timeout=6)
        if res.status_code == 200 and len(res.content) > 3000:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            local_path = os.path.join(DOWNLOAD_DIR, f"reddit_{post_id}.jpg")
            with open(local_path, "wb") as f:
                f.write(res.content)
            return local_path
    except Exception:
        pass
    return None


def get_reddit_trending_posts(genre_key="ALL"):
    """Fetches high-vote discussions matching the target genre."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    reddit_stories = []
    target_subs = GENRE_SUBREDDITS.get(genre_key, GENRE_SUBREDDITS.get("ALL", ["technology"]))

    for sub in target_subs[:3]:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=10"
        try:
            res = requests.get(url, headers=headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    if post.get("score", 0) > 80:
                        post_id = post.get("id", str(abs(hash(post.get("title", "")))))
                        img_url = post.get("url", "")
                        local_img = download_reddit_image(img_url, post_id)

                        reddit_stories.append({
                            "id": f"reddit_{post_id}",
                            "title": post.get("title", "").strip(),
                            "source": f"r/{sub}",
                            "score": post.get("score", 0),
                            "comments": post.get("num_comments", 0),
                            "link": f"https://reddit.com{post.get('permalink')}",
                            "image_url": img_url,
                            "image_path": local_img,
                            "category": "Community Discussion"
                        })
        except Exception:
            pass

    return reddit_stories