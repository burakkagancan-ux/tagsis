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
//   ALLOWED_ORIGIN  değişken/gizli  https://burakkagancan-ux.github.io (virgülle birden çok adres verilebilir)
//   IP_LIMIT        rate limit      IP başına dakikada en fazla istek (wrangler.toml)
//   GLOBAL_LIMIT    rate limit      tüm kullanıcılar için dakikada en fazla istek (Cloudflare konumu başına)

const MAX_BODY = 4_000_000;          // ~4 MB (eski Worker'la aynı); uygulama 1800 px JPEG gönderir (genelde 0,3-1 MB)
const VISION_TIMEOUT_MS = 20_000;

function origins(env) {
  return (env.ALLOWED_ORIGIN || "").split(",").map((s) => s.trim()).filter(Boolean);
}

function cors(env, origin) {
  const list = origins(env);
  return {
    "Access-Control-Allow-Origin": list.includes(origin) ? origin : list[0] || "",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function reply(env, origin, status, obj, extra) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...cors(env, origin), ...(extra || {}) },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = origins(env).includes(origin);
    const R = (status, obj, extra) => reply(env, origin, status, obj, extra);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: allowed ? 204 : 403, headers: cors(env, origin) });
    }
    if (request.method !== "POST") return R(405, { error: "Yalnızca POST isteği kabul edilir." });
    if (!allowed) return R(403, { error: "Bu adresten istek kabul edilmiyor." });

    // 1) İstek sınırı: önce IP başına, sonra genel sınır
    const ip = request.headers.get("CF-Connecting-IP") || "bilinmiyor";
    if (env.IP_LIMIT) {
      const { success } = await env.IP_LIMIT.limit({ key: "ip:" + ip });
      if (!success) return R(429, { error: "Çok sık okuma yapıldı. Lütfen bir dakika sonra tekrar deneyin." }, { "Retry-After": "60" });
    }
    if (env.GLOBAL_LIMIT) {
      const { success } = await env.GLOBAL_LIMIT.limit({ key: "global" });
      if (!success) return R(429, { error: "Hizmet şu an yoğun. Lütfen biraz sonra tekrar deneyin." }, { "Retry-After": "60" });
    }

    // 2) Boyut ve biçim denetimi
    const len = Number(request.headers.get("Content-Length") || "0");
    if (len > MAX_BODY) return R(413, { error: "Fotoğraf çok büyük. Daha küçük bir alan seçip tekrar deneyin." });
    let raw;
    try { raw = await request.text(); } catch { return R(400, { error: "İstek okunamadı." }); }
    if (raw.length > MAX_BODY) return R(413, { error: "Fotoğraf çok büyük. Daha küçük bir alan seçip tekrar deneyin." });
    let image;
    try { image = JSON.parse(raw).image; } catch { return R(400, { error: "Geçersiz istek." }); }
    if (typeof image !== "string" || image.length < 100) return R(400, { error: "Fotoğraf bulunamadı." });
    // Yalnızca JPEG (/9j/), PNG (iVBOR) ve WebP (UklGR) kabul edilir
    if (!/^(\/9j\/|iVBOR|UklGR)/.test(image) || /[^A-Za-z0-9+/=]/.test(image)) {
      return R(415, { error: "Desteklenmeyen dosya biçimi." });
    }

    if (!env.VISION_KEY) return R(500, { error: "Okuma hizmeti yapılandırılmamış." });

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
        if (code === 429) return R(429, { error: "Okuma kapasitesi doldu. Lütfen daha sonra tekrar deneyin." });
        // Google'ın hata mesajı (ör. "API key not valid") sorun tespiti için iletilir; anahtarı içermez
        const msg = (res.error && res.error.message) || (j.error && j.error.message) || ("HTTP " + r.status);
        return R(502, { error: "OCR hatası: " + String(msg).slice(0, 200) });
      }
      return R(200, { text: (res.fullTextAnnotation && res.fullTextAnnotation.text) || "" });
    } catch (e) {
      return R(504, { error: e && e.name === "AbortError" ? "Okuma zaman aşımına uğradı." : "Okuma hizmetine ulaşılamadı." });
    } finally {
      clearTimeout(timer);
    }
  },
};
