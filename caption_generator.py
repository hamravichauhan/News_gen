from config import PAGE_HANDLE


# ============================================================
#  CATEGORY TAG BANKS
#  Every tag here is tech-focused and mass-appeal.
#  Avoided: geopolitics, disaster, sports (off-brand)
# ============================================================
CATEGORY_TAGS = {
    "AI & Innovation": (
        "#AI #ArtificialIntelligence #ChatGPT #OpenAI #MachineLearning "
        "#FutureTech #TechIndia #AIRevolution"
    ),
    "Tech & Web Culture": (
        "#TechNews #BigTech #Google #Apple #Microsoft #InternetCulture "
        "#CreatorEconomy #TechIndia"
    ),
    "Gadgets & Consumer Hardware": (
        "#Gadgets #Smartphones #iPhone #Android #Samsung #TechReview "
        "#GadgetLover #NewLaunch"
    ),
    "Space & Deep Tech": (
        "#Space #ISRO #NASA #SpaceX #Astronomy #QuantumTech "
        "#DeepTech #SpaceNews"
    ),
    "Gaming & Esports": (
        "#Gaming #Esports #PlayStation #Xbox #PCGaming #Valorant "
        "#GamerLife #GameNews"
    ),
    "Business & Consumer Tech": (
        "#Startups #TechFunding #IndianStartups #VentureCapital "
        "#Innovation #TechBusiness"
    ),
    "Crypto & Web3": (
        "#Crypto #Bitcoin #Web3 #Blockchain #Ethereum #DeFi #CryptoTech"
    ),
}

# ============================================================
#  HOOK OPENERS
#  Short, punchy, curiosity-driven. First line is the scroll-stopper.
# ============================================================
HOOK_OPENERS = {
    "AI & Innovation": "🤖 AI just did something wild. Here's the breakdown:",
    "Tech & Web Culture": "📱 The internet is losing it over this:",
    "Gadgets & Consumer Hardware": "🔥 New tech just dropped — and it's a big deal:",
    "Space & Deep Tech": "🚀 Something massive just happened in space tech:",
    "Gaming & Esports": "🎮 Gamers, you need to see this:",
    "Business & Consumer Tech": "💰 The tech money moves you should know about:",
    "Crypto & Web3": "🪙 Crypto just made a move everyone's watching:",
}

DEFAULT_OPENER = "⚡ Big tech update just dropped:"

# ============================================================
#  HASHTAG BLOCKS — split into reach vs. niche for the algorithm
# ============================================================
REACH_TAGS = "#TechNews #TechIndia #Innovation #DailyTech #TechUpdate"

NICHE_TAGS = (
    "#extrovernerd #TechBriefing #Top10Tech #NerdTier "
    "#TechForEveryone #TrendingTech"
)

VIRAL_TAGS = "#ViralTech #TechTok #MustKnow #BreakingTech"

CTA_LINES = [
    "Which one surprised you the most? 👇",
    "Drop your take in the comments. 👇",
    "Agree or disagree? Let's hear it. 👇",
    "Tag someone who needs to see this. 👇",
    "Save this for later — you'll want it. 🔖",
]

FOLLOW_LINE = (
    f"Follow {PAGE_HANDLE} for daily tech briefings, "
    "nerd-tier analysis, and the stories that actually matter."
)


def _detect_category(story):
    """Pick the best category from the story's tags."""
    category = story.get("category", "").strip()
    if category in HOOK_OPENERS:
        return category

    # Fallback: scan keywords in the title
    title = (story.get("title", "") + " " + story.get("summary", "")).lower()
    for cat in HOOK_OPENERS.keys():
        if any(word in title for word in cat.lower().split()):
            return cat

    return "Tech & Web Culture"


def generate_instagram_caption(story):
    """Generates a punchy, engagement-optimized Instagram caption."""
    import random

    title = story.get("title", "").strip() or "Untitled tech story"
    summary = (story.get("summary") or story.get("description") or "").strip()
    category = _detect_category(story)
    source = story.get("source", "Tech Wire")
    published_time = (story.get("published_utc") or story.get("published") or "Recent")
    published_time = str(published_time)[:16]

    # Trim summary to a single readable sentence
    if summary:
        first_sentence = summary.split(".")[0].strip()
        if len(first_sentence) > 220:
            first_sentence = first_sentence[:217].rsplit(" ", 1)[0] + "..."
    else:
        first_sentence = "Full breakdown in the slides above."

    opener = HOOK_OPENERS.get(category, DEFAULT_OPENER)
    category_tags = CATEGORY_TAGS.get(category, "#Tech #Innovation")
    cta = random.choice(CTA_LINES)

    return f"""{opener}

{title}

{first_sentence}

━━━━━━━━━━━━━━━━━━━━━
📌 Source: {source}
🏷️ Category: {category}
🕒 Filed: {published_time} UTC

━━━━━━━━━━━━━━━━━━━━━
{cta}

{FOLLOW_LINE}

.
.
.
{REACH_TAGS}
{category_tags}
{NICHE_TAGS}
{VIRAL_TAGS}
""".strip()


# ============================================================
#  BONUS: Master caption for a whole carousel of 10 stories
# ============================================================
def generate_carousel_caption(stories, genre, date_display):
    """Builds the master caption for a full 10-slide carousel."""
    import random

    genre_display = genre.replace("_", " ").title()
    lines = [
        f"🚨 {genre_display.upper()} BRIEFING — {date_display}",
        "",
        f"Top 10 {genre_display} stories you need to know today:",
        "",
    ]

    for idx, s in enumerate(stories[:10], start=1):
        t = s.get("title", "").strip()
        if len(t) > 110:
            t = t[:107].rsplit(" ", 1)[0] + "..."
        lines.append(f"{idx:02d}. {t}")

    lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━",
        random.choice(CTA_LINES),
        "",
        FOLLOW_LINE,
        "",
        ".",
        ".",
        ".",
        "#extrovernerd #TechNews #DailyTech #Top10Tech #TechBriefing",
        "#AI #Gadgets #Space #Gaming #TechIndia #Innovation",
        "#BreakingTech #TechUpdate #TechTok #NerdTier",
    ])

    return "\n".join(lines)