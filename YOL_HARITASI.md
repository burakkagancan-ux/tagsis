# Yol haritası: küresel Tağşiş

Bu dosya projenin ana iş planıdır. Her oturumun başında okunur. Bir iş başlayınca, bitince ya da plan değişince aynı PR içinde güncellenir (durum, tarih, PR numarası).
İlk yazım: 08.10.2026 (rakip analizi ve kullanıcı kararıyla). Son güncelleme: 08.10.2026.

Durum işaretleri: ⬜ başlamadı · 🔄 sürüyor · ✅ bitti · ⏸ bekletiliyor · 👤 kullanıcının işi

---

## 0. Vizyon ve ilkeler (değişmez)

- **Amaç:** Para kazanan, küresel bir uygulama. Hedef onlarca dil (belki 60). Türkiye ilk pazar, son değil.
- **İlke:** Her bilgi kaynağa dayalı, tarafsız ve bilimsel. Gelir bu ilkeyi bozamaz.
  - Markadan para, reklam ya da ücretli sıralama yok.
  - Güvenlik uyarıları, kaynaklar ve kişisel hassasiyet uyarıları her zaman ücretsiz. Ücretli katmanda yalnızca kolaylık özellikleri olur.
  - Skor yok. "Güvenli / zararlı" denmez. Dil olasılık bildirir ("yol açabilir / bildirilmiştir").
- **Konumlanma:** "Etiketi okuyan, her uyarısının kaynağını gösteren, puan vermeyen tarayıcı. Gıda, kozmetik ve temizlik için tek uygulama." Rakiplerin en zayıf yeri bilimsel güvenilirlik; bizim en güçlü yerimiz bu.

### Her yeni özellik için ilke denetimi
Her PR açıklamasında bu beş soru yanıtlanır:
1. Gösterilen her bilginin resmi ya da hakemli bir kaynağı var mı?
2. Bir markayı, reklamı ya da geliri kayıran bir şey var mı? (Olmamalı.)
3. Güvenlik bilgisi ücretli katmana mı kaydı? (Kaymamalı.)
4. Yeni metin çeviri anahtarıyla mı yazıldı? Türkçe sabit metin eklendi mi?
5. Mevzuata bağlı bilgi ülke katmanında mı, yoksa tek ülkeye mi gömüldü?

---

## 1. Bugünkü durum (08.10.2026)

- **Ürün:** Tarayıcıdan çalışan uygulama (PWA). Bakanlık taklit/tağşiş listesi; fotoğraftan etiket okuma (gıda, kozmetik, temizlik); 333 sayfalık kaynaklı E kodu ansiklopedisi; karşılaştırma; kaydedilen ürünler; paylaşım kartı (hikâye ve gönderi boyutu).
- **Diller:** Yalnızca Türkçe. Çok dil altyapısı başladı (G-01).
- **Mevzuat:** AB, Türkiye (TGK 2013 listesi, kozmetik ekleri), ABD (FDA renkleri), Kaliforniya, ASEAN, AB endokrin listeleri, REACH.
- **Dağıtım:** GitHub Pages. Mağazada yok.
- **Gelir:** Yok, model seçilmedi.
- **Rakipler (ayrıntı: §8):** Yuka (85 milyon kullanıcı iddiası, 2025 geliri ~11,9 M$, Türkiye'de yok), Open Food Facts, CodeCheck, INCI Beauty, Think Dirty, EWG, Olive, Fig. Türkiye'de ÇabukBak ve Ürün Dedektörü (küçük, barkodlu, puanlı).

---

## 2. Fazlar

| Faz | Amaç | Çıkış ölçütü |
|---|---|---|
| **A. Temel** | Türkiye'de ürünü olgunlaştırmak | Telefon testleri tamam, besin değeri tablosu var, ölçüm çalışıyor |
| **B. Küresel altyapı** | Yeni dil ve ülke eklemeyi veri işine indirmek | İngilizce arayüz yayında, ülke katmanı çalışıyor, yeni dil eklemek = bir çeviri dosyası |
| **C. Mağaza ve hız** | Bulunurluk, hız, maliyet | Android ve iOS mağazada, cihaz içi okuma, barkod |
| **D. Gelir** | Sürdürülebilir gelir, ilkeyi bozmadan | Premium satışta, Bağımsızlık sayfası yayında |
| **E. Güven ve yönetişim** | Küresel ölçekte güven ve hukuki koruma | Yöntem sayfası, değişiklik kaydı, danışma kurulu, hukuki görüş |
| **F. Pazarlar** | Türkiye'den dünyaya | Sırayla: Türkiye → DACH ve Benelux → İngilizce pazarlar → MENA → ABD → 60 dil |

Fazlar kısmen paralel yürür. A ve B şimdi; C, B'nin ilk PR'larından sonra; D, C'den sonra (mağaza içi satın alma gerekiyor); E'nin bir kısmı her fazda; F, C'den sonra.

---

## 3. İş paketleri

Sütunlar: kimlik · iş · sahibi · bağımlılık · kabul ölçütü · durum.

### Faz A: Temel

| Kimlik | İş | Sahibi | Bağımlı | Kabul ölçütü | Durum |
|---|---|---|---|---|---|
| A-01 | Telefon testleri ve sonuçlara göre ayar | 👤 + Claude | — | Kullanıcının bulduğu her sorun PR'la kapanır | 🔄 👤 |
| A-02 | Besin değeri tablosu (şeker, yağ, doymuş yağ, tuz; 100 g başına; NHS/AB eşikleri; puansız renkli gösterim) | Claude | — | Etiketteki tablo okunur, eşik kaynakları görünür, testli | ⬜ |
| A-03 | Gizlilik dostu ölçüm: günlük tarama, mod, paylaşım, 7 gün sonra geri dönüş (kişisel veri ve metin yok; Worker KV) | Claude | — | Kişisel veri gönderilmez, KVKK notu güncellenir | ⬜ |
| A-04 | Fotoğraf okuma kalitesi: iki sütunlu etiket, kavisli ambalaj, otomatik kırpma önerisi | Claude | — | Gerçek etiket setinde ölçülen iyileşme | ⬜ |
| A-05 | Helal katmanı ("kaynağı belirsiz, sertifikaya bakın"; hüküm vermez) | Claude | — | Kaynaklı, yalnızca bilgi; MENA pazarının ön koşulu | ⬜ |
| A-06 | Aylık mevzuat izleme (EUR-Lex, Resmî Gazete; CosIng zaten var) | Claude | — | Değişiklik varsa otomatik issue ya da PR | ⬜ |

### Faz B: Küresel altyapı

| Kimlik | İş | Sahibi | Bağımlı | Kabul ölçütü | Durum |
|---|---|---|---|---|---|
| B-01 | Çok dil altyapısı: t() işlevi, i18n/tr.json, Intl tarih/sayı/çoğul, sağdan sola hazırlığı, yedek yazı tipi mekanizması; arayüz metinleri anahtara taşınır, Türkçe görünüm birebir aynı | Claude (bulut, `claude/cok-dil`) | — | Mevcut testler değişmeden geçer, test/ceviri.js eklenir | 🔄 |
| B-02 | İngilizce arayüz (en.json, dil seçici, terim sözlüğü i18n/sozluk.md) | Claude (bulut) | B-01 | İngilizce modda arayüz testi geçer, paylaşım kartı taşmaz | ⬜ |
| B-03 | Ana içerik dili İngilizce: ansiklopedi, gerekçeler ve notlar önce İngilizce yazılır, Türkçe dahil öteki diller oradan çevrilir | Claude | B-02 | Yeni içerik İngilizce anahtarla girer; mevcut Türkçe içeriğin çevrilme oranı raporlanır | ⬜ |
| B-04 | Resmi çok dilli adlar: AB katkı adları ve CLP ifadeleri (24 AB dili, resmi metin), Open Food Facts madde sözlüğü (ODbL, atıfla) | Claude | B-01 | Kaynak ve lisans her dosyada yazılı | ⬜ |
| B-05 | Ülke mevzuat katmanı: kullanıcının ülkesine göre öne çıkan kural; yeni ülke = yeni veri dosyası. İlk eklenecekler: Birleşik Krallık (FSA), ABD (FDA katkı listeleri) | Claude | B-01 | Türkiye/AB/ABD/Birleşik Krallık aynı modelde; kodda ülke adı geçmez | ⬜ |
| B-06 | Çeviri iş akışı: resmi çeviri > makine çevirisi + uzman kontrolü; her metinde "kontrol edildi / edilmedi" işareti; 60 dile ölçeklenir | Claude + 👤 (çevirmen bulmak) | B-02 | Kontrol edilmemiş metin arayüzde işaretli | ⬜ |
| B-07 | Latin dışı alfabeler: Noto yazı tipi yedeği, sağdan sola yerleşim (Arapça, Farsça, İbranice, Urduca) | Claude | B-01 | İlk Latin dışı dil eklenince | ⬜ |
| B-08 | İngilizce etiketlerde madde tanıma ölçümü ve eksik eş anlamlılar | Claude | B-02 | 10+ gerçekçi İngilizce etikette ölçüm | ⬜ |

### Faz C: Mağaza ve hız

| Kimlik | İş | Sahibi | Bağımlı | Kabul ölçütü | Durum |
|---|---|---|---|---|---|
| C-01 | Geliştirici hesapları: Google Play (tek sefer 25 $), Apple Developer (yıllık 99 $); mümkünse şirket adına (bkz. D-06) | 👤 | — | Hesaplar açık | ⬜ 👤 |
| C-02 | Android sürümü (TWA ya da Capacitor), kapalı test, sonra yayın | Claude | C-01 | Play Store'da yayında | ⬜ |
| C-03 | iOS sürümü (Capacitor) | Claude | C-01 | App Store'da yayında | ⬜ |
| C-04 | Cihaz içi metin okuma (Google ML Kit / Apple Vision); Google Vision yedek kalır. Tarama maliyeti sıfırlanır, bütün alfabeler okunur | Claude | C-02, C-03 | İnternetsiz okuma çalışır | ⬜ |
| C-05 | Barkod: önce ölçüm (Türkiye'de en çok satılan 100 ürünün kaçı Open Food Facts'te), sonra karma model (barkod → veritabanı, yoksa fotoğraf). Kullanıcı izniyle fotoğraf taraması barkodla eşleşir, Türkiye veritabanı büyür, Open Food Facts'e geri katkı verilir | Claude | C-02 | Ölçüm raporu; karar kullanıcıda | ⬜ |
| C-06 | Mağaza sayfaları çok dilli (ekran görüntüleri, açıklama) | Claude | B-02, C-02 | Türkçe ve İngilizce sayfa | ⬜ |
| C-07 | Alternatif ürün önerisi (aynı kategoride daha az uyarılı ürün; markadan para alınmaz) | Claude | C-05 | Yalnızca veritabanı yeterliyse | ⬜ |

### Faz D: Gelir

| Kimlik | İş | Sahibi | Bağımlı | Kabul ölçütü | Durum |
|---|---|---|---|---|---|
| D-01 | Gelir modeli kararı. Öneri: ücretsiz çekirdek + Premium kolaylık. **Her zaman ücretsiz:** bütün uyarılar, kaynaklar, kişisel uyarılar, ansiklopedi, paylaşım. **Premium adayları:** sınırsız kayıt ve geçmiş, aile profilleri, cihazlar arası eşitleme, gelişmiş karşılaştırma, internetsiz tam veri, reklamsız (zaten reklam yok) destek rozeti | 👤 karar, Claude öneri | — | Liste bu dosyaya yazılır | ⬜ 👤 |
| D-02 | Uygulama içi satın alma (Apple/Google; komisyon %15–30) | Claude | C-02, C-03, D-01 | Satın alma çalışır, geri yükleme çalışır | ⬜ |
| D-03 | Bağımsızlık sayfası: gelir kaynakları ve dağılımı herkese açık (Yuka örneği) | Claude + 👤 | D-02 | Yılda bir güncellenir | ⬜ |
| D-04 | B2B veri ve API lisansı (kaynaklı madde veritabanı; diyetisyen, eczane, e-ticaret). Sözleşmede: lisans alan değerlendirmeyi etkileyemez | 👤 + Claude | E-01 | Örnek sözleşme maddesi ve API taslağı | ⬜ |
| D-05 | Hibeler: TÜBİTAK BiGG ve 1512, KOSGEB, AB programları. Claude başvuru metnini hazırlar, kullanıcı başvurur | 👤 + Claude | — | Uygun çağrı listesi ve takvim | ⬜ |
| D-06 | Şirketleşme, vergi, mağaza hesaplarının şirkete geçmesi | 👤 | — | — | ⬜ 👤 |

### Faz E: Güven ve yönetişim

| Kimlik | İş | Sahibi | Bağımlı | Kabul ölçütü | Durum |
|---|---|---|---|---|---|
| E-01 | Herkese açık yöntem sayfası: renk ölçütleri (K1–K7), kaynak öncelik sırası, neyi yapmadığımız (teşhis, puan) | Claude | B-02 | Türkçe ve İngilizce yayında | ⬜ |
| E-02 | Herkese açık değişiklik kaydı: her değerlendirme değişikliği tarihi ve kaynağıyla (ör. E553b sarı oldu, IARC 2025) | Claude | — | Veri değişikliklerinden otomatik üretilir | ⬜ |
| E-03 | Düzeltme süreci: "Hata bildir" → yanıt süresi hedefi → değişiklik kaydı | Claude + 👤 | E-02 | Süreç yöntem sayfasında yazılı | ⬜ |
| E-04 | Bilim danışma kurulu (gıda bilimi, toksikoloji, dermatoloji) | 👤 | — | En az bir danışman; adları yöntem sayfasında | ⬜ 👤 |
| E-05 | Hukuki görüş (KVKK/GDPR, Google Vision, "zararlı" dili, ürün adı geçen paylaşım, Bakanlık listesi gösterimi). **Tetik:** mağazaya çıkış, ilk ücretli özellik ya da ilk yurtdışı pazar; hangisi önce gelirse | 👤 | Tetik | Görüş alındı, gereken değişiklikler PR'la yapıldı | ⏸ 👤 |
| E-06 | Gizlilik politikası ve kullanım koşulları, çok dilli | Claude + 👤 | E-05 | Mağaza zorunluluğu | ⬜ |

### Faz F: Pazarlar

| Kimlik | Pazar | Neden | Ön koşul | Durum |
|---|---|---|---|---|
| F-01 | **Türkiye** (mağaza lansmanı) | Bakanlık listesi en güçlü koz; Yuka yok; yerli rakipler küçük | C-02, E-05 | ⬜ |
| F-02 | **Arama motoru sayfaları:** her madde için kaynaklı web sayfası, pazarlama bütçesi olmadan trafik | Bütün pazarlar | B-03, E-01 | ⬜ |
| F-03 | **Almanya, Avusturya, Hollanda, Belçika** (Türkçe + Almanca + Felemenkçe) | 3–4 milyon Türkçe konuşan; AB mevzuatı hazır; CodeCheck zayıf | B-02, C-02 | ⬜ |
| F-04 | **İngilizce pazarlar** (Birleşik Krallık, İrlanda, Kanada, Avustralya) | "Kanıta dayalı alternatif" konumu | B-05 (Birleşik Krallık katmanı) | ⬜ |
| F-05 | **Körfez ve MENA** (Arapça) | Yuka yok, helal talebi yüksek | A-05, B-07, GSO mevzuat katmanı | ⬜ |
| F-06 | **ABD** | En çok ödeme yapan pazar; en kalabalık | B-05 (FDA + eyaletler), D-02 | ⬜ |
| F-07 | **60 dile ölçek.** Yeni dil ölçütü: kullanıcı talebi + resmi kaynak varlığı + çeviri kontrolcüsü | Küresel hedef | B-06 | ⬜ |

### Sürekli ürün işleri (her fazla paralel)

| Kimlik | İş | Durum |
|---|---|---|
| U-01 | Kozmetik ansiklopedisi (en yaygın ~300 madde; önce İngilizce, B-03) | ⬜ |
| U-02 | Temizlik ansiklopedisi (~30 madde) | ⬜ |
| U-03 | Temizlik: AB 2026/405 dijital ürün pasaportu hazırlığı (QR'dan içerik listesi okuma; 23.09.2029'dan itibaren zorunlu) | ⬜ |
| U-04 | Gıda ansiklopedisi açıkları: AB konsolide metin karşılaştırması, TGK 2023 (TEKNIK_BORC.md) | ⏸ |
| U-05 | Kozmetik PFAS bayrağının ad düzeyine indirilmesi (TEKNIK_BORC.md) | ⬜ |
| U-06 | Gelişim alanları ve teknik borç: CLAUDE.md "Gelişim alanları" ve TEKNIK_BORC.md | 🔄 |

---

## 4. Önerilen sıra (bir sonraki iş)

1. B-01 → B-02 (çok dil, bulut oturumunda sürüyor)
2. A-02 besin değeri tablosu
3. C-01 👤 hesaplar → C-02 Android → C-04 cihaz içi okuma
4. A-03 ölçüm
5. C-05 barkod ölçümü
6. B-05 ülke katmanı, B-03 İngilizce ana içerik
7. D-01 👤 gelir kararı → D-02
8. E-05 tetik gelince hukuki görüş → F-01 Türkiye lansmanı → F-03

Sıra kullanıcı kararıyla değişebilir; değişince bu bölüm güncellenir.

---

## 5. Ölçütler

| Faz | İzlenecek |
|---|---|
| A–C | Günlük tarama, mod dağılımı, paylaşım oranı, 7 ve 30 gün sonra geri dönen kullanıcı oranı, okuma başarısı (tanınma oranı) |
| D | Premium'a geçiş oranı (kıyas: Yuka Fransa %0,3, ABD %2), kullanıcı başına gelir, iptal oranı |
| E | Hata bildirimi sayısı ve çözülme süresi, değerlendirme değişikliği sayısı |
| F | Ülke ve dil başına kullanıcı, mağaza puanı, arama motorundan gelen trafik |

---

## 6. Kullanıcıdan beklenen kararlar ve işler

- 👤 Telefon testleri (A-01, sürekli)
- 👤 Geliştirici hesapları (C-01)
- 👤 Gelir modeli kararı (D-01)
- 👤 Şirketleşme (D-06)
- 👤 Danışma kurulu (E-04)
- 👤 Hukuki görüş, tetik gelince (E-05)
- 👤 Barkod kararı, C-05 ölçümünden sonra (CLAUDE.md'deki "barkod en sona, belki hiç" kararı bu ölçümle yeniden değerlendirilecek)
- 👤 Çeviri kontrolcüleri (B-06)

---

## 7. Riskler

| Risk | Önlem |
|---|---|
| Hukuki (yeni ülkelerde "zararlı" dili, ürün adı geçen paylaşım) | Kaynaklı, olasılık dili; E-05 tetiği; yöntem sayfası |
| Çeviri hatası 60 dilde katlanır | Ana içerik İngilizce (B-03), resmi çeviri önceliği, kontrol işareti (B-06) |
| Mevzuat bakımı her ülkede yük | Otomatik izleme (A-06), ülke katmanı veri olarak (B-05) |
| Tarama maliyeti ölçekle artar (Google Vision ~1,5 $ / 1.000 görüntü) | Cihaz içi okuma (C-04) |
| Barkodlu rakiplere göre yavaşlık | A-04, C-05 |
| Kişiye bağımlılık (bir mimar + Claude) | Belgeler güncel; büyüyünce insan geliştirici ve danışman (E-04) |
| Gelir baskısı ilkeyi aşındırır | §0 kuralları, Bağımsızlık sayfası (D-03), sözleşme maddesi (D-04) |
| Yerli rakiplerin hızlanması (Ürün Dedektörü 12 dilde) | Kaynak derinliği, temizlik modu ve Bakanlık listesi ile ayrışma |

---

## 8. Rakip izleme (üç ayda bir güncellenir)

Son bakış: 08.10.2026.

| Rakip | Ne izlenir |
|---|---|
| Yuka | Ülke listesi (Türkiye eklenirse kritik), gelir (yuka.io/en/independence), yeni özellikler |
| Open Food Facts | Türkiye ürün sayısı (08.10.2026: ~11.500) |
| ÇabukBak, Ürün Dedektörü, Besin App | İndirme sayısı, dil sayısı, özellikler |
| Olive, Fig, Bobby Approved | ABD'deki fiyatlama ve büyüme |
| CodeCheck, INCI Beauty, Think Dirty, EWG | Kozmetik ve temizlik kapsamı |
| Mevzuat | AB 2026/405 dijital ürün pasaportu takvimi; kozmetik için pasaport kararı |

Analizin kaynakları 08.10.2026 oturumunda toplandı: Yuka yardım ve bağımsızlık sayfaları, UPI, CBS, Fox News, Glossy, Sensor Tower, Osana, Olive, CodeCheck, INCI Beauty, Think Dirty, EWG, Open Food Facts, ÇabukBak, Ürün Dedektörü, REACH24H, SGS.
