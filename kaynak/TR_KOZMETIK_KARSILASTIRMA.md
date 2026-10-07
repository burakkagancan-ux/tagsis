# Türkiye kozmetik ekleri ile AB karşılaştırması (03.10.2026; satır satır karşılaştırma 07.10.2026)

## Türk mevzuatının durumu
- **Kozmetik Ürünler Yönetmeliği:** RG 08.05.2023, 32184 mükerrer. Ek II–VI, AB 1223/2009 ekleriyle uyumlu olarak yayımlandı.
- **Tek değişiklik:** RG 05.03.2024, 32480. Ek II ve Ek III'ü değiştirdi; AB (EU) 2023/1490 ve 2023/1545 ile uyum.
- **Sonrası:** mevzuat.gov.tr'deki güncel metinde (07.10.2026) 05.03.2024'ten sonra bir değişiklik işareti yok.
- **Taslak (Eylül 2026):** Basına göre Ticaret Bakanlığı bir değişiklik taslağını görüşe açtı ([Sabah, 02.09.2026](https://www.sabah.com.tr/ekonomi/kozmetikte-dogal-donem-7652594), [Karar](https://www.karar.com/guncel-haberler/kozmetik-urunlerde-yeni-donem-bazi-icerikler-yasaklanacak-karekod-2069502)). Taslağın resmi metni bulunamadı: TİTCK'nın görüş platformunda (ebs.titck.gov.tr, 07.10.2026) kozmetik taslağı yok. Haberlere göre içerdikleri:
  - D5 (decamethylcyclopentasiloxane): Saç spreyi, güneş kremi, nemlendirici ve fondötende 31.12.2026'dan itibaren yasak.
  - Hexyl salicylate: 3 yaş altı ürünlerde yasak (AB 2026/78).
  - Triclocarban: Diş macununda 6 yaş altı uyarısı (AB 2024/996).
  - Alüminyum bileşikleri: Güneş kremi kısıtlaması (AB 2026/909).
  - Saç boyaları: 16 yaş altı ve kına dövmesi uyarıları.
  - Karekod zorunluluğu.

## Satır satır karşılaştırma (07.10.2026)
- **Kaynak:** Resmî Gazete'deki ek PDF'leri: [20230508M1-1-1.pdf](https://www.resmigazete.gov.tr/eskiler/2023/05/20230508M1-1-1.pdf) (346 sayfa) ve [20240305-4-1.pdf](https://www.resmigazete.gov.tr/eskiler/2024/03/20240305-4-1.pdf) (41 sayfa). PDF'ler taranmış görüntü olduğu için macOS yazı tanıma (Vision) ile okundu; Ek III sayfaları yatay basıldığı için her sayfa dört yönde okunup en iyi sonuç alındı.
- **Yöntem:** CosIng'deki her AB kaydı (2023/1545'e kadar, 2.291 kayıt) Türk ekinde sırasıyla CAS numarası, EC numarası, renk indeks numarası, INCI adı ve sıra numarası (komşu numaralarla aynı sayfada) ile arandı. Bulunamayan 46 kayıt Türkçe adlarıyla arandı ve sayfa görüntüsüne bakıldı.
- **Sonuç:** Bor bileşikleri dışında AB'nin bütün kayıtları Türk eklerinde var.
- **Fark: bor bileşikleri.** Türk Ek II'si 1393'ten 1400'e atlıyor (RG sayfa 79). AB'nin şu kayıtları Türkiye'de yasaklı maddeler listesinde yok:
  - 1394 Diboron trioxide (boric oxide), AB 2019/831
  - 1395 Boric acid, AB 2019/831
  - 1396 Borates, tetraborates, octaborates and boric acid salts and esters, AB 2019/1966
  - 1397 Sodium perborate ve perborik asit tuzları (AB'de 2019/831 ile 1397–1399; 2026/78 ile 1397'de birleşti)
  - Borik asit ve tetraboratlar Türkiye'de Ek III 1a ve 1b'deki kullanım sınırlarıyla izinli (RG sayfa 102–103).
- **Sınırlama:** Yazı tanıma tek tek değerlerin (yüzde, ürün tipi) karşılaştırılmasına yetecek kadar güvenilir değil; karşılaştırma maddenin listede olup olmadığını kapsar. Türk eklerindeki koşullar AB metninin çevirisi olarak kabul edildi.

## Veriye yansıması
| AB değişikliği | Türkiye | `tr` |
|---|---|---|
| 2023/1545 ve öncesi | Yürürlükte | (alan yok) |
| AB Ek II 1394–1397 (bor bileşikleri) | Türk Ek II'de yok | `farkli` |
| 2024/858 (nano maddeler) | Yayımlanmadı | `yok` |
| 2024/996 (4-MBC, A vitamini, arbutin, kojik asit, triklosan/triklokarban) | Taslakta (kısmen) | `taslak` |
| 2025/877 (Omnibus VII, CMR) | Yayımlanmadı | `yok` |
| 2026/78 (hexyl salicylate vb.) | Taslakta (kısmen) | `taslak` |
| 2026/909 (alüminyum, saç boyaları, trifenil fosfat) | Taslakta (kısmen) | `taslak` |

- **Etikette görünen ifade:** Kartta "AB'de yasak" yazısı aynen kalıyor. (i) panelinde Türkiye durumu ayrıca yazılıyor (`tr_text`).
- **Taslaktaki D5 maddesi:** K3 listesine `tr_taslak` olarak eklendi (sarı).
- **Eksik AB kısıtlaması:** AB'nin kozmetik dışı mevzuattan gelen D4/D5/D6 kısıtlaması (REACH, (EU) 2024/1328) K3 listesinde `ab_reach` olarak var (sarı).

## Yapılamayan
- **Taslağın doğrulanması:** Taslağın kendisine değil, basın haberlerine ulaşıldı. Resmi metin yayımlanınca `tr` değerleri güncellenmeli (`TR_BY_REG`, gen_kozmetik.py).
