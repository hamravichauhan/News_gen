import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
POSTS_DIR = os.path.join(BASE_DIR, "instagram_posts")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

PAGE_HANDLE = "@extrovernerd"
TRENDS_RSS_INDIA = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=IN"

# ============================================================
#  TECH-ONLY, MASS-AUDIENCE RSS FEEDS
#  Every feed below returns high-resolution lead images in
#  its RSS <enclosure> or <media:content> tag — Instagram-ready.
#  Removed: INDIA_POLICY, GEOPOLITICS (off-brand for tech page)
# ============================================================
GENRE_FEEDS = {
    "AI_TECH": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.marktechpost.com/feed/",
        "https://news.mit.edu/rss/topic/artificial-intelligence2",
        "https://openai.com/blog/rss.xml",
        "https://blog.google/technology/ai/rss/"
    ],
    "GADGETS_HARDWARE": [
        "https://www.theverge.com/rss/index.xml",
        "https://arstechnica.com/gadgets/feed/",
        "https://www.engadget.com/rss.xml",
        "https://www.tomshardware.com/feeds/all",
        "https://9to5mac.com/feed/",
        "https://9to5google.com/feed/",
        "https://www.gsmarena.com/rss-news-reviews.php3"
    ],
    "DEV_SECURITY": [
        "https://thehackernews.com/feeds/posts/default",
        "https://www.bleepingcomputer.com/feed/",
        "https://dev.to/feed",
        "https://krebsonsecurity.com/feed/",
        "https://github.blog/feed/",
        "https://securityaffairs.com/feed"
    ],
    "SPACE_DEEPTECH": [
        "https://spacenews.com/feed/",
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "https://phys.org/rss-feed/space-news/",
        "https://www.space.com/feeds/all",
        "https://arstechnica.com/science/feed/"
    ],
    "GAMING_ESPORTS": [
        "https://feeds.feedburner.com/ign/news",
        "https://www.polygon.com/rss/index.xml",
        "https://www.gamespot.com/feeds/news/",
        "https://www.pcgamer.com/rss/"
    ],
    "INTERNET_CULTURE": [
        "https://mashable.com/feed",
        "https://knowyourmeme.com/newsfeed.rss",
        "https://www.dailydot.com/feed/"
    ],
    "BUSINESS_STARTUPS": [
        "https://techcrunch.com/category/startups/feed/",
        "https://inc42.com/feed/",
        "https://yourstory.com/feed"
    ],
    "CRYPTO_WEB3": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://decrypt.co/feed"
    ]
}

# ============================================================
#  HIGH-IMAGE-QUALITY FEED WHITELIST
#  These sources reliably publish 1200px+ lead images in RSS.
#  Prioritized by scraper.py when ranking visual stories.
# ============================================================
HIGH_IMAGE_QUALITY_SOURCES = [
    "techcrunch.com",
    "theverge.com",
    "engadget.com",
    "arstechnica.com",
    "venturebeat.com",
    "9to5mac.com",
    "9to5google.com",
    "gsmarena.com",
    "tomshardware.com",
    "space.com",
    "spacenews.com",
    "thehackernews.com",
    "bleepingcomputer.com",
    "polygon.com",
    "ign.com",
    "gamespot.com",
    "mashable.com",
    "dailydot.com"
]

# ============================================================
#  SUBREDDIT MAPPING — tech-only, no worldnews/geopolitics
# ============================================================
GENRE_SUBREDDITS = {
    "AI_TECH": ["MachineLearning", "artificial", "ChatGPT", "singularity", "OpenAI"],
    "DEV_SECURITY": ["programming", "netsec", "cybersecurity", "webdev"],
    "SPACE_DEEPTECH": ["space", "astronomy", "QuantumComputing"],
    "GADGETS_HARDWARE": ["gadgets", "hardware", "technology", "Android", "apple"],
    "GAMING_ESPORTS": ["gaming", "Games", "pcgaming", "esports"],
    "INTERNET_CULTURE": ["InternetIsBeautiful", "interestingasfuck", "technology"],
    "BUSINESS_STARTUPS": ["startups", "Entrepreneur"],
    "CRYPTO_WEB3": ["CryptoCurrency", "Bitcoin", "ethereum"],
    "ALL": ["technology", "gadgets", "MachineLearning", "artificial",
            "space", "gaming", "programming"]
}

# ============================================================
#  DEFAULT REDDIT POOL — tech-only
# ============================================================
REDDIT_SUBREDDITS = [
    "technology", "MachineLearning", "artificial", "gadgets",
    "technews", "programming", "webdev", "CyberSecurity",
    "Android", "apple", "pcgaming", "gaming",
    "space", "singularity", "OpenAI"
]

# ============================================================
#  CLASSIFICATION TAXONOMY — MASS-APPEAL TECH ONLY
# ============================================================
CATEGORY_TAXONOMY = {
    "AI & Innovation": [
        "ai", "artificial intelligence", "llm", "gpt", "openai", "deepmind",
        "model", "transformer", "neural", "agent", "robot", "robotics",
        "machine learning", "claude", "gemini", "anthropic", "nvidia", "gpu",
        "chatgpt", "copilot", "midjourney", "stable diffusion", "sora"
    ],
    "Tech & Web Culture": [
        "google", "apple", "microsoft", "meta", "software", "code", "github",
        "developer", "framework", "linux", "cloud", "aws", "open source",
        "algorithm", "app", "platform", "privacy", "security", "hacker",
        "iphone", "android", "windows", "macos", "chrome", "browser",
        "social media", "tiktok", "instagram", "youtube", "x.com", "twitter"
    ],
    "Gadgets & Consumer Hardware": [
        "phone", "smartphone", "laptop", "tablet", "earbuds", "headphones",
        "smartwatch", "wearable", "gpu", "cpu", "chip", "processor",
        "samsung", "oneplus", "xiaomi", "pixel", "macbook", "ipad",
        "review", "launch", "specs", "benchmark", "unboxing"
    ],
    "Space & Deep Tech": [
        "isro", "nasa", "spacex", "space", "moon", "mars", "rocket",
        "satellite", "orbit", "telescope", "quantum", "fusion", "physics",
        "astronomy", "cosmos", "solar", "starship", "artemis", "chandrayaan"
    ],
    "Gaming & Esports": [
        "game", "gaming", "playstation", "xbox", "nintendo", "steam",
        "esports", "valorant", "fortnite", "minecraft", "gta", "console",
        "pc gaming", "twitch", "streamer", "fps", "rpg"
    ],
    "Business & Consumer Tech": [
        "startup", "funding", "invest", "ipo", "acquisition", "merger",
        "valuation", "billion", "million", "revenue", "ceo", "layoff",
        "tech company", "silicon valley", "venture"
    ]
}