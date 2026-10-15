// Eski /tagsis/ service worker'ının yerine geçer: kendini kaldırır ve açık sekmeleri /umi/'ye götürür.
// Önbelleklere dokunmaz (aynı alan adındaki /umi/ uygulaması onları kendisi taşır).
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(
  self.registration.unregister()
    .then(() => self.clients.matchAll({ type: "window" }))
    .then((cs) => Promise.all(cs.map((c) => c.navigate(c.url.replace("/tagsis/", "/umi/")).catch(() => null))))
));
