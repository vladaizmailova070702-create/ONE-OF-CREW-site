"""Export the approved aura detail story with quiet editorial typography."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/originals/events/lady-style-motion-aura-detail.png"
OUTPUT = ROOT / "assets/web/vk-ads/lady-style-motion-aura-detail-story-9x16.jpg"
W, H = 1080, 1920
BLACK = (17, 17, 17)
IVORY = (245, 242, 236)
RED = (241, 43, 43)
FONTS = Path("C:/Windows/Fonts")


def face(filename, size):
    return ImageFont.truetype(str(FONTS / filename), size)


def render():
    source = Image.open(SOURCE).convert("RGB")
    canvas = source.resize((W, H), Image.Resampling.LANCZOS)

    # Let the approved shoulder, arm and hip remain the image's focal point.
    veil = Image.new("RGBA", (W, 1390), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for x in range(700):
        alpha = round(42 * (1 - x / 700))
        vd.line((x, 0, x, 1390), fill=(0, 0, 0, alpha))
    canvas.paste(veil, (0, 0), veil)
    draw = ImageDraw.Draw(canvas)

    def put(x, y, value, filename, size, color=IVORY):
        draw.text((x, y), value, font=face(filename, size), fill=color, anchor="lt")

    logo = Image.open(ROOT / "brand_assets/web/logo.png").convert("RGBA")
    logo.thumbnail((270, 75), Image.Resampling.LANCZOS)
    canvas.paste(logo, (73, 248), logo)

    put(66, 354, "Lady", "GARA.TTF", 194)
    put(124, 528, "Style", "GARAIT.TTF", 211)
    put(70, 737, "25+", "GARA.TTF", 109, RED)
    draw.line((70, 854, 485, 854), fill=RED, width=2)

    put(70, 882, "ДЛЯ ДЕВУШЕК И ЖЕНЩИН", "segoeui.ttf", 30)
    put(70, 936, "НАБОР В ГРУППУ С НУЛЯ", "seguisb.ttf", 33)
    put(70, 1020, "Ознакомительная", "GARAIT.TTF", 54)
    put(70, 1080, "тренировка", "GARAIT.TTF", 75)
    put(70, 1207, "с Ольгой Шах · в студии", "segoeui.ttf", 32)

    draw.rectangle((0, 1390, W, 1650), fill=BLACK)
    draw.line((70, 1391, 1010, 1391), fill=IVORY, width=2)
    put(70, 1410, "18 октября", "GARA.TTF", 62)
    put(630, 1418, "18:00–19:30", "segoeui.ttf", 40)
    put(70, 1480, "800", "GARA.TTF", 67, RED)
    put(180, 1478, "₽", "segoeui.ttf", 66, RED)
    put(338, 1480, "Хабаровск · Комсомольская, 78", "segoeui.ttf", 29)
    put(338, 1522, "3 этаж · офис 307", "segoeui.ttf", 29)
    put(70, 1565, "ЗАПИСЬ", "segoeui.ttf", 24)
    put(70, 1592, "+7 900 415-37-63", "seguisb.ttf", 49)
    put(580, 1600, "MAX · Telegram · WhatsApp", "segoeui.ttf", 26)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, "JPEG", quality=88, subsampling=0, optimize=True)
    print(f"{SOURCE.name}: {source.size}, {SOURCE.stat().st_size} B")
    print(f"{OUTPUT.name}: {canvas.size}, {OUTPUT.stat().st_size} B")


if __name__ == "__main__":
    render()
