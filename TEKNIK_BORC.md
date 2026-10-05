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
- ÇÖZÜLDÜ (04.10.2026): Yazı tipleri depoda (şimdi Bricolage Grotesque + Figtree; Schibsted kaldırıldı 04.10.2026) (fonts/, SIL OFL 1.1, @fontsource 5.3.0; latin + latin-ext, 400/600/800 woff2). Google'a istek gitmiyor; service worker önbelleğe alıyor (tagsis-v5).

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


## Temizlik: "Adı Yazılan Maddeler" bölümü (UX, 04.10.2026) — 1, 2, 3, 4, 6 KAPANDI (05.10.2026), 5 AÇIK
Bölüm etikette adı yazan maddeleri gösteriyor (js/arayuz_temizlik.js, renderT): notu olanlar (MIT, BIT, hipoklorit…) kart, diğerleri düz liste. 05.10.2026: sonuç ekranı gıda/kozmetik düzenine getirildi: tek "Dikkat Gerektirenler" başlığı (karıştırma, kapsül, tehlike ifadeleri, madde notları kart olarak; madde notunun ilk iki cümlesi görünür), listeler kapalı açılır bölümlerde ("Önlem İfadeleri", "İçerik Grupları", "Tanınan Maddeler"; tüm tanınan maddeler, CosIng notu altta, ad ve "Koruyucu" çipi tekrarı yok).

Alt maddeler:
1. Başlık özetteki "Tanınan madde" satırıyla uyuşmuyor; "Tanınan Maddeler" olmalı. — KAPANDI
2. Madde kartlarında açıklama yalnızca (i) arkasında; tehlike kartlarındaki gibi bir satırlık açıklama görünmeli. — KAPANDI
3. Kartlar ve düz liste karışık; liste "Diğer maddeler (N)" adıyla kapalı açılır bölüme (secBox) girmeli. — KAPANDI
4. "İşlevler AB…" notu bölümün başında; listenin altına inmeli. — KAPANDI
5. Adlar İngilizce ve büyük harf (INCI); yanına Türkçe ad eklenmeli (LIMONENE · limonen). Veri hazırlığı gerekir. — AÇIK
6. İşlev adı tekrarı ("PARFUM · Koku, Parfüm") kaldırılmalı. — KAPANDI


## Ansiklopedi: eksik bilgiler (05.10.2026)
Ansiklopedi yalnızca E kodlarını kapsıyor (333 sayfa). Temizlik ve kozmetikte ansiklopedi sayfası yok. Aşağıdakiler bilerek sonraya bırakıldı; sayılar `data/ansiklopedi.json`, `data/e_kodlari.json`, `data/kozmetik.json`, `data/temizlik.json`'dan 05.10.2026'da sayıldı.

### Gıda (E kodları)
- 181 sayfa elle incelenmiş (`review=curated`), **152 sayfa otomatik** (`review=auto`; 05.10.2026'da 5. parti ile 40 madde eklendi). Otomatik sayfada yalnızca bir satırlık ortak açıklama (`e_aciklama`, 171 farklı metin), kategori işlevi ve e_kodlari.json'dan gelen kurum satırı var. Bunların hepsinde eksik: "Nerelerde bulunur" (`found_in`), "Vücutta" (`in_the_body`), kanıt düzeyi, inceleme tarihi, madde özel özet. (192 sayfa döneminde sayılmıştı: 188'inde vegan durumu `unknown`, 139'unda profil uyarısı yok.)
- Öncelik 1, renkli (resmi kaynağı olduğu hâlde otomatik kalan, kaynak bulununca elle yazılacak, 11): E123, E154, E160f, E216, E217, E230, E284, E285, E320, E924a, E952.
- Öncelik 2, yeşil (141), kategoriye göre:
  - Asitlik düzenleyiciler (53): E260, E270, E296, E297, E325, E326, E327, E330, E331, E332, E333, E334, E335, E336, E337, E350, E351, E352, E353, E354, E355, E356, E357, E363, E380, E500, E501, E503, E504, E507, E508, E509, E511, E512, E513, E514, E515, E516, E517, E524, E525, E526, E527, E528, E529, E530, E574, E575, E576, E577, E578, E579, E585
  - Emülgatörler (1): E431 (EFSA yeniden değerlendirmesi bulunamadı)
  - Koruyucular (11): E214, E215, E218, E219, E239, E242, E243, E261, E262, E263, E1105
  - Antioksidanlar (1): E385 (EFSA görüşü yok; 2024 veri çağrısı açık)
  - Lezzet artırıcılar (12): E626, E627, E628, E629, E630, E631, E632, E633, E634, E635, E640, E650
  - Kıvam artırıcılar (11): E405, E406, E413, E416, E417, E418, E425, E426, E427, E441, E1204
  - Diğer (9): E920, E927b, E1103, E1200, E1505, E1517, E1518, E1519, E1521
  - Gazlar (10): E290, E938, E939, E941, E942, E943a, E943b, E944, E948, E949
  - Parlatıcılar (10): E901, E902, E903, E904, E905, E907, E912, E914, E1203, E1205
  - Topaklanmayı önleyiciler (8): E535, E536, E538, E551, E552, E553a, E553b, E558
  - Dengeleyiciler (6): E444, E445, E459, E999, E1201, E1202
  - Tatlandırıcılar (5): E957, E959, E960, E961, E969
  - Renklendiriciler (4): E101, E160d, E162, E172
- Yapılacak: her madde için EFSA/AB 1333/2008 kaynaklı elle kayıt (`kaynak/ansiklopedi.json` `kayitlar`), aynı biçim ve `test/ansiklopedi.js` doğrulamasıyla. Kaynağı güvenilir okunamayanlar (E101, E160d, E162, E172 gibi) otomatik kalabilir, nedeni kayda yazılır.
- **"Vücutta ne olur?" alanı kullanıcı beklentisini karşılamıyor (05.10.2026, kullanıcı geri bildirimi).** Kullanıcı belirti bekliyor (baş ağrısı, ishal gibi). Alan ise metabolizma ve kurum kararını anlatıyor. 181 elle kayıttan 172'sinde EFSA/ADI/IARC cümlesi var ve bu, "Kurumlar" bölümünü tekrar ediyor. Yalnızca 28 kayıtta belirti ya da hassasiyet geçiyor. Örnek: E440 "değişmeden emilmez… EFSA 2017 ADI gerekmedi". 152 otomatik sayfada alan hiç yok.
  - Önerilen çözüm (seçilmedi, önce kısa plan): `in_the_body` yerine yapılandırılmış "Olası etkiler" listesi. Her satırda belirti, kimde, hangi miktarda, kanıt düzeyi ve kaynak olur. Belirti yoksa "Normal kullanımda bilinen bir yan etki yok (kaynak, yıl)" yazılır. EFSA/ADI cümleleri Kurumlar bölümüne taşınır. Kısa bir "vücutta nasıl işlenir" satırı kalabilir.
  - Kurallar: Kaynak zorunlu (EFSA, JECFA, AB etiket zorunluluğu, hakemli derleme). Kanıt düzeyi üç seviyedir: "Resmi uyarı", "Duyarlı kişilerde bildirildi", "Kanıt tutarsız" (örneğin MSG ve baş ağrısı). Anekdot yazılmaz. Dil "yapar" değil "yol açabilir / bildirilmiştir" olur, miktar ve kişi belirtilir, teşhis ya da tedavi önerisi verilmez. Sabit bir "Şikâyetiniz varsa hekime danışın" notu eklenir. Belirtiler renk almaz, kırmızı yine yalnızca kişisel uyarıda kalır. Dil hukuki görüş maddesine de girer.
  - Alternatifler: Mevcut serbest metni belirti odaklı yeniden yazmak daha hızlıdır ama kaynak ve kanıt satır satır görünmez. Yalnızca başlığı "Güvenlik değerlendirmesi" yapmak en ucuz yoldur ama beklentiyi karşılamaz.
  - İlk parti önerisi: belirti zaten geçen 28 kayıt, polioller (E420, E421, E953, E965–E968), Southampton renkleri, sülfitler (E220–E228).

### Kozmetik
- Ansiklopedi sayfası yok. Veride 1.972 AB kaydı (`kozmetik.json`) ve 30.609 INCI adı (`kozmetik_inci.json`) var; yalnızca durum/gerekçe cümlesi ve CosIng işlevi var, "ne işe yarar / nerelerde bulunur / vücutta" açıklaması yok.
- `tr` (Türkiye ek durumu) 1.942 kayıtta boş (Resmî Gazete satır satır karşılaştırılamadı, bkz. 4).
- 225 kaydın bayrağı var; 302'si bilgi (komedojenite vb.) düzeyinde. En çok aranan ~200–300 yaygın madde (UV filtreleri, koruyucular, parabenler, yağlar, asitler, koku alerjenleri) için elle kayıt öncelikli; tamamı gerekmez.
- Yapılacak: ansiklopedi modeline `product_types: cosmetic` kayıtları (model ve doğrulama bunu zaten kabul ediyor), kayıt anahtarı INCI.

### Temizlik
- Ansiklopedi sayfası yok. `temizlik.json`: 8 madde notu (`subs`: MIT/CMIT/BIT/OIT, sodyum hipoklorit, asit, amonyak, enzimler), 22 içerik grubu, 98 temizliğe özgü eş anlamlı. Notu olmayan yaygın maddeler (LAS, SLES, STPP, perkarbonat, kostik soda, butil glikol, DDAC, zeolit, EDTA, sitrik asit…) yalnızca "tanınan madde" olarak CosIng işleviyle listeleniyor; açıklama yok.
- H/EUH/P ifadelerinin Türkçesi: EUH ve 23 P ifadesi çeviri (needs_review), SEA Yönetmeliği resmi metni okunamadı.
- Yapılacak: önce bu ~30 yaygın madde için kısa kayıt (ne işe yarar, nerede kullanılır, hangi H ifadesi), sonra ansiklopedi sayfası.
