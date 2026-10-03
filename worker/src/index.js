// Etiket Oku OCR Worker'ı (Cloudflare Workers)
// Görev: ocr.html'den gelen fotoğrafı Google Cloud Vision'a gönderip okunan metni döndürmek.
//
// İstek:  POST { "image": "<base64 JPEG/PNG, data: öneki olmadan>" }
// Yanıt:  200 { "text": "..." }  |  4xx/5xx { "error": "Türkçe açıklama" }
//
// Gizlilik: fotoğraf ve okunan metin hiçbir yere yazılmaz, kayda (log) geçirilmez.
//
// Ortam (Cloudflare panelinde / wrangler.toml):
//   VISION_KEY      gizli (secret)  Google Cloud Vision API anahtarı
//   ALLOWED_ORIGIN  değişken        https://burakkagancan-ux.github.io
//   IP_LIMIT        rate limit      IP başına dakikada en fazla istek (wrangler.toml)
//   GLOBAL_LIMIT    rate limit      tüm kullanıcılar için dakikada en fazla istek (Cloudflare konumu başına)

const MAX_BODY = 3_000_000;          // ~3 MB; uygulama 1800 px JPEG gönderir (genelde 0,3-1 MB)
const VISION_TIMEOUT_MS = 20_000;

function cors(env) {
  return {
    "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function reply(env, status, obj, extra) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...cors(env), ...(extra || {}) },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = env.ALLOWED_ORIGIN && origin === env.ALLOWED_ORIGIN;

    if (request.method === "OPTIONS") {
      return new Response(null, { status: allowed ? 204 : 403, headers: cors(env) });
    }
    if (request.method !== "POST") return reply(env, 405, { error: "Yalnızca POST isteği kabul edilir." });
    if (!allowed) return reply(env, 403, { error: "Bu adresten istek kabul edilmiyor." });

    // 1) İstek sınırı: önce IP başına, sonra genel sınır
    const ip = request.headers.get("CF-Connecting-IP") || "bilinmiyor";
    if (env.IP_LIMIT) {
      const { success } = await env.IP_LIMIT.limit({ key: "ip:" + ip });
      if (!success) return reply(env, 429, { error: "Çok sık okuma yapıldı. Lütfen bir dakika sonra tekrar deneyin." }, { "Retry-After": "60" });
    }
    if (env.GLOBAL_LIMIT) {
      const { success } = await env.GLOBAL_LIMIT.limit({ key: "global" });
      if (!success) return reply(env, 429, { error: "Hizmet şu an yoğun. Lütfen biraz sonra tekrar deneyin." }, { "Retry-After": "60" });
    }

    // 2) Boyut ve biçim denetimi
    const len = Number(request.headers.get("Content-Length") || "0");
    if (len > MAX_BODY) return reply(env, 413, { error: "Fotoğraf çok büyük. Daha küçük bir alan seçip tekrar deneyin." });
    let raw;
    try { raw = await request.text(); } catch { return reply(env, 400, { error: "İstek okunamadı." }); }
    if (raw.length > MAX_BODY) return reply(env, 413, { error: "Fotoğraf çok büyük. Daha küçük bir alan seçip tekrar deneyin." });
    let image;
    try { image = JSON.parse(raw).image; } catch { return reply(env, 400, { error: "Geçersiz istek." }); }
    if (typeof image !== "string" || image.length < 100) return reply(env, 400, { error: "Fotoğraf bulunamadı." });
    // Yalnızca JPEG (/9j/), PNG (iVBOR) ve WebP (UklGR) kabul edilir
    if (!/^(\/9j\/|iVBOR|UklGR)/.test(image) || /[^A-Za-z0-9+/=]/.test(image)) {
      return reply(env, 415, { error: "Desteklenmeyen dosya biçimi." });
    }

    if (!env.VISION_KEY) return reply(env, 500, { error: "Okuma hizmeti yapılandırılmamış." });

    // 3) Google Cloud Vision
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), VISION_TIMEOUT_MS);
    try {
      const r = await fetch("https://vision.googleapis.com/v1/images:annotate?key=" + encodeURIComponent(env.VISION_KEY), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requests: [{
            image: { content: image },
            features: [{ type: "DOCUMENT_TEXT_DETECTION" }],
            imageContext: { languageHints: ["tr", "en"] },
          }],
        }),
        signal: ctrl.signal,
      });
      const j = await r.json().catch(() => ({}));
      const res = (j.responses && j.responses[0]) || {};
      if (!r.ok || res.error) {
        const code = r.status === 429 || (j.error && j.error.status === "RESOURCE_EXHAUSTED") ? 429 : 502;
        return reply(env, code, { error: code === 429 ? "Günlük okuma kapasitesi doldu. Lütfen daha sonra tekrar deneyin." : "Okuma hizmetinde geçici bir sorun var." });
      }
      return reply(env, 200, { text: (res.fullTextAnnotation && res.fullTextAnnotation.text) || "" });
    } catch (e) {
      return reply(env, 504, { error: e && e.name === "AbortError" ? "Okuma zaman aşımına uğradı." : "Okuma hizmetine ulaşılamadı." });
    } finally {
      clearTimeout(timer);
    }
  },
};
