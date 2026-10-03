# Türk Gıda Kodeksi karşılaştırması (03.10.2026)

## 1. Alerjenler: Etiketleme Yönetmeliği Ek-1 ile `bilesenler.json`

Kaynak: Ek-1'in Türkçe metni ([DENİB genelge eki](https://www.denib.gov.tr/files/downloads/sirku_ekleri/2016-02-ek1-1.pdf)). Resmi metin mevzuat.gov.tr'den okunamadı. 14 madde ve madde 65'teki vurgulama kuralı, Bakanlığın [2021 kılavuzu](https://www.gidamuhendisleri.org.tr/wp-content/uploads/2021/05/176969.pdf) ile de doğrulandı.

| Ek-1 | Durum | Yapılan |
|---|---|---|
| 1 Gluten içeren tahıllar (buğday, kılçıksız buğday, kamut, çavdar, arpa, yulaf, melezleri) | Uyumlu | "kılçıksız buğday", "tritikale" (buğday×çavdar melezi) eklendi |
| 1 muafiyet: buğday glukoz şurubu (dekstroz dahil), buğday maltodekstrini, arpa glukoz şurubu | Zaten vardı | — |
| 2 Kabuklular | Uyumlu | Profildeki ad "Kabuklular" yapıldı |
| 4 Balık; muafiyet: vitamin/karotenoid taşıyıcısı ya da bira/şarap durultucusu olarak kullanılan balık jelatini, isinglass | Muafiyet notu yoktu | "Balık jelatini" ayrı kayıt oldu, muafiyet notu eklendi (uyarı sürer, çünkü kullanım amacı etiketten anlaşılmaz) |
| 6 Soya; muafiyetler: rafine soya yağı, soya kaynaklı tokoferol (E306) ve bitkisel sterol/stanol esterleri | Sterol eksikti | "Bitkisel sterol/stanol" nötr kaydı eklendi; soya yağı notu Ek-1 metnine göre düzeltildi. E306 zaten soya uyarısı vermiyordu |
| 7 Süt (laktoz dahil); muafiyet: laktitol | Uyumlu | E966 süt alerjeni sayılmıyor, doğru |
| 8 Sert kabuklu meyveler: badem, fındık, ceviz, kaju, pikan cevizi, Brezilya fındığı, Antep fıstığı, Macadamia/Queensland fındığı | Ad eksikleri | "Brezilya fındığı", "macadamia", "Queensland fındığı" eklendi |
| 12 Kükürt dioksit ve sülfitler (10 mg/kg veya 10 mg/L üzeri, toplam SO2 olarak) | Ad farklıydı | Ad "Kükürt dioksit ve sülfitler" yapıldı, eşik notu düzeltildi |
| 3, 5, 9, 10, 11, 13, 14 | Uyumlu | — |

Sıra (sülfit 12, acı bakla 13, yumuşakçalar 14) Ek-1 ile aynı.

## 2. Katkı maddeleri: Gıda Katkı Maddeleri Yönetmeliği Ek II ile `e_kodlari.json`

Kaynak: Ek II Bölüm B, [FAOLEX kopyası](https://faolex.fao.org/docs/pdf/tur152534ANNEX.pdf), 2013 ilk metni. Liste `kaynak/tgk_ek2_2013.tsv` dosyasında. PDF doğrudan indirilemedi, parça parça okundu, yani satırlar elle aktarılmış sayılır. GAİB rehberinin ekine erişilemedi.

- Ek II'de 321 kod var, bizde 329 kod vardı.
- **Bizde eksik olan 4 madde eklendi:** E420 sorbitol, E421 mannitol, E907 hidrojenize poli-1-deken, E964 poliglisitol şurubu.
- **Ek II'de olmayan 13 madde** için `tgk_note` alanı eklendi. Bunlar: E128, E154, E160f, E161g, E171 (2023'te çıkarıldı), E216, E217, E230, E243 (sonradan eklendi), E441 (jelatin katkı maddesi değil), E558, E924a, E969. Yeşil olanların durumu "doğrulanmadı" olarak işaretlendi (needs_review).
- **100 maddenin adı farklıydı.** Resmi ad `tgk_name` alanına yazıldı ve eş anlamlı olarak eklendi; böylece etikette resmi adıyla geçen madde (ör. "jellan gam", "karmosin", "ponzo 4R", "şellak", "sakkarinler") artık bulunuyor. Uygulamada gösterilen ad (`primary_name`) değişmedi, çünkü resmi adların bir kısmı İngilizce ("Sunset Yellow FCF"). Resmi ad bilgi panelinde "Yönetmelikteki adı" olarak gösteriliyor.

## 3. "Sülfit" eşleşmesi

Uygulama, tür belirtmeyen "sülfit" kelimesini zaten E220–E228'in hepsiyle eşleştiriyordu. "E228'e bağlı" görünmesinin nedeni, `gen_bilesenler.py`'nin çakışma raporunda yalnızca son kodu yazmasıydı. Rapor düzeltildi ve artık tüm kodları listeliyor. Kart başlığı da "Olası: E220…E228 · Koruyucu (türü belirtilmemiş)" oldu. Önceden ilk maddenin adı ("Kükürt dioksit") yazıyordu. Ek-1'deki "kükürt dioksit ve sülfitler" ifadesi alerjen grubuna bağlandı.

## Açık kalanlar

- Ek II'nin 2013 sonrası değişiklikleri (eklenen/çıkarılan kodlar) tek tek taranmadı.
- 110 maddenin sağlık değerlendirmesi hâlâ kaynakla doğrulanmadı (needs_review).
