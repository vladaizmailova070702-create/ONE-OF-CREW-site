from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / 'assets/originals/events'
OUTPUT = ROOT / 'assets/web/vk-ads'
OUTPUT.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1350
BLACK, IVORY, RED = (17, 17, 17), (246, 242, 235), (227, 38, 45)

def font(size, bold=True):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('ARIALNB.TTF' if bold else 'ARIALN.TTF'), size)

def draw_text(d, x, y, text, size, color, bold=True):
    d.text((x, y), text, font=font(size, bold), fill=color, anchor='lt')

def logo(canvas, x, y, width=250):
    mark = Image.open(ROOT / 'brand_assets/web/logo.png').convert('RGBA')
    mark.thumbnail((width, 70), Image.Resampling.LANCZOS)
    ImageDraw.Draw(canvas).rectangle((x - 15, y - 9, x + width + 15, y + 65), fill=BLACK)
    canvas.paste(mark, (x, y), mark)

def photograph(filename, height=950):
    im = Image.open(ORIGINALS / filename).convert('RGB')
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.Resampling.LANCZOS)
    return im.crop((0, 0, 1080, height))

def footer(canvas, accent=RED):
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 950, W, H), fill=BLACK)
    d.rectangle((60, 978, 1020, 983), fill=accent)
    draw_text(d, 60, 1010, '18 ОКТЯБРЯ', 68, IVORY)
    draw_text(d, 584, 1025, '18:00–19:30', 50, IVORY)
    draw_text(d, 60, 1097, '800', 69, accent)
    d.text((190, 1095), '₽', font=ImageFont.truetype('C:/Windows/Fonts/DejaVuSans-Bold.ttf', 65), fill=accent, anchor='lt')
    draw_text(d, 329, 1117, 'Комсомольская, 78  ·  3 этаж  ·  офис 307', 31, IVORY)
    d.rectangle((60, 1192, 1020, 1195), fill=(115, 110, 107))
    draw_text(d, 60, 1214, 'ЗАПИСЬ', 30, IVORY)
    draw_text(d, 60, 1250, '+7 900 415-37-63', 55, IVORY)
    draw_text(d, 561, 1260, 'MAX  ·  Telegram  ·  WhatsApp', 30, IVORY, False)

def save(canvas, name):
    out = OUTPUT / name
    canvas.save(out, 'JPEG', quality=88, subsampling=0, optimize=True)
    print(out.name, out.stat().st_size)

# 02: softer studio invitation, portrait left and information right.
im = Image.new('RGB', (W, H), BLACK)
im.paste(photograph('lady-style-intro-olga-blazer.png'), (0, 0))
d = ImageDraw.Draw(im)
logo(im, 721, 68, 250)
draw_text(d, 680, 214, 'LADY', 91, BLACK)
draw_text(d, 680, 309, 'STYLE', 91, BLACK)
draw_text(d, 680, 411, '25+', 112, RED)
d.rectangle((680, 552, 1002, 609), fill=BLACK)
draw_text(d, 696, 560, 'ГРУППА С НУЛЯ', 34, IVORY)
draw_text(d, 680, 646, 'ОЗНАКОМИТЕЛЬНАЯ', 29, BLACK)
draw_text(d, 680, 687, 'ТРЕНИРОВКА', 45, BLACK)
draw_text(d, 680, 782, 'ДЛЯ ДЕВУШЕК', 29, BLACK)
draw_text(d, 680, 819, 'И ЖЕНЩИН', 29, BLACK)
draw_text(d, 680, 865, 'С ОЛЬГОЙ ШАХ', 31, BLACK)
footer(im)
save(im, 'lady-style-intro-variant-02-4x5.jpg')

# 03: performance mood and large direct message.
im = Image.new('RGB', (W, H), BLACK)
im.paste(photograph('lady-style-intro-olga-dance.png'), (0, 0))
d = ImageDraw.Draw(im)
logo(im, 61, 60, 250)
draw_text(d, 60, 145, 'С ОЛЬГОЙ ШАХ', 31, IVORY)
draw_text(d, 60, 185, 'LADY', 107, IVORY)
draw_text(d, 60, 290, 'STYLE', 107, IVORY)
draw_text(d, 60, 403, '25+', 120, (255, 74, 79))
draw_text(d, 60, 549, 'ДЛЯ ДЕВУШЕК И ЖЕНЩИН', 28, IVORY)
draw_text(d, 60, 600, 'НАБОР С НУЛЯ', 46, IVORY)
draw_text(d, 60, 662, 'ОЗНАКОМИТЕЛЬНАЯ', 31, IVORY)
draw_text(d, 60, 706, 'ТРЕНИРОВКА', 50, IVORY)
footer(im, (255, 74, 79))
save(im, 'lady-style-intro-variant-03-4x5.jpg')

# 04: bold red editorial field with a tighter portrait crop.
im = Image.new('RGB', (W, H), IVORY)
portrait = Image.open(ORIGINALS / 'lady-style-intro-olga-portrait.png').convert('RGB')
portrait = portrait.resize((760, round(portrait.height * 760 / portrait.width)), Image.Resampling.LANCZOS)
im.paste(portrait.crop((0, 0, 650, 950)), (430, 0))
d = ImageDraw.Draw(im)
d.rectangle((0, 0, 526, 950), fill=RED)
logo(im, 62, 65, 250)
draw_text(d, 61, 192, 'LADY', 111, IVORY)
draw_text(d, 61, 301, 'STYLE', 111, IVORY)
draw_text(d, 61, 422, '25+', 125, IVORY)
d.rectangle((61, 578, 448, 639), fill=BLACK)
draw_text(d, 78, 586, 'НАБОР С НУЛЯ', 42, IVORY)
draw_text(d, 61, 685, 'ОЗНАКОМИТЕЛЬНАЯ', 32, IVORY)
draw_text(d, 61, 729, 'ТРЕНИРОВКА', 52, IVORY)
draw_text(d, 61, 826, 'ДЛЯ ДЕВУШЕК', 29, IVORY)
draw_text(d, 61, 865, 'И ЖЕНЩИН', 29, IVORY)
draw_text(d, 61, 909, 'С ОЛЬГОЙ ШАХ', 28, IVORY)
footer(im)
save(im, 'lady-style-intro-variant-04-4x5.jpg')
