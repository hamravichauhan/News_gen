from config import PAGE_HANDLE

CATEGORY_TAGS = {
    "Tech & AI": "#TechIndia #ArtificialIntelligence #FutureTech #Innovation",
    "Culture & Internet": (
        "#InternetCulture #TrendingNow #PopCulture #CreatorEconomy"
    ),
    "Geopolitics & Power": (
        "#IndianPolitics #NationalNews #Policy #Governance"
    ),
    "Disaster & Climate": "#WeatherUpdate #ClimateAlert #IndiaUpdates",
    "Business & Markets": "#IndianEconomy #Startups #Markets #Finance",
    "Sports & Esports": "#IndianSports #CricketUpdates #TeamIndia",
}


def generate_instagram_caption(story):
  """Generates a human-written, high-engagement Instagram caption."""
  title = story.get("title", "").strip()
  category = story.get("category", "Culture & Internet")
  source = story.get("source", "National Wire")
  published_time = story.get("published_utc", "Recent")[:16]

  hook_openers = {
      "Tech & AI": "The tech landscape is shifting rapidly. Here's what's unfolding:",
      "Culture & Internet": (
          "What everyone is talking about across the web right now:"
      ),
      "Geopolitics & Power": (
          "A major development just surfaced on the national front:"
      ),
      "Disaster & Climate": (
          "Important climate and regional update you should know:"
      ),
      "Business & Markets": "Key business movements shaping the headlines today:",
      "Sports & Esports": (
          "The latest score and headline from the sporting arena:"
      ),
  }
  opener = hook_openers.get(
      category, "A major update just came in across national headlines:"
  )
  category_tags = CATEGORY_TAGS.get(
      category, "#CurrentAffairs #TrendingInIndia"
  )

  return f"""{opener}

{title}

━━━━━━━━━━━━━━━━━━━━━
Key Context:
• Coverage monitored via {source} in the latest 24-hour cycle.
• Filed under: {category}.
• Timestamp: {published_time} UTC.

━━━━━━━━━━━━━━━━━━━━━
What are your thoughts on this? Let's discuss in the comments below.

Follow {PAGE_HANDLE} for fast, clear daily breakdowns and nerd-tier analysis.

.
.
.
#extrovernerd #IndiaNews #DailyDigest #CurrentAffairs #IndiaUpdates {category_tags}
""".strip()