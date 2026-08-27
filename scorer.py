import re

VIRAL_TRIGGER_WORDS = [
    "ai", "isro", "scam", "arrest", "bans", "records", "breakthrough",
    "launch", "billion", "crore", "reveals", "warning", "crisis", "modi",
    "apple", "google", "nvidia", "deepseek", "chatgpt", "openai", "meta",
    "spacex", "hack", "leak", "exploit", "unveils", "antitrust"
]


def safe_text(value):
    """Safely converts strings, lists, or None into a clean string."""
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    elif isinstance(value, str):
        return value
    return ""


def calculate_virality_score(story, trending_keywords=None):
    """
    Calculates a 0-100 virality score based on:
    1. Google Trends / Realtime Keyword overlap (+35 pts)
    2. Multi-source validation saturation (+20 pts)
    3. High-engagement viral triggers & numbers (+15 pts)
    4. Verified visual asset readiness (+15 pts)
    5. Reddit / Community engagement signal (+15 pts)
    """
    score = 15  # Base floor score
    title_raw = safe_text(story.get("title", ""))
    title_lower = title_raw.lower()

    if not title_lower:
        story["virality_score"] = 0
        return story

    # Normalize trending keywords set safely
    clean_trends = set()
    if trending_keywords:
        for kw in trending_keywords:
            if isinstance(kw, str):
                clean_trends.add(kw.lower().strip())
            elif isinstance(kw, (list, set, tuple)):
                clean_trends.update(str(x).lower().strip() for x in kw)

    # 1. Google Trends Match (+35 pts max)
    title_words = set(re.findall(r'\w+', title_lower))
    matches = title_words.intersection(clean_trends)
    if matches:
        score += min(35, len(matches) * 12)

    # 2. Multi-Source Saturation (+20 pts max)
    source_count = story.get("source_count", 1)
    if isinstance(source_count, (int, float)):
        if source_count >= 3:
            score += 20
        elif source_count == 2:
            score += 12

    # 3. High-Engagement Viral Triggers & Hard Stats (+15 pts max)
    if any(re.search(r'\b' + re.escape(w) + r'\b', title_lower) for w in VIRAL_TRIGGER_WORDS):
        score += 10
    if re.search(r'\d+', title_raw):  # Numeric data/percentages/figures
        score += 5

    # 4. Verified Visual Asset Bonus (+15 pts)
    # Prioritizes items that have downloaded image assets ready for slide rendering
    if story.get("image_path"):
        score += 15
    elif story.get("image_url"):
        score += 8

    # 5. Reddit / Community Upvote Signal (+15 pts max)
    source_str = safe_text(story.get("source", "")).lower()
    if "r/" in source_str:
        raw_score = story.get("score", 0)
        reddit_votes = raw_score if isinstance(raw_score, (int, float)) else 0
        if reddit_votes > 500:
            score += 15
        elif reddit_votes > 150:
            score += 8

    story["virality_score"] = min(100, max(0, score))
    return story