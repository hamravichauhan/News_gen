import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from config import PAGE_HANDLE, POSTS_DIR

HD_CARD_SIZE = (2160, 2700)
FINAL_CARD_SIZE = (1080, 1350)

# ─── PREMIUM EDITORIAL PALETTE ───────────────────────────────────────────────
COLOR_BG_DARK        = (10, 12, 16)
COLOR_TEXT_PRIMARY   = (248, 249, 250)     # Optical Bright White
COLOR_TEXT_SUBTITLE  = (215, 222, 232)     # High-Legibility Slate White
COLOR_TEXT_MUTED     = (148, 163, 184)     # Muted Slate
COLOR_GOLD_ACCENT    = (230, 198, 135)     # Luxury Champagne Gold
COLOR_GLASS_FILL     = (18, 22, 30)
COLOR_GLASS_BORDER   = (255, 255, 255, 45) # Translucent Glass Edge


def load_scaled_font(size, bold=False):
    """Loads system fonts with guaranteed macOS and Linux/Ubuntu support."""
    font_candidates = [
        # Linux (Ubuntu GitHub Actions Runner)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/HelveticaBold.ttc" if bold else "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]

    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size=size, index=0)
            except Exception:
                try:
                    return ImageFont.truetype(fp, size=size)
                except Exception:
                    continue
    return ImageFont.load_default()


def draw_tracked_text(draw, pos, text, font, fill, spacing=4):
    """Renders text with custom letter-spacing (tracking) for a luxury feel."""
    x, y = pos
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + spacing
    return x


def wrap_text_tokens(text, font, max_width, draw):
    """Splits headlines cleanly into wrapped token arrays."""
    words = text.split()
    if not words:
        return []
    lines = []
    curr_line = []
    for word in words:
        trial = curr_line + [word]
        w = draw.textlength(" ".join(trial), font=font)
        if w > max_width and curr_line:
            lines.append(curr_line)
            curr_line = [word]
        else:
            curr_line = trial
    if curr_line:
        lines.append(curr_line)
    return lines


def is_highlight_token(word):
    """Identifies critical numbers, metrics, and key verbs for gold styling."""
    cleaned = re.sub(r'[^\w\s₹$%]', '', word).lower()
    if re.search(r'\d', word) or any(c in word for c in ['₹', '$', '%']):
        return True
    if cleaned in ['dead', 'killed', 'missing', 'bans', 'scam', 'arrested', 'record', 'alert', 'crisis', 'breakthrough', 'warns', 'dethrones', 'ai', 'isro', 'apple', 'nvidia', 'google']:
        return True
    return False


def process_hd_background(raw_image_path):
    """Scales background with smooth cinematic depth."""
    target_w, target_h = HD_CARD_SIZE
    if raw_image_path and os.path.exists(raw_image_path):
        try:
            with Image.open(raw_image_path) as img:
                img = img.convert("RGBA")
                img = ImageOps.exif_transpose(img)
                w, h = img.size

                if w < 600 or h < 600:
                    blurred_bg = img.resize((target_w, target_h), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(60))
                    scale = min((target_w * 0.92) / w, (target_h * 0.58) / h)
                    new_w, new_h = int(w * scale), int(h * scale)
                    sharp_fg = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    blurred_bg.paste(sharp_fg, ((target_w - new_w) // 2, int(target_h * 0.12)), sharp_fg)
                    return blurred_bg
                else:
                    target_ratio = target_w / target_h
                    if (w / h) > target_ratio:
                        crop_w = int(h * target_ratio)
                        cropped = img.crop(((w - crop_w) // 2, 0, (w + crop_w) // 2, h))
                    else:
                        crop_h = int(w / target_ratio)
                        cropped = img.crop((0, (h - crop_h) // 2, w, (h + crop_h) // 2))
                    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"[-] Image processing fallback: {e}")
    return Image.new("RGBA", HD_CARD_SIZE, color=COLOR_BG_DARK)


def build_cover_card(top_stories, date_str, output_path):
    """Slide 1: Luxury Magazine Executive Index."""
    card = Image.new("RGBA", HD_CARD_SIZE, color=COLOR_BG_DARK)

    # Ambient Editorial Radial Glow
    overlay = Image.new("RGBA", HD_CARD_SIZE, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(overlay)
    for r in range(900, 0, -15):
        alpha = int(35 * (r / 900))
        glow_draw.ellipse([-250, -250, 950, 950], fill=(99, 102, 241, alpha))
    card = Image.alpha_composite(card, overlay).convert("RGB")
    draw = ImageDraw.Draw(card)

    font_main = load_scaled_font(size=120, bold=True)
    font_sub = load_scaled_font(size=50, bold=False)
    font_brand = load_scaled_font(size=54, bold=True)
    font_list = load_scaled_font(size=44, bold=False)
    font_num = load_scaled_font(size=46, bold=True)
    font_meta = load_scaled_font(size=42, bold=False)

    # Top Brand Header
    draw_tracked_text(draw, (120, 110), PAGE_HANDLE.upper(), font_brand, COLOR_TEXT_PRIMARY, spacing=6)
    date_w = draw.textlength(date_str, font=font_meta)
    draw.text((HD_CARD_SIZE[0] - 120 - date_w, 120), date_str, font=font_meta, fill=COLOR_TEXT_MUTED)

    # Title & Subtitle
    draw.text((120, 240), "THE DAILY BRIEF", font=font_main, fill=COLOR_GOLD_ACCENT)
    draw.text((120, 380), "Top 10 Essential Briefings Across Tech & World Affairs", font=font_sub, fill=COLOR_TEXT_MUTED)
    draw.line([(120, 470), (HD_CARD_SIZE[0] - 120, 470)], fill=(255, 255, 255, 50), width=2)

    # Clean Index Items
    y_pos = 530
    for idx, s in enumerate(top_stories[:10], start=1):
        num_str = f"{idx:02d}"
        draw.text((120, y_pos), num_str, font=font_num, fill=COLOR_GOLD_ACCENT)

        short_title = s["title"][:76] + "..." if len(s["title"]) > 76 else s["title"]
        draw.text((220, y_pos), short_title, font=font_list, fill=COLOR_TEXT_PRIMARY)
        y_pos += 184

    # Footer
    draw.line([(120, 2460), (HD_CARD_SIZE[0] - 120, 2460)], fill=(255, 255, 255, 50), width=2)
    draw_tracked_text(draw, (120, 2510), "SWIPE FOR FULL TAKEAWS", font=font_meta, fill=COLOR_GOLD_ACCENT, spacing=3)

    follow_label = f"FOLLOW {PAGE_HANDLE.upper()}"
    follow_w = draw.textlength(follow_label, font=font_brand)
    draw_tracked_text(draw, (HD_CARD_SIZE[0] - 120 - follow_w, 2505), follow_label, font=font_brand, fill=COLOR_TEXT_PRIMARY, spacing=4)

    final_card = card.resize(FINAL_CARD_SIZE, Image.Resampling.LANCZOS)
    final_card.save(output_path, "JPEG", quality=100, subsampling=0, optimize=True)
    return output_path


def build_carousel_slide(story, slide_index, total_slides, output_path):
    """
    Slides 2–11: Luxury Editorial Photo Card.
    Renders Headline + Complete Briefing Takeaway Context.
    """
    raw_image_path = story.get("image_path")
    bg = process_hd_background(raw_image_path)

    overlay = Image.new("RGBA", HD_CARD_SIZE, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Top Subtle Shade
    for y in range(450):
        alpha = int(220 * (1 - (y / 450)))
        draw_overlay.line([(0, y), (HD_CARD_SIZE[0], y)], fill=(8, 10, 14, alpha))

    # Bottom Gradient Tint (Stronger base for title + summary readability)
    for y in range(HD_CARD_SIZE[1]):
        if y > 900:
            alpha = int(255 * ((y - 900) / (HD_CARD_SIZE[1] - 900)) ** 1.25)
            draw_overlay.line([(0, y), (HD_CARD_SIZE[0], y)], fill=(8, 10, 14, min(252, alpha)))

    card = Image.alpha_composite(bg, overlay).convert("RGB")
    draw = ImageDraw.Draw(card)

    font_title = load_scaled_font(size=96, bold=True)
    font_summary = load_scaled_font(size=56, bold=False)
    font_brand = load_scaled_font(size=54, bold=True)
    font_badge = load_scaled_font(size=46, bold=True)
    font_footer = load_scaled_font(size=44, bold=False)

    # 1. Top Bar
    draw_tracked_text(draw, (120, 110), PAGE_HANDLE.upper(), font_brand, COLOR_TEXT_PRIMARY, spacing=5)

    # Counter Badge
    badge_text = f" {slide_index:02d} / {total_slides:02d} "
    badge_w = draw.textlength(badge_text, font=font_badge)
    badge_box = [HD_CARD_SIZE[0] - 120 - badge_w - 24, 95, HD_CARD_SIZE[0] - 120, 175]
    draw.rounded_rectangle(badge_box, radius=14, fill=COLOR_GLASS_FILL)
    draw.rounded_rectangle(badge_box, radius=14, outline=COLOR_GLASS_BORDER, width=2)
    draw.text((HD_CARD_SIZE[0] - 120 - badge_w - 12, 110), badge_text, font=font_badge, fill=COLOR_GOLD_ACCENT)

    # 2. Extract and Wrap Text Lines
    title_text = story.get("title", "").strip()
    summary_text = story.get("summary", "").strip()

    title_lines = wrap_text_tokens(title_text, font_title, max_width=1920, draw=draw)[:3]
    summary_lines = wrap_text_tokens(summary_text, font_summary, max_width=1920, draw=draw)[:3] if summary_text else []

    title_line_height = 125
    summary_line_height = 78

    total_block_height = (len(title_lines) * title_line_height) + (len(summary_lines) * summary_line_height) + (35 if summary_lines else 0)
    y_pos = max(1350, 2400 - total_block_height)

    # Render Headline with Gold Highlights
    space_w = draw.textlength(" ", font=font_title)
    for line_tokens in title_lines:
        x_cursor = 120
        for word in line_tokens:
            word_w = draw.textlength(word, font=font_title)
            color = COLOR_GOLD_ACCENT if is_highlight_token(word) else COLOR_TEXT_PRIMARY

            # Drop shadow
            for dx, dy in [(-2, -2), (2, -2), (-2, 2), (3, 3), (0, 4)]:
                draw.text((x_cursor + dx, y_pos + dy), word, font=font_title, fill=(0, 0, 0))

            draw.text((x_cursor, y_pos), word, font=font_title, fill=color)
            x_cursor += word_w + space_w

        y_pos += title_line_height

    # Render Complete Briefing Context (Summary)
    if summary_lines:
        y_pos += 25
        for line_tokens in summary_lines:
            line_str = " ".join(line_tokens)
            # Soft shadow
            draw.text((122, y_pos + 2), line_str, font=font_summary, fill=(0, 0, 0))
            draw.text((120, y_pos), line_str, font=font_summary, fill=COLOR_TEXT_SUBTITLE)
            y_pos += summary_line_height

    # 3. Clean Footer
    draw.line([(120, 2460), (HD_CARD_SIZE[0] - 120, 2460)], fill=(255, 255, 255, 50), width=2)
    source_label = f"SOURCE: {story.get('source', 'VERIFIED SOURCE').upper()}"
    draw_tracked_text(draw, (120, 2510), source_label[:45], font=font_footer, fill=COLOR_TEXT_MUTED, spacing=2)

    follow_label = f"FOLLOW {PAGE_HANDLE.upper()}"
    follow_w = draw.textlength(follow_label, font=font_brand)
    draw_tracked_text(draw, (HD_CARD_SIZE[0] - 120 - follow_w, 2505), follow_label, font=font_brand, fill=COLOR_TEXT_PRIMARY, spacing=4)

    # 4. Save Final Post
    final_post = card.resize(FINAL_CARD_SIZE, Image.Resampling.LANCZOS)
    final_post.save(output_path, "JPEG", quality=100, subsampling=0, optimize=True)

    if raw_image_path and os.path.exists(raw_image_path):
        try:
            os.remove(raw_image_path)
        except Exception:
            pass

    return output_path


def build_instagram_post(story):
    """Builds a single standalone luxury post and matching caption file."""
    post_id = story["id"]
    output_card_path = os.path.join(POSTS_DIR, f"post_{post_id}.jpg")
    output_caption_path = os.path.join(POSTS_DIR, f"post_{post_id}_caption.txt")

    build_carousel_slide(story, slide_index=1, total_slides=1, output_path=output_card_path)

    from caption_generator import generate_instagram_caption
    caption_text = generate_instagram_caption(story)
    with open(output_caption_path, "w", encoding="utf-8") as f:
        f.write(caption_text)

    return output_card_path, output_caption_path