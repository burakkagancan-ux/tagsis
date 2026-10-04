const CACHE = "tagsis-v7";
// Uygulamanın çevrimdışı da açılabilmesi için ilk kurulumda önbelleğe alınan dosyalar
const CORE = [
  "./", "index.html", "ocr.html", "manifest.webmanifest",
  "js/ortak.js", "js/gida.js", "js/kozmetik.js", "js/eslesme.js", "js/temizlik.js",
  "js/arayuz.js", "js/arayuz_kozmetik.js", "js/arayuz_temizlik.js", "js/arayuz_sayfa.js",
  "icon-192.png", "icon-512.png", "apple-touch-icon.png",
  "data/tagsis.json", "data/durum.json", "data/arsiv.json", "data/e_kodlari.json", "data/bilesenler.json", "data/e_aciklama.json",
  "fonts/fonts.css", "fonts/schibsted-grotesk-latin-400-normal.woff2", "fonts/schibsted-grotesk-latin-ext-400-normal.woff2",
  "fonts/schibsted-grotesk-latin-600-normal.woff2", "fonts/schibsted-grotesk-latin-ext-600-normal.woff2",
  "fonts/schibsted-grotesk-latin-800-normal.woff2", "fonts/schibsted-grotesk-latin-ext-800-normal.woff2",
];
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.all(CORE.map((u) => c.add(u).catch(() => null))))   // biri alınamazsa kurulum yine tamamlanır
      .then(() => self.skipWaiting())
  );
});
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
// Önce ağ (güncel veri), ağ yoksa son kaydedilen kopya (çevrimdışı açılış)
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  const nav = req.mode === "navigate";
  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
        return res;
      })
      // index.html?q=... gibi adresler için sorgu kısmı yok sayılır
      .catch(() => caches.match(req, { ignoreSearch: nav }).then((hit) => hit || (nav ? caches.match("./") : undefined)))
  );
});
