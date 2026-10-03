# Teknik borç

Bilerek ertelenen işler. Yayına (mağaza/duyuru) çıkmadan önce kapatılmalı.

## 1. OCR Worker'a istek sınırı yok — yüksek öncelik
- **Durum:** `ocr.html`, Cloudflare Worker'a (`inapp-ocr-3a8f…workers.dev`) istek atıyor; Worker da Google Cloud Vision'ı çağırıyor. Worker yalnızca `ALLOWED_ORIGIN` başlığına bakıyor. Bu başlığı tarayıcı dışından istek atan biri kolayca taklit edebilir, yani bu kontrol tek başına koruma sağlamaz.
- **Risk:** Adresi bulan biri yüksek hacimde istek atarak Vision kotasını ve faturayı şişirebilir. Google Cloud'da bütçe uyarısı kurulu (03.10.2026). Uyarı yalnızca haber verir, harcamayı durdurmaz.
- **Önerilen çözüm:**
  1. Worker'a Cloudflare Rate Limiting bağlaması: IP başına ör. dakikada 10, günde 100 istek.
  2. Görüntü boyutu üst sınırı (ör. 4 MB). Aşan istek reddedilir.
  3. İsteğe bağlı: Cloudflare Turnstile (görünmez doğrulama).
  4. İsteğe bağlı: bütçe aşılınca Vision API'yi otomatik kapatan bütçe → Pub/Sub → Cloud Function.
- **Kod:** Worker kodu bu depoda yok. Önce depoya eklenmeli (`worker/`), sonra sınır eklenmeli.

## 2. Worker'ın kayıt (log) tutmadığının doğrulanması
- `ocr.html` gizlilik notu "fotoğraf ve metin kaydedilmez" diyor. Worker kodunda `console.log` ile görüntü ya da metin yazılmadığı ve Workers Logs/Logpush'ın kapalı olduğu kontrol edilmeli.

## 3. Google Fonts
- `index.html`, yazı tipini Google Fonts'tan yüklüyor. Bu yüzden kullanıcının IP adresi Google'a gidiyor. Gizlilik metniyle tutarlı olması için yazı tipi depoya alınabilir (self-host).
