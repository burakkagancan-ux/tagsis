# Türkiye kozmetik ekleri ile AB karşılaştırması (03.10.2026)

## Türk mevzuatının durumu
- **Kozmetik Ürünler Yönetmeliği:** RG 08.05.2023, 32184 mükerrer. Ek II–VI, AB 1223/2009 ekleriyle uyumlu olarak yayımlandı.
- **Tek değişiklik:** RG 05.03.2024, 32480. Ek II ve Ek III'ü değiştirdi; AB (EU) 2023/1490 ile uyum ([KPMG duyurusu](https://kpmgvergi.com/yayinlar/mali-bultenler/gumruk/kozmetik-urunler-yonetmeligi-ek-ii-sayili-yasakli-bilesikler-listesinde-degisiklik-yapilacaktir/2334), [KPMG özeti](https://kpmgvergi.com/yayinlar/mali-bultenler/gumruk/kozmetik-urunler-yonetmeliginde-degisiklik-yapilmasina-dair-yonetmelik/2545)).
- **Sonrası:** 05.03.2024'ten sonra yayımlanmış bir değişiklik bulunamadı (web araması, 03.10.2026).
- **Taslak (Eylül 2026):** Ticaret Bakanlığı bir değişiklik taslağını görüşe açtı ([Karar](https://www.karar.com/guncel-haberler/kozmetik-urunlerde-yeni-donem-bazi-icerikler-yasaklanacak-karekod-2069502), [Takvim](https://www.takvim.com.tr/guncel/2026/09/02/ticaret-bakanligindan-kozmetik-urunlere-siki-denetim-gunes-kremleri-ve-sac-boyalarina-yasak-geliyor)). Haberlere göre içerdikleri:
  - D5 (decamethylcyclopentasiloxane): Saç spreyi, güneş kremi, nemlendirici ve fondötende 31.12.2026'dan itibaren yasak.
  - Hexyl salicylate: 3 yaş altı ürünlerde yasak (AB 2026/78).
  - Triclocarban: Diş macununda 6 yaş altı uyarısı (AB 2024/996).
  - Alüminyum bileşikleri: Güneş kremi kısıtlaması (AB 2026/909).
  - Saç boyaları: 16 yaş altı ve kına dövmesi uyarıları.
  - Karekod zorunluluğu.

## Veriye yansıması
| AB değişikliği | Türkiye | `tr` |
|---|---|---|
| 2023/1490 ve öncesi | Yürürlükte | (alan yok) |
| 2024/858 (nano maddeler) | Yayımlanmadı | `yok` |
| 2024/996 (4-MBC, A vitamini, arbutin, kojik asit, triklosan/triklokarban) | Taslakta (kısmen) | `taslak` |
| 2025/877 (Omnibus VII, CMR) | Yayımlanmadı | `yok` |
| 2026/78 (hexyl salicylate vb.) | Taslakta (kısmen) | `taslak` |
| 2026/909 (alüminyum, saç boyaları, trifenil fosfat) | Taslakta (kısmen) | `taslak` |

- **Etikette görünen ifade:** Kartta "AB'de yasak" yazısı aynen kalıyor. (i) panelinde Türkiye durumu ayrıca yazılıyor.
- **Taslaktaki D5 maddesi:** K3 listesine `tr_taslak` olarak eklendi (sarı).
- **Eksik AB kısıtlaması:** AB'nin kozmetik dışı mevzuattan gelen D4/D5/D6 kısıtlaması (REACH, (EU) 2024/1328) eksikti. Bu kısıtlama durulanmayan üründe 6 Haziran 2027'den itibaren %0,1 ve üzerini yasaklıyor. K3 listesine `ab_reach` olarak eklendi (sarı).

## Yapılamayan
- **Satır satır karşılaştırma:** Ek II–VI'nın Türkçe metni (Resmî Gazete PDF'leri) bu ortamdan okunamadı. Bu yüzden satır satır karşılaştırma yapılamadı. 2023 yönetmeliği AB ekleriyle uyumlu ilan edildiği için tek tek fark beklenmiyor.
- **Taslağın doğrulanması:** Taslağın kendisine değil, basın haberlerine ulaşıldı. Resmî metin yayımlanınca `tr` değerleri güncellenmeli (`TR_BY_REG`, gen_kozmetik.py).
