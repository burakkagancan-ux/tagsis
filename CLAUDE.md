# Proje notları (Claude için)

Bu dosya her yeni Claude oturumunda okunur. Güncel durum, kararlar ve çalışma kuralları burada.
Son güncelleme: 03.10.2026.

## Roller ve dil
- Kullanıcı (BKC) iş mimarı, kod yazmıyor. Claude yazılımcı. Dil: Türkçe.
- Neyin test edildiği / edilemediği her seferinde açıkça söylenir. Telefon testlerini kullanıcı yapar.
- Değişiklikler `claude/...` dalında yapılır, PR açılır; kullanıcı GitHub'da "Merge pull request" der.

## Ürün
- Son tüketiciye Tarım ve Orman Bakanlığı taklit/tağşiş listesini gösteren PWA (index.html) ve etiketteki içerik listesini fotoğraftan okuyup analiz eden "Etiket oku" sayfası (ocr.html).
- Site: https://burakkagancan-ux.github.io/tagsis/ (GitHub Pages, main dalı).
- Gıda: E kodları (data/e_kodlari.json, gen_e_kodlari.py, TGK ile karşılaştırılmış), bileşen grupları (data/bilesenler.json), açıklamalar (data/e_aciklama.json), profiller (alerjen, laktoz, vegan, vejetaryen, hamile, bebek, çocuk, PKU, evcil hayvan, koku alerjisi).
- Kozmetik: AB 1223/2009 ekleri (data/kozmetik.json, 1.972 kayıt) + CosIng INCI listesi ve 2.978 eş anlamlı (data/kozmetik_inci.json). Üretim: gen_kozmetik.py (CosIng verisi: `git clone https://github.com/inhouse-work/cosing ../cosing`, commit 268e3cd), kaynak/kozmetik_guncellemeler.tsv (2024-2026 AB değişiklikleri), kaynak/kozmetik_esanlamlilar.tsv.
- Kozmetik K3 ("tartışmalı katman"): kaynak/kozmetik_k3.tsv → kozmetik.json `watch` alanı + `meta.watch_lists`. AB olası endokrin bozucu öncelik listesi (A/B, 28 madde), Kaliforniya HSC §108980 (AB 2762: 2025, AB 496: 2027), ASEAN Ek II farkı (mikonazol). Eşleştirme yalnızca INCI adıyla; CAS belgeleme için.
- Bakanlık verisi: fetch_data_arsivli.py, .github/workflows/update.yml (her gün 05:00 UTC).
- OCR: ocr.html → Cloudflare Worker (worker/, https://inapp-ocr-3a8f.burakkagancan.workers.dev) → Google Cloud Vision. Worker'a ulaşılamazsa Tesseract.js.

## ocr.html yapısı
- `/*LOGIC-START*/ ... /*LOGIC-END*/` arası saf mantık; testler bu bölümü eval ile yükler.
- Gıda: buildIndex, analyze, summarize. OCR toleransı (findNames): ocrFixF ("rn"->"m", harf arası rakam) ve short1 (4-8 harfli tek sözcük, mesafe 1, tek aday, yalnızca B: bileşen gruplarında kabul; yalnızca sondaki ek farkı sayılmaz: "alkolü" alkol değildir). Kozmetik: buildKIndex, looksCosmetic, inciItems, kLookup (bantlı Levenshtein, byFirst/bySecond kovaları; ocrFix: "rn"->"m", harf içi rakam; KSHORT: 5-6 harfli sık adlarda benzer yazım, kSegment içinde kapalı), kMatch, kSegment (virgülsüz listeleri böler), isProse (talimat/adres ayıklar), kResult, analyzeK (.extra), summarizeK(res, K) (.ban, .ed: K3 özetleri). K3 rengi kResult'ta: watch_lists[liste].level en az renk olur.
- Arayüz: Gıda | Kozmetik anahtarı (localStorage "tur"), ürün tipi ("ktip"), fotoğraf kırpma (CROP, prep()), mod başına durum satırı (setSt/STMSG), profil (localStorage "profil").

## Worker (worker/)
- Cloudflare Workers Builds, GitHub main'den otomatik dağıtır (root directory: worker). Panelde kod düzenlenmez.
- Korumalar: IP başına 6/dk, genel 30/dk (IP_LIMIT/GLOBAL_LIMIT), ALLOWED_ORIGIN (panelde secret, virgülle çoklu), ~4 MB, JPEG/PNG/WebP, 20 sn zaman aşımı, observability kapalı, keep_vars. wrangler.toml'a [vars] ALLOWED_ORIGIN EKLENMEZ (secret ile çakışır).

## Testler
- `node test/cases.js` (gıda), `node test/kozmetik_veri.js`, `node test/kozmetik_cases.js` (20 durum, 3'ü gerçek OCR çıktısı), `node test/kozmetik_k3.js` (K3 veri bütünlüğü + 8 durum), `node test/ocr_tolerans.js` (OCR karışmaları, yanlış eşleşme ve yeni eş anlamlılar), `node test/e_dogrulama.js` (E kodu kaynakları), `node worker/test.mjs` (14 durum).
- test/kozmetik_cases.js'i başka betikten `require` et (node -e içinde çalışmıyor).
- Tarayıcı: `python3 -m http.server 8765 &` + Playwright; "Okunan Metin" details kapalı, textarea'ya yazmadan önce summary'ye tıkla. OCR isteği `page.route('**/inapp-ocr-3a8f**')` ile taklit edilir.

## Kararlar
- Bakanlık verisi değiştirilmez. Marka eşleşmesi suçlama değil, nötr bağlantı.
- Uygulama asla "güvenli/uygun" demez; "bulunamadı, bu bir onay değildir" der. "Zararlı" ifadesi her zaman kaynağa (yönetmelik, tarih) bağlanır.
- Kozmetik, besin tablosu ve helalin önüne geçti. Gıda ve kozmetik JSON'ları ayrı; kozmetik dosyaları yalnızca Kozmetik seçilince yüklenir. Kamera kilitlenmez.
- Etiket oku'daki "Profilim" kutusu kalıyor. Kırpma kalıyor.
- K3 renkleri (03.10.2026, kullanıcı kararı): başka büyük pazarda yasak (Kaliforniya, ASEAN) → turuncu; AB endokrin bozucu öncelik listesi ve SIN List → sarı. AB Ek II'deki madde kırmızı kalır, K3 yalnızca not ekler.
- CYCLOMETHICONE, D4 kaydından (II/1388) çıkarıldı: kozmetik yönetmeliğinde yasak değil.
- "Görüntüyü iyileştir" düğmesi kaldırıldı (03.10.2026): Google Vision yolunda etkisi yoktu; yedek OCR'da (Tesseract) gri ton + kontrast hep açık.
- Temizlik ürünleri ayrı bir faz olacak (kozmetiğe karıştırılmaz; AB deterjan ve CLP mevzuatı).
- Barkod en sona; belki hiç kapsama alınmaz.
- İş sırası (kullanıcı, 03.10.2026): telefon testleri (kullanıcı) → besin değeri tablosu → aylık mevzuat izleme → hukuki görüş en son. Google Fonts ön yüz işiyle birlikte. CI bekleyebilir. Google Cloud Vision dakikalık kotası düşürüldü.
- E kodu renk ölçütleri değişmedi; kaynak taramasında E407/E407a ve E968 EFSA ADI aşımı nedeniyle (K6) sarıya, E154/E160f/E230 AB listesinde olmadığı için (K1) kırmızıya geçti.

## Bilinen sınırlamalar
- E kodları: 57 kayıt needs_review (çoğu vegan/helal kaynak bayrakları ve Türkiye izin durumu); renkli (sarı/kırmızı) kayıtların hepsi kaynaklı (`sources`). Kozmetik CosIng verisi 2024 başı; 2026 değişikliklerinin sıra numaraları doğrulanmadı; TR kozmetik ekleri satır satır karşılaştırılamadı (bkz. kaynak/TR_KOZMETIK_KARSILASTIRMA.md, `tr` alanı); ABD renk tablosu (US_COLORS) ve eş anlamlılar bilgiye dayalı.
- OCR: iki sütunlu etikette kesik adlar, ağır bozulmalar, 2024 sonrası INCI'ler (ör. STEVIOL GLYCOSIDES) tanınmıyor.
- K3: ChemSec SIN List yok (uygulamada yeniden kullanım için ChemSec'ten yazılı izin gerekiyor, info@chemsec.org). Kanada Hotlist, Çin, Japonya, Kore, Brezilya, Washington eyaleti eklenmedi. ASEAN satırı needs_review.
- GLYCERIN gibi maddelerde "kaynağı belirsiz" vegan uyarısı sık çıkıyor.

## Eş anlamlı ölçümü (03.10.2026)
- 25 gerçekçi Türkçe gıda etiketi ve 17 INCI listesiyle denetlendi: temiz metinde kozmetik %100, gıdada eksik 5 ifade bulunup eklendi (amonyak sülfitli karamel, briliant mavi FCF, koyulaştırıcı, aroma güçlendirici, stabilizörler).
- Yapay OCR hatası testi (tek harf karışması): kozmetik %92 -> %98, gıda %74 -> %88; yeni yanlış eşleşme yok. Kalan zayıflık: iki harfi bozulmuş adlar, 4 harften kısa sözcükler (süt, palm).

## Sıradaki işler
1. Telefon testleri (kullanıcı yapıyor) ve sonuçlara göre ayar.
2. Faz 2: besin değeri tablosu okuma. Ardından helal ("kaynağı belirsiz, sertifikaya bakın").
3. Aylık mevzuat izleme (GitHub Actions: EUR-Lex, Resmî Gazete, CosIng -> issue). Türkiye taslağı yayımlanınca `TR_BY_REG` güncellenir.
4. Google Fonts'u depoya alma (ön yüz işleriyle birlikte).
5. Hukuki görüş hazırlığı (KVKK / Google Vision, "zararlı" dili, arşiv gösterimi) — en son.
6. Sonra: temizlik ürünleri fazı, CI ile testler, SIN List (ChemSec izni), barkod (belki hiç).

## Belgeler (Claude Docs)
- Kozmetik araştırması: https://claude.ai/code/artifact/690f07f0-5bc7-4600-bd75-aa9d38fbfb21
- SWOT analizi: https://claude.ai/code/artifact/bf937ec9-f5fd-4517-8171-747190a098d0
