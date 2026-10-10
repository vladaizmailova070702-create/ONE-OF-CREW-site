from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / 'assets/originals/events'
OUTPUT = ROOT / 'assets/web/vk-ads'
OUTPUT.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1350
BLACK, IVORY, RED = (17, 17, 17), (246, 242, 235), (227, 38, 45)

def typeface(size, bold=True):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('ARIALNB.TTF' if bold else 'ARIALN.TTF'), size)

def write(d, x, y, text, size, color, bold=True):
    d.text((x, y), text, font=typeface(size, bold), fill=color, anchor='lt')

def logo(im, x, y):
    mark = Image.open(ROOT / 'brand_assets/web/logo.png').convert('RGBA')
    mark.thumbnail((250, 70), Image.Resampling.LANCZOS)
    ImageDraw.Draw(im).rectangle((x - 15, y - 9, x + 265, y + 65), fill=BLACK)
    im.paste(mark, (x, y), mark)

def base(filename):
    photo = Image.open(ORIGINALS / filename).convert('RGB')
    photo = photo.resize((W, round(photo.height * W / photo.width)), Image.Resampling.LANCZOS)
    im = Image.new('RGB', (W, H), BLACK)
    im.paste(photo.crop((0, 0, W, 950)), (0, 0))
    return im

def footer(im):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 950, W, H), fill=BLACK)
    d.rectangle((60, 978, 1020, 983), fill=RED)
    write(d, 60, 1010, '18 ОКТЯБРЯ', 68, IVORY)
    write(d, 584, 1025, '18:00–19:30', 50, IVORY)
    write(d, 60, 1097, '800', 69, (255, 74, 79))
    d.text((190, 1095), '₽', font=ImageFont.truetype('C:/Windows/Fonts/DejaVuSans-Bold.ttf', 65), fill=(255, 74, 79), anchor='lt')
    write(d, 329, 1117, 'Комсомольская, 78  ·  3 этаж  ·  офис 307', 31, IVORY)
    d.rectangle((60, 1192, 1020, 1195), fill=(115, 110, 107))
    write(d, 60, 1214, 'ЗАПИСЬ', 30, IVORY)
    write(d, 60, 1250, '+7 900 415-37-63', 55, IVORY)
    write(d, 561, 1260, 'MAX  ·  Telegram  ·  WhatsApp', 30, IVORY, False)

def save(im, filename):
    out = OUTPUT / filename
    im.save(out, 'JPEG', quality=88, subsampling=0, optimize=True)
    print(out.name, out.stat().st_size)

# 05: warm, human movement with the dancer seen only from behind.
im = base('lady-style-faceless-dance.png')
d = ImageDraw.Draw(im)
logo(im, 62, 65)
write(d, 61, 188, 'LADY', 104, BLACK)
write(d, 61, 288, 'STYLE', 104, BLACK)
write(d, 61, 399, '25+', 118, RED)
write(d, 61, 552, 'ЖЕНСТВЕННОСТЬ', 42, BLACK)
write(d, 61, 602, 'В ДВИЖЕНИИ', 49, BLACK)
d.rectangle((61, 696, 460, 754), fill=BLACK)
write(d, 77, 703, 'ГРУППА С НУЛЯ', 39, IVORY)
write(d, 61, 786, 'ОЗНАКОМИТЕЛЬНАЯ', 34, BLACK)
write(d, 61, 830, 'ТРЕНИРОВКА', 51, BLACK)
write(d, 61, 900, 'ДЛЯ ДЕВУШЕК И ЖЕНЩИН', 27, BLACK)
footer(im)
save(im, 'lady-style-intro-variant-05-faceless-4x5.jpg')

# 06: hands and fabric convey femininity without a face or named person.
im = base('lady-style-faceless-red-skirt.png')
d = ImageDraw.Draw(im)
logo(im, 62, 65)
write(d, 61, 192, 'ЖЕНСТВЕННОСТЬ', 47, IVORY)
write(d, 61, 255, 'В ДВИЖЕНИИ', 65, IVORY)
d.rectangle((61, 356, 461, 360), fill=RED)
write(d, 61, 409, 'LADY', 100, IVORY)
write(d, 61, 510, 'STYLE', 100, IVORY)
write(d, 61, 620, '25+', 115, (255, 74, 79))
write(d, 61, 748, 'НАБОР В ГРУППУ С НУЛЯ', 33, IVORY)
write(d, 61, 793, 'ДЛЯ ДЕВУШЕК И ЖЕНЩИН', 29, IVORY)
write(d, 61, 838, 'ОЗНАКОМИТЕЛЬНАЯ', 32, IVORY)
write(d, 61, 878, 'ТРЕНИРОВКА', 49, IVORY)
footer(im)
save(im, 'lady-style-intro-variant-06-faceless-4x5.jpg')
