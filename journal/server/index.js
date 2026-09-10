/* Журнал ONE OF — функция синхронизации для Yandex Cloud Functions.
 *
 * Хранит один JSON-файл с записями журнала в приватном бакете Object
 * Storage. Приложение забирает его при запуске (GET) и присылает
 * обновлённую копию после каждой правки (POST).
 *
 * Переменные окружения функции:
 *   BUCKET               имя приватного бакета для данных
 *   OBJECT_KEY           имя файла в бакете (по умолчанию journal.json)
 *   JOURNAL_KEY          ключ доступа — его же вписывают в приложении
 *   ALLOW_ORIGIN         откуда пускать (например https://oneofstudio.ru)
 *   AWS_ACCESS_KEY_ID    статический ключ сервисного аккаунта
 *   AWS_SECRET_ACCESS_KEY
 *
 * Инструкция по установке — docs/JOURNAL.md
 */

const crypto = require("crypto");
const { S3Client, GetObjectCommand, PutObjectCommand } = require("@aws-sdk/client-s3");

const s3 = new S3Client({
  region: "ru-central1",
  endpoint: "https://storage.yandexcloud.net"
});

const BUCKET = process.env.BUCKET;
const OBJECT_KEY = process.env.OBJECT_KEY || "journal.json";
const JOURNAL_KEY = process.env.JOURNAL_KEY || "";
const ALLOW_ORIGIN = process.env.ALLOW_ORIGIN || "*";

function cors() {
  return {
    "Access-Control-Allow-Origin": ALLOW_ORIGIN,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Journal-Key",
    "Access-Control-Max-Age": "86400",
    "Cache-Control": "no-store"
  };
}

function reply(statusCode, body) {
  return {
    statusCode: statusCode,
    headers: Object.assign({ "Content-Type": "application/json; charset=utf-8" }, cors()),
    body: JSON.stringify(body)
  };
}

// сравнение за постоянное время, чтобы ключ нельзя было подобрать по задержке
function keyMatches(given) {
  const a = Buffer.from(String(given || ""), "utf8");
  const b = Buffer.from(JOURNAL_KEY, "utf8");
  if (!JOURNAL_KEY || a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

function header(headers, name) {
  if (!headers) return "";
  const want = name.toLowerCase();
  for (const k of Object.keys(headers)) {
    if (k.toLowerCase() === want) return headers[k];
  }
  return "";
}

async function readStored() {
  try {
    const res = await s3.send(new GetObjectCommand({ Bucket: BUCKET, Key: OBJECT_KEY }));
    const text = await res.Body.transformToString("utf-8");
    return JSON.parse(text);
  } catch (e) {
    // файла ещё нет — журнал пустой, это не ошибка
    if (e && (e.name === "NoSuchKey" || e.Code === "NoSuchKey" || e.$metadata?.httpStatusCode === 404)) {
      return null;
    }
    throw e;
  }
}

module.exports.handler = async function (event) {
  const method = (event && (event.httpMethod || event.method) || "GET").toUpperCase();

  if (method === "OPTIONS") {
    return { statusCode: 204, headers: cors(), body: "" };
  }

  if (!BUCKET || !JOURNAL_KEY) {
    return reply(500, { ok: false, error: "Функция не настроена: задайте BUCKET и JOURNAL_KEY." });
  }

  if (!keyMatches(header(event.headers, "X-Journal-Key"))) {
    return reply(401, { ok: false, error: "Неверный ключ доступа." });
  }

  try {
    if (method === "GET") {
      const stored = await readStored();
      if (!stored) return reply(200, { ok: true, updatedAt: 0, data: null });
      return reply(200, { ok: true, updatedAt: stored.updatedAt || 0, data: stored.data || null });
    }

    if (method === "POST") {
      let raw = event.body || "";
      if (event.isBase64Encoded) raw = Buffer.from(raw, "base64").toString("utf-8");

      let incoming;
      try {
        incoming = JSON.parse(raw);
      } catch (e) {
        return reply(400, { ok: false, error: "Тело запроса — не JSON." });
      }
      if (!incoming || typeof incoming !== "object" || !incoming.data) {
        return reply(400, { ok: false, error: "В запросе нет поля data." });
      }

      const payload = {
        updatedAt: Number(incoming.updatedAt) || Date.now(),
        data: incoming.data,
        savedAt: new Date().toISOString()
      };

      await s3.send(new PutObjectCommand({
        Bucket: BUCKET,
        Key: OBJECT_KEY,
        Body: JSON.stringify(payload),
        ContentType: "application/json; charset=utf-8"
      }));

      return reply(200, { ok: true, updatedAt: payload.updatedAt });
    }

    return reply(405, { ok: false, error: "Поддерживаются только GET и POST." });
  } catch (e) {
    console.error(e);
    return reply(500, { ok: false, error: "Хранилище недоступно: " + (e.message || "неизвестная ошибка") });
  }
};
