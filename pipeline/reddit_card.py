"""Renders a fake social-post 'hook card' (avatar, username, title, reactions) as an overlay image."""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_BOLD = "assets/fonts/Fredoka-Bold.ttf"
EMOJI_FONT = "C:/Windows/Fonts/seguiemj.ttf"

CARD_RADIUS = 34
CARD_PADDING = 34
AVATAR_SIZE = 76
CHECKMARK_BLUE = (29, 155, 240)
TITLE_COLOR = (20, 20, 20)
META_COLOR = (80, 80, 80)
ICON_COLOR = (60, 60, 60)
REACTION_EMOJIS = "\U0001F60A \U00002764\U0000FE0F \U0001F62E \U0001F525"

DEFAULT_AWARD_ICONS = [
    "assets/reddit_icons/icon_r2_c4.png",
    "assets/reddit_icons/icon_r2_c8.png",
    "assets/reddit_icons/icon_r2_c5.png",
    "assets/reddit_icons/icon_r4_c3.png",
    "assets/reddit_icons/icon_r5_c6.png",
    "assets/reddit_icons/icon_r3_c3.png",
    "assets/reddit_icons/icon_r3_c5.png",
]


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_heart_outline(draw, cx, cy, size, color, width):
    points = []
    for i in range(100):
        t = 2 * math.pi * i / 100
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        points.append((cx + hx * size / 34, cy - hy * size / 34))
    draw.polygon(points, outline=color, width=width)


def _draw_comment_outline(draw, x, y, w, h, color, width):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h * 0.3, outline=color, width=width)
    tail = [(x + w * 0.22, y + h * 0.92), (x + w * 0.22, y + h * 1.3), (x + w * 0.48, y + h * 0.92)]
    draw.polygon(tail, fill=color)
    draw.rectangle([x + w * 0.22, y + h * 0.9, x + w * 0.5, y + h * 0.98], fill="white")
    draw.line([(x + w * 0.22, y + h * 0.92), (x + w * 0.22, y + h * 1.28)], fill=color, width=width)
    draw.line([(x + w * 0.22, y + h * 1.28), (x + w * 0.46, y + h * 0.94)], fill=color, width=width)


def _draw_share_icon(draw, x, y, size, color, width):
    box_y = y + size * 0.35
    draw.rounded_rectangle(
        [x, box_y, x + size, y + size], radius=size * 0.15, outline=color, width=width
    )
    cx = x + size / 2
    draw.line([(cx, y), (cx, box_y + size * 0.15)], fill=color, width=width)
    draw.polygon(
        [(cx - size * 0.22, y + size * 0.22), (cx + size * 0.22, y + size * 0.22), (cx, y)],
        outline=color,
        width=width,
    )


def _draw_checkmark(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CHECKMARK_BLUE)
    draw.line(
        [(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.55, cy - r * 0.4)],
        fill="white",
        width=max(2, r // 4),
        joint="curve",
    )


def render_card(
    title: str,
    username: str = "StoryHub",
    card_width: int = 900,
    award_icons: list[str] | None = DEFAULT_AWARD_ICONS,
) -> np.ndarray:
    """Render the hook card and return it as an RGBA numpy array sized to its own content.

    award_icons: image file paths drawn in a row below the username. Defaults to a curated
    set of Reddit-style award icons; pass an empty list to fall back to plain emoji reactions.
    """
    title_font = ImageFont.truetype(FONT_BOLD, 42)
    username_font = ImageFont.truetype(FONT_BOLD, 34)
    meta_font = ImageFont.truetype(FONT_BOLD, 28)
    emoji_font = ImageFont.truetype(EMOJI_FONT, 30)

    probe = Image.new("RGBA", (card_width, 10))
    probe_draw = ImageDraw.Draw(probe)
    inner_width = card_width - 2 * CARD_PADDING - AVATAR_SIZE - 20
    title_lines = _wrap_text(probe_draw, title, title_font, inner_width)

    header_h = AVATAR_SIZE
    reactions_h = 44
    title_h = len(title_lines) * (title_font.size + 10)
    footer_h = 40
    card_height = CARD_PADDING * 2 + header_h + 12 + reactions_h + title_h + 16 + footer_h

    pad = 40
    canvas = Image.new("RGBA", (card_width + pad * 2, int(card_height) + pad * 2), (0, 0, 0, 0))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [pad, pad, pad + card_width, pad + card_height], radius=CARD_RADIUS, fill=(0, 0, 0, 110)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.alpha_composite(canvas, shadow)

    card = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle(
        [pad, pad, pad + card_width, pad + card_height], radius=CARD_RADIUS, fill=(255, 255, 255, 255)
    )

    x = pad + CARD_PADDING
    y = pad + CARD_PADDING

    avatar_colors = [(255, 107, 107), (78, 205, 196), (69, 183, 209), (155, 89, 182)]
    avatar_color = avatar_colors[len(username) % len(avatar_colors)]
    draw.ellipse([x, y, x + AVATAR_SIZE, y + AVATAR_SIZE], fill=avatar_color)
    draw.text(
        (x + AVATAR_SIZE / 2, y + AVATAR_SIZE / 2 - 6),
        "\U0001F4D6",
        font=emoji_font,
        anchor="mm",
        embedded_color=True,
    )

    name_x = x + AVATAR_SIZE + 18
    draw.text((name_x, y + 12), username, font=username_font, fill=(30, 30, 30))
    name_w = draw.textlength(username, font=username_font)
    _draw_checkmark(draw, name_x + name_w + 22, y + 12 + username_font.size / 2, 14)

    reaction_y = y + AVATAR_SIZE + 4
    if award_icons:
        icon_x = x
        icon_size = 40
        for icon_path in award_icons:
            award_img = Image.open(icon_path).convert("RGBA").resize((icon_size, icon_size))
            card.alpha_composite(award_img, (int(icon_x), int(reaction_y)))
            icon_x += icon_size + 6
    else:
        draw.text((x, reaction_y), REACTION_EMOJIS, font=emoji_font, fill=(0, 0, 0), embedded_color=True)

    title_y = reaction_y + reactions_h
    for line in title_lines:
        draw.text((x, title_y), line, font=title_font, fill=TITLE_COLOR)
        title_y += title_font.size + 10

    footer_y = title_y + 12
    icon_h = 26
    _draw_heart_outline(draw, x + icon_h * 0.55, footer_y + icon_h * 0.5, icon_h, ICON_COLOR, 3)
    draw.text((x + icon_h + 14, footer_y), "99+", font=meta_font, fill=META_COLOR)

    comment_x = x + 110
    _draw_comment_outline(draw, comment_x, footer_y, icon_h * 1.1, icon_h * 0.85, ICON_COLOR, 3)
    draw.text((comment_x + icon_h * 1.1 + 18, footer_y), "99+", font=meta_font, fill=META_COLOR)

    share_x = x + 220
    _draw_share_icon(draw, share_x, footer_y - 2, icon_h, ICON_COLOR, 3)
    draw.text((share_x + icon_h + 10, footer_y), "Share", font=meta_font, fill=META_COLOR)

    card = Image.alpha_composite(canvas, card)
    return np.array(card)
