import os
import json
from PIL import Image, ImageDraw, ImageOps
from config import POSTS_DIR, PAGE_HANDLE
from generator import load_scaled_font, wrap_text_tokens, process_hd_background, is_highlight_token, HIGHLIGHT_GOLD, TEXT_WHITE

HD_CARD_SIZE = (2160, 2700)
FINAL_CARD_SIZE = (1080, 1350)
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evergreen_database.json")

def render_evergreen_visual_card(story):
    """Renders a magazine-grade, photo-backed evergreen card with prominent numbers."""
    post_id = story["id"]
    output_card_path = os.path.join(POSTS_DIR, f"{post_id}.jpg")
    output_caption_path = os.path.join(POSTS_DIR, f"{post_id}_caption.txt")
    raw_image_path = story.get("image_path")

    # 1. Base HD Image with Dark Overlay
    bg = process_hd_background(raw_image_path)

    # 2. Cinematic Gradients
    overlay = Image.new("RGBA", HD_CARD_SIZE, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Top brand banner shade
    for y in range(400):
        alpha = int(220 * (1 - (y / 400)))
        draw_overlay.line([(0, y), (HD_CARD_SIZE[0], y)], fill=(6, 8, 12, alpha))

    # Deep bottom gradient for readability
    for y in range(HD_CARD_SIZE[1]):
        if y > 1000:
            alpha = int(255 * ((y - 1000) / (HD_CARD_SIZE[1] - 1000)))
            draw_overlay.line([(0, y), (HD_CARD_SIZE[0], y)], fill=(8, 10, 15, alpha))

    card = Image.alpha_composite(bg, overlay).convert("RGB")
    draw = ImageDraw.Draw(card)

    # 3. Scaled Fonts
    font_title = load_scaled_font(size=108, bold=True)
    font_header = load_scaled_font(size=56, bold=True)
    font_meta = load_scaled_font(size=46, bold=False)
    font_badge = load_scaled_font(size=44, bold=True)

    # 4. Top Header & Category Pill
    draw.text((120, 110), PAGE_HANDLE.upper(), font=font_header, fill=(255, 255, 255, 245))

    cat_text = f"  {story.get('category', 'TECH CONCEPT')}  "
    cat_w = draw.textlength(cat_text, font=font_badge)
    draw.rounded_rectangle([HD_CARD_SIZE[0] - 120 - cat_w - 20, 95, HD_CARD_SIZE[0] - 120, 175], radius=16, fill=(40, 46, 68))
    draw.text((HD_CARD_SIZE[0] - 120 - cat_w - 10, 110), cat_text, font=font_badge, fill=HIGHLIGHT_GOLD)

    # 5. Tokenized Headline with Gold Word Highlighting
    token_lines = wrap_text_tokens(story["title"], font_title, max_width=1920, draw=draw)[:4]
    line_height = 142
    total_text_height = len(token_lines) * line_height
    y_pos = max(1600, 2380 - total_text_height)

    space_w = draw.textlength(" ", font=font_title)

    for line_tokens in token_lines:
        x_cursor = 120
        for word in line_tokens:
            word_w = draw.textlength(word, font=font_title)
            color = HIGHLIGHT_GOLD if is_highlight_token(word) else TEXT_WHITE

            # Drop Shadow for 3D Contrast
            for dx, dy in [(-3, -3), (3, -3), (-3, 3), (4, 4), (0, 5)]:
                draw.text((x_cursor + dx, y_pos + dy), word, font=font_title, fill=(0, 0, 0))

            draw.text((x_cursor, y_pos), word, font=font_title, fill=color)
            x_cursor += word_w + space_w

        y_pos += line_height

    # 6. Prominent Footer
    draw.line([(120, 2460), (2040, 2460)], fill=(255, 255, 255, 80), width=3)
    draw.text((120, 2510), "📌 SAVE THIS FOR LATER", font=font_meta, fill=HIGHLIGHT_GOLD)

    follow_label = f"FOLLOW {PAGE_HANDLE.upper()}"
    follow_w = draw.textlength(follow_label, font=font_header)
    draw.text((HD_CARD_SIZE[0] - 120 - follow_w, 2510), follow_label, font=font_header, fill=(255, 255, 255))

    # 7. Downscale 2x Canvas to 1080x1350 with Lanczos Antialiasing
    final_post = card.resize(FINAL_CARD_SIZE, Image.Resampling.LANCZOS)
    final_post.save(output_card_path, "JPEG", quality=100, subsampling=0, optimize=True)

    # 8. Save Caption
    with open(output_caption_path, "w", encoding="utf-8") as f:
        f.write(story["caption"])

    # 9. Clean raw download
    if raw_image_path and os.path.exists(raw_image_path):
        try:
            os.remove(raw_image_path)
        except Exception:
            pass

    return output_card_path, output_caption_path

def generate_pending_evergreens(count=3):
    if not os.path.exists(DB_FILE):
        return
    with open(DB_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    rendered = 0
    for p in reversed(posts):  # Render newest harvested items first
        if rendered >= count:
            break
        out_path = os.path.join(POSTS_DIR, f"{p['id']}.jpg")
        if not os.path.exists(out_path):
            img_p, cap_p = render_evergreen_visual_card(p)
            print(f"   📸 Rendered: {os.path.basename(img_p)}")
            print(f"   📝 Caption:  {os.path.basename(cap_p)}\n")
            rendered += 1