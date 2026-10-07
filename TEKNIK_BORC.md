# Teknik borç

Bilerek ertelenen işler. Yayına (mağaza/duyuru) çıkmadan önce kapatılmalı.

## 2. Worker'ın kayıt (log) tutmaması — KAPANDI (kodda log yok, observability kapalı, panelde Exports/Logpush tanımlı değil)
- `ocr.html` gizlilik notu "fotoğraf ve metin kaydedilmez" diyor. Worker kodunda `console.log` ile görüntü ya da metin yazılmadığı ve Workers Logs/Logpush'ın kapalı olduğu kontrol edilmeli.

## 3. Google Fonts
- ÇÖZÜLDÜ (04.10.2026): Yazı tipleri depoda (şimdi Bricolage Grotesque + Figtree; Schibsted kaldırıldı 04.10.2026) (fonts/, SIL OFL 1.1, @fontsource 5.3.0; latin + latin-ext, 400/600/800 woff2). Google'a istek gitmiyor; service worker önbelleğe alıyor (tagsis-v5).

## 4. Kozmetik verisi (data/kozmetik.json) — KAPANDI (07.10.2026)
- **Türkiye ekleri — KAPANDI:** Ek II–VI, Resmî Gazete'deki ek PDF'lerinden (2023 yönetmeliği ve 05.03.2024 değişikliği) yazı tanımayla okunup AB'nin 2.291 kaydıyla satır satır karşılaştırıldı (kaynak/TR_KOZMETIK_KARSILASTIRMA.md). Tek fark: AB Ek II 1394–1397 (boric oxide, borik asit, boratlar, sodyum perborat) Türkiye'de yasaklı listede yok; bu kayıtlarda `tr: farkli`, kartın (i) panelinde açıklanıyor. Sınır: yazı tanıma yüzde ve ürün tipi değerlerinin tek tek karşılaştırılmasına yetmiyor; karşılaştırma maddenin listede olup olmadığını kapsıyor.
- **Anlık görüntü yaşı — KAPANDI:** `cosing_al.py` artık Komisyon'un CosIng arama servisinden indiriyor (inhouse-work/cosing kopyası bırakıldı). Veri 28.04.2026'ya (2026/909) kadar güncel; 2026/78 ve 2026/909 ayrıca resmi metinden doğrulandı, numara çakışması CosIng'in konsolide numaralarıyla çözüldü (Ek II 1767; Ek III 381–386). 2025/877'nin eksik 7 CMR kaydı eklendi. CosIng'den çıkarılan 1.474 INCI adı `kaynak/cosing/ingredients_eski.csv`'de korunuyor (eski etiketlerde tanınsın diye).
  - Düzeltilen eski hatalar: CosIng'de aynı numarayı taşıyan iki kaydın biri kayboluyordu (ör. Ek III 269 BASIC RED 51); "Please consider entry 419…" gibi koşullu CosIng notları artık yasak sayılmıyor (MINERAL OIL, SQUALENE gibi yaygın adlar kırmızı olmuyor); gümüş çinko zeolit Ek V/61 ile koşullu izinli göründüğü için artık kırmızı değil.
- **Doğrulama — KAPANDI:** `kaynak/kozmetik_guncellemeler.tsv`'de `inceleme=1` satır kalmadı (2025/877 N,N-dimethyl-p-toluidine resmi metinle doğrulandı).
- **Otomatik güncelleme — KAPANDI:** `.github/workflows/cosing.yml` ayda bir (her ayın 1'i) CosIng'den indirir; değişiklik varsa testleri çalıştırıp PR açar. Yeni AB değişikliği gelirse güncelleme tablosuna Türkçe not ve Türkiye durumu elle eklenir.
- **Eş anlamlılar — KAPANDI (ABD renkleri):** `kaynak/kozmetik_abd_renkler.tsv`'deki 33 satırın hepsi 21 CFR 74/82'deki (eCFR) kimyasal tanımla ve AB Ek IV CAS'ıyla tutarlı; eksik 3 ABD rengi eklendi (FD&C Blue No. 2, D&C Black No. 2 ve 3). Eş anlamlıların hepsi yeni INCI listesinde geçerli hedefe bağlı.
  - Kalan: Kurala göre üretilen Türkçe kimyasal adlar (992 ad) gerçek Türk etiketlerinde görülen yazımlarla denetlenmeli; bunun için etiket fotoğrafı gerekiyor (telefon testleriyle birlikte).

## 5. Kozmetik K3 (kaynak/kozmetik_k3.tsv) — KAPANDI (07.10.2026), 1 madde AÇIK
- **Kaliforniya — KAPANDI:** Satırlar HSC §108980'in resmi metniyle (AB 60 ile değişik hali, yürürlük 01.01.2026; Kaliforniya Yasama Meclisi toplu veri dosyası) karşılaştırıldı. Eksikler eklendi: perborat ve boratların ek CAS'ları, musk ketone (yasak değil üst sınır; yeni sarı liste `ca_sinir`).
- **ASEAN — KAPANDI:** Mikonazol, Singapur HSA'nın yayımladığı resmi ASEAN ekleriyle (sürüm 2026-1, 22.06.2026) doğrulandı; aynı sürümde eklenen 4 mantar ilacı (bifonazol, klotrimazol, tiyabendazol, tiyokonazol) eklendi.
- **AB taslağı — KAPANDI:** `ab_taslak` satırları Komisyon'un Konsey'e 21.09.2026'da ilettiği resmi taslakla (D117774) doğrulandı; taslaktaki diğer maddeler (Basic Brown 16, Basic Blue 99, prostaglandin benzeri kirpik serumu maddeleri, cıvalı koruyucular, CBD sınırı) eklendi. Kabul edilince güncelleme tablosuna taşınmalı.
- **REACH D4/D5/D6 — KAPANDI:** (EU) 2024/1328 resmi metniyle doğrulandı; D6 tarihi düzeltildi (durulanan üründe de 6 Haziran 2027).
- **AB endokrin listesi:** Komisyon sayfasında (07.10.2026) B grubu için yeni veri çağrısı yok; 28 madde değişmedi. Taslak tüzük B grubundan 4 maddeyi kapsıyor.
- **SIN List — AÇIK (kullanıcı işi):** ChemSec'ten yazılı izin gerekiyor (info@chemsec.org). Kod tarafında yapılacak bir şey yok; izin gelince liste eklenir.
- Kalan `inceleme=1` satırlar ikincil kaynaklı listeler: Danimarka (resmi duyuru bulunamadı), Fransa ANSES (Légifrance metni okunmadı), komedojenite (Fulton 1989 taranmış tablo), Türkiye taslağı (resmi metin yok).

## ocr.html tek dosyada — KAPANDI (04.10.2026)
- ~1.550 satırlık ocr.html gıda, kozmetik, temizlik ve arayüz kodunu birlikte taşıyordu. Kod `js/` klasöründe alana göre 9 dosyaya bölündü (derleme adımı yok, davranış değişmedi; eski ve yeni sayfanın sonuç ekranları tarayıcıda birebir karşılaştırıldı). Kalan: arayüz kodunun sözdizimi dışında otomatik testi yok (tarayıcı testi CI'da çalışmıyor).

## Veri kod dosyalarının içinde — KAPANDI (04.10.2026)
- Üreteçlerdeki (gen_e_kodlari.py 120 KB, gen_e_aciklama.py, gen_bilesenler.py, gen_temizlik.py, gen_kozmetik.py) gömülü veri `kaynak/` altındaki JSON/TSV dosyalarına taşındı: `e_kodlari_maddeler.json`, `e_kodlari_ek.json`, `e_aciklama.tsv`, `bilesenler.json`, `temizlik_ifadeler.tsv`, `temizlik_birlesik.tsv`, `temizlik_onlemler.tsv`, `temizlik_gruplar.json`, `kozmetik_listeler.json`, `kozmetik_islevler.tsv`, `kozmetik_tr_sozcukler.tsv`, `kozmetik_abd_renkler.tsv`. Üretilen data/*.json dosyaları birebir aynı kaldı.
- CI ("Testler") üreteçleri çalıştırıp data/ değişmiş mi diye bakar: kaynak dosya düzeltilip üreteç çalıştırılmazsa ya da JSON elle düzenlenirse hata verir.

## CosIng verisi depo dışında — KAPANDI (04.10.2026)
- gen_kozmetik.py artık `../cosing` kopyasına ihtiyaç duymaz; kullanılan kısım `kaynak/cosing/` altında (Ek II–VI aynen, INCI listesinden 3 sütun; ~3 MB, sürüm `surum.txt`, lisans `LICENSE.txt`). Yenilemek için `python3 cosing_al.py`. Verinin eski olması (2024 başı) ayrı sorun, bkz. 4.


## Temizlik: "Adı Yazılan Maddeler" bölümü (UX, 04.10.2026) — 1, 2, 3, 4, 6 KAPANDI (05.10.2026), 5 AÇIK
Bölüm etikette adı yazan maddeleri gösteriyor (js/arayuz_temizlik.js, renderT): notu olanlar (MIT, BIT, hipoklorit…) kart, diğerleri düz liste. 05.10.2026: sonuç ekranı gıda/kozmetik düzenine getirildi: tek "Dikkat Gerektirenler" başlığı (karıştırma, kapsül, tehlike ifadeleri, madde notları kart olarak; madde notunun ilk iki cümlesi görünür), listeler kapalı açılır bölümlerde ("Önlem İfadeleri", "İçerik Grupları", "Tanınan Maddeler"; tüm tanınan maddeler, CosIng notu altta, ad ve "Koruyucu" çipi tekrarı yok).

Alt maddeler:
1. Başlık özetteki "Tanınan madde" satırıyla uyuşmuyor; "Tanınan Maddeler" olmalı. — KAPANDI
2. Madde kartlarında açıklama yalnızca (i) arkasında; tehlike kartlarındaki gibi bir satırlık açıklama görünmeli. — KAPANDI
3. Kartlar ve düz liste karışık; liste "Diğer maddeler (N)" adıyla kapalı açılır bölüme (secBox) girmeli. — KAPANDI
4. "İşlevler AB…" notu bölümün başında; listenin altına inmeli. — KAPANDI
5. Adlar İngilizce ve büyük harf (INCI); yanına Türkçe ad eklenmeli (LIMONENE · limonen). Veri hazırlığı gerekir. — AÇIK
6. İşlev adı tekrarı ("PARFUM · Koku, Parfüm") kaldırılmalı. — KAPANDI


## Paylaşım sayacı KV bağlaması — KAPANDI (06.10.2026)
- `paylasim-sayac` KV namespace'i Cloudflare panelinde oluşturuldu, ID `worker/wrangler.toml` içinde `SAYAC` olarak bağlandı. Dağıtımdan sonra /sayac sayım yapar (ürün, metin, IP saklanmaz).

## Ansiklopedi: eksik bilgiler (05.10.2026)
Ansiklopedi yalnızca E kodlarını kapsıyor (333 sayfa). Temizlik ve kozmetikte ansiklopedi sayfası yok. Aşağıdakiler bilerek sonraya bırakıldı; sayılar `data/ansiklopedi.json`, `data/e_kodlari.json`, `data/kozmetik.json`, `data/temizlik.json`'dan 05.10.2026'da sayıldı.

### Gıda (E kodları)
- 300 sayfa elle incelenmiş (`review=curated`), **33 sayfa otomatik** (`review=auto`; 06.10.2026'da 6. parti ile 39, 7. ve 8. partilerle 40'ar madde eklendi). Otomatik sayfada yalnızca bir satırlık ortak açıklama (`e_aciklama`), kategori işlevi ve e_kodlari.json'dan gelen kurum satırı var. Bunların hepsinde eksik: "Nerelerde bulunur" (`found_in`), "Vücutta" (`in_the_body`), kanıt düzeyi, inceleme tarihi, madde özel özet.
- ÇÖZÜLDÜ (06.10.2026, 6. parti): 11 renkli madde (E123, E154, E160f, E216, E217, E230, E284, E285, E320, E924a, E952) resmi kaynakla elle yazıldı; e_kodlari kaynakları Wikipedia/ikincil siteler yerine EFSA, EUR-Lex, JECFA/IARC (inchem), FDA. Gerekçe düzeltmeleri: E154 (EFSA 2010, 1129/2011), E230 (2003/114/AT), E924a (IARC 1999), E952 ("1996" ve "1970" kaldırıldı; SCF 2000), E216/E217 (2006/52/AT; "doğrulanmalı" kalktı). Aynı partide koruyucular (E214, E215, E218, E219, E239, E242, E243, E261–E263, E1105), lezzet artırıcılar (E626–E635, E640, E650), tatlandırıcılar (E957, E959, E960, E961, E969).
- 6. partiden açık kalanlar:
  - E920 (L-sistein) atlandı: AB kullanım koşulları ve kaynak (kıl/hayvansal/mikrobiyal) şartnamesi okunamadı, EFSA katkı değerlendirmesi yok.
  - E285: boraksın CLP Repr. 1B sınıflandırması resmi kaynakta doğrulanamadı (yalnızca borik asit için, Tüzük 790/2009); gerekçe metni değiştirilmedi.
  - California AB 418 kaynağı LegiScan kopyası (leginfo 403); eCFR ve SCF (food.ec.europa.eu) kaynakları resmi alan listesinde olmadığı için `official:false`.
  - KAPANDI (07.10.2026): Yeşil maddelerin tarama ekranı gerekçeleri (E239, E242, E243, E261–E263, E626–E629, E640, E650) ansiklopedideki EFSA/JECFA kaynaklarıyla yeniden yazıldı (`kaynak/e_kodlari_ek.json` `dogrulama`). Paraben grubundaki (E214, E215, E218, E219) desteklenmeyen "endokrin etkileri tartışmalı" ifadesi ve `debated` bayrağı kaldırıldı; gerekçe EFSA 2004 grup ADI'sine dayanıyor.
  - E626–E635 `uretim` kaynağı: yem tüzüğü (CELEX:32018R0238) kaynak olarak kaldırıldı, kayıt "doğrulanmadı" (`dogrulandi=0`) oldu (07.10.2026). Gıda katkısı için resmi üretim kaynağı hâlâ bulunmadı (`vegan: unknown`).
  - AB kullanım koşulları çoğunlukla legislation.gov.uk'nin 31.12.2020 anlık görüntüsünden; güncel konsolide EUR-Lex metni okunamadı. TGK 2023 (Resmî Gazete) okunamadı, TR durumu 2013 listesine göre.
- ÇÖZÜLDÜ (06.10.2026, 7. parti): 40 asitlik düzenleyici (E260–E524 arası). EFSA yeniden değerlendirmesi olanlar: tartaratlar E334–E337, E353, E354 (2020), klorürler E507–E509, E511 (2019), sülfatlar E513–E517 (2019), E512 (2018). Diğerleri JECFA + AB Ek II (çoğu Grup I, quantum satis) kaynaklı, kanıt düzeyi "sınırlı". AB 2024/1451 ile tartaratlar Grup I'den çıkıp üst sınırlı yeni gruba alındı (16.12.2024).
- 7. partiden açık kalanlar:
  - KAPANDI (07.10.2026, kullanıcı kararı): Ortak gerekçe (`DEFAULT_REASON`) "…bu uygulamada ayrıntılı bir değerlendirme yapılmadı." oldu; kurum değerlendirmesi yokmuş gibi okunmuyor.
  - E270 üretim kaynağı 2008/84/AT direktifi; yürürlükten kalkmış olabilir, doğrulanmadı. E353 üretim kaynağı oiv.int (resmi değil); resmi karşılığı AB 2019/934.
  - legislation.gov.uk Ek II tabloları 31.12.2020 anlık görüntüsü; E355–E357 için dolgu ve içecek tozu kullanımları okunamadı (429).
- ÇÖZÜLDÜ (06.10.2026, 8. parti): asitlik düzenleyiciler E525–E530, E574–E579, E585; kıvam artırıcılar E405, E406, E413, E416–E418, E425–E427, E441, E1204; gazlar E290, E938, E939, E941–E944, E948, E949; dengeleyiciler E444, E445, E459, E999, E1201, E1202.
- 8. partiden açık kalanlar:
  - KAPANDI (07.10.2026, kullanıcı kararı): E459 (beta-siklodekstrin) K6 ölçütüyle sarıya geçti (EFSA 2016: markaya bağlı tüketim senaryosunda ADI aşımı), E407/E968 ile aynı.
  - KAPANDI (07.10.2026): E425 (konjak) tarama gerekçesine EFSA 2017 günde 3 g koşulu ve AB 2003/52/AT jöleli şekerleme yasağı yazıldı. Risk rengi yeşil kaldı (K1–K7 ölçütlerinden hiçbirine girmiyor).
  - E579/E585 kategorisi "asitlik düzenleyici"; JECFA'ya göre renk stabilizatörü, AB'de yalnızca zeytinde (150 mg/kg demir olarak).
  - E441 (jelatin) AB 1333/2008 Madde 3'e göre katkı maddesi sayılmıyor; e_kodlari.json'da kaynağı yok.
- Kalan otomatik sayfalar, hepsi yeşil (33), kategoriye göre:
  - Emülgatörler (1): E431 (EFSA yeniden değerlendirmesi bulunamadı)
  - Antioksidanlar (1): E385 (EFSA görüşü yok; 2024 veri çağrısı açık)
  - Diğer (9): E920, E927b, E1103, E1200, E1505, E1517, E1518, E1519, E1521
  - Parlatıcılar (10): E901, E902, E903, E904, E905, E907, E912, E914, E1203, E1205
  - Topaklanmayı önleyiciler (8): E535, E536, E538, E551, E552, E553a, E553b, E558
  - Renklendiriciler (4): E101, E160d, E162, E172
- Yapılacak: her madde için EFSA/AB 1333/2008 kaynaklı elle kayıt (`kaynak/ansiklopedi.json` `kayitlar`), aynı biçim ve `test/ansiklopedi.js` doğrulamasıyla. Kaynağı güvenilir okunamayanlar (E101, E160d, E162, E172 gibi) otomatik kalabilir, nedeni kayda yazılır.
- **"Vücutta ne olur?" alanı kullanıcı beklentisini karşılamıyor (05.10.2026, kullanıcı geri bildirimi).** Kullanıcı belirti bekliyor (baş ağrısı, ishal gibi). Alan ise metabolizma ve kurum kararını anlatıyor. 181 elle kayıttan 172'sinde EFSA/ADI/IARC cümlesi var ve bu, "Kurumlar" bölümünü tekrar ediyor. Yalnızca 28 kayıtta belirti ya da hassasiyet geçiyor. Örnek: E440 "değişmeden emilmez… EFSA 2017 ADI gerekmedi". 33 otomatik sayfada alan hiç yok.
  - Önerilen çözüm (seçilmedi, önce kısa plan): `in_the_body` yerine yapılandırılmış "Olası etkiler" listesi. Her satırda belirti, kimde, hangi miktarda, kanıt düzeyi ve kaynak olur. Belirti yoksa "Normal kullanımda bilinen bir yan etki yok (kaynak, yıl)" yazılır. EFSA/ADI cümleleri Kurumlar bölümüne taşınır. Kısa bir "vücutta nasıl işlenir" satırı kalabilir.
  - Kurallar: Kaynak zorunlu (EFSA, JECFA, AB etiket zorunluluğu, hakemli derleme). Kanıt düzeyi üç seviyedir: "Resmi uyarı", "Duyarlı kişilerde bildirildi", "Kanıt tutarsız" (örneğin MSG ve baş ağrısı). Anekdot yazılmaz. Dil "yapar" değil "yol açabilir / bildirilmiştir" olur, miktar ve kişi belirtilir, teşhis ya da tedavi önerisi verilmez. Sabit bir "Şikâyetiniz varsa hekime danışın" notu eklenir. Belirtiler renk almaz, kırmızı yine yalnızca kişisel uyarıda kalır. Dil hukuki görüş maddesine de girer.
  - Alternatifler: Mevcut serbest metni belirti odaklı yeniden yazmak daha hızlıdır ama kaynak ve kanıt satır satır görünmez. Yalnızca başlığı "Güvenlik değerlendirmesi" yapmak en ucuz yoldur ama beklentiyi karşılamaz.
  - İlk parti önerisi: belirti zaten geçen 28 kayıt, polioller (E420, E421, E953, E965–E968), Southampton renkleri, sülfitler (E220–E228).

### Kozmetik
- Ansiklopedi sayfası yok. Veride 2.009 AB kaydı (`kozmetik.json`) ve 35.081 INCI adı (`kozmetik_inci.json`) var; yalnızca durum/gerekçe cümlesi ve CosIng işlevi var, "ne işe yarar / nerelerde bulunur / vücutta" açıklaması yok.
- `tr` (Türkiye ek durumu): Türk ekleriyle satır satır karşılaştırıldı; yalnızca 2024 sonrası AB değişikliklerinde ve bor bileşiklerinde dolu, diğerleri AB ile aynı (bkz. 4).
- 225 kaydın bayrağı var; 302'si bilgi (komedojenite vb.) düzeyinde. En çok aranan ~200–300 yaygın madde (UV filtreleri, koruyucular, parabenler, yağlar, asitler, koku alerjenleri) için elle kayıt öncelikli; tamamı gerekmez.
- Yapılacak: ansiklopedi modeline `product_types: cosmetic` kayıtları (model ve doğrulama bunu zaten kabul ediyor), kayıt anahtarı INCI.

### Temizlik
- Ansiklopedi sayfası yok. `temizlik.json`: 8 madde notu (`subs`: MIT/CMIT/BIT/OIT, sodyum hipoklorit, asit, amonyak, enzimler), 22 içerik grubu, 98 temizliğe özgü eş anlamlı. Notu olmayan yaygın maddeler (LAS, SLES, STPP, perkarbonat, kostik soda, butil glikol, DDAC, zeolit, EDTA, sitrik asit…) yalnızca "tanınan madde" olarak CosIng işleviyle listeleniyor; açıklama yok.
- H/EUH/P ifadelerinin Türkçesi: EUH ve 23 P ifadesi çeviri (needs_review), SEA Yönetmeliği resmi metni okunamadı.
- Yapılacak: önce bu ~30 yaygın madde için kısa kayıt (ne işe yarar, nerede kullanılır, hangi H ifadesi), sonra ansiklopedi sayfası.
