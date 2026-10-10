from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/originals/events/lady-style-intro-olga-portrait.png'
OUT = ROOT / 'assets/web/vk-ads/lady-style-intro-18-october-4x5.jpg'
W, H = 1080, 1350
IVORY = (246, 242, 235)
BLACK = (17, 17, 17)
RED = (223, 34, 42)

photo = Image.open(SOURCE).convert('RGB')
photo = photo.resize((1080, round(photo.height * 1080 / photo.width)), Image.Resampling.LANCZOS)
canvas = Image.new('RGB', (W, H), BLACK)
canvas.paste(photo.crop((0, 0, 1080, 950)), (0, 0))
d = ImageDraw.Draw(canvas)

def font(size, bold=False, narrow=False):
    name = 'ARIALNB.TTF' if bold and narrow else 'ARIALN.TTF' if narrow else 'arialbd.ttf' if bold else 'arial.ttf'
    return ImageFont.truetype('C:/Windows/Fonts/' + name, size)

def write(x, y, s, size, fill=BLACK, bold=False, narrow=False):
    d.text((x, y), s, font=font(size, bold, narrow), fill=fill, anchor='lt')

# A quiet invitation and a strong, legible hierarchy on the clean side of the portrait.
d.rectangle((60, 62, 340, 137), fill=BLACK)
logo = Image.open(ROOT / 'brand_assets/web/logo.png').convert('RGBA')
logo.thumbnail((240, 59), Image.Resampling.LANCZOS)
canvas.paste(logo, (80, 69), logo)
write(365, 85, 'ХАБАРОВСК', 25, BLACK, True, True)
write(61, 158, 'ДЛЯ ДЕВУШЕК И ЖЕНЩИН', 26, BLACK, True, True)
write(61, 196, 'НАБОР В ГРУППУ', 34, BLACK, True, True)
write(61, 242, 'LADY', 124, BLACK, True, True)
write(61, 358, 'STYLE', 124, BLACK, True, True)
write(61, 479, '25+', 120, RED, True, True)
d.rectangle((62, 640, 458, 699), fill=BLACK)
write(79, 650, 'МОЖНО С НУЛЯ', 39, IVORY, True, True)
write(61, 739, 'ОЗНАКОМИТЕЛЬНАЯ', 35, BLACK, True, True)
write(61, 780, 'ТРЕНИРОВКА', 55, BLACK, True, True)
write(61, 863, 'С ОЛЬГОЙ ШАХ', 31, BLACK, True, True)

# Information panel, spaced for mobile feed legibility.
d.rectangle((0, 950, W, H), fill=BLACK)
d.rectangle((60, 980, 1020, 984), fill=RED)
write(60, 1011, '18 ОКТЯБРЯ', 69, IVORY, True, True)
write(585, 1025, '18:00–19:30', 50, IVORY, True, True)
write(60, 1098, '800', 69, (255, 73, 78), True, True)
d.text((190, 1095), '₽', font=ImageFont.truetype('C:/Windows/Fonts/DejaVuSans-Bold.ttf', 65), fill=(255, 73, 78), anchor='lt')
write(331, 1118, 'Комсомольская, 78  ·  3 этаж  ·  офис 307', 31, IVORY, True, True)
d.rectangle((60, 1194, 1020, 1196), fill=(116, 110, 107))
write(60, 1214, 'ЗАПИСЬ', 31, IVORY, True, True)
write(60, 1250, '+7 900 415-37-63', 55, IVORY, True, True)
write(562, 1260, 'MAX  ·  Telegram  ·  WhatsApp', 30, IVORY, False, True)

OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, 'JPEG', quality=88, subsampling=0, optimize=True)
print(OUT, OUT.stat().st_size)
