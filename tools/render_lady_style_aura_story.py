from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/originals/events/lady-style-aura-story-background.png'
OUTPUT = ROOT / 'assets/web/vk-ads/lady-style-aura-story-9x16.jpg'
W, H = 1080, 1920
BLACK, IVORY, RED = (17, 17, 17), (245, 242, 236), (241, 43, 43)

source = Image.open(SOURCE).convert('RGB')
canvas = source.resize((W, H), Image.Resampling.LANCZOS)
d = ImageDraw.Draw(canvas)

def face(size, bold=True):
    name = 'ARIALNB.TTF' if bold else 'ARIALN.TTF'
    return ImageFont.truetype('C:/Windows/Fonts/' + name, size)

def put(x, y, value, size, color=IVORY, bold=True):
    d.text((x, y), value, font=face(size, bold), fill=color, anchor='lt')

# Reserve the top 12% and bottom 15% for story interface overlays.
logo = Image.open(ROOT / 'brand_assets/web/logo.png').convert('RGBA')
logo.thumbnail((285, 75), Image.Resampling.LANCZOS)
canvas.paste(logo, (72, 250), logo)

put(67, 367, 'LADY', 180)
put(67, 519, 'STYLE', 180)
put(67, 683, '25+', 157, RED)
d.rectangle((70, 852, 453, 858), fill=RED)
put(70, 881, 'ДЛЯ ДЕВУШЕК И ЖЕНЩИН', 35)
put(70, 933, 'НАБОР В ГРУППУ', 50)
put(70, 997, 'С НУЛЯ', 75, RED)
put(70, 1090, 'ОЗНАКОМИТЕЛЬНАЯ', 38)
put(70, 1142, 'ТРЕНИРОВКА', 58)

# Compact information field leaves the full trouser silhouette visible.
d.rectangle((0, 1390, W, 1650), fill=BLACK)
d.rectangle((70, 1390, 1010, 1396), fill=RED)
put(70, 1407, '18 ОКТЯБРЯ', 57)
put(608, 1415, '18:00–19:30', 45)
put(70, 1474, '800', 65, RED)
d.text((196, 1474), '₽', font=ImageFont.truetype('C:/Windows/Fonts/DejaVuSans-Bold.ttf', 60), fill=RED, anchor='lt')
put(338, 1480, 'ХАБАРОВСК · КОМСОМОЛЬСКАЯ, 78', 31)
put(338, 1518, '3 ЭТАЖ · ОФИС 307', 31)
put(70, 1559, 'ЗАПИСЬ', 27)
put(70, 1587, '+7 900 415-37-63', 54)
put(580, 1600, 'MAX · Telegram · WhatsApp', 27, IVORY, False)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUTPUT, 'JPEG', quality=88, subsampling=0, optimize=True)
print(OUTPUT, OUTPUT.stat().st_size)
