/* Журнал ONE OF — service worker.
   Держит приложение работоспособным без интернета.
   При изменении файлов приложения поднимите VERSION — иначе у уже
   установленных копий останется старый кэш. */

var VERSION = "journal-v9";
var SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "../brand_assets/web/journal-icon-192.png",
  "../brand_assets/web/journal-icon-512.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(VERSION).then(function (c) {
      // не валим установку, если один файл не отдался
      return Promise.all(SHELL.map(function (u) {
        return c.add(new Request(u, { cache: "reload" })).catch(function () {});
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        return k === VERSION ? null : caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;

  var url = new URL(req.url);

  // запросы синхронизации мимо кэша — всегда в сеть
  if (req.headers.get("X-Journal-Key") || req.headers.get("X-Student-Token")) return;

  // кабинет родителей кэшировать нельзя: он показывает живые долги,
  // а его настройка (config.js) должна читаться свежей
  if (url.pathname.indexOf("/journal/me/") >= 0) return;

  // /sync — сами записи журнала, всегда с сервера
  if (url.pathname === "/sync" || url.pathname === "/sync/") return;

  // страница: сеть вперёд, кэш как запасной вариант
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req).then(function (res) {
        var copy = res.clone();
        caches.open(VERSION).then(function (c) { c.put("./index.html", copy); });
        return res;
      }).catch(function () {
        return caches.match("./index.html").then(function (r) {
          return r || caches.match("./");
        });
      })
    );
    return;
  }

  // шрифты и статика: кэш вперёд, сеть в фоне
  var isFont = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";
  if (isFont || url.origin === self.location.origin) {
    e.respondWith(
      caches.match(req).then(function (hit) {
        var net = fetch(req).then(function (res) {
          if (res && (res.ok || res.type === "opaque")) {
            var copy = res.clone();
            caches.open(VERSION).then(function (c) { c.put(req, copy); });
          }
          return res;
        }).catch(function () { return hit; });
        return hit || net;
      })
    );
  }
});
