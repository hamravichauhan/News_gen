import os
import json
import re
import requests
import feedparser
from config import DOWNLOAD_DIR, TRENDS_RSS_INDIA, REDDIT_SUBREDDITS

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evergreen_database.json")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_trending_tech_seeds():
    """Finds rising tech/science terms from Google Trends and Reddit."""
    seeds = set()
    
    # 1. Google Trends (India)
    try:
        feed = feedparser.parse(TRENDS_RSS_INDIA)
        for entry in feed.entries[:15]:
            title = entry.title.strip()
            # Clean non-alphanumeric
            cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', title)
            words = [w for w in cleaned.split() if len(w) > 3]
            seeds.update(words)
    except Exception as e:
        print(f"[-] Trends fetch error: {e}")

    # 2. Reddit Tech / Sci Subreddits
    headers = {"User-Agent": "ExtrovernerdEvergreen/2.0"}
    for sub in REDDIT_SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=5"
        try:
            res = requests.get(url, headers=headers, timeout=6)
            if res.status_code == 200:
                for child in res.json().get("data", {}).get("children", []):
                    post_title = child.get("data", {}).get("title", "")
                    words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', '', post_title).split() if len(w) > 4]
                    seeds.update(words[:3])
        except Exception:
            pass

    # Curated fallbacks in case feeds are silent
    seeds.update(["Quantum computing", "Neural network", "Kubernetes", "Blockchain", "Cybersecurity", "Space telescope", "Semiconductor"])
    return list(seeds)

def search_wikipedia_concept(keyword):
    """Finds the most relevant conceptual Wikipedia page for a trending keyword."""
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={keyword}&limit=1&namespace=0&format=json"
    headers = {"User-Agent": "ExtrovernerdEvergreen/2.0"}
    try:
        res = requests.get(search_url, headers=headers, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if len(data) >= 2 and data[1]:
                page_title = data[1][0]
                # Filter out generic person/year disambiguations
                if not any(page_title.endswith(x) for x in ["(disambiguation)", "(film)", "(album)"]):
                    return page_title
    except Exception:
        pass
    return None

def fetch_concept_details(wiki_title):
    """Fetches summary, structured sentences, and thumbnail from Wikipedia REST API."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title.replace(' ', '_')}"
    headers = {"User-Agent": "ExtrovernerdEvergreen/2.0"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            extract = data.get("extract", "")
            if len(extract) < 80:
                return None

            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', extract) if len(s.strip()) > 25]
            if len(sentences) < 2:
                return None

            image_url = None
            if "originalimage" in data:
                image_url = data["originalimage"].get("source")
            elif "thumbnail" in data:
                image_url = data["thumbnail"].get("source")

            return {
                "title": data.get("title", wiki_title),
                "description": data.get("description", "Core Concept"),
                "highlights": sentences[:3],
                "image_url": image_url
            }
    except Exception as e:
        print(f"[-] Wikipedia fetch error for {wiki_title}: {e}")
    return None

def download_hd_image(image_url, post_id):
    """Downloads image locally."""
    if not image_url:
        # Fallback to Unsplash Source API if Wikipedia has no photo
        image_url = f"https://images.unsplash.com/photo-1518770660439-4636190af475?w=1600&auto=format&fit=crop&q=80"
    try:
        res = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        if res.status_code == 200 and len(res.content) > 5000:
            local_path = os.path.join(DOWNLOAD_DIR, f"{post_id}.jpg")
            with open(local_path, "wb") as f:
                f.write(res.content)
            return local_path
    except Exception:
        pass
    return None

def auto_harvest_trending_evergreen(max_new_topics=3):
    """Scans trends, extracts concepts, downloads photos, and updates the local DB."""
    db = load_db()
    existing_titles = {item["title"].lower() for item in db}
    
    print("[*] Scanning live Google Trends and Reddit for tech seeds...")
    seeds = get_trending_tech_seeds()
    added_count = 0

    for seed in seeds:
        if added_count >= max_new_topics:
            break

        concept_title = search_wikipedia_concept(seed)
        if not concept_title or concept_title.lower() in existing_titles:
            continue

        details = fetch_concept_details(concept_title)
        if not details:
            continue

        post_id = "evg_" + re.sub(r'\W+', '_', concept_title.lower()).strip('_')
        image_path = download_hd_image(details["image_url"], post_id)

        entry = {
            "id": post_id,
            "category": "TECH CONCEPT",
            "title": f"How It Works: {details['title']}",
            "description": details.get("description", "Technology Deep Dive"),
            "highlights": details["highlights"],
            "image_path": image_path,
            "source": "Open Encyclopedia & Lab Research",
            "caption": f"""How does {details['title']} actually work? 💡

{details['description']}

━━━━━━━━━━━━━━━━━━━━━
Key Mental Model:
• {details['highlights'][0]}
• {details['highlights'][1]}
{f'• {details["highlights"][2]}' if len(details['highlights']) > 2 else ''}

━━━━━━━━━━━━━━━━━━━━━
Save this post to your tech & system design collection.

Follow @extrovernerd for clean breakdowns, developer toolkits, and nerd culture.

.
.
.
#extrovernerd #TechEducation #SystemDesign #CheatSheet #Developers #ComputerScience #STEM"""
        }

        db.append(entry)
        existing_titles.add(concept_title.lower())
        added_count += 1
        print(f"   ✨ Added trending concept: {details['title']}")

    save_db(db)
    print(f"[+] Evergreen database updated. Total items in library: {len(db)}")
    return db