import re
from config import CATEGORY_TAXONOMY


def safe_text(value):
    """Safely converts strings, lists, or None into a clean lowercase string."""
    if isinstance(value, list):
        return " ".join(str(v) for v in value).lower()
    elif isinstance(value, str):
        return value.lower()
    return ""


def classify_story(title, description=""):
    combined = (safe_text(title) + " " + safe_text(description)).lower()

    scores = {}
    for category, keywords in CATEGORY_TAXONOMY.items():
        score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', combined))
        scores[category] = score

    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else "Tech & Web Culture"


def verify_and_tag(stories):
    tagged = []
    for story in stories:
        title = story.get("title", "")
        if not title:
            continue
        
        # Ensure category is always a clean string
        cat = story.get("category")
        if not cat or isinstance(cat, list):
            cat = classify_story(title, story.get("description", ""))
        
        story["category"] = str(cat)
        tagged.append(story)
    return tagged