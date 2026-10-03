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
- Bakanlık verisi: fetch_data_arsivli.py, .github/workflows/update.yml (her gün 05:00 UTC).
- OCR: ocr.html → Cloudflare Worker (worker/, https://inapp-ocr-3a8f.burakkagancan.workers.dev) → Google Cloud Vision. Worker'a ulaşılamazsa Tesseract.js.

## ocr.html yapısı
- `/*LOGIC-START*/ ... /*LOGIC-END*/` arası saf mantık; testler bu bölümü eval ile yükler.
- Gıda: buildIndex, analyze, summarize. Kozmetik: buildKIndex, looksCosmetic, inciItems, kLookup (bantlı Levenshtein, byFirst/bySecond kovaları), kMatch, kSegment (virgülsüz listeleri böler), isProse (talimat/adres ayıklar), kResult, analyzeK (.extra), summarizeK.
- Arayüz: Gıda | Kozmetik anahtarı (localStorage "tur"), ürün tipi ("ktip"), fotoğraf kırpma (CROP, prep()), mod başına durum satırı (setSt/STMSG), profil (localStorage "profil").

## Worker (worker/)
- Cloudflare Workers Builds, GitHub main'den otomatik dağıtır (root directory: worker). Panelde kod düzenlenmez.
- Korumalar: IP başına 6/dk, genel 30/dk (IP_LIMIT/GLOBAL_LIMIT), ALLOWED_ORIGIN (panelde secret, virgülle çoklu), ~4 MB, JPEG/PNG/WebP, 20 sn zaman aşımı, observability kapalı, keep_vars. wrangler.toml'a [vars] ALLOWED_ORIGIN EKLENMEZ (secret ile çakışır).

## Testler
- `node test/cases.js` (gıda), `node test/kozmetik_veri.js`, `node test/kozmetik_cases.js` (20 durum, 3'ü gerçek OCR çıktısı), `node worker/test.mjs` (14 durum).
- test/kozmetik_cases.js'i başka betikten `require` et (node -e içinde çalışmıyor).
- Tarayıcı: `python3 -m http.server 8765 &` + Playwright; "Okunan Metin" details kapalı, textarea'ya yazmadan önce summary'ye tıkla. OCR isteği `page.route('**/inapp-ocr-3a8f**')` ile taklit edilir.

## Kararlar
- Bakanlık verisi değiştirilmez. Marka eşleşmesi suçlama değil, nötr bağlantı.
- Uygulama asla "güvenli/uygun" demez; "bulunamadı, bu bir onay değildir" der. "Zararlı" ifadesi her zaman kaynağa (yönetmelik, tarih) bağlanır.
- Kozmetik, besin tablosu ve helalin önüne geçti. Gıda ve kozmetik JSON'ları ayrı; kozmetik dosyaları yalnızca Kozmetik seçilince yüklenir. Kamera kilitlenmez.
- Etiket oku'daki "Profilim" kutusu kalıyor. Kırpma kalıyor.
- Açık: "Görüntüyü iyileştir" kaldırılsın mı; "başka ülkede yasak" turuncu mu sarı mı; temizlik ürünleri ayrı faz mı.

## Bilinen sınırlamalar
- 110 E kodu needs_review. Kozmetik CosIng verisi 2024 başı; 2026 değişikliklerinin sıra numaraları doğrulanmadı; TR kozmetik ekleri madde madde karşılaştırılmadı; ABD renk tablosu (US_COLORS) ve eş anlamlılar bilgiye dayalı.
- OCR: iki sütunlu etikette kesik adlar, ağır bozulmalar, 2024 sonrası INCI'ler (ör. STEVIOL GLYCOSIDES) tanınmıyor.
- GLYCERIN gibi maddelerde "kaynağı belirsiz" vegan uyarısı sık çıkıyor.

## Sıradaki işler
1. Telefon testleri (eş anlamlılar, Türkçe etiketler, kırpma) ve sonuçlara göre ayar.
2. Hukuki görüş hazırlığı (KVKK / Google Vision, "zararlı" dili, arşiv gösterimi) — kullanıcı avukata soracak.
3. Kozmetik K3: AB endokrin bozucu öncelik listesi (28), Kaliforniya AB 2762/AB 496, ASEAN, ChemSec SIN List.
4. Faz 2: besin değeri tablosu okuma; helal ("kaynağı belirsiz, sertifikaya bakın").
5. Teknik borç: TEKNIK_BORC.md (Google Fonts, TR kozmetik ekleri, eksik 2026 AB değişiklikleri, CI ile testler).

## Belgeler (Claude Docs)
- Kozmetik araştırması: https://claude.ai/code/artifact/690f07f0-5bc7-4600-bd75-aa9d38fbfb21
- SWOT analizi: https://claude.ai/code/artifact/bf937ec9-f5fd-4517-8171-747190a098d0
