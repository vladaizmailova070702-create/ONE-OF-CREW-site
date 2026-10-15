"""Render Sunday master-class ads from a generated studio photograph."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/originals/events/lady-style-sunday-dance.png"
OUT = ROOT / "assets/web/vk-ads"
LOGO = ROOT / "brand_assets/web/logo.png"
FONTS = Path("C:/Windows/Fonts")
CREAM = (249, 243, 234)
RED = (241, 47, 52)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def line(draw, text, x, y, name, size, color=CREAM, max_width=None):
    if max_width:
        while draw.textbbox((0, 0), text, font=font(name, size))[2] > max_width:
            size -= 1
    draw.text((x, y), text, font=font(name, size), fill=color, anchor="lt")


def base(width, height, crop_box):
    source = Image.open(SOURCE).convert("RGB")
    canvas = source.crop(crop_box).resize((width, height), Image.Resampling.LANCZOS)
    shade = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for x in range(width):
        alpha = int(160 * max(0, 1 - x / (width * 0.79)))
        d.line((x, 0, x, height), fill=(0, 0, 0, alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shade)
    return canvas


def add_logo(canvas, xy, max_size):
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail(max_size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, xy)


def render_tiktok(source):
    w, h = 1080, 1920
    canvas = base(w, h, (0, 0, source.width, source.height))
    add_logo(canvas, (74, 208), (245, 76))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 326, 632, 398), radius=7, fill=RED)
    line(d, "УЖЕ В ЭТО ВОСКРЕСЕНЬЕ", 94, 340, "seguisb.ttf", 39, (255, 255, 255), 515)
    line(d, "LADY", 62, 444, "GARA.TTF", 164)
    line(d, "STYLE", 62, 607, "GARA.TTF", 164)
    line(d, "25+", 70, 789, "GARA.TTF", 108, RED)
    d.line((74, 918, 540, 918), fill=CREAM, width=2)
    line(d, "МАСТЕР-КЛАСС С ОЛЬГОЙ ШАХ", 74, 948, "seguisb.ttf", 31, max_width=590)
    line(d, "Можно без опыта", 74, 1004, "segoeui.ttf", 37)

    d.rounded_rectangle((48, 1124, 802, 1518), radius=9, fill=(12, 10, 10, 225), outline=(163, 55, 57, 255), width=2)
    line(d, "18 ОКТЯБРЯ  •  18:00–19:30", 78, 1149, "seguisb.ttf", 42, max_width=695)
    line(d, "800 ₽", 78, 1217, "seguisb.ttf", 62, RED)
    line(d, "Хабаровск · Комсомольская, 78", 78, 1304, "segoeui.ttf", 32, max_width=685)
    line(d, "3 этаж, офис 307", 78, 1355, "segoeui.ttf", 32)
    d.line((78, 1414, 756, 1414), fill=RED, width=3)
    line(d, "ЗАПИСЬ  +7 900 415-37-63", 78, 1432, "seguisb.ttf", 39, max_width=685)
    return canvas.convert("RGB")


def render_telegram(source):
    w, h = 1080, 1350
    # Crop away the emptiest upper and lower edges; keep the dancer in frame.
    canvas = base(w, h, (0, 220, source.width, 1397))
    add_logo(canvas, (62, 80), (225, 70))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((58, 173, 661, 246), radius=7, fill=RED)
    line(d, "УЖЕ В ЭТО ВОСКРЕСЕНЬЕ", 80, 187, "seguisb.ttf", 42, (255, 255, 255), 555)
    line(d, "LADY", 48, 283, "GARA.TTF", 156)
    line(d, "STYLE", 48, 443, "GARA.TTF", 156)
    line(d, "25+", 58, 624, "GARA.TTF", 100, RED)
    line(d, "Мастер-класс · можно без опыта", 62, 751, "seguisb.ttf", 31, max_width=765)

    d.rounded_rectangle((45, 832, 1035, 1271), radius=9, fill=(12, 10, 10, 231), outline=(163, 55, 57, 255), width=2)
    line(d, "18 ОКТЯБРЯ  ·  18:00–19:30", 72, 861, "seguisb.ttf", 47, max_width=930)
    line(d, "800 ₽", 72, 933, "seguisb.ttf", 65, RED)
    line(d, "С Ольгой Шах · Хабаровск", 319, 952, "segoeui.ttf", 34, max_width=680)
    line(d, "Комсомольская, 78 · 3 этаж · офис 307", 72, 1038, "segoeui.ttf", 34, max_width=930)
    d.line((72, 1100, 1005, 1100), fill=RED, width=3)
    line(d, "ЗАПИСАТЬСЯ", 72, 1123, "seguisb.ttf", 35)
    line(d, "+7 900 415-37-63", 72, 1171, "seguisb.ttf", 52)
    line(d, "Telegram · MAX · WhatsApp", 613, 1193, "segoeui.ttf", 28, max_width=390)
    return canvas.convert("RGB")


def main():
    source = Image.open(SOURCE)
    print(f"Source: {source.width}x{source.height}, {SOURCE.stat().st_size} bytes")
    print(f"Logo: {LOGO.stat().st_size} bytes")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rendered in (
        ("lady-style-sunday-tiktok-9x16.jpg", render_tiktok(source)),
        ("lady-style-sunday-telegram-4x5.jpg", render_telegram(source)),
    ):
        path = OUT / name
        rendered.save(path, "JPEG", quality=84, optimize=True, progressive=True, subsampling=0)
        print(f"{path}: {rendered.width}x{rendered.height}, {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
