"""Локальный сервер журнала ONE OF.

Делает две вещи:

1. Раздаёт приложение на http://localhost:8123/journal/.

2. Хранит записи журнала ФАЙЛОМ на диске и отдаёт их приложению по
   адресу /sync. Это главное: записи перестают зависеть от браузера —
   чистка истории Chrome их больше не уносит, а резервная копия
   становится обычным файлом, который можно скопировать хоть на флешку.

   Файл лежит в  %USERPROFILE%\\OneOfJournal\\journal.json
   (папку можно задать переменной окружения JOURNAL_DATA_DIR).
   Рядом, в backups\\, сервер держит по снимку на день за последний
   месяц.

Запускается под pythonw.exe, то есть без окна консоли. Поэтому лог
запросов отключён: под pythonw потока ошибок не существует, и встроенное
логирование http.server роняло бы каждый запрос.

Слушает только 127.0.0.1 — из локальной сети и из интернета сервер
недоступен, брандмауэр ничего не спрашивает.

Аргументы: journal_server.py [корень раздачи] [порт]
"""

import json
import os
import shutil
import sys
import tempfile
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8123
HOST = "127.0.0.1"

# корень раздачи — папка проекта, то есть родительская для tools/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) > 1:
    ROOT = sys.argv[1]

# второй аргумент — порт: пригодится, чтобы открыть журнал на старом
# адресе и выгрузить записи, оставшиеся там
if len(sys.argv) > 2:
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        pass

DATA_DIR = os.environ.get("JOURNAL_DATA_DIR") or os.path.join(
    os.path.expanduser("~"), "OneOfJournal"
)
DATA_FILE = os.path.join(DATA_DIR, "journal.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
BACKUP_KEEP = 30

# Записи отдаём только своим страницам. Без этой проверки любой сайт,
# открытый в браузере, смог бы вычитать журнал с localhost.
ALLOWED_ORIGINS = {
    "http://localhost:%d" % PORT,
    "http://127.0.0.1:%d" % PORT,
}


def read_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_data(payload):
    """Пишем через временный файл: обрыв записи не оставит огрызок."""
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, prefix=".journal-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_FILE)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    make_backup()


def make_backup():
    """Снимок на каждый день; старше месяца — удаляем."""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d")
        shutil.copyfile(DATA_FILE, os.path.join(BACKUP_DIR, "journal-%s.json" % stamp))
        snaps = sorted(
            n for n in os.listdir(BACKUP_DIR)
            if n.startswith("journal-") and n.endswith(".json")
        )
        for old in snaps[:-BACKUP_KEEP]:
            os.unlink(os.path.join(BACKUP_DIR, old))
    except OSError:
        pass  # снимок — приятное дополнение, из-за него ничего не ломаем


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

    # ---------- записи журнала ----------

    def _origin_ok(self):
        origin = self.headers.get("Origin")
        return origin is None or origin in ALLOWED_ORIGINS

    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        origin = self.headers.get("Origin")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _sync_get(self):
        if not self._origin_ok():
            self._send_json(403, {"ok": False, "error": "Чужая страница."})
            return
        stored = read_data()
        if not stored:
            self._send_json(200, {"ok": True, "updatedAt": 0, "data": None,
                                  "file": DATA_FILE})
            return
        self._send_json(200, {
            "ok": True,
            "updatedAt": stored.get("updatedAt") or 0,
            "data": stored.get("data"),
            "file": DATA_FILE,
        })

    def _sync_post(self):
        if not self._origin_ok():
            self._send_json(403, {"ok": False, "error": "Чужая страница."})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > 32 * 1024 * 1024:
            self._send_json(400, {"ok": False, "error": "Пустой или слишком большой запрос."})
            return
        try:
            incoming = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"ok": False, "error": "Тело запроса — не JSON."})
            return
        if not isinstance(incoming, dict) or not incoming.get("data"):
            self._send_json(400, {"ok": False, "error": "В запросе нет поля data."})
            return
        payload = {
            "updatedAt": incoming.get("updatedAt") or int(time.time() * 1000),
            "data": incoming["data"],
            "savedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        try:
            write_data(payload)
        except OSError as e:
            self._send_json(500, {"ok": False, "error": "Не удалось записать файл: %s" % e})
            return
        self._send_json(200, {"ok": True, "updatedAt": payload["updatedAt"]})

    # ---------- маршрутизация ----------

    def _is_sync(self):
        return self.path.split("?")[0].rstrip("/") == "/sync"

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

    def do_OPTIONS(self):
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
        else:
            self.send_response(403)
            self.end_headers()

    def do_GET(self):
        if self._is_sync():
            self._sync_get()
            return
        if self._redirected():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._redirected():
            return
        super().do_HEAD()

    def do_POST(self):
        if self._is_sync():
            self._sync_post()
            return
        self.send_response(405)
        self.end_headers()

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
