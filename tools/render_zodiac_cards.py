"""Render the ONE OF STUDIO zodiac dance image series from generated photos."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "originals" / "zodiac"
OUTPUT = ROOT / "assets" / "web" / "zodiac"
LOGO = ROOT / "brand_assets" / "web" / "logo.png"
PREVIEW = ROOT / "temporary screenshots" / "zodiac-final-contact.jpg"
COVER_PREVIEW = ROOT / "temporary screenshots" / "zodiac-covers-contact.jpg"

CARDS = [
    ("01", "aries", "ОВЕН", "BREAKING"),
    ("02", "taurus", "ТЕЛЕЦ", "LADY STYLE"),
    ("03", "gemini", "БЛИЗНЕЦЫ", "CHOREO"),
    ("04", "cancer", "РАК", "CONTEMPORARY"),
    ("05", "leo", "ЛЕВ", "VOGUE"),
    ("06", "virgo", "ДЕВА", "JAZZ-FUNK"),
    ("07", "libra", "ВЕСЫ", "K-POP COVER DANCE"),
    ("08", "scorpio", "СКОРПИОН", "DANCEHALL"),
    ("09", "sagittarius", "СТРЕЛЕЦ", "HIP-HOP"),
    ("10", "capricorn", "КОЗЕРОГ", "HOUSE"),
    ("11", "aquarius", "ВОДОЛЕЙ", "POPPING"),
    ("12", "pisces", "РЫБЫ", "LYRICAL JAZZ"),
]


def data_url(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


STUDIO_BADGES = {
    "taurus": "ИДЁТ НАБОР В СТУДИИ",
    "gemini": "НАПРАВЛЕНИЕ СТУДИИ",
    "virgo": "ВХОДИТ В CHOREO",
    "libra": "НАПРАВЛЕНИЕ СТУДИИ",
    "sagittarius": "ВХОДИТ В CHOREO",
}


def card_html(photo: Path, number: str, slug: str, sign: str, style: str) -> str:
    badge = STUDIO_BADGES.get(slug)
    badge_html = f'<div class="badge">{badge}</div>' if badge else ""
    sign_size = {"gemini": 122, "scorpio": 112, "aquarius": 114}.get(
        slug, 126 if len(sign) >= 8 else 146
    )
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
    <style>
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1350px; }}
      .card {{ position: relative; width: 1080px; height: 1350px; overflow: hidden;
               background: #f2eee8; color: #171717; font-family: Arial, sans-serif; }}
      .photo {{ position: absolute; width: 100%; height: 100%; object-fit: cover; }}
      .wash {{ position: absolute; inset: 48% 0 0; background: linear-gradient(0deg,
                rgba(248,246,241,.90), rgba(248,246,241,.38) 54%, transparent 100%);
                mask-image: linear-gradient(90deg,#000 0%,#000 46%,transparent 86%); }}
      .brand {{ position: absolute; left: 52px; top: 52px; width: 300px; height: 88px;
                display: flex; align-items: center; justify-content: center;
                background: #171717; border-bottom: 5px solid #b42125; }}
      .brand img {{ width: 252px; height: auto; display: block; }}
      .number {{ position: absolute; right: 54px; top: 65px; font-size: 24px; font-weight: 800;
                 letter-spacing: 2px; color: #a51d22; }}
      .badge {{ position: absolute; left: 58px; bottom: 474px; padding: 12px 18px;
                background: #aa2025; color: #fff; font-size: 23px; line-height: 1;
                font-weight: 900; letter-spacing: .4px; }}
      .copy {{ position: absolute; left: 58px; right: 45px; bottom: 95px; }}
      .eyebrow {{ font-size: 30px; line-height: 1.17; font-weight: 800; letter-spacing: .5px;
                  margin-bottom: 18px; max-width: 760px; }}
      .sign {{ font-family: 'Arial Black', Arial, sans-serif; font-size: {sign_size}px;
               line-height: .94; letter-spacing: -5px; font-weight: 900; white-space: nowrap; }}
      .rule {{ margin-top: 19px; height: 8px; width: 130px; background: #b42125; }}
      .style {{ margin-top: 20px; font-size: 48px; font-weight: 900; letter-spacing: .5px; }}
    </style></head><body>
    <div class="card"><img class="photo" src="{data_url(photo)}"><div class="wash"></div>
    <div class="brand"><img src="{data_url(LOGO)}" alt="ONE OF STUDIO"></div>
    <div class="number">{number} / 12</div>{badge_html}
    <div class="copy"><div class="eyebrow">ТВОЙ СТИЛЬ ТАНЦА<br>ПО ЗНАКУ ЗОДИАКА</div>
    <div class="sign">{sign}</div><div class="rule"></div><div class="style">{style}</div></div>
    </div></body></html>"""


def cover_html(photo: Path, part: int, signs: str) -> str:
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
    <style>
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1350px; }}
      .cover {{ position: relative; width: 1080px; height: 1350px; overflow: hidden;
                background: #f2eee8; color: #171717; font-family: Arial, sans-serif; }}
      .photo {{ position: absolute; width: 100%; height: 100%; object-fit: cover; }}
      .wash {{ position: absolute; inset: 0; background: linear-gradient(90deg,
                rgba(248,246,241,.91), rgba(248,246,241,.78) 32%,
                rgba(248,246,241,.24) 61%, transparent 78%); }}
      .floor-wash {{ position: absolute; inset: 72% 0 0; background: linear-gradient(0deg,
                rgba(248,246,241,.81),transparent); mask-image: linear-gradient(90deg,
                #000 0%, #000 39%, transparent 78%); }}
      .brand {{ position: absolute; left: 52px; top: 52px; width: 300px; height: 88px;
                display: flex; align-items: center; justify-content: center;
                background: #171717; border-bottom: 5px solid #b42125; }}
      .brand img {{ width: 252px; height: auto; display: block; }}
      .part {{ position: absolute; left: 58px; top: 220px; padding: 13px 20px;
               background: #ab2025; color: #fff; font-size: 36px; font-weight: 900; }}
      .title {{ position: absolute; left: 52px; top: 330px; width: 650px;
                font-family: 'Arial Black', Arial, sans-serif; font-size: 80px;
                line-height: .99; letter-spacing: -3px; font-weight: 900; }}
      .range {{ position: absolute; left: 58px; top: 758px; font-size: 36px;
                font-weight: 900; letter-spacing: .4px; }}
      .red-rule {{ position: absolute; left: 58px; top: 825px; width: 150px;
                   height: 8px; background: #b42125; }}
      .contact {{ position: absolute; left: 58px; bottom: 58px; width: 670px;
                  font-weight: 800; }}
      .address {{ font-size: 27px; line-height: 1.2; margin-bottom: 25px; }}
      .contact-row {{ display: flex; align-items: baseline; gap: 18px; margin-top: 12px; }}
      .label {{ width: 160px; color: #a51d22; font-size: 25px; }}
      .value {{ font-size: 32px; }}
    </style></head><body>
    <div class="cover"><img class="photo" src="{data_url(photo)}"><div class="wash"></div>
    <div class="floor-wash"></div><div class="brand"><img src="{data_url(LOGO)}"
    alt="ONE OF STUDIO"></div><div class="part">ЧАСТЬ {part} / 2</div>
    <div class="title">ТВОЙ СТИЛЬ<br>ТАНЦА<br>ПО ЗНАКУ<br>ЗОДИАКА</div>
    <div class="range">{signs}</div><div class="red-rule"></div>
    <div class="contact"><div class="address">ХАБАРОВСК · УЛ. КОМСОМОЛЬСКАЯ, 78</div>
    <div class="contact-row"><span class="label">САЙТ</span>
    <span class="value">oneofstudio.ru</span></div>
    <div class="contact-row"><span class="label">TELEGRAM</span>
    <span class="value">t.me/one_of_studio_khv</span></div></div>
    </div></body></html>"""


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    previews: list[tuple[str, Image.Image]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for number, slug, sign, style in CARDS:
            source = SOURCE / f"{slug}.png"
            if not source.is_file():
                raise FileNotFoundError(source)
            page.set_content(card_html(source, number, slug, sign, style), wait_until="load")
            page.locator(".photo").evaluate("img => img.decode()")
            png = page.locator(".card").screenshot()
            image = Image.open(BytesIO(png)).convert("RGB")
            target = OUTPUT / f"{number}-{slug}.webp"
            image.save(target, format="WEBP", quality=82, method=6, exif=b"")
            previews.append((slug, ImageOps.contain(image, (216, 270))))
            print(f"{target.relative_to(ROOT)}: {target.stat().st_size} bytes")
        cover_previews = []
        for part, signs in [(1, "ОВЕН — ДЕВА"), (2, "ВЕСЫ — РЫБЫ")]:
            source = SOURCE / f"cover-part-{part}.png"
            page.set_content(cover_html(source, part, signs), wait_until="load")
            page.locator(".photo").evaluate("img => img.decode()")
            png = page.locator(".cover").screenshot()
            image = Image.open(BytesIO(png)).convert("RGB")
            target = OUTPUT / f"cover-part-{part}.webp"
            image.save(target, format="WEBP", quality=82, method=6, exif=b"")
            cover_previews.append(ImageOps.contain(image, (432, 540)))
            print(f"{target.relative_to(ROOT)}: {target.stat().st_size} bytes")
        browser.close()

    sheet = Image.new("RGB", (1120, 910), "#ebe9e5")
    draw = ImageDraw.Draw(sheet)
    for index, (sign, image) in enumerate(previews):
        x = 20 + (index % 4) * 280
        y = 12 + (index // 4) * 300
        sheet.paste(image, (x, y + 22))
        draw.text((x, y), sign, fill="#171717")
    PREVIEW.parent.mkdir(exist_ok=True)
    sheet.save(PREVIEW, quality=90)
    print(f"Contact sheet: {PREVIEW.relative_to(ROOT)}")
    cover_sheet = Image.new("RGB", (924, 590), "#ebe9e5")
    for index, image in enumerate(cover_previews):
        cover_sheet.paste(image, (20 + index * 452, 25))
    cover_sheet.save(COVER_PREVIEW, quality=90)
    print(f"Cover sheet: {COVER_PREVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
