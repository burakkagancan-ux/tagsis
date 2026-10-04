# Teknik borç

Bilerek ertelenen işler. Yayına (mağaza/duyuru) çıkmadan önce kapatılmalı.

## 1. OCR Worker'a istek sınırı — KAPANDI (03.10.2026: worker/ depoda, Workers Builds ile dağıtılıyor, IP ve genel istek sınırı çalışıyor). Kalan: Google Cloud Vision "Requests per minute" kotasının düşürülmesi.
- **Durum:** `ocr.html`, Cloudflare Worker'a (`inapp-ocr-3a8f…workers.dev`) istek atıyor; Worker da Google Cloud Vision'ı çağırıyor. Worker yalnızca `ALLOWED_ORIGIN` başlığına bakıyor. Bu başlığı tarayıcı dışından istek atan biri kolayca taklit edebilir, yani bu kontrol tek başına koruma sağlamaz.
- **Risk:** Adresi bulan biri yüksek hacimde istek atarak Vision kotasını ve faturayı şişirebilir. Google Cloud'da bütçe uyarısı kurulu (03.10.2026). Uyarı yalnızca haber verir, harcamayı durdurmaz.
- **Önerilen çözüm:**
  1. Worker'a Cloudflare Rate Limiting bağlaması: IP başına ör. dakikada 10, günde 100 istek.
  2. Görüntü boyutu üst sınırı (ör. 4 MB). Aşan istek reddedilir.
  3. İsteğe bağlı: Cloudflare Turnstile (görünmez doğrulama).
  4. İsteğe bağlı: bütçe aşılınca Vision API'yi otomatik kapatan bütçe → Pub/Sub → Cloud Function.
- **Kod:** Worker kodu bu depoda yok. Önce depoya eklenmeli (`worker/`), sonra sınır eklenmeli.

## 2. Worker'ın kayıt (log) tutmaması — KAPANDI (kodda log yok, observability kapalı, panelde Exports/Logpush tanımlı değil)
- `ocr.html` gizlilik notu "fotoğraf ve metin kaydedilmez" diyor. Worker kodunda `console.log` ile görüntü ya da metin yazılmadığı ve Workers Logs/Logpush'ın kapalı olduğu kontrol edilmeli.

## 3. Google Fonts
- ÇÖZÜLDÜ (04.10.2026): Schibsted Grotesk depoda (fonts/, SIL OFL 1.1, @fontsource 5.3.0; latin + latin-ext, 400/600/800 woff2). Google'a istek gitmiyor; service worker önbelleğe alıyor (tagsis-v5).

## 4. Kozmetik verisi (data/kozmetik.json) — yayın öncesi
- **Türkiye ekleri:** Durum karşılaştırması yapıldı (kaynak/TR_KOZMETIK_KARSILASTIRMA.md): son TR değişikliği 05.03.2024 (AB 2023/1490), sonraki AB değişiklikleri `tr` alanında. Ek II–VI satır satır karşılaştırması Resmî Gazete metnine erişilemediği için yapılamadı; Eylül 2026 taslağının resmî metni de görülmedi.
- **Anlık görüntü yaşı:** CosIng verisi 2024 başına ait (inhouse-work/cosing @268e3cd). Sonraki değişiklikler `kaynak/kozmetik_guncellemeler.tsv` ile elle eklendi. Eksikler: 2026/78 ile eklenen 15 CMR maddesinin adları; 2026/909'daki alüminyum, çinko tuzları, DHHB ve 4 saç boyası; 2026 sonu taslak (benzofenon-1/-2, BHA, paraben, CBD).
- **Doğrulama:** `inceleme=1` olan güncellemeler (needs_review) EUR-Lex metniyle satır satır karşılaştırılmalı; 2026/78 ve 2026/909 ek sıra numaraları doğrulanamadı.
- **Otomatik güncelleme:** CosIng verisi artık depoda (`kaynak/cosing/`, `cosing_al.py` ile alınır). Kaynak depo inhouse-work/cosing 13.05.2024'ten beri güncellenmiyor (268e3cd en son commit), yani oradan yeni veri gelmez. Daha yeni veri için Komisyon'un CosIng sitesinden indirme gerekir (bu ortamdan erişilemedi); aylık mevzuat izleme işine bağlı.
- **Eş anlamlılar:** `kaynak/kozmetik_esanlamlilar.tsv` (Türkçe/İngilizce yaygın adlar) ve ABD renklendirici tablosu (`kaynak/kozmetik_abd_renkler.tsv`) (FD&C/D&C → CI) bilgiye dayanarak yazıldı; FDA 21 CFR 74/82 listeleriyle karşılaştırılmalı. Türkçe kimyasal adlar kuralla üretiliyor (975 ad); Türk etiketlerinde görülen gerçek yazımlarla denetlenmeli.

## 5. Kozmetik K3 (kaynak/kozmetik_k3.tsv)
- **Kaynak denetimi:** Kaliforniya listesi HSC §108980 metninin Justia kopyasından (2024 kodu) alındı; resmi leginfo sitesinden karşılaştırılmadı. ASEAN satırı (mikonazol) ikincil kaynaktan (CIRS), needs_review.
- **Güncelleme:** AB endokrin bozucu listesinin B grubu için ikinci veri çağrısı ve SCCS görüşleri izlenmeli; tarihleri elle güncellenir.
- **SIN List:** ChemSec'in veri yeniden kullanım koşulları belirsiz; yazılı izin alınmadan eklenmemeli.

## ocr.html tek dosyada — KAPANDI (04.10.2026)
- ~1.550 satırlık ocr.html gıda, kozmetik, temizlik ve arayüz kodunu birlikte taşıyordu. Kod `js/` klasöründe alana göre 9 dosyaya bölündü (derleme adımı yok, davranış değişmedi; eski ve yeni sayfanın sonuç ekranları tarayıcıda birebir karşılaştırıldı). Kalan: arayüz kodunun sözdizimi dışında otomatik testi yok (tarayıcı testi CI'da çalışmıyor).

## Veri kod dosyalarının içinde — KAPANDI (04.10.2026)
- Üreteçlerdeki (gen_e_kodlari.py 120 KB, gen_e_aciklama.py, gen_bilesenler.py, gen_temizlik.py, gen_kozmetik.py) gömülü veri `kaynak/` altındaki JSON/TSV dosyalarına taşındı: `e_kodlari_maddeler.json`, `e_kodlari_ek.json`, `e_aciklama.tsv`, `bilesenler.json`, `temizlik_ifadeler.tsv`, `temizlik_birlesik.tsv`, `temizlik_onlemler.tsv`, `temizlik_gruplar.json`, `kozmetik_listeler.json`, `kozmetik_islevler.tsv`, `kozmetik_tr_sozcukler.tsv`, `kozmetik_abd_renkler.tsv`. Üretilen data/*.json dosyaları birebir aynı kaldı.
- CI ("Testler") üreteçleri çalıştırıp data/ değişmiş mi diye bakar: kaynak dosya düzeltilip üreteç çalıştırılmazsa ya da JSON elle düzenlenirse hata verir.

## CosIng verisi depo dışında — KAPANDI (04.10.2026)
- gen_kozmetik.py artık `../cosing` kopyasına ihtiyaç duymaz; kullanılan kısım `kaynak/cosing/` altında (Ek II–VI aynen, INCI listesinden 3 sütun; ~3 MB, sürüm `surum.txt`, lisans `LICENSE.txt`). Yenilemek için `python3 cosing_al.py`. Verinin eski olması (2024 başı) ayrı sorun, bkz. 4.


## Temizlik: "Adı Yazılan Maddeler" bölümü (UX, 04.10.2026)
- Bölüm etikette adı yazan maddeleri gösteriyor (js/arayuz_temizlik.js, renderT): notu olanlar (MIT, BIT, hipoklorit…) kart, diğerleri düz liste. Değerlendirmede bulunan sorunlar ve öneriler (kullanıcı ertelendi):
  1. Başlık özetteki "Tanınan madde" satırıyla uyuşmuyor; başlık "Tanınan Maddeler" olabilir. (önerilen)
  2. Madde kartlarında açıklama yalnızca (i) arkasında; tehlike kartlarındaki gibi bir satırlık açıklama görünmeli. (önerilen)
  3. Kartlar ve düz liste karışık; liste "Diğer maddeler (N)" adıyla kapalı açılır bölüme (secBox) girebilir. (önerilen)
  4. "İşlevler AB…" notu bölümün başında; listenin altına inebilir.
  5. Adlar İngilizce ve büyük harf (INCI); yanına Türkçe ad (LIMONENE · limonen). Veri hazırlığı gerekir.
  6. İşlev adı tekrarı ("PARFUM · Koku, Parfüm"); tekrar kaldırılmalı. (önerilen)
