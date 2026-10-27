"""Render the ONE OF STUDIO rehearsal-types social carousel from archive cutouts."""

from __future__ import annotations

import math
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "originals" / "rehearsal-types"
OUTPUT = ROOT / "assets" / "web" / "rehearsal-types"
JPG_OUTPUT = OUTPUT / "jpg"
PREVIEW = ROOT / "temporary screenshots" / "rehearsal-types-contact.jpg"
LOGO = ROOT / "brand_assets" / "web" / "logo.png"
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_REGULAR = Path("C:/Windows/Fonts/arial.ttf")
WIDTH, HEIGHT = 1080, 1350
INK = "#191816"
RED = "#b5242b"
PAPER = (245, 237, 221)

CARDS = [
    {"number": 1, "slug": "repeat", "source": "01-repeat.png", "title": ["МОЖНО ЕЩЁ РАЗ", "С НАЧАЛА?"], "quote": "«Теперь точно запомню.»", "height": 775, "x": 405, "y": 545},
    {"number": 2, "slug": "learned", "source": "02-learned.png", "title": ["УЖЕ", "ВЫУЧИЛА"], "quote": "«Пока все повторяют, я покажу.»", "height": 830, "x": 430, "y": 495, "tape_top": (0.91, 0.26)},
    {"number": 3, "slug": "face", "source": "03-face.png", "title": ["ТАНЦУЮ", "ЛИЦОМ"], "quote": "«Мой взгляд тоже в хорео.»", "height": 835, "x": 395, "y": 510},
    {"number": 4, "slug": "count", "source": "04-count.png", "title": ["СЧИТАЮ", "ВСЛУХ"], "quote": "«Пять, шесть, семь, восемь!»", "width": 830, "x": 140, "y": 510, "tape_top": (0.86, 0.19)},
    {"number": 5, "slug": "one-more-run", "source": "05-run.png", "title": ["ЕЩЁ ОДИН", "ПРОГОН!"], "quote": "«На этот раз идеально.»", "height": 820, "x": 405, "y": 510},
    {"number": 6, "slug": "improv", "source": "06-improv.png", "title": ["ЗАБЫЛА", "СВЯЗКУ"], "quote": "«Зато импровизация удалась.»", "height": 825, "x": 420, "y": 515, "tape_top": (0.94, 0.18)},
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def base_page() -> Image.Image:
    page = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    # Quiet paper fibers, with enough flat space for bold type to remain crisp.
    texture = Image.effect_noise((WIDTH, HEIGHT), 8).convert("L")
    tint = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    tint.putalpha(texture.point(lambda value: int(value * 0.045)))
    page = Image.alpha_composite(page.convert("RGBA"), tint).convert("RGB")
    return page


def ink_marks(page: Image.Image, variant: int) -> None:
    overlay = Image.new("RGBA", page.size)
    draw = ImageDraw.Draw(overlay)
    points = []
    for x in range(-60, 380, 7):
        y = 1030 + 68 * math.sin(x / 77 + variant * 0.65)
        points.append((x, int(y)))
    draw.line(points, fill=(181, 36, 43, 24), width=4, joint="curve")
    page.paste(overlay, mask=overlay.getchannel("A"))


def logo(page: Image.Image) -> None:
    x, y, w, h = 780, 42, 250, 76
    draw = ImageDraw.Draw(page)
    draw.rectangle((x, y, x + w, y + h), fill=INK)
    draw.rectangle((x, y + h - 5, x + w, y + h), fill=RED)
    source = Image.open(LOGO).convert("RGBA")
    source.thumbnail((218, 61), Image.Resampling.LANCZOS)
    page.paste(source, (x + (w - source.width) // 2, y + 6), source)


def trim_and_gray(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    # Remove faint AI extraction halos; the hard edge is intentional paper cutting.
    alpha = alpha.point(lambda value: 0 if value < 130 else 255)
    bounds = alpha.getbbox()
    if not bounds:
        raise ValueError(f"Empty cutout: {path}")
    image.putalpha(alpha)
    image = image.crop(bounds)
    gray = ImageOps.autocontrast(ImageOps.grayscale(image), cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.10)
    return Image.merge("RGBA", (gray, gray, gray, image.getchannel("A")))


def tape(page: Image.Image, center: tuple[int, int], angle: float, length: int = 105) -> None:
    strip = Image.new("RGBA", (length + 20, 58))
    d = ImageDraw.Draw(strip)
    polygon = [(6, 8), (length + 8, 3), (length + 12, 41), (3, 49)]
    d.polygon(polygon, fill=(255, 252, 238, 245))
    d.line([(17, 16), (length - 5, 13)], fill=(255, 255, 255, 150), width=2)
    rotated = strip.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    shadow = Image.new("RGBA", rotated.size, (48, 38, 32, 0))
    shadow.putalpha(rotated.getchannel("A").filter(ImageFilter.GaussianBlur(8)).point(lambda a: int(a * 0.28)))
    x = int(center[0] - rotated.width / 2)
    y = int(center[1] - rotated.height / 2)
    page.paste(shadow, (x + 5, y + 7), shadow)
    page.paste(rotated, (x, y), rotated)


def collage_person(page: Image.Image, source_name: str, *, x: int, y: int, height: int | None = None, width: int | None = None, tape_angle: float = -19, tape_top: tuple[float, float] | None = None) -> None:
    person = trim_and_gray(SOURCE / source_name)
    if height:
        w = round(person.width * height / person.height)
        person = person.resize((w, height), Image.Resampling.LANCZOS)
    elif width:
        h = round(person.height * width / person.width)
        person = person.resize((width, h), Image.Resampling.LANCZOS)
    else:
        raise ValueError("Height or width required")
    silhouette = person.getchannel("A")
    backing = silhouette.filter(ImageFilter.MaxFilter(39))
    black_layer = Image.new("RGBA", person.size, (17, 17, 17, 0))
    black_layer.putalpha(backing)
    page.paste(black_layer, (x + 11, y + 10), black_layer)
    page.paste(person, (x, y), person)
    top_band = silhouette.crop((0, 20, person.width, min(120, person.height))).getbbox()
    bottom_band = silhouette.crop((0, max(0, person.height - 120), person.width, person.height - 20)).getbbox()
    top_x = (top_band[0] + top_band[2]) // 2 if top_band else person.width // 2
    bottom_x = (bottom_band[0] + bottom_band[2]) // 2 if bottom_band else person.width // 2
    if tape_top:
        tape(page, (x + int(person.width * tape_top[0]), y + int(person.height * tape_top[1])), tape_angle)
    else:
        tape(page, (x + top_x, y + 72), tape_angle)
    tape(page, (x + bottom_x, y + person.height - 60), -tape_angle * 0.8, 85)


def draw_fit_text(page: Image.Image, lines: list[str], top: int, max_width: int = 960, max_size: int = 120) -> int:
    draw = ImageDraw.Draw(page)
    size = max_size
    while size > 70:
        candidate = font(FONT_BOLD, size)
        if all(draw.textbbox((0, 0), line, font=candidate, stroke_width=2)[2] <= max_width for line in lines):
            break
        size -= 2
    face = font(FONT_BOLD, size)
    line_step = int(size * 1.05)
    for line in lines:
        draw.text((64, top), line, font=face, fill=INK, stroke_width=2, stroke_fill=INK)
        top += line_step
    return top


def save(page: Image.Image, stem: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    JPG_OUTPUT.mkdir(parents=True, exist_ok=True)
    webp = OUTPUT / f"{stem}.webp"
    jpg = JPG_OUTPUT / f"{stem}.jpg"
    page.save(webp, "WEBP", quality=82, method=6, exif=b"")
    page.save(jpg, "JPEG", quality=87, optimize=True, progressive=True, exif=b"")
    print(f"{webp.relative_to(ROOT)} {webp.stat().st_size} bytes; {jpg.relative_to(ROOT)} {jpg.stat().st_size} bytes")


def render_card(card: dict) -> Image.Image:
    page = base_page()
    ink_marks(page, card["number"])
    logo(page)
    draw = ImageDraw.Draw(page)
    draw.text((66, 66), f"РЕПЕТИЦИЯ  /  {card['number']:02d}—06", font=font(FONT_BOLD, 27), fill=RED)
    bottom = draw_fit_text(page, card["title"], 154)
    draw.text((69, bottom + 25), card["quote"], font=font(FONT_REGULAR, 43), fill=INK)
    collage_person(page, card["source"], x=card["x"], y=card["y"], height=card.get("height"), width=card.get("width"), tape_angle=-17 if card["number"] % 2 else 21, tape_top=card.get("tape_top"))
    save(page, f"{card['number']:02d}-{card['slug']}")
    return page


def render_cover() -> Image.Image:
    page = base_page()
    ink_marks(page, 0)
    logo(page)
    draw = ImageDraw.Draw(page)
    draw.text((66, 66), "ONE OF STUDIO  /  ХАБАРОВСК", font=font(FONT_BOLD, 27), fill=RED)
    bottom = draw_fit_text(page, ["КАКОЙ ТЫ", "НА РЕПЕТИЦИИ?"], 205, max_size=116)
    draw.text((69, bottom + 17), "ШЕСТЬ ТИПАЖЕЙ. НАЙДИ СЕБЯ.", font=font(FONT_REGULAR, 37), fill=INK)
    collage_person(page, "01-repeat.png", x=5, y=790, height=535, tape_angle=17)
    collage_person(page, "03-face.png", x=339, y=733, height=595, tape_angle=-19)
    collage_person(page, "05-run.png", x=720, y=800, height=525, tape_angle=16)
    draw = ImageDraw.Draw(page)
    draw.rectangle((66, 637, 246, 687), fill=RED)
    draw.text((81, 643), "ЛИСТАЙ →", font=font(FONT_BOLD, 32), fill="#fffaf0")
    save(page, "00-cover")
    return page


def main() -> None:
    pages = [render_cover()] + [render_card(card) for card in CARDS]
    package = OUTPUT / "ONE_OF_STUDIO_rehearsal_types_JPG.zip"
    with ZipFile(package, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(JPG_OUTPUT.glob("*.jpg")):
            archive.write(path, path.name)
    print(f"JPG package: {package.relative_to(ROOT)} {package.stat().st_size} bytes")
    preview = Image.new("RGB", (4 * 270, 2 * 338), (231, 224, 210))
    for index, page in enumerate(pages):
        thumb = page.resize((270, 338), Image.Resampling.LANCZOS)
        preview.paste(thumb, ((index % 4) * 270, (index // 4) * 338))
    PREVIEW.parent.mkdir(exist_ok=True)
    preview.save(PREVIEW, quality=92)
    print(f"Contact sheet: {PREVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
