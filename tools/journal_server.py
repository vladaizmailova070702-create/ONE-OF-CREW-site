"""Локальный сервер журнала ONE OF.

Раздаёт файлы проекта на http://127.0.0.1:8123/ — журнал открывается
по адресу http://127.0.0.1:8123/journal/.

Запускается под pythonw.exe, то есть без окна консоли. Поэтому лог
запросов отключён: под pythonw потока ошибок не существует, и встроенное
логирование http.server роняло бы каждый запрос.

Слушает только 127.0.0.1 — из локальной сети и из интернета сервер
недоступен, брандмауэр ничего не спрашивает.
"""

import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8123
HOST = "127.0.0.1"

# корень раздачи — папка проекта, то есть родительская для tools/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) > 1:
    ROOT = sys.argv[1]


class Handler(SimpleHTTPRequestHandler):
    # типы, которые Windows по умолчанию отдаёт как octet-stream:
    # с ними приложение не установилось бы значком
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        ".webmanifest": "application/manifest+json",
        ".js": "text/javascript",
        ".json": "application/json",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, *args):
        pass  # под pythonw писать некуда

    def _redirected(self):
        """Держим всех на одном адресе — http://localhost:8123.

        Браузер хранит записи журнала отдельно для localhost и для
        127.0.0.1: это разные адреса, и на втором журнал выглядит
        пустым. Поэтому со второго уводим на первый.
        """
        # ?keep — не уводить: нужен, чтобы заглянуть в записи, случайно
        # оставшиеся на старом адресе, и выгрузить их копией
        if "keep" in self.path:
            return False
        host = (self.headers.get("Host") or "").split(":")[0]
        if host in ("127.0.0.1", "::1", "[::1]"):
            self.send_response(302)
            self.send_header("Location", "http://localhost:%d%s" % (PORT, self.path))
            self.end_headers()
            return True
        return False

    def do_GET(self):
        if self._redirected():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._redirected():
            return
        super().do_HEAD()

    def end_headers(self):
        # журнал правится часто — пусть браузер не держит старую версию
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    if not os.path.isfile(os.path.join(ROOT, "journal", "index.html")):
        return 2
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        return 1  # порт занят — вероятно, сервер уже запущен
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
