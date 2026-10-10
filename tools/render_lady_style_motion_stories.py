"""Export three Lady Style story posters with exact, editable event typography."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets/originals/events"
OUTPUT_DIR = ROOT / "assets/web/vk-ads"
W, H = 1080, 1920
BLACK = (17, 17, 17)
IVORY = (245, 242, 236)
RED = (241, 43, 43)

VARIANTS = (
    ("jazz-funk", 0, 95),
    ("heels", 245, 105),
    ("fusion", 245, 190),
)


def font(size, bold=True):
    name = "ARIALNB.TTF" if bold else "ARIALN.TTF"
    return ImageFont.truetype("C:/Windows/Fonts/" + name, size)


def render(name, upward_shift, scrim_strength):
    source_name = "heels-denim" if name == "heels" else name
    original = SOURCE_DIR / f"lady-style-motion-{source_name}.png"
    source = Image.open(original).convert("RGB")
    photo = source.resize((W, H), Image.Resampling.LANCZOS)
    if upward_shift:
        shifted = Image.new("RGB", (W, H), BLACK)
        shifted.paste(photo, (0, -upward_shift))
        blend = Image.new("L", (W, H), 255)
        bd = ImageDraw.Draw(blend)
        for y in range(1500, 1751):
            alpha = round(255 * (1750 - y) / 250)
            bd.line((0, y, W, y), fill=max(0, alpha))
        bd.rectangle((0, 1751, W, H), fill=0)
        canvas = Image.composite(shifted, photo, blend)
    else:
        canvas = photo.copy()

    # Keep display text crisp over movement without covering the dancer.
    veil = Image.new("RGBA", (W, 1390), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for x in range(W):
        fade = max(0.0, 1.0 - x / 775)
        alpha = round(scrim_strength * fade)
        vd.line((x, 0, x, 1390), fill=(0, 0, 0, alpha))
    canvas.paste(veil, (0, 0), veil)
    draw = ImageDraw.Draw(canvas)

    def put(x, y, value, size, color=IVORY, bold=True):
        draw.text((x, y), value, font=font(size, bold), fill=color, anchor="lt")

    logo = Image.open(ROOT / "brand_assets/web/logo.png").convert("RGBA")
    logo.thumbnail((285, 75), Image.Resampling.LANCZOS)
    canvas.paste(logo, (72, 246), logo)

    put(67, 365, "LADY", 180)
    put(67, 517, "STYLE", 180)
    put(67, 681, "25+", 157, RED)
    draw.rectangle((70, 849, 453, 855), fill=RED)
    put(70, 876, "ДЛЯ ДЕВУШЕК И ЖЕНЩИН", 35)
    put(70, 928, "НАБОР В ГРУППУ", 50)
    put(70, 992, "С НУЛЯ", 75, RED)
    put(70, 1085, "ОЗНАКОМИТЕЛЬНАЯ", 38)
    put(70, 1137, "ТРЕНИРОВКА", 58)
    put(70, 1219, "С ОЛЬГОЙ ШАХ · В СТУДИИ", 34)

    # Compact info field keeps both the event offer and the contact in the safe area.
    draw.rectangle((0, 1390, W, 1650), fill=BLACK)
    draw.rectangle((70, 1390, 1010, 1396), fill=RED)
    put(70, 1407, "18 ОКТЯБРЯ", 57)
    put(608, 1415, "18:00–19:30", 45)
    put(70, 1474, "800", 65, RED)
    draw.text(
        (196, 1474),
        "₽",
        font=ImageFont.truetype("C:/Windows/Fonts/DejaVuSans-Bold.ttf", 60),
        fill=RED,
        anchor="lt",
    )
    put(338, 1480, "ХАБАРОВСК · КОМСОМОЛЬСКАЯ, 78", 31)
    put(338, 1518, "3 ЭТАЖ · ОФИС 307", 31)
    put(70, 1559, "ЗАПИСЬ", 27)
    put(70, 1587, "+7 900 415-37-63", 54)
    put(580, 1600, "MAX · Telegram · WhatsApp", 27, IVORY, False)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"lady-style-motion-{name}-story-9x16.jpg"
    canvas.save(output, "JPEG", quality=88, subsampling=0, optimize=True)
    print(f"{original.name}: {source.size}, {original.stat().st_size} B")
    print(f"{output.name}: {canvas.size}, {output.stat().st_size} B")


if __name__ == "__main__":
    for variant in VARIANTS:
        render(*variant)
