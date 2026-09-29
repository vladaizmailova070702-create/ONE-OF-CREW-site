from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/originals/recruitment-posters'
OUT.mkdir(parents=True, exist_ok=True)
WEB = ROOT / 'assets/web/recruitment-posters'
WEB.mkdir(parents=True, exist_ok=True)

S = 2
IVORY = '#F5F2EC'
INK = '#111111'
RED = '#EB2528'
MUTED = '#55514D'
WHITE = '#FFFFFF'
FONT_DIR = Path('C:/Windows/Fonts')
LOGO = Image.open(ROOT / 'brand_assets/web/logo.png').convert('RGBA')

GROUPS = [
    {'title': 'CHOREO 9+', 'age': '9–16 ЛЕТ', 'schedule': 'СР 18:00–19:00  /  ВС 14:00–15:00', 'address': 'УЛ. ИСТОМИНА, 41  ·  СИНИЙ ЗАЛ'},
    {'title': 'CHOREO 16+', 'age': '16–30 ЛЕТ', 'schedule': 'ВС 13:00–15:00', 'address': 'УЛ. КОМСОМОЛЬСКАЯ, 78  ·  3 ЭТАЖ, ОФИС 308'},
    {'title': 'K-POP 12+', 'age': '12–25 ЛЕТ', 'schedule': 'ВС 15:00–17:00', 'address': 'УЛ. КОМСОМОЛЬСКАЯ, 78  ·  3 ЭТАЖ, ОФИС 308'},
    {'title': 'LADY STYLE 25+', 'age': 'ОТ 25 ЛЕТ', 'schedule': 'ВС 18:00–19:30', 'address': 'УЛ. КОМСОМОЛЬСКАЯ, 78  ·  3 ЭТАЖ, ОФИС 307'},
]


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), round(size * S))


def rect(draw, box, fill, width=0, outline=None):
    draw.rectangle(tuple(round(v * S) for v in box), fill=fill, width=round(width * S), outline=outline)


def line(draw, points, fill, width):
    draw.line([(round(x*S), round(y*S)) for x,y in points], fill=fill, width=round(width*S), joint='curve')


def text(draw, value, x, y, size, color, family='arialbd.ttf', max_width=None):
    f = font(family, size)
    if max_width is not None:
        while draw.textlength(value, font=f) > max_width*S and size > 14:
            size -= 1
            f = font(family, size)
    draw.text((round(x*S), round(y*S)), value, font=f, fill=color, anchor='lt')
    return size, draw.textlength(value, font=f)/S


def logo(canvas, x, y, width):
    im = LOGO.copy()
    height = round(width * im.height / im.width)
    im = im.resize((round(width*S), round(height*S)), Image.Resampling.LANCZOS)
    ImageDraw.Draw(canvas).rectangle((round(x*S),round(y*S),round((x+width)*S),round((y+height)*S)), fill=INK)
    canvas.alpha_composite(im, (round(x*S), round(y*S)))
    return height


def make(format_name, width, height, header_y, first_y, row_h, footer_y):
    im = Image.new('RGBA', (width*S, height*S), IVORY)
    d = ImageDraw.Draw(im)

    # A strong cropped diagonal mark ties the layouts to the studio covers.
    line(d, [(width-105, 0), (width-210, header_y+105)], RED, 31)
    line(d, [(width-32, 0), (width-135, header_y+105)], RED, 11)
    logo(im, 55, header_y, 360)
    text(d, 'ХАБАРОВСК  /  ТАНЦЕВАЛЬНАЯ СТУДИЯ', 55, header_y+109, 27, MUTED, 'ARIALN.TTF', width-110)
    text(d, 'НАБОР В ГРУППЫ', 52, header_y+156, 112 if format_name=='post' else 119, INK, 'impact.ttf', width-104)
    rect(d, (55, first_y-25, width-55, first_y-18), RED)

    for i, group in enumerate(GROUPS):
        y=first_y+i*row_h
        if i:
            line(d, [(55,y-14),(width-55,y-14)], '#A9A29A', 2)
        rect(d, (55,y+10,64,y+row_h-34), RED)
        text(d, f'{i+1:02d}', 84, y+5, 28, RED, 'arialbd.ttf')
        title_x=148
        text(d, group['title'], title_x, y+5, 58 if format_name=='post' else 65, INK, 'impact.ttf', width-title_x-66)
        # The age label is on its own line to keep every group title large.
        text(d, group['age'], title_x, y+70, 33 if format_name=='post' else 35, RED, 'arialbd.ttf', width-title_x-66)
        text(d, group['schedule'], title_x, y+108, 35 if format_name=='post' else 38, INK, 'arialbd.ttf', width-title_x-60)
        text(d, group['address'], title_x, y+150, 31 if format_name=='post' else 34, MUTED, 'ARIALNB.TTF', width-title_x-60)

    rect(d, (0,footer_y,width,height), INK)
    rect(d, (55,footer_y+32,64,height-50), RED)
    text(d, 'ЗАПИСЬ ОТКРЫТА', 86, footer_y+23, 58 if format_name=='post' else 66, WHITE, 'impact.ttf', width-140)
    text(d, 'Пиши +79004153763 (WhatsApp, Max, Telegram)', 86, footer_y+102, 35 if format_name=='post' else 39, WHITE, 'arialbd.ttf', width-140)
    text(d, 'oneofstudio.ru', 86, height-44, 23, '#CBC5BD', 'arial.ttf', width-140)
    result=im.convert('RGB').resize((width,height), Image.Resampling.LANCZOS)
    png=OUT / f'group-recruitment-{format_name}.png'
    jpg=OUT / f'group-recruitment-{format_name}.jpg'
    webp=WEB / f'group-recruitment-{format_name}.webp'
    result.save(png, optimize=True)
    result.save(jpg, quality=94, subsampling=0, optimize=True)
    result.save(webp, 'WEBP', quality=84, method=6)
    return {'format':format_name,'size':[width,height],'png_bytes':png.stat().st_size,'jpg_bytes':jpg.stat().st_size,'webp_bytes':webp.stat().st_size}


if __name__ == '__main__':
    data=[make('post',1080,1350,36,340,205,1170),make('story',1080,1920,225,565,248,1635)]
    (OUT/'export-metadata.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False))
