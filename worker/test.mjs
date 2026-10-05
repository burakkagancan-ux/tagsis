// Worker'ın yerel testi: node worker/test.mjs  (Vision ve rate limit taklit edilir)
import w from "./src/index.js";
const ORIGIN = "https://burakkagancan-ux.github.io";
let calls = 0, visionReply = () => ({ status: 200, body: { responses: [{ fullTextAnnotation: { text: "Aqua, Glycerin" } }] } });
globalThis.fetch = async (url, opt) => { calls++; const v = visionReply(url, opt); return new Response(JSON.stringify(v.body), { status: v.status }); };
const lim = n => { let c = 0; return { limit: async () => ({ success: ++c <= n }) }; };
const env = () => ({ VISION_KEY: "k", ALLOWED_ORIGIN: ORIGIN, IP_LIMIT: lim(6), GLOBAL_LIMIT: lim(30) });
const img = "/9j/" + "A".repeat(200);
const req = (body, o = {}) => new Request("https://x.workers.dev/", { method: o.method || "POST", headers: { "Content-Type": "application/json", "Origin": o.origin ?? ORIGIN, "CF-Connecting-IP": "1.2.3.4", ...(o.h || {}) }, body: o.method === "OPTIONS" || o.method === "GET" ? undefined : body });
let fail = 0;
async function t(name, r, e, status, check) {
  const res = await w.fetch(r, e); const txt = await res.text(); let j = {}; try { j = JSON.parse(txt); } catch {}
  const ok = res.status === status && (!check || check(j, res));
  if (!ok) { fail++; console.log("HATA", name, res.status, txt); } else console.log("ok  ", name, res.status, j.error || j.text || "");
}
await t("başarılı okuma", req(JSON.stringify({ image: img })), env(), 200, j => j.text === "Aqua, Glycerin");
await t("CORS başlığı", req(JSON.stringify({ image: img })), env(), 200, (j, r) => r.headers.get("Access-Control-Allow-Origin") === ORIGIN);
await t("ön kontrol (OPTIONS)", req(null, { method: "OPTIONS" }), env(), 204);
await t("yabancı köken", req(JSON.stringify({ image: img }), { origin: "https://evil.example" }), env(), 403);
await t("GET reddi", req(null, { method: "GET" }), env(), 405);
await t("bozuk JSON", req("{x"), env(), 400);
await t("resim değil", req(JSON.stringify({ image: "SGVsbG8".repeat(30) })), env(), 415);
await t("çok büyük", req(JSON.stringify({ image: "/9j/" + "A".repeat(4_100_000) })), env(), 413);
{ const e = env(); for (let i = 0; i < 6; i++) await w.fetch(req(JSON.stringify({ image: img })), e); await t("IP sınırı (7. istek)", req(JSON.stringify({ image: img })), e, 429, (j, r) => r.headers.get("Retry-After") === "60"); }
{ const e = env(); e.IP_LIMIT = lim(1000); for (let i = 0; i < 30; i++) await w.fetch(req(JSON.stringify({ image: img })), e); await t("genel sınır (31. istek)", req(JSON.stringify({ image: img })), e, 429); }
visionReply = () => ({ status: 429, body: { error: { status: "RESOURCE_EXHAUSTED" } } });
await t("Vision kotası doldu", req(JSON.stringify({ image: img })), env(), 429);
visionReply = () => ({ status: 400, body: { responses: [{ error: { message: "API key not valid" } }] } });
await t("Vision hatası mesajı iletilir", req(JSON.stringify({ image: img })), env(), 502, j => j.error === "OCR hatası: API key not valid");
{ const e = env(); e.ALLOWED_ORIGIN = "http://localhost:8765, " + ORIGIN; visionReply = () => ({ status: 200, body: { responses: [{ fullTextAnnotation: { text: "x" } }] } });
  await t("birden çok köken", req(JSON.stringify({ image: img }), { origin: "http://localhost:8765" }), e, 200, (j, r) => r.headers.get("Access-Control-Allow-Origin") === "http://localhost:8765"); }
{ const e = env(); delete e.VISION_KEY; visionReply = () => ({ status: 200, body: {} }); await t("anahtar yok", req(JSON.stringify({ image: img })), e, 500); }
// Paylaşım sayacı
const kv = () => { const m = new Map(); return { m, get: async (k) => m.get(k) ?? null, put: async (k, v) => { m.set(k, v); }, list: async ({ prefix }) => ({ keys: [...m.keys()].filter((k) => k.startsWith(prefix)).map((name) => ({ name })) }) }; };
const sreq = (q, o = {}) => new Request("https://x.workers.dev/sayac" + q, { method: o.method || "POST", headers: { "Origin": o.origin ?? ORIGIN, "CF-Connecting-IP": "1.2.3.4" } });
{ const e = env(); const before = calls; await t("sayaç bağlı değil: 204", sreq("?t=s"), e, 204); if (calls !== before) { fail++; console.log("HATA sayaç Vision'a gitti"); } }
{ const e = env(); e.SAYAC = kv(); await w.fetch(sreq("?t=s"), e); await w.fetch(sreq("?t=s"), e); await w.fetch(sreq("?t=d"), e);
  const gun = new Date().toISOString().slice(0, 10);
  await t("sayaç artar (2 paylaşım, 1 indirme)", sreq("", { method: "GET" }), e, 200, (j) => j.gunler[gun].s === 2 && j.gunler[gun].d === 1);
  if ([...e.SAYAC.m.keys()].some((k) => !/^g:\d{4}-\d{2}-\d{2}:[sd]$/.test(k))) { fail++; console.log("HATA sayaç anahtarı yalnızca gün + tür olmalı"); }
  await t("sayaç: yabancı köken sayılmaz", sreq("?t=s", { origin: "https://evil.example" }), e, 403);
  await t("sayaç: bilinmeyen tür s sayılır", sreq("?t=<x>"), e, 204, () => e.SAYAC.m.get("g:" + gun + ":s") === "3"); }
{ const e = env(); e.SAYAC = kv(); e.SAYAC_LIMIT = lim(10); for (let i = 0; i < 10; i++) await w.fetch(sreq("?t=s"), e); await t("sayaç IP sınırı (11. istek)", sreq("?t=s"), e, 429); }
console.log(fail ? fail + " hata" : "tüm testler geçti");
process.exit(fail ? 1 : 0);
