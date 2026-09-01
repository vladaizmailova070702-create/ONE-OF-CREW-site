# -*- coding: utf-8 -*-
"""Рендер афиш ONE OF STUDIO из promo/poster.html в PNG + JPG.

Запуск (из корня проекта, локальный сервер на 8123 должен быть поднят —
см. .claude/launch.json, конфигурация one-of-crew-site):

    python promo/render.py

Форматы:
    poster-post.jpg   1080×1350  — лента VK / Instagram (4:5)
    poster-story.jpg  1080×1920  — сторис (9:16)
"""
import os
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/promo/poster.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
FORMATS = [("post", "", 1080, 1350), ("story", "?f=story", 1080, 1920)]


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        for name, query, w, h in FORMATS:
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg.goto(BASE + query, wait_until="load")
            pg.wait_for_timeout(2500)  # ждём шрифты Google Fonts и фото
            path = os.path.join(OUT, f"poster-{name}.png")  # промежуточный кадр
            pg.locator(".poster").screenshot(path=path)
            pg.close()
            print("rendered", path)
        b.close()

    # JPG-версии для загрузки в соцсети; промежуточный PNG удаляем — он
    # весит в 9 раз больше при неотличимой картинке и не нужен в репозитории.
    from PIL import Image
    for name, _, _, _ in FORMATS:
        src = os.path.join(OUT, f"poster-{name}.png")
        dst = os.path.join(OUT, f"poster-{name}.jpg")
        Image.open(src).convert("RGB").save(dst, "JPEG", quality=90, optimize=True, progressive=True)
        os.remove(src)
        print(f"{os.path.basename(dst)} {round(os.path.getsize(dst)/1024, 1)} KB")


if __name__ == "__main__":
    main()
