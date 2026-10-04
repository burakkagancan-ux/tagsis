# Proje notları (Claude için)

Bu dosya her yeni Claude oturumunda okunur. Güncel durum, kararlar ve çalışma kuralları burada.
Son güncelleme: 04.10.2026.

## Roller ve dil
- Kullanıcı (BKC) iş mimarı, kod yazmıyor. Claude yazılımcı. Dil: Türkçe.
- Neyin test edildiği / edilemediği her seferinde açıkça söylenir. Telefon testlerini kullanıcı yapar.
- Değişiklikler `claude/...` dalında yapılır, PR açılır; kullanıcı GitHub'da "Merge pull request" der.

## Ürün
- Son tüketiciye Tarım ve Orman Bakanlığı taklit/tağşiş listesini gösteren PWA (index.html) ve etiketteki içerik listesini fotoğraftan okuyup analiz eden "Etiket oku" sayfası (ocr.html).
- Site: https://burakkagancan-ux.github.io/tagsis/ (GitHub Pages, main dalı).
- Gıda: E kodları (data/e_kodlari.json, gen_e_kodlari.py, TGK ile karşılaştırılmış), bileşen grupları (data/bilesenler.json), açıklamalar (data/e_aciklama.json), profiller (alerjen, laktoz, vegan, vejetaryen, hamile, bebek, çocuk, PKU, evcil hayvan, tansiyon/tuz kısıtlaması, koku alerjisi).
- Kozmetik: AB 1223/2009 ekleri (data/kozmetik.json, 1.972 kayıt) + CosIng INCI listesi ve 2.978 eş anlamlı (data/kozmetik_inci.json). Üretim: gen_kozmetik.py (CosIng verisi: `git clone https://github.com/inhouse-work/cosing ../cosing`, commit 268e3cd), kaynak/kozmetik_guncellemeler.tsv (2024-2026 AB değişiklikleri), kaynak/kozmetik_esanlamlilar.tsv.
- Kozmetik K3 ("tartışmalı katman"): kaynak/kozmetik_k3.tsv → kozmetik.json `watch` alanı + `meta.watch_lists`. AB olası endokrin bozucu öncelik listesi (A/B, 28 madde), Kaliforniya HSC §108980 (AB 2762: 2025, AB 496: 2027), ASEAN Ek II farkı (mikonazol). Eşleştirme yalnızca INCI adıyla; CAS belgeleme için.
- Kozmetik endokrin (04.10.2026, araştırma: https://claude.ai/code/artifact/f3487ffa-3ac4-4f20-910f-1980191e91af): K3'e eklenen listeler `eu_svhc_ed` (REACH aday listesi, endokrin gerekçesi: butylparaben, resorcinol), `ab_taslak` (AB Eylül 2026 taslağı: BP-1, BP-2 yasak; BHA %0,07; butylparaben çocuk sınırı), `dk` (Danimarka, 3 yaş altı paraben yasağı), `fr` (Fransa ANSES listesi; yalnızca ikincil kaynakta adı geçen 7 madde). 28'lik AB listesindeki sonuçlanmış maddelere durum notu (not_tr) yazıldı. Kind `ed` olan listeler özette "Endokrin bozucu şüphesi" satırına, `child` olanlar çocuk kartına girer. Hamile/bebek/çocuk profilinde ayrı "Endokrin bozucu şüphesi" kartı. Hepsi sarı; dil "şüphe/aday".
- Kozmetik komedojenite (04.10.2026, araştırma: https://claude.ai/code/artifact/7755a9ba-cfdc-4dde-8397-116f813f3d27): K3 listesi `komedo` (level `info`, kind `comedo`), Fulton 1989'da en yüksek bulunan 9 madde. Kullanıcı kararı: skor verilmez, yalnızca bilgi notu. Renk değiştirmez (Dikkat Gerektiren'e girmez); özette "Gözenek tıkayıcı olabilir" satırı + gri "Gözenek tıkayıcı olabilecek madde" kartı (ayrıntı (i) düğmesinde: madde notu, Draelos 2006, kaynak). Profil gerekmez; ürün tipi "Durulanan" seçiliyse kart, satır ve çip gösterilmez. Dil: "sivilce yapar", skor (4/5) kullanılmaz.
- "Birlikte dikkat" eşleşmeleri: data/eslesmeler.json, gen_eslesmeler.py (gen_e_kodlari.py ve gen_kozmetik.py'den SONRA çalıştır; kozmetik INCI listeleri AB koşul metinlerinden üretilir). 10 kural: gıda 6 (benzoat + C vitamini, Southampton renkleri + sodyum benzoat, polioller, fosfatlar, alüminyum, sülfitler), kozmetik 4 (nitrozamin ikilisi, formaldehit salıcılar, parabenler, florürler). Türleri: cift (iki grup birlikte) ve toplam (aynı gruptan en az 2). "içermez" ve "içerebilir" sayılmaz.
- Temizlik (04.10.2026, araştırma: https://claude.ai/code/artifact/2d7d721b-ba03-4e5a-a0a6-d03ae9fbb323): data/temizlik.json, gen_temizlik.py (veri dosyanın içinde; kozmetik_inci.json ile INCI denetimi yapar). Dört katman: (1) zararlılık ifadeleri: 75 H + 33 EUH + 12 birleşik ifade; koddan (H318, EUH 208, H360FD) ve Türkçe/İngilizce metinden bulunur ("yol açar" yerine "neden olur" biçimi de); (2) AB 648/2004 Ek VII / TR Deterjanlar Hakkında Yönetmelik Ek-7 içerik grupları (21 grup) ve yüzde bantları (%5'ten az, %5-15, %15-30, %30 ve üzeri; bant grubun önünde ya da arkasında olabilir; enzim/dezenfektan/optik parlatıcı/parfüm/koruyucu bantsız), "fosfat içermez/fosfatsız" beyanı; (3) INCI ile yazılan maddeler kozmetik INCI dizininden (koku alerjeni, koruyucu, CI kodlu renklendirici işaretlenir; tüm tanınanlar CosIng işleviyle listelenir, kozmetiğe özgü işlevler TFUNC_SKIP ile gizlenir; kozmetik sınır/yasak renkleri kullanılmaz). Temizliğe özgü eş anlamlılar: kaynak/temizlik_esanlamlilar.tsv (98 ad: LAS, SLES, STPP, perkarbonat, kostik, tuz ruhu, butil glikol, DDAC, enzimlerin Türkçesi…; tür kisa olanlar yalnızca büyük harfle yazılmışsa eşleşir), kozmetik eş anlamlıları da geçerli; "sulph" -> "sulf"; (4) temizliğe özgü madde notları (izotiyazolinonlar MIT/CMIT/BIT/OIT, sodyum hipoklorit, asit, amonyak, enzimler; kimyasal adlarla da aranır). Uyarı kelimesi (TEHLİKE/DİKKAT, yalnızca büyük harf) okunur. Karıştırma kartı: klor bazlı ağartıcı, sodyum hipoklorit, hidroklorik asit, amonyak ya da EUH206/031/032/029 görülünce (kaynak: Sağlık Bakanlığı Sağlıklı Temizlik Rehberi + CLP).
- Bakanlık verisi: fetch_data_arsivli.py, .github/workflows/update.yml (her gün 05:00 UTC).
- OCR: ocr.html → Cloudflare Worker (worker/, https://inapp-ocr-3a8f.burakkagancan.workers.dev) → Google Cloud Vision. Worker'a ulaşılamazsa Tesseract.js.

## ocr.html yapısı
- `/*LOGIC-START*/ ... /*LOGIC-END*/` arası saf mantık; testler bu bölümü eval ile yükler.
- Gıda: buildIndex, analyze (besin değerleri tablosu satırlarını "Tuz 1,2 g" atar; m.ord = içerik listesindeki sıra), summarize (.sodium: tuz, gizli sodyum kaynakları, tuzun sırası). OCR toleransı (findNames): ocrFixF ("rn"->"m", harf arası rakam) ve short1 (4-8 harfli tek sözcük, mesafe 1, tek aday, yalnızca B: bileşen gruplarında kabul; yalnızca sondaki ek farkı sayılmaz: "alkolü" alkol değildir). Kozmetik: buildKIndex, looksCosmetic, inciItems, kLookup (bantlı Levenshtein, byFirst/bySecond kovaları; KNOFUZZ: tek başına kalan "chloride/chlorite/silikat" benzer yazımla eşleşmez, yoksa CHLORINE (Ek II, kırmızı) olur; ocrFix: "rn"->"m", harf içi rakam; KSHORT: 5-6 harfli sık adlarda benzer yazım, kSegment içinde kapalı), kMatch, kSegment (virgülsüz listeleri böler), isProse (talimat/adres ayıklar), kResult (aynı madde birden çok AB kaydındaysa ürün tipi notu bir kez yazılır, ör. MIT: V/39 ve V/57), analyzeK (.extra), summarizeK(res, K) (.ban, .ed: K3 özetleri). K3 rengi kResult'ta: watch_lists[liste].level en az renk olur.
- Temizlik: buildTIndex, tCodes, tPhrases (ifadenin ≥5 harfli bir sözcüğü metinde aynen geçerse çevresindeki pencere bantlı Levenshtein ile karşılaştırılır; uzun eşleşme kısa olanı yutar: H413 > H412, H350i > H350), tPrep/tGroups (bantlar), tAliasMap/tLook (temizlik eş anlamlısı > kozmetik dizini > boşluksuz yazım > sulph), tInci (kısa parçada tLook, olmazsa kMatch benzer yazımı yalnızca düz yazı değilse ve ≥8 harfse; uzun parçada yalnızca birebir ad; kSegment yavaş olduğu için kullanılmaz), analyzeT, summarizeT, looksCleaning (gıda ve kozmetik modunda "temizlik ürününe benziyor" öneri kartı).
- Arayüz: Gıda | Kozmetik | Temizlik anahtarı (localStorage "tur": gida/koz/tem), ürün tipi ("ktip"), fotoğraf kırpma (CROP, prep()), mod başına durum satırı (setSt/STMSG), profil (localStorage "profil").

## Worker (worker/)
- Cloudflare Workers Builds, GitHub main'den otomatik dağıtır (root directory: worker). Panelde kod düzenlenmez.
- Korumalar: IP başına 6/dk, genel 30/dk (IP_LIMIT/GLOBAL_LIMIT), ALLOWED_ORIGIN (panelde secret, virgülle çoklu), ~4 MB, JPEG/PNG/WebP, 20 sn zaman aşımı, observability kapalı, keep_vars. wrangler.toml'a [vars] ALLOWED_ORIGIN EKLENMEZ (secret ile çakışır).

## Testler
- `node test/cases.js` (gıda), `node test/kozmetik_veri.js`, `node test/kozmetik_cases.js` (20 durum, 3'ü gerçek OCR çıktısı), `node test/kozmetik_k3.js` (K3 veri bütünlüğü + 12 durum, komedojenite dahil), `node test/ocr_tolerans.js` (OCR karışmaları, yanlış eşleşme ve yeni eş anlamlılar), `node test/e_dogrulama.js` (E kodu kaynakları), `node test/sodyum.js` (tuz/sodyum, besin tablosu satırı, olumsuzluk), `node test/eslesme.js` (birlikte dikkat), `node test/temizlik.js` (veri bütünlüğü + 17 etiket durumu + 5 eş anlamlı/CI durumu + gıda/kozmetik metninde yanlış eşleşme + hız), `node test/sozdizimi.js` (sayfalardaki tüm script bloklarının sözdizimi; arayüz kodu başka testte çalışmaz, her değişiklikten sonra çalıştır), `node worker/test.mjs` (14 durum).
- test/kozmetik_cases.js'i başka betikten `require` et (node -e içinde çalışmıyor).
- Tarayıcı: `python3 -m http.server 8765 &` + Playwright; "Okunan Metin" details kapalı, textarea'ya yazmadan önce summary'ye tıkla. OCR isteği `page.route('**/inapp-ocr-3a8f**')` ile taklit edilir.

## Kararlar
- Bakanlık verisi değiştirilmez. Marka eşleşmesi suçlama değil, nötr bağlantı.
- Uygulama asla "güvenli/uygun" demez; "bulunamadı, bu bir onay değildir" der. "Zararlı" ifadesi her zaman kaynağa (yönetmelik, tarih) bağlanır.
- Kozmetik, besin tablosu ve helalin önüne geçti. Gıda ve kozmetik JSON'ları ayrı; kozmetik dosyaları yalnızca Kozmetik seçilince yüklenir. Kamera kilitlenmez.
- Etiket oku'daki "Profilim" kutusu kalıyor. Kırpma kalıyor.
- Arayüz adları (kullanıcı, 04.10.2026): alt menü "Liste | Etiket Oku | Hassasiyetlerim"; profil kutusu ve sayfası "Hassasiyetlerim"; okuma düğmesi "Analiz Et"; "Ürün Tipi". Hassasiyetlerim kutularındaki seçenekler Türkçe alfabeye göre sıralı. Liste sayfasında "Veriyi güncelle" (elle yapıştırma) kaldırıldı; veri yalnızca data/tagsis.json + arsiv.json'dan gelir. Sayaç: "N Firma/Ürün Listelendi." ve altında "Son Kontrol: … · Son Liste Güncelleme: …".
- K3 renkleri (03.10.2026, kullanıcı kararı): başka büyük pazarda yasak (Kaliforniya, ASEAN) → turuncu; AB endokrin bozucu öncelik listesi ve SIN List → sarı. AB Ek II'deki madde kırmızı kalır, K3 yalnızca not ekler.
- CYCLOMETHICONE, D4 kaydından (II/1388) çıkarıldı: kozmetik yönetmeliğinde yasak değil.
- "Görüntüyü iyileştir" düğmesi kaldırıldı (03.10.2026): Google Vision yolunda etkisi yoktu; yedek OCR'da (Tesseract) gri ton + kontrast hep açık.
- Birlikte dikkat (03.10.2026): her kural resmi kaynağa dayanır; dil olasılık bildirir ("oluşabilir"), "tehlikeli/zehir" denmez; renk sarı, kırmızı yok. Kaynaksız "şu ikisi birlikte zehir" iddiaları eklenmez. E210-E213 kartları benzen notunu tek başına da gösterir ve sarı kalır (kullanıcı kararı, 03.10.2026). Kart görünümü: başlık + "Bu üründe" görünür; açıklama, kaynak ve not (i) düğmesinin arkasında.
- Gizli sodyum (03.10.2026): yalnızca "Tansiyon / tuz kısıtlaması" profili seçilince kart çıkar. Tuz, sodyumlu E kodları (adında sodyum geçen 42 kod), soya sosu ve bulyon gösterilir. Miktar hesaplanmaz; tuz ilk 3 bileşendeyse belirtilir. Eşik bilgisi NHS'e dayanır: 100 g'da >1,5 g yüksek, <0,3 g düşük.
- Temizlik ürünleri ayrı mod (kozmetiğe karıştırılmaz; AB deterjan ve CLP mevzuatı). Renkler (kullanıcı kararı, 04.10.2026): ciddi tehlike kırmızı (H314, H318, H304, H300-H301/H310-H311/H330-H331, H334, CMR H340-H362, H370, H372, EUH070, EUH071, EUH380/381); diğer sağlık, karıştırma, alerji ve çevre uyarıları sarı; H290, EUH210 vb. bilgi (gri). Kırmızı burada "yasak" değil, ürünün resmi tehlike sınıfı; kartta "üreticinin etikete yazmak zorunda olduğu bilgi" denir. Kozmetik Ek II "yasak" renkleri temizlikte kullanılmaz. Profil: "Koku alerjisi (kozmetik, temizlik)", yeni "Astım / solunum hassasiyeti (temizlik)" (PROF.astim; H33x, EUH071, EUH211/212, enzim, sprey, parfüm); hamile/bebek/çocuk için CMR, endokrin ve yutma/göz tehlikesi kartı.
- Barkod en sona; belki hiç kapsama alınmaz.
- İş sırası (kullanıcı, 03.10.2026): telefon testleri (kullanıcı) → besin değeri tablosu → aylık mevzuat izleme → hukuki görüş en son. Google Fonts ön yüz işiyle birlikte. CI bekleyebilir. Google Cloud Vision dakikalık kotası düşürüldü.
- E kodu renk ölçütleri değişmedi; kaynak taramasında E407/E407a ve E968 EFSA ADI aşımı nedeniyle (K6) sarıya, E154/E160f/E230 AB listesinde olmadığı için (K1) kırmızıya geçti.

## Bilinen sınırlamalar
- E kodları: 57 kayıt needs_review (çoğu vegan/helal kaynak bayrakları ve Türkiye izin durumu); renkli (sarı/kırmızı) kayıtların hepsi kaynaklı (`sources`). Kozmetik CosIng verisi 2024 başı; 2026 değişikliklerinin sıra numaraları doğrulanmadı; TR kozmetik ekleri satır satır karşılaştırılamadı (bkz. kaynak/TR_KOZMETIK_KARSILASTIRMA.md, `tr` alanı); ABD renk tablosu (US_COLORS) ve eş anlamlılar bilgiye dayalı.
- OCR: iki sütunlu etikette kesik adlar, ağır bozulmalar, 2024 sonrası INCI'ler (ör. STEVIOL GLYCOSIDES) tanınmıyor.
- K3: ChemSec SIN List yok (uygulamada yeniden kullanım için ChemSec'ten yazılı izin gerekiyor, info@chemsec.org). Kanada Hotlist, Çin, Japonya, Kore, Brezilya, Washington eyaleti eklenmedi. ASEAN satırı needs_review.
- Temizlik: SEA Yönetmeliği resmi metni okunamadı; H ifadelerinin Türkçesi SEA'ya dayalı firma listesinden (CRAD), EUH Türkçesi çeviri (needs_review). Piktogramlar tanınmaz. AB 2026/405 (yeni deterjan tüzüğü, uygulama 2029) Ek V metni okunamadı. İzotiyazolinon sınıflandırma kaynakları genel ECHA C&L bağlantısı; madde bazında doğrulanmadı. Telefonda test edilmedi.
- GLYCERIN gibi maddelerde "kaynağı belirsiz" vegan uyarısı sık çıkıyor.

## Eş anlamlı ölçümü (03.10.2026)
- 25 gerçekçi Türkçe gıda etiketi ve 17 INCI listesiyle denetlendi: temiz metinde kozmetik %100, gıdada eksik 5 ifade bulunup eklendi (amonyak sülfitli karamel, briliant mavi FCF, koyulaştırıcı, aroma güçlendirici, stabilizörler).
- Yapay OCR hatası testi (tek harf karışması): kozmetik %92 -> %98, gıda %74 -> %88; yeni yanlış eşleşme yok. Kalan zayıflık: iki harfi bozulmuş adlar, 4 harften kısa sözcükler (süt, palm).

## Sıradaki işler
1. Telefon testleri (kullanıcı yapıyor) ve sonuçlara göre ayar.
2. Faz 2: helal ("kaynağı belirsiz, sertifikaya bakın"). Besin değeri tablosu ve yeşil aklama bekleyen geliştirmeler (sıraya alınmadı; yeşil aklama ikinci fotoğraf gerektirdiği için ertelendi).
3. Aylık mevzuat izleme (GitHub Actions: EUR-Lex, Resmî Gazete, CosIng -> issue). Türkiye taslağı yayımlanınca `TR_BY_REG` güncellenir.
4. Google Fonts'u depoya alma (ön yüz işleriyle birlikte).
5. Hukuki görüş hazırlığı (KVKK / Google Vision, "zararlı" dili, arşiv gösterimi) — en son.
6. Sonra: temizlik ikinci sürüm (gelişim alanlarına bakın), CI ile testler, SIN List (ChemSec izni), barkod (belki hiç).

## Gelişim alanları (bilerek sonraya bırakılan genişletmeler)
- Birlikte dikkat: şimdilik 10 kural; kaynağı bulunan yeni eşleşmelerle artırılacak.
- Endokrin: Fransa ANSES listesinin tam metni (Légifrance, bu ortamdan erişilemedi), edlists.org Liste I-III, AB CLP ED HH 1/2 sınıflandırması almış maddeler, ChemSec SIN List (izin gerekli).
- Komedojenite: şimdilik 9 madde (Fulton 1989'da 4–5); kaynakla artırılacak. Adaylar: isopropyl palmitate, isopropyl isostearate, butyl stearate, decyl oleate, lauric/myristic acid (taşıyıcıya bağlı), D&C Red 36. Fulton tabloları görüntü olduğu için sayısal notlar tam okunamadı.
- AB Eylül 2026 taslağı yayımlanınca `ab_taslak` kayıtları kozmetik_guncellemeler.tsv'ye gerçek değişiklik olarak taşınmalı.

- Temizlik: çamaşır kapsülü/çocuk uyarıları, mikroorganizmalı temizleyiciler, P (önlem) ifadeleri, EUH208 içindeki madde adını ayrıca gösterme, AB 2026/405 Ek V (2029 öncesi mevzuat izlemesine).

## Belgeler (Claude Docs)
- Kozmetik araştırması: https://claude.ai/code/artifact/690f07f0-5bc7-4600-bd75-aa9d38fbfb21
- Endokrin bozucu araştırması: https://claude.ai/code/artifact/f3487ffa-3ac4-4f20-910f-1980191e91af
- Komedojenite araştırması: https://claude.ai/code/artifact/7755a9ba-cfdc-4dde-8397-116f813f3d27
- Temizlik araştırması: https://claude.ai/code/artifact/2d7d721b-ba03-4e5a-a0a6-d03ae9fbb323
- SWOT analizi: https://claude.ai/code/artifact/bf937ec9-f5fd-4517-8171-747190a098d0
