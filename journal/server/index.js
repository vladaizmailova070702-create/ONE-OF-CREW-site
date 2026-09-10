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
    "Access-Control-Allow-Headers": "Content-Type, X-Journal-Key, X-Student-Token",
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

/* ---------- кабинет ученика ----------
 * Родитель открывает /journal/me/ со своей ссылкой. Токен из неё
 * приходит заголовком X-Student-Token и НЕ попадает в адрес запроса,
 * поэтому не оседает в логах хранилища и CDN.
 *
 * В ответ уходит срез по одному ученику: посещения и деньги за месяц.
 * Ни других учеников, ни телефонов, ни заметок — сюда не попадает
 * ничего, кроме того, что родитель и так знает про своего ребёнка.
 */

const MONTH_NAMES = ["январь","февраль","март","апрель","май","июнь",
                     "июль","август","сентябрь","октябрь","ноябрь","декабрь"];
// предложный падеж — для «в сентябре», а не «в сентябрь»
const MONTH_IN = ["январе","феврале","марте","апреле","мае","июне",
                  "июле","августе","сентябре","октябре","ноябре","декабре"];

// журнал ведут в Хабаровске (UTC+10), функция считает в UTC —
// без сдвига первые часы нового месяца отнеслись бы к прошлому
const TZ_OFFSET_HOURS = Number(process.env.TZ_OFFSET_HOURS || 10);

function pad2(n) { return (n < 10 ? "0" : "") + n; }

function currentMonth() {
  const d = new Date(Date.now() + TZ_OFFSET_HOURS * 3600 * 1000);
  return d.getUTCFullYear() + "-" + pad2(d.getUTCMonth() + 1);
}

function monthLabel(ym) {
  const p = String(ym).split("-");
  return MONTH_NAMES[parseInt(p[1], 10) - 1] + " " + p[0];
}

function monthIn(ym) {
  const p = String(ym).split("-");
  return MONTH_IN[parseInt(p[1], 10) - 1] + " " + p[0];
}

function shiftMonth(ym, back) {
  const p = String(ym).split("-");
  const d = new Date(Date.UTC(+p[0], +p[1] - 1 - back, 1));
  return d.getUTCFullYear() + "-" + pad2(d.getUTCMonth() + 1);
}

function visitDates(sessions, studentId, ym) {
  const out = [];
  for (const k of Object.keys(sessions || {})) {
    const s = sessions[k];
    if (!s || !s.date || String(s.date).slice(0, 7) !== ym) continue;
    if ((s.present || []).indexOf(studentId) >= 0) out.push(s.date);
  }
  return out.sort();
}

function paidIn(payments, studentId, ym) {
  return (payments || []).reduce(function (a, p) {
    return a + (p.studentId === studentId && p.month === ym ? (Number(p.amount) || 0) : 0);
  }, 0);
}

// то же правило, что в приложении: абонемент — фиксированная сумма,
// разовые — цена занятия, умноженная на число посещений
function chargeIn(data, student, ym) {
  const fee = Number(student.fee) || 0;
  if (student.plan === "single") return visitDates(data.sessions, student.id, ym).length * fee;
  return fee;
}

function studentView(data, student) {
  const ym = currentMonth();
  const groups = Array.isArray(data.groups) ? data.groups : [];
  const g = groups.filter(function (x) { return x.id === student.group; })[0] || null;

  const visits = visitDates(data.sessions, student.id, ym);
  const charge = chargeIn(data, student, ym);
  const paid = paidIn(data.payments, student.id, ym);

  const history = [];
  for (let back = 1; back <= 3; back++) {
    const m = shiftMonth(ym, back);
    const c = chargeIn(data, student, m);
    const p = paidIn(data.payments, student.id, m);
    if (c > 0 || p > 0) {
      history.push({ month: m, monthLabel: monthLabel(m), charge: c, paid: p });
    }
  }

  const payments = (data.payments || [])
    .filter(function (p) { return p.studentId === student.id && p.month === ym; })
    .map(function (p) { return { date: p.date, amount: Number(p.amount) || 0, kind: p.kind || "" }; })
    .sort(function (a, b) { return String(a.date).localeCompare(String(b.date)); });

  return {
    ok: true,
    name: student.name || "",
    plan: student.plan === "single" ? "single" : "month",
    group: g ? { name: g.name, time: g.time, meta: g.meta } : null,
    month: ym,
    monthLabel: monthLabel(ym),
    monthIn: monthIn(ym),
    visits: visits,
    charge: charge,
    paid: paid,
    left: Math.max(0, charge - paid),
    payments: payments,
    history: history
  };
}

async function handleStudent(token) {
  // короткий токен — заведомо не наш, отвечаем как на любой неверный
  if (!token || token.length < 16) {
    return reply(404, { ok: false, error: "Ссылка не действует." });
  }
  const stored = await readStored();
  const data = stored && stored.data;
  if (!data || !Array.isArray(data.students)) {
    return reply(404, { ok: false, error: "Ссылка не действует." });
  }
  const student = data.students.filter(function (s) { return s.token && s.token === token; })[0];
  if (!student) {
    return reply(404, { ok: false, error: "Ссылка не действует." });
  }
  return reply(200, studentView(data, student));
}

module.exports.handler = async function (event) {
  const method = (event && (event.httpMethod || event.method) || "GET").toUpperCase();

  if (method === "OPTIONS") {
    return { statusCode: 204, headers: cors(), body: "" };
  }

  if (!BUCKET || !JOURNAL_KEY) {
    return reply(500, { ok: false, error: "Функция не настроена: задайте BUCKET и JOURNAL_KEY." });
  }

  // кабинет родителя — до проверки хозяйского ключа, у него свой
  const studentToken = header(event.headers, "X-Student-Token");
  if (studentToken) {
    if (method !== "GET") {
      return reply(405, { ok: false, error: "Кабинет только читает." });
    }
    try {
      return await handleStudent(String(studentToken));
    } catch (e) {
      console.error(e);
      return reply(500, { ok: false, error: "Не удалось прочитать данные." });
    }
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
