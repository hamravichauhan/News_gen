import os
from config import PAGE_HANDLE
from evergreen_harvester import auto_harvest_trending_evergreen
from evergreen_generator import generate_pending_evergreens

def run():
    print("\n" + "=" * 65)
    print(f"🧠 DYNAMIC EVERGREEN HARVESTER FOR {PAGE_HANDLE.upper()}")
    print("=" * 65)

    # 1. Harvest trending concepts and auto-download high-res imagery
    auto_harvest_trending_evergreen(max_new_topics=3)

    # 2. Render high-contrast visual posts with captions
    print("🎨 Rendering new evergreen visual cards...")
    generate_pending_evergreens(count=3)

    print("=" * 65)
    print("✅ EVERGREEN POSTS GENERATED IN 'instagram_posts/'")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run()