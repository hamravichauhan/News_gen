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

## Pure, strictly categorized RSS feeds
GENRE_FEEDS = {
    "AI_TECH": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.marktechpost.com/feed/",
        "https://news.mit.edu/rss/topic/artificial-intelligence2"
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
    "INDIA_POLICY": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://indianexpress.com/section/explained/feed/",
        "https://www.livemint.com/rss/politics",
        "https://economictimes.indiatimes.com/news/politics/rssfeeds/17246130.cms"
    ],
    "GEOPOLITICS": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://foreignpolicy.com/feed/",
        "https://thediplomat.com/feed/",
        "https://apnews.com/hub/world-news/rss"
    ],
    "BUSINESS_STARTUPS": [
        "https://techcrunch.com/category/startups/feed/",
        "https://inc42.com/feed/",
        "https://yourstory.com/feed",
        "https://www.livemint.com/rss/companies",
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://www.bloomberg.com/feed/podcast/technology.xml"
    ],
    "CRYPTO_WEB3": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://decrypt.co/feed",
        "https://bitcoinmagazine.com/feed"
    ],
    "GADGETS_HARDWARE": [
        "https://www.theverge.com/rss/index.xml",
        "https://arstechnica.com/gadgets/feed/",
        "https://www.engadget.com/rss.xml",
        "https://www.tomshardware.com/feeds/all",
        "https://9to5mac.com/feed/",
        "https://9to5google.com/feed/"
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
    ]
}

# Subreddit mapping
GENRE_SUBREDDITS = {
    "AI_TECH": ["MachineLearning", "artificial", "ChatGPT", "singularity"],
    "DEV_SECURITY": ["programming", "netsec", "cybersecurity", "webdev"],
    "SPACE_DEEPTECH": ["space", "astronomy", "QuantumComputing"],
    "INDIA_POLICY": ["india", "IndiaSpeaks", "IndiaTech"],
    "GEOPOLITICS": ["geopolitics", "worldnews"],
    "BUSINESS_STARTUPS": ["startups", "Entrepreneur", "business"],
    "CRYPTO_WEB3": ["CryptoCurrency", "Bitcoin", "ethereum"],
    "GADGETS_HARDWARE": ["gadgets", "hardware", "technology"],
    "GAMING_ESPORTS": ["gaming", "Games", "pcgaming", "esports"],
    "INTERNET_CULTURE": ["InternetIsBeautiful", "interestingasfuck", "technology"],
    "ALL": ["technology", "worldnews", "space", "gadgets"]
}

REDDIT_SUBREDDITS = [
    "technology", "MachineLearning", "artificial", "space", "ProgrammerHumor",
    "technews", "gadgets", "science", "Futurology", "CyberSecurity",
    "webdev", "programming", "IndiaTech", "cryptocurrency", "gaming"
]

# Classification taxonomy required by classifier.py
CATEGORY_TAXONOMY = {
    "AI & Innovation": [
        "ai", "artificial intelligence", "llm", "gpt", "openai", "deepmind",
        "model", "transformer", "neural", "agent", "robot", "robotics",
        "machine learning", "claude", "gemini", "anthropic", "nvidia", "gpu"
    ],
    "Tech & Web Culture": [
        "google", "apple", "microsoft", "meta", "software", "code", "github",
        "developer", "framework", "linux", "cloud", "aws", "open source",
        "algorithm", "app", "platform", "privacy", "security", "hacker"
    ],
    "Space & Deep Tech": [
        "isro", "nasa", "spacex", "space", "moon", "mars", "rocket",
        "satellite", "orbit", "telescope", "quantum", "fusion", "physics",
        "astronomy", "cosmos", "solar"
    ],
    "National & Policy": [
        "india", "government", "parliament", "policy", "cabinet", "ministry",
        "court", "supreme court", "economy", "gdp", "tax", "rbi", "delhi",
        "mumbai", "isro", "digital india", "upi"
    ],
    "Business & Markets": [
        "startup", "funding", "invest", "market", "stocks", "ipo", "acquisition",
        "merger", "valuation", "billion", "million", "revenue", "ceo", "layoff"
    ]
}