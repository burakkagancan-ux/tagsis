# -*- coding: utf-8 -*-
"""
E kodlu gıda katkı maddeleri veri tabanını (data/e_kodlari.json) üretir.

Kullanım:  python3 gen_e_kodlari.py
- data/e_kodlari.json bu dosyadan üretilir; JSON'u elle düzenlemeyin, değişikliği burada yapın.
- Her kayıt için E kodu eş anlamlıları (e100, e-100, e 100, ins 100, ins100; harfli
  kodlarda e150(a), e 150 (a)) ve Türkçe karakterleri sadeleştirilmiş yazımlar
  (zerdeçal -> zerdecal) otomatik eklenir.
- "Bu listedeki özel uyarı ölçütlerinden hiçbirine girmiyor" açıklaması, reason=None
  olan kayıtlara kategori adıyla otomatik yazılır.
- counts (sayımlar) her çalıştırmada yeniden hesaplanır.

Not: Bu betik 03.10.2026'da depodaki e_kodlari.json v0.2.1'den geri üretildi
(özgün betik kayboldu). v0.3.0: TGK izinli katkı listesi (kaynak/tgk_ek2_2013.tsv)
ile karşılaştırma -> tgk_name / tgk_note alanları, resmi adlar eş anlamlı olarak eklendi,
eksik 4 madde (E420, E421, E907, E964) eklendi.
"""
import json, os, re

VERSION = '0.3.0'
LAST_UPDATED = '2026-10-03'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "e_kodlari.json")

TR = str.maketrans("çğıöşüâîûİ", "cgiosuaiui")
def fold(s):
    return s.translate(TR)

TGK_TSV = os.path.join(HERE, "kaynak", "tgk_ek2_2013.tsv")

# TGK listesiyle karşılaştırmada özel durumlar (2013 metninden sonraki değişiklikler, bağlam)
TGK_NOTES = {
    "E171": "Türk Gıda Kodeksi'nde 13.10.2023 tarihli değişiklikle izinli listeden çıkarıldı; 1 Nisan 2024'ten sonra piyasaya arz edilemez.",
    "E243": "2013 tarihli izinli listede yoktu; sonradan Türk Gıda Kodeksi izinli listesine eklendi.",
    "E441": "Jelatin katkı maddesi değil gıda bileşeni sayılır; bu yüzden izinli katkı listesinde yer almaz.",
}
TGK_MISSING = "Türk Gıda Kodeksi izinli katkı listesinin 2013 metninde yok; Türkiye'deki güncel izin durumu doğrulanmadı."


def load_tgk(path=TGK_TSV):
    """kaynak/tgk_ek2_2013.tsv -> {E kodu: resmi Türkçe ad}"""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            k, v = line.rstrip("\n").split("\t")
            out[k] = v
    return out


# Resmi adda virgül/eğik çizgi ayrı adları ayırıyorsa (ör. "Koşineal, Karminik asit, Karminler") parçalar
# ayrı eş anlamlı olur. Diğerlerinde virgül adın parçasıdır ("Balmumu, beyaz ve sarı"), bölünmez.
TGK_SPLIT = {"E110", "E120", "E122", "E124", "E132", "E151", "E160b", "E160c", "E162",
             "E410", "E413", "E427", "E466", "E468", "E469"}


def tgk_aliases(eid, name):
    """Resmi adı etiketlerde geçebilecek biçimlere çevirir: parantezsiz ad, (izinliyse) parçalar, anlamlı parantez içi."""
    if not name:
        return []
    low = name.replace("İ", "i").replace("I", "ı").lower()
    out = []
    def add(x):
        x = " ".join(x.split()).strip(" ,/")
        if len(re.sub(r"[^a-zçğıöşü]", "", x)) >= 4 and x not in out:
            out.append(x)
    inner, outer = [], low
    while "(" in outer:
        m = re.search(r"\(([^()]*)\)", outer)
        if not m:
            break
        inner.append(m.group(1))
        outer = outer[:m.start()] + " " + outer[m.end():]
    if eid in TGK_SPLIT:
        for part in re.split(r"[,/]", outer):
            add(part)
    else:
        add(outer)
        if "(" in low:
            add(low)
    for x in inner:
        if re.search(r"[a-zçğıöşü]{4}", x):
            add(x)
    return out


DEFAULT_REASON = "{K}. Bu listedeki özel uyarı ölçütlerinden hiçbirine girmiyor; ayrıntılı bir değerlendirme yapılmamıştır."

# Bağlam gerektiren eş anlamlılar (ör. "karamel" yalnızca "renklendirici (karamel)" gibi kullanımlarda E150 sayılır)
CONTEXT = {
    "KARAMEL": [{'alias': 'karamel', 'requires_any': ['renklendirici', 'renklendiriciler', 'renk verici', 'renk vericiler', 'colour', 'color', 'colouring', 'coloring']},
     {'alias': 'caramel', 'requires_any': ['renklendirici', 'renklendiriciler', 'renk verici', 'renk vericiler', 'colour', 'color', 'colouring', 'coloring']}],
}

META = {'description': 'E kodlu (INS numaralı) gıda katkı maddeleri veri tabanı taslağı. Gemini konuşmasındaki şemayı (id, primary_name, aliases, flags, risk_level, '
                'reason, agencies) temel alır.',
 'context_aliases': 'Yalnızca bağlam varsa sayılan eş anlamlılar: ör. “karamel” ancak önünde “renklendirici” gibi bir sözcük varsa E150 sayılır; “karamel '
                    'aroması” sayılmaz.',
 'design_change': 'risk_level artık kullanıcı profilinden bağımsız genel sağlık/mevzuat seviyesidir. Vegan, helal, alerjen gibi yaşam tarzı ve hassasiyet '
                  'uyarıları yalnızca flags ile verilir (ör. E120 genel olarak green, ancak non_vegan bayrağı taşır).',
 'risk_levels': {'red': "K1: AB'de gıda katkısı olarak yasak/geri çekilmiş ya da listede yok; K2: AB'de zorunlu uyarı etiketi gerektiriyor (Southampton 6); "
                        "K3: ABD'de yasak ya da izni iptal edilmiş.",
                 'yellow': "K4: IARC sınıflandırması (madde veya yan ürünü); K5: zorunlu alerjen/fenilalanin/laksatif uyarısı; K6: EFSA'nın ADI aşım uyarısı; "
                           "K7: AB'de üreme toksisitesi sınıflaması.",
                 'green': "Yukarıdaki ölçütlerden hiçbirine girmiyor. 'Güvenli' anlamına gelmez, 'bu listede özel uyarı yok' anlamına gelir.",
                 'unrated': 'İzin durumu doğrulanamadı.'},
 'flags': {'eu_warning_label': "AB'de zorunlu uyarı etiketi",
           'hyperactivity': 'Çocuklarda dikkat/aktivite uyarısı',
           'banned_eu': "AB'de yasak/geri çekilmiş/listede yok",
           'fda_banned': "ABD'de yasak veya izni iptal",
           'iarc_listed': 'IARC sınıflandırması var',
           'allergen_sulphite': 'Sülfit alerjeni',
           'phenylalanine': 'Fenilketonüri (PKU) uyarısı',
           'laxative_polyols': 'Laksatif etkili poliol',
           'fodmap': 'Hassas bağırsak/FODMAP',
           'pet_risk': 'Evcil hayvanlar için toksik',
           'non_vegan': 'Hayvansal kaynaklı (vegan değil)',
           'vegan_suspect': 'Kaynak bitkisel veya hayvansal olabilir',
           'non_vegetarian': 'Kesim yan ürünü',
           'insect_derived': 'Böcek kaynaklı',
           'halal_suspect': 'Helal uygunluğu belirsiz',
           'allergen_soy_possible': 'Soya alerjeni olabilir',
           'allergen_egg': 'Yumurta alerjeni',
           'gmo_suspect': "GDO'lu soya kaynaklı olabilir",
           'reproductive_toxicity': "AB'de üreme toksisitesi sınıflı",
           'debated': 'Bilimsel/kamuoyu tartışması var',
           'sodium': 'Sodyum içerir (tansiyon takibi)',
           'aluminium': 'Alüminyum içerir'},
 'verification': {'checked_in_session': 'Bu çalışmada kaynakla doğrulandı (E127, E203).',
                  'checked_2026_10': "03.10.2026'da kaynakla doğrulandı; kaynaklar kaydın 'sources' alanında.",
                  'general_knowledge': 'Model bilgisine dayanıyor; yayımlanmadan önce kaynakla doğrulanmalı.',
                  'partially_checked': 'İddianın bir kısmı (ör. Türkiye durumu) kaynakla doğrulandı, kalanı model bilgisi.',
                  'inventory_only': 'Yalnızca kod ve isim envanteri; özel bir iddia içermiyor.'},
 'sources': [{'name': 'FAIA E-numbers (kod/isim envanteri)',
              'url': 'https://faia.org.uk/e-numbers/',
              'note': "AB'de onaylı katkı listesi olarak sunuluyor ancak güncel değil: E171 ve E203'ü hâlâ içeriyor. İzin durumu için kaynak olarak "
                      'kullanılmadı.'},
             {'name': 'FDA: Red No. 3 izninin iptali (15 Ocak 2025)',
              'url': 'https://www.fda.gov/food/hfp-constituent-updates/fda-revoke-authorization-use-red-no-3-food-and-ingested-drugs'},
             {'name': 'Resmî Gazete 13.10.2023 (32338 mük.): TGK Gıda Katkı Maddeleri Yönetmeliği',
              'url': 'https://www.resmigazete.gov.tr/eskiler/2023/10/20231013M1-1.htm'},
             {'name': 'TGK Gıda Katkı Maddeleri rehberi, Ek 1 izinli katkı listesi (Türkçe adlar için kaynak)',
              'url': 'https://www.gaib.org.tr/tr/site/download-file/7004.html?class=AnnouncementFiles'},
             {'name': 'AB Tüzüğü 2018/98: E203 kalsiyum sorbatın listeden çıkarılması', 'url': 'https://www.legislation.gov.uk/eur/2018/98/data.html'}],
 'caveats': ["Türk Gıda Kodeksi izinli katkı listesi (Ek II) ile karşılaştırma 2013 tarihli ilk metne dayanır (kaynak/tgk_ek2_2013.tsv); sonraki değişiklikler (ör. E171'in 2023'te çıkarılması) tgk_note alanında ayrıca belirtilmiştir.",
             'CSPI ve diğer tüketici kuruluşlarının derecelendirmeleri eklenmedi; doğrulanmadan kurum adıyla renk atanmadı.',
             "Gıda katkısı sayılmayan gizli şeker, maya özütü, kazeinat gibi maddeler bu dosyada yoktur; ayrı bir 'bileşen' listesi olarak kurulmalıdır. Maya "
             'özütünü E621 ile eş anlamlı yapmak doğru değildir (doğal glutamat içerir, katkı olarak eklenen E621 değildir).',
             'Bazı eş anlamlılar bir grubu paylaşır (karamel, sülfit, polisorbat, modifiye nişasta vb.); eşleştirme birden fazla kayıt döndürebilir, en yüksek '
             'riskli olan gösterilmelidir.',
             "Çıplak sayılar (ör. '102') eş anlamlı olarak eklenmedi; yanlış eşleşmeyi önlemek için yalnızca 'e102', 'e-102', 'e 102', 'ins 102' biçimleri "
             "var. Etiketlerdeki 'renklendirici (tartrazin)' gibi kalıplar eşleştirme algoritmasında ele alınmalıdır.",
             "Listenin tamamı AB envanterine dayanır; yalnızca INS'te olup AB'de E kodu olmayan maddeler (ör. INS 1xx'in bir kısmı) dahil değildir."]}

# Alanlar: (id, primary_name, name_en, category, eş anlamlılar, flags, risk_level, reason,
#           agencies, eu_status, needs_review, verification, context)
# reason=None -> DEFAULT_REASON; context -> CONTEXT anahtarı
ITEMS = [
    ('E100', 'Kurkumin', 'Curcumin', 'Renklendirici', ['kurkumin', 'curcumin', 'c.i. 75300', 'ci 75300', 'zerdeçal', 'turmeric', 'curcuma', 'natural yellow 3'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E101', 'Riboflavin', 'Riboflavin', 'Renklendirici', ['riboflavin', "riboflavin-5'-fosfat", 'laktoflavin', "riboflavin-5'-phosphate", 'lactoflavin', 'vitamin b2', 'b2 vitamini'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E102', 'Tartrazin', 'Tartrazine', 'Renklendirici', ['tartrazin', 'tartrazine', 'c.i. 19140', 'ci 19140', 'fd&c yellow 5', 'yellow 5', 'acid yellow 23', 'food yellow 4', 'sarı 5'], ['hyperactivity', 'eu_warning_label'], 'red', "AB'de bu renklendiriciyi içeren ürünlerin etiketinde “çocukların dikkat ve aktivitesi üzerinde olumsuz etkisi olabilir” uyarısı zorunludur (2007 Southampton çalışması sonrası). ABD'de “Sarı 5” adıyla izinlidir.", ['EU_warning_label'], 'listed', True, 'general_knowledge', None),
    ('E104', 'Kinolin sarısı', 'Quinoline yellow', 'Renklendirici', ['kinolin sarısı', 'quinoline yellow', 'c.i. 47005', 'ci 47005', 'quinoline yellow ws', 'd&c yellow 10', 'food yellow 13', 'acid yellow 3'], ['hyperactivity', 'eu_warning_label'], 'red', "AB'de bu renklendiriciyi içeren ürünlerin etiketinde “çocukların dikkat ve aktivitesi üzerinde olumsuz etkisi olabilir” uyarısı zorunludur (2007 Southampton çalışması sonrası). ABD'de gıdada kullanımına izin verilmiyor.", ['EU_warning_label'], 'listed', True, 'general_knowledge', None),
    ('E110', 'Gün batımı sarısı FCF', 'Sunset yellow FCF', 'Renklendirici', ['gün batımı sarısı fcf', 'turuncu sarı s', 'sunset yellow fcf', 'orange yellow s', 'c.i. 15985', 'ci 15985', 'fd&c yellow 6', 'yellow 6', 'sarı 6', 'food yellow 3'], ['hyperactivity', 'eu_warning_label'], 'red', "AB'de bu renklendiriciyi içeren ürünlerin etiketinde “çocukların dikkat ve aktivitesi üzerinde olumsuz etkisi olabilir” uyarısı zorunludur (2007 Southampton çalışması sonrası).", ['EU_warning_label'], 'listed', True, 'general_knowledge', None),
    ('E120', 'Karmin', 'Carmine', 'Renklendirici', ['karmin', 'koşineal', 'karminik asit', 'carmine', 'cochineal', 'carminic acid', 'c.i. 75470', 'ci 75470', 'natural red 4', 'doğal kırmızı 4', 'crimson lake', 'carmine lake', 'cochineal extract', 'koşinil', 'koşinil özütü', 'carmines', 'karminler', 'koşinil ekstresi', 'koşinil ekstraktı'], ['non_vegan', 'insect_derived', 'halal_suspect'], 'green', 'Koşinil böceğinden elde edilen kırmızı boyadır (vegan değildir). Helal uygunluğu din otoritelerine göre değişir. Nadir alerjik reaksiyonlar bildirilmiştir.', [], 'listed', True, 'general_knowledge', None),
    ('E122', 'Azorubin', 'Azorubine', 'Renklendirici', ['azorubin', 'karmoizin', 'azorubine', 'carmoisine', 'c.i. 14720', 'ci 14720', 'food red 3'], ['hyperactivity', 'eu_warning_label'], 'red', "AB'de bu renklendiriciyi içeren ürünlerin etiketinde “çocukların dikkat ve aktivitesi üzerinde olumsuz etkisi olabilir” uyarısı zorunludur (2007 Southampton çalışması sonrası). ABD'de gıdada izinli değil.", ['EU_warning_label'], 'listed', True, 'general_knowledge', None),
    ('E123', 'Amarant', 'Amaranth', 'Renklendirici', ['amarant', 'amaranth', 'c.i. 16185', 'ci 16185', 'food red 9', 'fd&c red 2', 'red 2', 'kırmızı 2'], ['fda_banned'], 'red', "ABD'de 1976'da (Kırmızı No. 2) yasaklandı; AB'de yalnızca sınırlı ürünlerde izinlidir.", ['FDA_banned_1976'], 'listed', True, 'general_knowledge', None),
    ('E124', 'Ponceau 4R', 'Ponceau 4R', 'Renklendirici', ['ponceau 4r', 'koşineal kırmızısı a', 'cochineal red a', 'c.i. 16255', 'ci 16255', 'food red 7', 'new coccine', 'yeni koksin'], ['hyperactivity', 'eu_warning_label'], 'red', "AB'de bu renklendiriciyi içeren ürünlerin etiketinde “çocukların dikkat ve aktivitesi üzerinde olumsuz etkisi olabilir” uyarısı zorunludur (2007 Southampton çalışması sonrası). ABD'de gıdada izinli değil.", ['EU_warning_label'], 'listed', True, 'general_knowledge', None),
    ('E127', 'Eritrosin', 'Erythrosine', 'Renklendirici', ['eritrosin', 'erythrosine', 'c.i. 45430', 'ci 45430', 'fd&c red 3', 'red 3', 'kırmızı 3', 'food red 14'], ['fda_banned'], 'red', "ABD FDA, erkek sıçanlarda tümör bulgusu nedeniyle 15 Ocak 2025'te iznini iptal etti (gıdada son kullanım tarihi 15 Ocak 2027); FDA ayrıca insanlarda zarar kanıtı olmadığını belirtiyor. AB'de yalnızca kokteyl ve şekerli kiraz gibi sınırlı ürünlerde izinlidir.", ['FDA_revoked_2025'], 'listed', True, 'checked_in_session', None),
    ('E128', 'Kırmızı 2G', 'Red 2G', 'Renklendirici', ['kırmızı 2g', 'red 2g', 'c.i. 18050', 'ci 18050', 'acid red 1', 'food red 10'], ['banned_eu'], 'red', "AB'de gıda renklendiricisi olarak izni 2007'de geri çekildi.", ['EU_withdrawn_2007'], 'withdrawn', True, 'general_knowledge', None),
    ('E129', 'Allura kırmızısı AC', 'Allura red AC', 'Renklendirici', ['allura kırmızısı ac', 'allura red ac', 'c.i. 16035', 'ci 16035', 'fd&c red 40', 'red 40', 'kırmızı 40', 'food red 17'], ['hyperactivity', 'eu_warning_label'], 'red', "AB'de bu renklendiriciyi içeren ürünlerin etiketinde “çocukların dikkat ve aktivitesi üzerinde olumsuz etkisi olabilir” uyarısı zorunludur (2007 Southampton çalışması sonrası).", ['EU_warning_label'], 'listed', True, 'general_knowledge', None),
    ('E131', 'Patent mavisi V', 'Patent blue V', 'Renklendirici', ['patent mavisi v', 'patent blue v', 'c.i. 42051', 'ci 42051', 'food blue 5'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E132', 'İndigotin', 'Indigotine', 'Renklendirici', ['indigotin', 'indigo karmin', 'indigotine', 'indigo carmine', 'c.i. 73015', 'ci 73015', 'fd&c blue 2', 'blue 2', 'mavi 2', 'food blue 1'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E133', 'Parlak mavi FCF', 'Brilliant blue FCF', 'Renklendirici', ['parlak mavi fcf', 'briliant mavi fcf', 'brilliant mavi fcf', 'briliant mavi', 'brilliant blue fcf', 'c.i. 42090', 'ci 42090', 'fd&c blue 1', 'blue 1', 'mavi 1', 'food blue 2'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E140', 'Klorofiller ve klorofilinler', 'Chlorophylls and chlorophyllins', 'Renklendirici', ['klorofiller ve klorofilinler', 'chlorophylls and chlorophyllins', 'c.i. 75810', 'ci 75810', 'klorofil', 'chlorophyll'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E141', 'Klorofil ve klorofilinlerin bakır kompleksleri', 'Copper complexes of chlorophylls and chlorophyllins', 'Renklendirici', ['klorofil ve klorofilinlerin bakır kompleksleri', 'copper complexes of chlorophylls and chlorophyllins', 'c.i. 75815', 'ci 75815', 'bakırlı klorofil', 'bakır klorofilin', 'chlorophyllin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E142', 'Yeşil S', 'Green S', 'Renklendirici', ['yeşil s', 'green s', 'c.i. 44090', 'ci 44090', 'food green 4', 'lissamine green'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E150a', 'Sade karamel', 'Plain caramel', 'Renklendirici', ['sade karamel', 'plain caramel', 'karamel rengi', 'caramel colour'], [], 'green', None, [], 'listed', False, 'inventory_only', 'KARAMEL'),
    ('E150b', 'Kostik sülfit karamel', 'Caustic sulphite caramel', 'Renklendirici', ['kostik sülfit karamel', 'kostik sülfitli karamel', 'caustic sulphite caramel', 'karamel rengi', 'caramel colour'], [], 'green', None, [], 'listed', False, 'inventory_only', 'KARAMEL'),
    ('E150c', 'Amonyak karamel', 'Ammonia caramel', 'Renklendirici', ['amonyak karamel', 'amonyaklı karamel', 'ammonia caramel', 'karamel rengi', 'caramel colour'], ['iarc_listed'], 'yellow', "Üretim yan ürünü 4-metilimidazol (4-MEI) IARC'ye göre Grup 2B (olası kanserojen) sınıfındadır; kola ve benzeri gazlı içeceklerde yaygındır.", ['IARC_2B_4MEI'], 'listed', True, 'general_knowledge', 'KARAMEL'),
    ('E150d', 'Sülfit amonyak karamel', 'Sulphite ammonia caramel', 'Renklendirici', ['sülfit amonyak karamel', 'amonyak sülfitli karamel', 'amonyum sülfitli karamel', 'sülfitli amonyak karamel', 'sulphite ammonia caramel', 'karamel rengi', 'caramel colour'], ['iarc_listed'], 'yellow', "Üretim yan ürünü 4-metilimidazol (4-MEI) IARC'ye göre Grup 2B (olası kanserojen) sınıfındadır; kola ve benzeri gazlı içeceklerde yaygındır.", ['IARC_2B_4MEI'], 'listed', True, 'general_knowledge', 'KARAMEL'),
    ('E151', 'Parlak siyah BN', 'Brilliant black BN', 'Renklendirici', ['parlak siyah bn', 'siyah pn', 'brilliant black bn', 'black pn', 'c.i. 28440', 'ci 28440', 'food black 1', 'brilliant black pn'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E153', 'Bitkisel karbon', 'Vegetable carbon', 'Renklendirici', ['bitkisel karbon', 'vegetable carbon', 'c.i. 77266', 'ci 77266', 'carbon black', 'karbon siyahı', 'bitkisel kömür'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E154', 'Kahverengi FK', 'Brown FK', 'Renklendirici', ['kahverengi fk', 'brown fk', 'food brown 1'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E155', 'Kahverengi HT', 'Brown HT', 'Renklendirici', ['kahverengi ht', 'brown ht', 'c.i. 20285', 'ci 20285', 'food brown 3', 'chocolate brown ht'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E160a', 'Karotenler', 'Carotenes', 'Renklendirici', ['karotenler', 'carotenes', 'c.i. 75130', 'ci 75130', 'c.i. 40800', 'ci 40800', 'beta-karoten', 'beta karoten', 'betakaroten', 'beta-carotene', 'karoten'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E160b', 'Annatto', 'Annatto', 'Renklendirici', ['annatto', 'biksin', 'norbiksin', 'bixin', 'norbixin', 'c.i. 75120', 'ci 75120', 'natural orange 4', 'urucum', 'roucou', 'annatto extract'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E160c', 'Paprika ekstresi', 'Paprika extract', 'Renklendirici', ['paprika ekstresi', 'kapsantin', 'kapsorubin', 'paprika extract', 'capsanthin', 'capsorubin', 'paprika oleoresin', 'paprika oleorezini', 'kırmızı biber ekstresi', 'paprika özütü', 'paprika ekstraktı', 'kırmızı biber ekstraktı', 'kırmızı biber özütü'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E160d', 'Likopen', 'Lycopene', 'Renklendirici', ['likopen', 'lycopene', 'c.i. 75125', 'ci 75125', 'domates ekstresi', 'tomato extract', 'domates ekstraktı', 'domates özütü'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E160e', "Beta-apo-8'-karotenal (C30)", "Beta-apo-8'-carotenal (C30)", 'Renklendirici', ["beta-apo-8'-karotenal (c30)", "beta-apo-8'-karotenal", "beta-apo-8'-carotenal (c30)", "beta-apo-8'-carotenal", 'c.i. 40820', 'ci 40820', 'apokarotenal'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E160f', "Beta-apo-8'-karotenoik asidin etil esteri (C30)", "Ethyl ester of beta-apo-8'-carotenoic acid (C30)", 'Renklendirici', ["beta-apo-8'-karotenoik asidin etil esteri (c30)", "beta-apo-8'-karotenoik asidin etil esteri", "ethyl ester of beta-apo-8'-carotenoic acid (c30)", "ethyl ester of beta-apo-8'-carotenoic acid"], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E161b', 'Lutein', 'Lutein', 'Renklendirici', ['lutein', 'ksantofil', 'xanthophyll', 'kadife çiçeği ekstresi', 'marigold extract', 'kadife çiçeği ekstraktı', 'kadife çiçeği özütü'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E161g', 'Kantaksantin', 'Canthaxanthin', 'Renklendirici', ['kantaksantin', 'canthaxanthin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E162', 'Pancar kırmızısı', 'Beetroot red', 'Renklendirici', ['pancar kırmızısı', 'betanin', 'beetroot red', 'pancar rengi', 'pancar ekstresi', 'beet red', 'natural red 33', 'pancar ekstraktı', 'pancar özütü'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E163', 'Antosiyaninler', 'Anthocyanins', 'Renklendirici', ['antosiyaninler', 'anthocyanins', 'antosiyanin', 'anthocyanin', 'üzüm kabuğu ekstresi', 'grape skin extract', 'siyah havuç ekstresi', 'black carrot extract', 'enocyanin', 'üzüm kabuğu ekstraktı', 'üzüm kabuğu özütü', 'siyah havuç ekstraktı', 'siyah havuç özütü'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E170', 'Kalsiyum karbonat', 'Calcium carbonate', 'Renklendirici', ['kalsiyum karbonat', 'calcium carbonate', 'c.i. 77220', 'ci 77220', 'pigment white 18', 'tebeşir', 'chalk', 'kireç taşı', 'limestone'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E171', 'Titanyum dioksit', 'Titanium dioxide', 'Renklendirici', ['titanyum dioksit', 'titanium dioxide', 'c.i. 77891', 'ci 77891', 'pigment white 6', 'pw6', 'titania', 'titanium(iv) oxide', 'titanyum(iv) oksit', 'tio2', 'titanyum oksit', 'titanium oxide'], ['banned_eu'], 'red', "EFSA 2021'de genotoksisite endişesini ortadan kaldıramadı; AB'de gıdada kullanımı 2022'de yasaklandı. Türkiye'de 13 Ekim 2023 tarihli Gıda Katkı Maddeleri Yönetmeliği'ne göre, E171 içeren gıdaların piyasaya arzına 1 Nisan 2024'e kadar izin verildi.", ['EU_banned_2022', 'TR_withdrawn_2024'], 'banned', True, 'partially_checked', None),
    ('E172', 'Demir oksitler ve hidroksitler', 'Iron oxides and hydroxides', 'Renklendirici', ['demir oksitler ve hidroksitler', 'iron oxides and hydroxides', 'c.i. 77491', 'ci 77491', 'c.i. 77492', 'ci 77492', 'c.i. 77499', 'ci 77499', 'iron oxide', 'demir oksit', 'demir hidroksit'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E173', 'Alüminyum', 'Aluminium', 'Renklendirici', ['alüminyum', 'aluminium', 'c.i. 77000', 'ci 77000', 'pigment metal 1', 'aluminum'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E174', 'Gümüş', 'Silver', 'Renklendirici', ['gümüş', 'silver', 'c.i. 77820', 'ci 77820', 'gümüş varak'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E175', 'Altın', 'Gold', 'Renklendirici', ['altın', 'gold', 'c.i. 77480', 'ci 77480', 'altın varak', 'pigment metal 3'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E180', 'Litolrubin BK', 'Litholrubine BK', 'Renklendirici', ['litolrubin bk', 'litholrubine bk', 'c.i. 15850', 'ci 15850', 'pigment red 57', 'rubine pigment'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E200', 'Sorbik asit', 'Sorbic acid', 'Koruyucu', ['sorbik asit', 'sorbic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E202', 'Potasyum sorbat', 'Potassium sorbate', 'Koruyucu', ['potasyum sorbat', 'potassium sorbate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E203', 'Kalsiyum sorbat', 'Calcium sorbate', 'Koruyucu', ['kalsiyum sorbat', 'calcium sorbate'], ['banned_eu'], 'red', "AB gıda katkı listesinden 12 Ağustos 2018'de çıkarıldı; gerekçe yeterli genotoksisite verisinin bulunmamasıdır (kanıtlanmış zarar değil, veri eksikliği).", ['EU_withdrawn_2018'], 'withdrawn', True, 'checked_in_session', None),
    ('E210', 'Benzoik asit', 'Benzoic acid', 'Koruyucu', ['benzoik asit', 'benzoic acid', 'benzoat', 'benzoate'], ['iarc_listed'], 'yellow', 'Benzoatlar C vitamini (askorbik asit) içeren içeceklerde benzen oluşturabilir (benzen IARC Grup 1); sektör bu nedenle formülleri düzenledi. Southampton çalışmasının karışımlarında sodyum benzoat da vardı, ancak AB bu madde için ayrı bir uyarı etiketi zorunlu tutmaz.', [], 'listed', True, 'general_knowledge', None),
    ('E211', 'Sodyum benzoat', 'Sodium benzoate', 'Koruyucu', ['sodyum benzoat', 'sodium benzoate', 'benzoat', 'benzoate'], ['iarc_listed', 'sodium'], 'yellow', 'Benzoatlar C vitamini (askorbik asit) içeren içeceklerde benzen oluşturabilir (benzen IARC Grup 1); sektör bu nedenle formülleri düzenledi. Southampton çalışmasının karışımlarında sodyum benzoat da vardı, ancak AB bu madde için ayrı bir uyarı etiketi zorunlu tutmaz.', [], 'listed', True, 'general_knowledge', None),
    ('E212', 'Potasyum benzoat', 'Potassium benzoate', 'Koruyucu', ['potasyum benzoat', 'potassium benzoate', 'benzoat', 'benzoate'], ['iarc_listed'], 'yellow', 'Benzoatlar C vitamini (askorbik asit) içeren içeceklerde benzen oluşturabilir (benzen IARC Grup 1); sektör bu nedenle formülleri düzenledi. Southampton çalışmasının karışımlarında sodyum benzoat da vardı, ancak AB bu madde için ayrı bir uyarı etiketi zorunlu tutmaz.', [], 'listed', True, 'general_knowledge', None),
    ('E213', 'Kalsiyum benzoat', 'Calcium benzoate', 'Koruyucu', ['kalsiyum benzoat', 'calcium benzoate', 'benzoat', 'benzoate'], ['iarc_listed'], 'yellow', 'Benzoatlar C vitamini (askorbik asit) içeren içeceklerde benzen oluşturabilir (benzen IARC Grup 1); sektör bu nedenle formülleri düzenledi. Southampton çalışmasının karışımlarında sodyum benzoat da vardı, ancak AB bu madde için ayrı bir uyarı etiketi zorunlu tutmaz.', [], 'listed', True, 'general_knowledge', None),
    ('E214', 'Etil p-hidroksibenzoat', 'Ethyl p-hydroxybenzoate', 'Koruyucu', ['etil p-hidroksibenzoat', 'etilparaben', 'ethyl p-hydroxybenzoate', 'ethylparaben', 'paraben', 'parabens'], ['debated'], 'green', 'Paraben grubu koruyucu; endokrin etkileri üzerine tartışmalı çalışmalar vardır.', [], 'listed', True, 'general_knowledge', None),
    ('E215', 'Sodyum etil p-hidroksibenzoat', 'Sodium ethyl p-hydroxybenzoate', 'Koruyucu', ['sodyum etil p-hidroksibenzoat', 'sodium ethyl p-hydroxybenzoate', 'paraben', 'parabens'], ['debated', 'sodium'], 'green', 'Paraben grubu koruyucu; endokrin etkileri üzerine tartışmalı çalışmalar vardır.', [], 'listed', True, 'general_knowledge', None),
    ('E216', 'Propil p-hidroksibenzoat', 'Propyl p-hydroxybenzoate', 'Koruyucu', ['propil p-hidroksibenzoat', 'propilparaben', 'propyl p-hydroxybenzoate', 'propylparaben', 'paraben', 'parabens'], ['banned_eu'], 'red', "AB gıda katkı maddeleri listesinde yer almıyor (genel bilgi; doğrulanmalı). ABD'de California AB 418 ile 2027'den itibaren gıdada yasaklanıyor.", ['EU_not_listed', 'CA_AB418_2027'], 'not_listed', True, 'general_knowledge', None),
    ('E217', 'Sodyum propil p-hidroksibenzoat', 'Sodium propyl p-hydroxybenzoate', 'Koruyucu', ['sodyum propil p-hidroksibenzoat', 'sodium propyl p-hydroxybenzoate', 'paraben', 'parabens'], ['banned_eu', 'sodium'], 'red', "AB gıda katkı maddeleri listesinde yer almıyor (genel bilgi; doğrulanmalı). ABD'de California AB 418 ile 2027'den itibaren gıdada yasaklanıyor.", ['EU_not_listed', 'CA_AB418_2027'], 'not_listed', True, 'general_knowledge', None),
    ('E218', 'Metil p-hidroksibenzoat', 'Methyl p-hydroxybenzoate', 'Koruyucu', ['metil p-hidroksibenzoat', 'metilparaben', 'methyl p-hydroxybenzoate', 'methylparaben', 'paraben', 'parabens'], ['debated'], 'green', 'Paraben grubu koruyucu; endokrin etkileri üzerine tartışmalı çalışmalar vardır.', [], 'listed', True, 'general_knowledge', None),
    ('E219', 'Sodyum metil p-hidroksibenzoat', 'Sodium methyl p-hydroxybenzoate', 'Koruyucu', ['sodyum metil p-hidroksibenzoat', 'sodium methyl p-hydroxybenzoate', 'paraben', 'parabens'], ['debated', 'sodium'], 'green', 'Paraben grubu koruyucu; endokrin etkileri üzerine tartışmalı çalışmalar vardır.', [], 'listed', True, 'general_knowledge', None),
    ('E220', 'Kükürt dioksit', 'Sulphur dioxide', 'Koruyucu', ['kükürt dioksit', 'sulphur dioxide', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites', 'sulfur dioxide', 'so2', 'sülfür dioksit'], ['allergen_sulphite'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E221', 'Sodyum sülfit', 'Sodium sulphite', 'Koruyucu', ['sodyum sülfit', 'sodium sulphite', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites'], ['allergen_sulphite', 'sodium'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E222', 'Sodyum hidrojen sülfit', 'Sodium hydrogen sulphite', 'Koruyucu', ['sodyum hidrojen sülfit', 'sodyum bisülfit', 'sodium hydrogen sulphite', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites', 'sodium bisulfite'], ['allergen_sulphite', 'sodium'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E223', 'Sodyum metabisülfit', 'Sodium metabisulphite', 'Koruyucu', ['sodyum metabisülfit', 'sodium metabisulphite', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites', 'sodium metabisulfite'], ['allergen_sulphite', 'sodium'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E224', 'Potasyum metabisülfit', 'Potassium metabisulphite', 'Koruyucu', ['potasyum metabisülfit', 'potassium metabisulphite', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites', 'potassium metabisulfite'], ['allergen_sulphite'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E226', 'Kalsiyum sülfit', 'Calcium sulphite', 'Koruyucu', ['kalsiyum sülfit', 'calcium sulphite', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites'], ['allergen_sulphite'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E227', 'Kalsiyum hidrojen sülfit', 'Calcium hydrogen sulphite', 'Koruyucu', ['kalsiyum hidrojen sülfit', 'calcium hydrogen sulphite', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites'], ['allergen_sulphite'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E228', 'Potasyum hidrojen sülfit', 'Potassium hydrogen sulphite', 'Koruyucu', ['potasyum hidrojen sülfit', 'potassium hydrogen sulphite', 'sülfit', 'sülfitler', 'sulfite', 'sulphite', 'sulphites'], ['allergen_sulphite'], 'yellow', "Sülfit grubu koruyucu: 10 mg/kg (veya 10 mg/l) üzerinde içeren ürünlerde AB'de alerjen olarak etikette belirtilmesi zorunludur; astımlılarda reaksiyona yol açabilir.", ['EU_allergen_label'], 'listed', True, 'general_knowledge', None),
    ('E230', 'Bifenil', 'Biphenyl', 'Koruyucu', ['bifenil', 'difenil', 'biphenyl', 'diphenyl'], [], 'unrated', "Bu maddenin AB'deki güncel izin durumu bu çalışmada doğrulanmadı (genel bilgiye göre narenciye kabuğu yüzey işlemi için kullanılırdı).", [], 'verify', True, 'general_knowledge', None),
    ('E234', 'Nisin', 'Nisin', 'Koruyucu', ['nisin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E235', 'Natamisin', 'Natamycin', 'Koruyucu', ['natamisin', 'natamycin', 'pimarisin', 'pimaricin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E239', 'Hekzametilen tetramin', 'Hexamethylene tetramine', 'Koruyucu', ['hekzametilen tetramin', 'hexamethylene tetramine', 'hexamine', 'metenamin', 'urotropin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E242', 'Dimetil dikarbonat', 'Dimethyl dicarbonate', 'Koruyucu', ['dimetil dikarbonat', 'dimethyl dicarbonate', 'dmdc'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E243', 'Etil lauroil arjinat', 'Ethyl lauroyl arginate', 'Koruyucu', ['etil lauroil arjinat', 'etil laurol arjinat', 'ethyl lauroyl arginate', 'lae', 'lauric arginate ethyl ester', 'etil lauril arjinat'], [], 'green', None, [], 'listed', False, 'checked_in_session', None),
    ('E249', 'Potasyum nitrit', 'Potassium nitrite', 'Koruyucu', ['potasyum nitrit', 'potassium nitrite', 'nitrit', 'nitrite', 'nitritler'], ['iarc_listed'], 'yellow', 'IARC, nitrit ve nitratın vücutta nitrozamin oluşturabilecek koşullarda alımını Grup 2A (muhtemelen kanserojen) olarak sınıflandırıyor. Sucuk, sosis, salam gibi işlenmiş etlerde rengi korumak ve botulizmi önlemek için kullanılır.', ['IARC_2A_koşullu'], 'listed', True, 'general_knowledge', None),
    ('E250', 'Sodyum nitrit', 'Sodium nitrite', 'Koruyucu', ['sodyum nitrit', 'sodium nitrite', 'nitrit', 'nitrite', 'nitritler', 'kür tuzu', 'curing salt'], ['iarc_listed', 'sodium'], 'yellow', 'IARC, nitrit ve nitratın vücutta nitrozamin oluşturabilecek koşullarda alımını Grup 2A (muhtemelen kanserojen) olarak sınıflandırıyor. Sucuk, sosis, salam gibi işlenmiş etlerde rengi korumak ve botulizmi önlemek için kullanılır.', ['IARC_2A_koşullu'], 'listed', True, 'general_knowledge', None),
    ('E251', 'Sodyum nitrat', 'Sodium nitrate', 'Koruyucu', ['sodyum nitrat', 'sodium nitrate', 'nitrat', 'nitrate', 'nitratlar'], ['iarc_listed', 'sodium'], 'yellow', 'IARC, nitrit ve nitratın vücutta nitrozamin oluşturabilecek koşullarda alımını Grup 2A (muhtemelen kanserojen) olarak sınıflandırıyor. Sucuk, sosis, salam gibi işlenmiş etlerde rengi korumak ve botulizmi önlemek için kullanılır.', ['IARC_2A_koşullu'], 'listed', True, 'general_knowledge', None),
    ('E252', 'Potasyum nitrat', 'Potassium nitrate', 'Koruyucu', ['potasyum nitrat', 'potassium nitrate', 'nitrat', 'nitrate', 'güherçile', 'saltpetre', 'saltpeter'], ['iarc_listed'], 'yellow', 'IARC, nitrit ve nitratın vücutta nitrozamin oluşturabilecek koşullarda alımını Grup 2A (muhtemelen kanserojen) olarak sınıflandırıyor. Sucuk, sosis, salam gibi işlenmiş etlerde rengi korumak ve botulizmi önlemek için kullanılır.', ['IARC_2A_koşullu'], 'listed', True, 'general_knowledge', None),
    ('E260', 'Asetik asit', 'Acetic acid', 'Asitlik düzenleyici / mineral tuz', ['asetik asit', 'acetic acid', 'etanoik asit'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E261', 'Potasyum asetat', 'Potassium acetate', 'Koruyucu', ['potasyum asetat', 'potassium acetate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E262', 'Sodyum asetatlar', 'Sodium acetates', 'Koruyucu', ['sodyum asetatlar', 'sodium acetates', 'sodyum asetat', 'sodyum diasetat', 'sodium diacetate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E263', 'Kalsiyum asetat', 'Calcium acetate', 'Koruyucu', ['kalsiyum asetat', 'calcium acetate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E270', 'Laktik asit', 'Lactic acid', 'Asitlik düzenleyici / mineral tuz', ['laktik asit', 'lactic acid', 'süt asidi'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E280', 'Propiyonik asit', 'Propionic acid', 'Koruyucu', ['propiyonik asit', 'propionic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E281', 'Sodyum propiyonat', 'Sodium propionate', 'Koruyucu', ['sodyum propiyonat', 'sodium propionate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E282', 'Kalsiyum propiyonat', 'Calcium propionate', 'Koruyucu', ['kalsiyum propiyonat', 'calcium propionate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E283', 'Potasyum propiyonat', 'Potassium propionate', 'Koruyucu', ['potasyum propiyonat', 'potassium propionate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E284', 'Borik asit', 'Boric acid', 'Koruyucu', ['borik asit', 'boric acid'], ['reproductive_toxicity'], 'yellow', "AB'de yalnızca havyar (mersin balığı yumurtası) için izinlidir; borik asit AB sınıflandırmasında üreme toksisitesi (Kategori 1B) kapsamındadır.", ['EU_CLP_Repr1B'], 'listed', True, 'general_knowledge', None),
    ('E285', 'Boraks', 'Borax', 'Koruyucu', ['boraks', 'sodyum tetraborat', 'borax', 'sodium tetraborate', 'sodyum tetraborat (boraks)'], ['reproductive_toxicity', 'sodium'], 'yellow', "AB'de yalnızca havyar (mersin balığı yumurtası) için izinlidir; boraks AB sınıflandırmasında üreme toksisitesi (Kategori 1B) kapsamındadır.", ['EU_CLP_Repr1B'], 'listed', True, 'general_knowledge', None),
    ('E290', 'Karbondioksit', 'Carbon dioxide', 'Gaz / itici gaz', ['karbondioksit', 'carbon dioxide', 'karbon dioksit', 'co2'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E296', 'Malik asit', 'Malic acid', 'Asitlik düzenleyici / mineral tuz', ['malik asit', 'malic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E297', 'Fumarik asit', 'Fumaric acid', 'Asitlik düzenleyici / mineral tuz', ['fumarik asit', 'fumaric acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E300', 'Askorbik asit', 'Ascorbic acid', 'Antioksidan', ['askorbik asit', 'ascorbic acid', 'c vitamini', 'vitamin c', 'l-askorbik asit'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E301', 'Sodyum askorbat', 'Sodium ascorbate', 'Antioksidan', ['sodyum askorbat', 'sodium ascorbate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E302', 'Kalsiyum askorbat', 'Calcium ascorbate', 'Antioksidan', ['kalsiyum askorbat', 'calcium ascorbate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E304', 'Askorbik asidin yağ asidi esterleri', 'Fatty acid esters of ascorbic acid', 'Antioksidan', ['askorbik asidin yağ asidi esterleri', 'askorbil palmitat', 'askorbil stearat', 'fatty acid esters of ascorbic acid', 'ascorbyl palmitate', 'ascorbyl stearate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E306', 'Tokoferoller', 'Tocopherols', 'Antioksidan', ['tokoferoller', 'e vitamini ekstresi', 'tocopherols', 'tocopherol-rich extract', 'e vitamini', 'vitamin e', 'tokoferol', 'e vitamini ekstraktı', 'e vitamini özütü'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E307', 'Alfa-tokoferol', 'Alpha-tocopherol', 'Antioksidan', ['alfa-tokoferol', 'alpha-tocopherol'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E308', 'Gama-tokoferol', 'Gamma-tocopherol', 'Antioksidan', ['gama-tokoferol', 'gamma-tocopherol'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E309', 'Delta-tokoferol', 'Delta-tocopherol', 'Antioksidan', ['delta-tokoferol', 'delta-tocopherol'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E310', 'Propil gallat', 'Propyl gallate', 'Antioksidan', ['propil gallat', 'propyl gallate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E311', 'Oktil gallat', 'Octyl gallate', 'Antioksidan', ['oktil gallat', 'octyl gallate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E312', 'Dodesil gallat', 'Dodecyl gallate', 'Antioksidan', ['dodesil gallat', 'dodecyl gallate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E315', 'Eritorbik asit', 'Erythorbic acid', 'Antioksidan', ['eritorbik asit', 'erythorbic acid', 'izoaskorbik asit', 'isoascorbic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E316', 'Sodyum eritorbat', 'Sodium erythorbate', 'Antioksidan', ['sodyum eritorbat', 'sodium erythorbate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E319', 'Tersiyer bütilhidrokinon (TBHQ)', 'Tertiary-butyl hydroquinone (TBHQ)', 'Antioksidan', ['tersiyer bütilhidrokinon (tbhq)', 'tersiyer bütilhidrokinon', 'tertiary-butyl hydroquinone (tbhq)', 'tertiary-butyl hydroquinone', 'tbhq'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E320', 'Bütillenmiş hidroksianisol (BHA)', 'Butylated hydroxyanisole (BHA)', 'Antioksidan', ['bütillenmiş hidroksianisol (bha)', 'bütillenmiş hidroksianisol', 'butylated hydroxyanisole (bha)', 'butylated hydroxyanisole', 'bha', 'bütilhidroksianisol'], ['iarc_listed'], 'yellow', "IARC'ye göre Grup 2B (olası kanserojen); AB'de kullanımı düzey sınırlarına bağlıdır. Paketli yağ, cips ve sakızlarda bulunabilir.", ['IARC_2B'], 'listed', True, 'general_knowledge', None),
    ('E321', 'Bütillenmiş hidroksitoluen (BHT)', 'Butylated hydroxytoluene (BHT)', 'Antioksidan', ['bütillenmiş hidroksitoluen (bht)', 'bütillenmiş hidroksitoluen', 'butylated hydroxytoluene (bht)', 'butylated hydroxytoluene', 'bht', 'bütilhidroksitoluen'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E322', 'Lesitinler', 'Lecithins', 'Emülgatör', ['lesitinler', 'lecithins', 'lesitin', 'lecithin', 'soya lesitini', 'soy lecithin', 'soya fasulyesi lesitini', 'ayçiçek lesitini', 'sunflower lecithin', 'soya lesitin', 'ayçiçeği lesitini', 'ayçiçeği lesitin', 'kolza lesitini'], ['allergen_soy_possible', 'gmo_suspect'], 'green', "Çoğunlukla soya veya ayçiçeğinden elde edilir; soya alerjisi olanlar için önemlidir. AB'de GDO'lu soya etiketlenmek zorundadır; AB dışından gelen ürünlerde GDO'lu soya kaynaklı olabilir.", [], 'listed', True, 'general_knowledge', None),
    ('E325', 'Sodyum laktat', 'Sodium lactate', 'Asitlik düzenleyici / mineral tuz', ['sodyum laktat', 'sodium lactate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E326', 'Potasyum laktat', 'Potassium lactate', 'Asitlik düzenleyici / mineral tuz', ['potasyum laktat', 'potassium lactate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E327', 'Kalsiyum laktat', 'Calcium lactate', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum laktat', 'calcium lactate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E330', 'Sitrik asit', 'Citric acid', 'Asitlik düzenleyici / mineral tuz', ['sitrik asit', 'citric acid', 'limon asidi', 'limon tuzu'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E331', 'Sodyum sitratlar', 'Sodium citrates', 'Asitlik düzenleyici / mineral tuz', ['sodyum sitratlar', 'sodium citrates', 'sodyum sitrat', 'trisodyum sitrat'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E332', 'Potasyum sitratlar', 'Potassium citrates', 'Asitlik düzenleyici / mineral tuz', ['potasyum sitratlar', 'potassium citrates', 'potasyum sitrat'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E333', 'Kalsiyum sitratlar', 'Calcium citrates', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum sitratlar', 'calcium citrates', 'kalsiyum sitrat'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E334', 'Tartarik asit (L-(+))', 'Tartaric acid (L-(+))', 'Asitlik düzenleyici / mineral tuz', ['tartarik asit (l-(+))', 'tartarik asit)', 'tartaric acid (l-(+))', 'tartaric acid)', 'şarap asidi'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E335', 'Sodyum tartaratlar', 'Sodium tartrates', 'Asitlik düzenleyici / mineral tuz', ['sodyum tartaratlar', 'sodium tartrates'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E336', 'Potasyum tartaratlar', 'Potassium tartrates', 'Asitlik düzenleyici / mineral tuz', ['potasyum tartaratlar', 'potassium tartrates', 'kremortartar', 'cream of tartar'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E337', 'Sodyum potasyum tartarat', 'Sodium potassium tartrate', 'Asitlik düzenleyici / mineral tuz', ['sodyum potasyum tartarat', 'sodium potassium tartrate', 'rochelle tuzu', 'rochelle salt'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E338', 'Fosforik asit', 'Phosphoric acid', 'Asitlik düzenleyici / mineral tuz', ['fosforik asit', 'phosphoric acid', 'ortofosforik asit'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E339', 'Sodyum fosfatlar', 'Sodium phosphates', 'Asitlik düzenleyici / mineral tuz', ['sodyum fosfatlar', 'sodium phosphates', 'sodyum fosfat', 'monosodyum fosfat', 'disodyum fosfat', 'trisodyum fosfat'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E340', 'Potasyum fosfatlar', 'Potassium phosphates', 'Asitlik düzenleyici / mineral tuz', ['potasyum fosfatlar', 'potassium phosphates', 'potasyum fosfat'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E341', 'Kalsiyum fosfatlar', 'Calcium phosphates', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum fosfatlar', 'calcium phosphates', 'kalsiyum fosfat', 'trikalsiyum fosfat', 'tricalcium phosphate', 'monokalsiyum fosfat', 'dikalsiyum fosfat'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E343', 'Magnezyum fosfatlar', 'Magnesium phosphates', 'Asitlik düzenleyici / mineral tuz', ['magnezyum fosfatlar', 'magnesium phosphates'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E350', 'Sodyum malatlar', 'Sodium malates', 'Asitlik düzenleyici / mineral tuz', ['sodyum malatlar', 'sodium malates'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E351', 'Potasyum malat', 'Potassium malate', 'Asitlik düzenleyici / mineral tuz', ['potasyum malat', 'potassium malate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E352', 'Kalsiyum malatlar', 'Calcium malates', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum malatlar', 'calcium malates'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E353', 'Metatartarik asit', 'Metatartaric acid', 'Asitlik düzenleyici / mineral tuz', ['metatartarik asit', 'metatartaric acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E354', 'Kalsiyum tartarat', 'Calcium tartrate', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum tartarat', 'calcium tartrate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E355', 'Adipik asit', 'Adipic acid', 'Asitlik düzenleyici / mineral tuz', ['adipik asit', 'adipic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E356', 'Sodyum adipat', 'Sodium adipate', 'Asitlik düzenleyici / mineral tuz', ['sodyum adipat', 'sodium adipate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E357', 'Potasyum adipat', 'Potassium adipate', 'Asitlik düzenleyici / mineral tuz', ['potasyum adipat', 'potassium adipate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E363', 'Süksinik asit', 'Succinic acid', 'Asitlik düzenleyici / mineral tuz', ['süksinik asit', 'succinic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E380', 'Triamonyum sitrat', 'Triammonium citrate', 'Asitlik düzenleyici / mineral tuz', ['triamonyum sitrat', 'triammonium citrate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E385', 'Kalsiyum disodyum etilen diamin tetraasetat', 'Calcium disodium ethylene diamine tetra-acetate', 'Antioksidan', ['kalsiyum disodyum etilen diamin tetraasetat', 'kalsiyum disodyum edta', 'calcium disodium ethylene diamine tetra-acetate', 'calcium disodium edta', 'edta'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E392', 'Biberiye ekstreleri', 'Extracts of rosemary', 'Antioksidan', ['biberiye ekstreleri', 'extracts of rosemary', 'biberiye özütü', 'rosemary extract', 'biberiye ekstresi', 'biberiye ekstraktı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E400', 'Aljinik asit', 'Alginic acid', 'Kıvam artırıcı / jelleştirici', ['aljinik asit', 'alginic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E401', 'Sodyum aljinat', 'Sodium alginate', 'Kıvam artırıcı / jelleştirici', ['sodyum aljinat', 'sodium alginate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E402', 'Potasyum aljinat', 'Potassium alginate', 'Kıvam artırıcı / jelleştirici', ['potasyum aljinat', 'potassium alginate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E403', 'Amonyum aljinat', 'Ammonium alginate', 'Kıvam artırıcı / jelleştirici', ['amonyum aljinat', 'ammonium alginate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E404', 'Kalsiyum aljinat', 'Calcium alginate', 'Kıvam artırıcı / jelleştirici', ['kalsiyum aljinat', 'calcium alginate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E405', 'Propan-1,2-diol aljinat', 'Propane-1,2-diol alginate', 'Kıvam artırıcı / jelleştirici', ['propan-1,2-diol aljinat', 'propane-1,2-diol alginate', 'propilen glikol aljinat'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E406', 'Agar', 'Agar', 'Kıvam artırıcı / jelleştirici', ['agar', 'agar agar', 'agar-agar'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E407', 'Karagenan', 'Carrageenan', 'Kıvam artırıcı / jelleştirici', ['karagenan', 'carrageenan', 'karragenan', 'carrageen', 'irish moss'], ['debated'], 'green', "Kırmızı deniz yosunundan elde edilir. EFSA'nın 2018 değerlendirmesi mevcut kullanım düzeylerinde güvenlik endişesi bildirmemiştir; bazı laboratuvar ve hayvan çalışmaları bağırsak iltihabıyla ilişki öne sürmektedir (tartışmalı).", ['EFSA_2018_reeval'], 'listed', True, 'general_knowledge', None),
    ('E407a', 'İşlenmiş eucheuma deniz yosunu', 'Processed eucheuma seaweed', 'Kıvam artırıcı / jelleştirici', ['işlenmiş eucheuma deniz yosunu', 'processed eucheuma seaweed', 'pes', 'karagenan', 'carrageenan'], ['debated'], 'green', "Karagenan ile aynı kaynaktan (deniz yosunu); tartışma için E407'ye bakınız.", ['EFSA_2018_reeval'], 'listed', True, 'general_knowledge', None),
    ('E410', 'Keçiboynuzu zamkı', 'Locust bean gum', 'Kıvam artırıcı / jelleştirici', ['keçiboynuzu zamkı', 'locust bean gum', 'carob gum', 'harnup zamkı', 'keçiboynuzu unu', 'lbg', 'keçi boynuzu zamkı', 'keçiboynuzu gam', 'keçiboynuzu gamı', 'keçiboynuzu sakızı', 'harnup gamı', 'harnup gam', 'harnup sakızı', 'keçi boynuzu gamı', 'keçi boynuzu gam', 'keçi boynuzu sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E412', 'Guar zamkı', 'Guar gum', 'Kıvam artırıcı / jelleştirici', ['guar zamkı', 'guar gum', 'guar sakızı', 'guar gamı', 'guar gam'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E413', 'Tragakant', 'Tragacanth', 'Kıvam artırıcı / jelleştirici', ['tragakant', 'tragacanth', 'kitre', 'kitre zamkı', 'gum tragacanth', 'kitre gamı', 'kitre gam', 'kitre sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E414', 'Arap zamkı', 'Gum arabic', 'Kıvam artırıcı / jelleştirici', ['arap zamkı', 'akasya zamkı', 'gum arabic', 'acacia gum', 'arabic gum', 'akasya sakızı', 'akasya gamı', 'arap gamı', 'gam arabik', 'arap gam', 'arap sakızı', 'akasya gam'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E415', 'Ksantan zamkı', 'Xanthan gum', 'Kıvam artırıcı / jelleştirici', ['ksantan zamkı', 'xanthan gum', 'xanthan', 'ksantan', 'ksantan gam', 'zantan gam', 'xanthan gam', 'ksantan gamı', 'ksantan sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E416', 'Karaya zamkı', 'Karaya gum', 'Kıvam artırıcı / jelleştirici', ['karaya zamkı', 'karaya gum', 'karaya gamı', 'karaya gam', 'karaya sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E417', 'Tara zamkı', 'Tara gum', 'Kıvam artırıcı / jelleştirici', ['tara zamkı', 'tara gum', 'tara gamı', 'tara gam', 'tara sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E418', 'Gellan zamkı', 'Gellan gum', 'Kıvam artırıcı / jelleştirici', ['gellan zamkı', 'gellan gum', 'gellan', 'gellan gam', 'gellan gamı', 'gellan sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E420', 'Sorbitol', 'Sorbitol', 'Tatlandırıcı', ['sorbitol', 'sorbitol şurubu', 'sorbitol syrup', 'sorbit'], ['laxative_polyols', 'fodmap'], 'yellow', "Poliol (şeker alkolü): %10'dan fazla ilave poliol içeren ürünlerde AB'de “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur; hassas bağırsak (FODMAP) diyetinde kaçınılır.", [], 'listed', True, 'general_knowledge', None),
    ('E421', 'Mannitol', 'Mannitol', 'Tatlandırıcı', ['mannitol', 'manitol'], ['laxative_polyols', 'fodmap'], 'yellow', "Poliol (şeker alkolü): %10'dan fazla ilave poliol içeren ürünlerde AB'de “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur; hassas bağırsak (FODMAP) diyetinde kaçınılır.", [], 'listed', True, 'general_knowledge', None),
    ('E422', 'Gliserol', 'Glycerol', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['gliserol', 'glycerol', 'gliserin', 'glycerin', 'glycerine'], ['vegan_suspect', 'halal_suspect'], 'green', 'Bitkisel veya hayvansal yağlardan elde edilebilir.', [], 'listed', True, 'general_knowledge', None),
    ('E425', 'Konjak', 'Konjac', 'Kıvam artırıcı / jelleştirici', ['konjak', 'konjac', 'konjak zamkı', 'glukomannan', 'glucomannan', 'konjak gamı', 'konjak gam', 'konjak sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E426', 'Soya hemiselülozu', 'Soybean hemicellulose', 'Kıvam artırıcı / jelleştirici', ['soya hemiselülozu', 'soybean hemicellulose'], ['allergen_soy_possible'], 'green', 'Soyadan elde edilir (soya alerjisi olanlar için önemlidir).', [], 'listed', True, 'general_knowledge', None),
    ('E427', 'Kasya zamkı', 'Cassia gum', 'Kıvam artırıcı / jelleştirici', ['kasya zamkı', 'cassia gum', 'sinameki gam', 'sinameki gamı', 'cassia gam', 'kasya gamı', 'kasya gam', 'kasya sakızı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E431', 'Polioksietilen (40) stearat', 'Polyoxyethylene (40) stearate', 'Emülgatör', ['polioksietilen (40) stearat', 'polioksietilen stearat', 'polyoxyethylene (40) stearate', 'polyoxyethylene stearate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E432', 'Polioksietilen sorbitan monolaurat', 'Polyoxyethylene sorbitan monolaurate', 'Emülgatör', ['polioksietilen sorbitan monolaurat', 'polisorbat 20', 'polyoxyethylene sorbitan monolaurate', 'polysorbate 20', 'tween 20', 'polisorbat', 'polysorbate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E433', 'Polioksietilen sorbitan monooleat', 'Polyoxyethylene sorbitan mono-oleate', 'Emülgatör', ['polioksietilen sorbitan monooleat', 'polisorbat 80', 'polyoxyethylene sorbitan mono-oleate', 'polysorbate 80', 'tween 80', 'polisorbat', 'polysorbate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E434', 'Polioksietilen sorbitan monopalmitat', 'Polyoxyethylene sorbitan monopalmitate', 'Emülgatör', ['polioksietilen sorbitan monopalmitat', 'polisorbat 40', 'polyoxyethylene sorbitan monopalmitate', 'polysorbate 40', 'tween 40', 'polisorbat', 'polysorbate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E435', 'Polioksietilen sorbitan monostearat', 'Polyoxyethylene sorbitan monostearate', 'Emülgatör', ['polioksietilen sorbitan monostearat', 'polisorbat 60', 'polyoxyethylene sorbitan monostearate', 'polysorbate 60', 'tween 60', 'polisorbat', 'polysorbate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E436', 'Polioksietilen sorbitan tristearat', 'Polyoxyethylene sorbitan tristearate', 'Emülgatör', ['polioksietilen sorbitan tristearat', 'polisorbat 65', 'polyoxyethylene sorbitan tristearate', 'polysorbate 65', 'tween 65', 'polisorbat', 'polysorbate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E440', 'Pektinler', 'Pectins', 'Kıvam artırıcı / jelleştirici', ['pektinler', 'pectins', 'pektin', 'pectin', 'amidli pektin', 'amidlenmiş pektin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E441', 'Jelatin', 'Gelatine', 'Kıvam artırıcı / jelleştirici', ['jelatin', 'gelatine', 'gelatin', 'sığır jelatini', 'domuz jelatini', 'beef gelatin', 'bovine gelatin', 'porcine gelatin'], ['non_vegan', 'non_vegetarian', 'halal_suspect'], 'green', "Hayvan kemik ve derisinden elde edilir; domuz veya sığır kaynaklı olabilir. AB'de katkı maddesi değil gıda sayıldığı için etikette genellikle E koduyla değil “jelatin” olarak yazılır.", [], 'not_an_additive_in_eu', True, 'general_knowledge', None),
    ('E442', 'Amonyum fosfatidler', 'Ammonium phosphatides', 'Emülgatör', ['amonyum fosfatidler', 'ammonium phosphatides'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E444', 'Sükroz asetat izobütirat', 'Sucrose acetate isobutyrate', 'Stabilizatör / dolgu', ['sükroz asetat izobütirat', 'sucrose acetate isobutyrate', 'sais'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E445', 'Odun reçinesi gliserol esterleri', 'Glycerol esters of wood rosins', 'Stabilizatör / dolgu', ['odun reçinesi gliserol esterleri', 'glycerol esters of wood rosins', 'ester gum', 'reçine esteri'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E450', 'Difosfatlar', 'Diphosphates', 'Asitlik düzenleyici / mineral tuz', ['difosfatlar', 'diphosphates', 'pirofosfat', 'difosfat', 'disodyum difosfat', 'tetrasodyum difosfat', 'sodyum asit pirofosfat', 'sodyum pirofosfat', 'sapp'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E451', 'Trifosfatlar', 'Triphosphates', 'Asitlik düzenleyici / mineral tuz', ['trifosfatlar', 'triphosphates', 'trifosfat', 'pentasodyum trifosfat', 'sodyum tripolifosfat', 'stpp'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E452', 'Polifosfatlar', 'Polyphosphates', 'Asitlik düzenleyici / mineral tuz', ['polifosfatlar', 'polyphosphates', 'polifosfat', 'sodyum polifosfat', 'sodyum hekzametafosfat'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E459', 'Beta-siklodekstrin', 'Beta-cyclodextrin', 'Stabilizatör / dolgu', ['beta-siklodekstrin', 'beta-cyclodextrin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E460', 'Selüloz', 'Cellulose', 'Kıvam artırıcı / jelleştirici', ['selüloz', 'cellulose', 'mikrokristalin selüloz', 'microcrystalline cellulose', 'selüloz tozu', 'powdered cellulose'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E461', 'Metil selüloz', 'Methyl cellulose', 'Kıvam artırıcı / jelleştirici', ['metil selüloz', 'methyl cellulose'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E462', 'Etil selüloz', 'Ethyl cellulose', 'Kıvam artırıcı / jelleştirici', ['etil selüloz', 'ethyl cellulose'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E463', 'Hidroksipropil selüloz', 'Hydroxypropyl cellulose', 'Kıvam artırıcı / jelleştirici', ['hidroksipropil selüloz', 'hydroxypropyl cellulose'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E464', 'Hidroksipropil metil selüloz', 'Hydroxypropyl methyl cellulose', 'Kıvam artırıcı / jelleştirici', ['hidroksipropil metil selüloz', 'hydroxypropyl methyl cellulose', 'hpmc', 'hipromelloz'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E465', 'Etil metil selüloz', 'Ethyl methyl cellulose', 'Kıvam artırıcı / jelleştirici', ['etil metil selüloz', 'ethyl methyl cellulose'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E466', 'Karboksimetil selüloz', 'Carboxy methyl cellulose', 'Kıvam artırıcı / jelleştirici', ['karboksimetil selüloz', 'carboxy methyl cellulose', 'cmc', 'selüloz gam', 'cellulose gum', 'sodyum karboksimetil selüloz', 'sodyum karboksi metil selüloz'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E468', 'Çapraz bağlı sodyum karboksimetil selüloz', 'Crosslinked sodium carboxy methyl cellulose', 'Kıvam artırıcı / jelleştirici', ['çapraz bağlı sodyum karboksimetil selüloz', 'crosslinked sodium carboxy methyl cellulose', 'kroskarmelloz sodyum', 'croscarmellose sodium'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E469', 'Enzimatik hidrolize karboksimetil selüloz', 'Enzymatically hydrolysed carboxy methyl cellulose', 'Kıvam artırıcı / jelleştirici', ['enzimatik hidrolize karboksimetil selüloz', 'enzymatically hydrolysed carboxy methyl cellulose'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E470a', 'Yağ asitlerinin sodyum, potasyum ve kalsiyum tuzları', 'Sodium, potassium and calcium salts of fatty acids', 'Emülgatör', ['yağ asitlerinin sodyum, potasyum ve kalsiyum tuzları', 'sodium, potassium and calcium salts of fatty acids', 'yağ asidi tuzları', 'fatty acid salts'], ['vegan_suspect', 'halal_suspect', 'sodium'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E470b', 'Yağ asitlerinin magnezyum tuzları', 'Magnesium salts of fatty acids', 'Emülgatör', ['yağ asitlerinin magnezyum tuzları', 'magnesium salts of fatty acids', 'magnezyum stearat', 'magnesium stearate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E471', 'Yağ asitlerinin mono ve digliseritleri', 'Mono- and diglycerides of fatty acids', 'Emülgatör', ['yağ asitlerinin mono ve digliseritleri', 'mono- and diglycerides of fatty acids', 'mono ve digliseritler', 'mono- and diglycerides', 'mono ve digliserit', 'monogliserit', 'digliserit', 'gliserol monostearat', 'glycerol monostearate', 'gms', 'mono ve di gliseritler', 'mono digliseritler', 'mono ve digliseridler', 'mono ve digliseritleri'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E472a', 'Yağ asitlerinin mono ve digliseritlerinin asetik asit esterleri', 'Acetic acid esters of mono- and diglycerides of fatty acids', 'Emülgatör', ['yağ asitlerinin mono ve digliseritlerinin asetik asit esterleri', 'acetic acid esters of mono- and diglycerides of fatty acids', 'acetem'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E472b', 'Yağ asitlerinin mono ve digliseritlerinin laktik asit esterleri', 'Lactic acid esters of mono- and diglycerides of fatty acids', 'Emülgatör', ['yağ asitlerinin mono ve digliseritlerinin laktik asit esterleri', 'lactic acid esters of mono- and diglycerides of fatty acids', 'lactem'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E472c', 'Yağ asitlerinin mono ve digliseritlerinin sitrik asit esterleri', 'Citric acid esters of mono- and diglycerides of fatty acids', 'Emülgatör', ['yağ asitlerinin mono ve digliseritlerinin sitrik asit esterleri', 'citric acid esters of mono- and diglycerides of fatty acids', 'citrem'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E472d', 'Yağ asitlerinin mono ve digliseritlerinin tartarik asit esterleri', 'Tartaric acid esters of mono- and diglycerides of fatty acids', 'Emülgatör', ['yağ asitlerinin mono ve digliseritlerinin tartarik asit esterleri', 'tartaric acid esters of mono- and diglycerides of fatty acids'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E472e', 'Yağ asitlerinin mono ve digliseritlerinin mono ve diasetiltartarik asit esterleri', 'Mono- and diacetyltartaric acid esters of mono- and diglycerides of fatty acids', 'Emülgatör', ['yağ asitlerinin mono ve digliseritlerinin mono ve diasetiltartarik asit esterleri', 'mono- and diacetyltartaric acid esters of mono- and diglycerides of fatty acids', 'datem'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E472f', 'Yağ asitlerinin mono ve digliseritlerinin karışık asetik ve tartarik asit esterleri', 'Mixed acetic and tartaric acid esters of mono- and diglycerides of fatty acids', 'Emülgatör', ['yağ asitlerinin mono ve digliseritlerinin karışık asetik ve tartarik asit esterleri', 'mixed acetic and tartaric acid esters of mono- and diglycerides of fatty acids'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E473', 'Yağ asitlerinin sükroz esterleri', 'Sucrose esters of fatty acids', 'Emülgatör', ['yağ asitlerinin sükroz esterleri', 'sucrose esters of fatty acids', 'sükroz esterleri', 'sucrose esters'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E474', 'Sükrogliseritler', 'Sucroglycerides', 'Emülgatör', ['sükrogliseritler', 'sucroglycerides'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E475', 'Yağ asitlerinin poligliserol esterleri', 'Polyglycerol esters of fatty acids', 'Emülgatör', ['yağ asitlerinin poligliserol esterleri', 'polyglycerol esters of fatty acids', 'poligliserol esterleri', 'polyglycerol esters'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E476', 'Poligliserol polirisinoleat', 'Polyglycerol polyricinoleate', 'Emülgatör', ['poligliserol polirisinoleat', 'polyglycerol polyricinoleate', 'pgpr'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E477', 'Yağ asitlerinin propan-1,2-diol esterleri', 'Propane-1,2-diol esters of fatty acids', 'Emülgatör', ['yağ asitlerinin propan-1,2-diol esterleri', 'propane-1,2-diol esters of fatty acids', 'propilen glikol esterleri'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E479b', 'Mono ve digliseritlerle etkileştirilmiş termal oksitlenmiş soya yağı', 'Thermally oxidised soya bean oil interacted with mono- and diglycerides of fatty acids', 'Emülgatör', ['mono ve digliseritlerle etkileştirilmiş termal oksitlenmiş soya yağı', 'thermally oxidised soya bean oil interacted with mono- and diglycerides of fatty acids'], ['allergen_soy_possible'], 'green', 'Soya yağından elde edilir (soya alerjisi olanlar için önemlidir).', [], 'listed', True, 'general_knowledge', None),
    ('E481', 'Sodyum stearoil-2-laktilat', 'Sodium stearoyl-2-lactylate', 'Emülgatör', ['sodyum stearoil-2-laktilat', 'sodium stearoyl-2-lactylate', 'ssl', 'sodyum stearoil laktilat'], ['vegan_suspect', 'halal_suspect', 'sodium'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E482', 'Kalsiyum stearoil-2-laktilat', 'Calcium stearoyl-2-lactylate', 'Emülgatör', ['kalsiyum stearoil-2-laktilat', 'calcium stearoyl-2-lactylate', 'csl', 'kalsiyum stearoil laktilat'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E483', 'Stearil tartarat', 'Stearyl tartrate', 'Emülgatör', ['stearil tartarat', 'stearyl tartrate'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E491', 'Sorbitan monostearat', 'Sorbitan monostearate', 'Emülgatör', ['sorbitan monostearat', 'sorbitan monostearate', 'span 60'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E492', 'Sorbitan tristearat', 'Sorbitan tristearate', 'Emülgatör', ['sorbitan tristearat', 'sorbitan tristearate', 'span 65'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E493', 'Sorbitan monolaurat', 'Sorbitan monolaurate', 'Emülgatör', ['sorbitan monolaurat', 'sorbitan monolaurate', 'span 20'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E494', 'Sorbitan monooleat', 'Sorbitan monooleate', 'Emülgatör', ['sorbitan monooleat', 'sorbitan monooleate', 'span 80'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E495', 'Sorbitan monopalmitat', 'Sorbitan monopalmitate', 'Emülgatör', ['sorbitan monopalmitat', 'sorbitan monopalmitate', 'span 40'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E500', 'Sodyum karbonatlar', 'Sodium carbonates', 'Asitlik düzenleyici / mineral tuz', ['sodyum karbonatlar', 'sodium carbonates', 'sodyum bikarbonat', 'sodium bicarbonate', 'baking soda', 'yemek sodası', 'sodyum hidrojen karbonat', 'karbonat'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E501', 'Potasyum karbonatlar', 'Potassium carbonates', 'Asitlik düzenleyici / mineral tuz', ['potasyum karbonatlar', 'potassium carbonates'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E503', 'Amonyum karbonatlar', 'Ammonium carbonates', 'Asitlik düzenleyici / mineral tuz', ['amonyum karbonatlar', 'ammonium carbonates', 'amonyum bikarbonat', 'ammonium bicarbonate', 'amonyum hidrojen karbonat'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E504', 'Magnezyum karbonatlar', 'Magnesium carbonates', 'Asitlik düzenleyici / mineral tuz', ['magnezyum karbonatlar', 'magnesium carbonates'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E507', 'Hidroklorik asit', 'Hydrochloric acid', 'Asitlik düzenleyici / mineral tuz', ['hidroklorik asit', 'hydrochloric acid', 'tuz ruhu'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E508', 'Potasyum klorür', 'Potassium chloride', 'Asitlik düzenleyici / mineral tuz', ['potasyum klorür', 'potassium chloride'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E509', 'Kalsiyum klorür', 'Calcium chloride', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum klorür', 'calcium chloride'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E511', 'Magnezyum klorür', 'Magnesium chloride', 'Asitlik düzenleyici / mineral tuz', ['magnezyum klorür', 'magnesium chloride'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E512', 'Kalay(II) klorür', 'Stannous chloride', 'Asitlik düzenleyici / mineral tuz', ['kalay(ıı) klorür', 'kalay klorür', 'stannous chloride', 'tin chloride'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E513', 'Sülfürik asit', 'Sulphuric acid', 'Asitlik düzenleyici / mineral tuz', ['sülfürik asit', 'sulphuric acid', 'kükürt asidi'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E514', 'Sodyum sülfatlar', 'Sodium sulphates', 'Asitlik düzenleyici / mineral tuz', ['sodyum sülfatlar', 'sodium sulphates'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E515', 'Potasyum sülfatlar', 'Potassium sulphates', 'Asitlik düzenleyici / mineral tuz', ['potasyum sülfatlar', 'potassium sulphates'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E516', 'Kalsiyum sülfat', 'Calcium sulphate', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum sülfat', 'calcium sulphate', 'alçı taşı', 'gypsum'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E517', 'Amonyum sülfat', 'Ammonium sulphate', 'Asitlik düzenleyici / mineral tuz', ['amonyum sülfat', 'ammonium sulphate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E520', 'Alüminyum sülfat', 'Aluminium sulphate', 'Asitlik düzenleyici / mineral tuz', ['alüminyum sülfat', 'aluminium sulphate'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E521', 'Alüminyum sodyum sülfat', 'Aluminium sodium sulphate', 'Asitlik düzenleyici / mineral tuz', ['alüminyum sodyum sülfat', 'aluminium sodium sulphate'], ['sodium', 'aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E522', 'Alüminyum potasyum sülfat', 'Aluminium potassium sulphate', 'Asitlik düzenleyici / mineral tuz', ['alüminyum potasyum sülfat', 'aluminium potassium sulphate', 'şap', 'alum'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E523', 'Alüminyum amonyum sülfat', 'Aluminium ammonium sulphate', 'Asitlik düzenleyici / mineral tuz', ['alüminyum amonyum sülfat', 'aluminium ammonium sulphate'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E524', 'Sodyum hidroksit', 'Sodium hydroxide', 'Asitlik düzenleyici / mineral tuz', ['sodyum hidroksit', 'sodium hydroxide', 'kostik soda', 'caustic soda', 'lye'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E525', 'Potasyum hidroksit', 'Potassium hydroxide', 'Asitlik düzenleyici / mineral tuz', ['potasyum hidroksit', 'potassium hydroxide', 'kostik potas'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E526', 'Kalsiyum hidroksit', 'Calcium hydroxide', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum hidroksit', 'calcium hydroxide', 'sönmüş kireç', 'slaked lime'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E527', 'Amonyum hidroksit', 'Ammonium hydroxide', 'Asitlik düzenleyici / mineral tuz', ['amonyum hidroksit', 'ammonium hydroxide', 'amonyak'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E528', 'Magnezyum hidroksit', 'Magnesium hydroxide', 'Asitlik düzenleyici / mineral tuz', ['magnezyum hidroksit', 'magnesium hydroxide'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E529', 'Kalsiyum oksit', 'Calcium oxide', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum oksit', 'calcium oxide', 'sönmemiş kireç', 'quicklime'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E530', 'Magnezyum oksit', 'Magnesium oxide', 'Asitlik düzenleyici / mineral tuz', ['magnezyum oksit', 'magnesium oxide'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E535', 'Sodyum ferrosiyanür', 'Sodium ferrocyanide', 'Topaklanmayı önleyici', ['sodyum ferrosiyanür', 'sodium ferrocyanide'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E536', 'Potasyum ferrosiyanür', 'Potassium ferrocyanide', 'Topaklanmayı önleyici', ['potasyum ferrosiyanür', 'potassium ferrocyanide'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E538', 'Kalsiyum ferrosiyanür', 'Calcium ferrocyanide', 'Topaklanmayı önleyici', ['kalsiyum ferrosiyanür', 'calcium ferrocyanide'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E541', 'Sodyum alüminyum fosfat', 'Sodium aluminium phosphate', 'Asitlik düzenleyici / mineral tuz', ['sodyum alüminyum fosfat', 'sodium aluminium phosphate'], ['sodium', 'aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E551', 'Silikon dioksit', 'Silicon dioxide', 'Topaklanmayı önleyici', ['silikon dioksit', 'silicon dioxide', 'silika', 'silica', 'silisyum dioksit', 'amorf silika'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E552', 'Kalsiyum silikat', 'Calcium silicate', 'Topaklanmayı önleyici', ['kalsiyum silikat', 'calcium silicate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E553a', 'Magnezyum silikat', 'Magnesium silicate', 'Topaklanmayı önleyici', ['magnezyum silikat', 'magnezyum trisilikat', 'magnesium silicate', 'magnesium trisilicate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E553b', 'Talk', 'Talc', 'Topaklanmayı önleyici', ['talk', 'talc', 'talkum'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E554', 'Sodyum alüminyum silikat', 'Sodium aluminium silicate', 'Topaklanmayı önleyici', ['sodyum alüminyum silikat', 'sodium aluminium silicate'], ['sodium', 'aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E555', 'Potasyum alüminyum silikat', 'Potassium aluminium silicate', 'Topaklanmayı önleyici', ['potasyum alüminyum silikat', 'potassium aluminium silicate'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E556', 'Alüminyum kalsiyum silikat', 'Aluminium calcium silicate', 'Topaklanmayı önleyici', ['alüminyum kalsiyum silikat', 'aluminium calcium silicate'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E558', 'Bentonit', 'Bentonite', 'Topaklanmayı önleyici', ['bentonit', 'bentonite'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E559', 'Alüminyum silikat', 'Aluminium silicate', 'Topaklanmayı önleyici', ['alüminyum silikat', 'kaolin', 'aluminium silicate'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E570', 'Yağ asitleri', 'Fatty acids', 'Emülgatör', ['yağ asitleri', 'fatty acids', 'stearik asit', 'stearic acid', 'yağ asidi'], ['vegan_suspect', 'halal_suspect'], 'green', 'Yağ asidi kaynağı bitkisel veya hayvansal (sığır/domuz dahil) olabilir; etikette kaynak çoğu zaman belirtilmez.', [], 'listed', True, 'general_knowledge', None),
    ('E574', 'Glukonik asit', 'Gluconic acid', 'Asitlik düzenleyici / mineral tuz', ['glukonik asit', 'gluconic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E575', 'Glukono delta-lakton', 'Glucono delta-lactone', 'Asitlik düzenleyici / mineral tuz', ['glukono delta-lakton', 'glucono delta-lactone', 'gdl', 'glukonolakton'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E576', 'Sodyum glukonat', 'Sodium gluconate', 'Asitlik düzenleyici / mineral tuz', ['sodyum glukonat', 'sodium gluconate'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E577', 'Potasyum glukonat', 'Potassium gluconate', 'Asitlik düzenleyici / mineral tuz', ['potasyum glukonat', 'potassium gluconate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E578', 'Kalsiyum glukonat', 'Calcium gluconate', 'Asitlik düzenleyici / mineral tuz', ['kalsiyum glukonat', 'calcium gluconate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E579', 'Demir(II) glukonat', 'Ferrous gluconate', 'Asitlik düzenleyici / mineral tuz', ['demir(ıı) glukonat', 'demir glukonat', 'ferrous gluconate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E585', 'Demir(II) laktat', 'Ferrous lactate', 'Asitlik düzenleyici / mineral tuz', ['demir(ıı) laktat', 'demir laktat', 'ferrous lactate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E586', '4-Heksilresorsinol', '4-Hexylresorcinol', 'Antioksidan', ['4-heksilresorsinol', '4-hexylresorcinol'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E620', 'Glutamik asit', 'Glutamic acid', 'Lezzet artırıcı', ['glutamik asit', 'glutamic acid', 'l-glutamik asit', 'glutamat', 'glutamate'], ['debated'], 'yellow', "Glutamatlar (E620-E625): EFSA 2017'de grup ADI (30 mg/kg vücut ağırlığı/gün) belirledi ve bazı yüksek tüketim senaryolarında bu değerin aşılabileceğini belirtti. “Nörotoksin” iddiası resmi kurumlarca bu şekilde sınıflandırılmıyor; duyarlı kişilerde baş ağrısı bildirimleri var.", ['EFSA_ADI_2017'], 'listed', True, 'general_knowledge', None),
    ('E621', 'Monosodyum glutamat', 'Monosodium glutamate', 'Lezzet artırıcı', ['monosodyum glutamat', 'monosodium glutamate', 'msg', 'çin tuzu', 'chinese salt', 'sodyum glutamat', 'sodium glutamate', 'glutamat', 'glutamate', 'flavour enhancer 621', 'aroma arttırıcı (monosodyum glutamat)', 'monosodyum glutamat (çin tuzu)'], ['debated', 'sodium'], 'yellow', "Glutamatlar (E620-E625): EFSA 2017'de grup ADI (30 mg/kg vücut ağırlığı/gün) belirledi ve bazı yüksek tüketim senaryolarında bu değerin aşılabileceğini belirtti. “Nörotoksin” iddiası resmi kurumlarca bu şekilde sınıflandırılmıyor; duyarlı kişilerde baş ağrısı bildirimleri var.", ['EFSA_ADI_2017'], 'listed', True, 'general_knowledge', None),
    ('E622', 'Monopotasyum glutamat', 'Monopotassium glutamate', 'Lezzet artırıcı', ['monopotasyum glutamat', 'monopotassium glutamate', 'glutamat', 'glutamate'], ['debated'], 'yellow', "Glutamatlar (E620-E625): EFSA 2017'de grup ADI (30 mg/kg vücut ağırlığı/gün) belirledi ve bazı yüksek tüketim senaryolarında bu değerin aşılabileceğini belirtti. “Nörotoksin” iddiası resmi kurumlarca bu şekilde sınıflandırılmıyor; duyarlı kişilerde baş ağrısı bildirimleri var.", ['EFSA_ADI_2017'], 'listed', True, 'general_knowledge', None),
    ('E623', 'Kalsiyum diglutamat', 'Calcium diglutamate', 'Lezzet artırıcı', ['kalsiyum diglutamat', 'calcium diglutamate', 'glutamat', 'glutamate'], ['debated'], 'yellow', "Glutamatlar (E620-E625): EFSA 2017'de grup ADI (30 mg/kg vücut ağırlığı/gün) belirledi ve bazı yüksek tüketim senaryolarında bu değerin aşılabileceğini belirtti. “Nörotoksin” iddiası resmi kurumlarca bu şekilde sınıflandırılmıyor; duyarlı kişilerde baş ağrısı bildirimleri var.", ['EFSA_ADI_2017'], 'listed', True, 'general_knowledge', None),
    ('E624', 'Monoamonyum glutamat', 'Monoammonium glutamate', 'Lezzet artırıcı', ['monoamonyum glutamat', 'monoammonium glutamate', 'glutamat', 'glutamate'], ['debated'], 'yellow', "Glutamatlar (E620-E625): EFSA 2017'de grup ADI (30 mg/kg vücut ağırlığı/gün) belirledi ve bazı yüksek tüketim senaryolarında bu değerin aşılabileceğini belirtti. “Nörotoksin” iddiası resmi kurumlarca bu şekilde sınıflandırılmıyor; duyarlı kişilerde baş ağrısı bildirimleri var.", ['EFSA_ADI_2017'], 'listed', True, 'general_knowledge', None),
    ('E625', 'Magnezyum diglutamat', 'Magnesium diglutamate', 'Lezzet artırıcı', ['magnezyum diglutamat', 'magnesium diglutamate', 'glutamat', 'glutamate'], ['debated'], 'yellow', "Glutamatlar (E620-E625): EFSA 2017'de grup ADI (30 mg/kg vücut ağırlığı/gün) belirledi ve bazı yüksek tüketim senaryolarında bu değerin aşılabileceğini belirtti. “Nörotoksin” iddiası resmi kurumlarca bu şekilde sınıflandırılmıyor; duyarlı kişilerde baş ağrısı bildirimleri var.", ['EFSA_ADI_2017'], 'listed', True, 'general_knowledge', None),
    ('E626', 'Guanilik asit', 'Guanylic acid', 'Lezzet artırıcı', ['guanilik asit', 'guanylic acid'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E627', 'Disodyum guanilat', 'Disodium guanylate', 'Lezzet artırıcı', ['disodyum guanilat', 'disodium guanylate', 'ribonükleotit'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E628', 'Dipotasyum guanilat', 'Dipotassium guanylate', 'Lezzet artırıcı', ['dipotasyum guanilat', 'dipotassium guanylate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E629', 'Kalsiyum guanilat', 'Calcium guanylate', 'Lezzet artırıcı', ['kalsiyum guanilat', 'calcium guanylate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E630', 'İnosinik asit', 'Inosinic acid', 'Lezzet artırıcı', ['inosinik asit', 'inosinic acid'], ['vegan_suspect'], 'green', 'Hayvansal (et/balık) veya fermantasyon kaynaklı olabilir; kaynak belirtilmeyebilir.', [], 'listed', True, 'general_knowledge', None),
    ('E631', 'Disodyum inosinat', 'Disodium inosinate', 'Lezzet artırıcı', ['disodyum inosinat', 'disodium inosinate', 'ribonükleotit'], ['vegan_suspect', 'sodium'], 'green', 'Hayvansal (et/balık) veya fermantasyon kaynaklı olabilir; kaynak belirtilmeyebilir.', [], 'listed', True, 'general_knowledge', None),
    ('E632', 'Dipotasyum inosinat', 'Dipotassium inosinate', 'Lezzet artırıcı', ['dipotasyum inosinat', 'dipotassium inosinate'], ['vegan_suspect'], 'green', 'Hayvansal (et/balık) veya fermantasyon kaynaklı olabilir; kaynak belirtilmeyebilir.', [], 'listed', True, 'general_knowledge', None),
    ('E633', 'Kalsiyum inosinat', 'Calcium inosinate', 'Lezzet artırıcı', ['kalsiyum inosinat', 'calcium inosinate'], ['vegan_suspect'], 'green', 'Hayvansal (et/balık) veya fermantasyon kaynaklı olabilir; kaynak belirtilmeyebilir.', [], 'listed', True, 'general_knowledge', None),
    ('E634', "Kalsiyum 5'-ribonükleotitler", "Calcium 5'-ribonucleotides", 'Lezzet artırıcı', ["kalsiyum 5'-ribonükleotitler", "calcium 5'-ribonucleotides", 'ribonükleotit'], ['vegan_suspect'], 'green', 'Hayvansal (et/balık) veya fermantasyon kaynaklı olabilir; kaynak belirtilmeyebilir.', [], 'listed', True, 'general_knowledge', None),
    ('E635', "Disodyum 5'-ribonükleotitler", "Disodium 5'-ribonucleotides", 'Lezzet artırıcı', ["disodyum 5'-ribonükleotitler", "disodium 5'-ribonucleotides", 'ribonükleotit'], ['vegan_suspect', 'sodium'], 'green', 'Hayvansal (et/balık) veya fermantasyon kaynaklı olabilir; kaynak belirtilmeyebilir.', [], 'listed', True, 'general_knowledge', None),
    ('E640', 'Glisin ve sodyum tuzu', 'Glycine and its sodium salt', 'Lezzet artırıcı', ['glisin ve sodyum tuzu', 'glycine and its sodium salt', 'glisin', 'glycine'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E650', 'Çinko asetat', 'Zinc acetate', 'Lezzet artırıcı', ['çinko asetat', 'zinc acetate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E900', 'Dimetilpolisiloksan', 'Dimethylpolysiloxane', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['dimetilpolisiloksan', 'dimethylpolysiloxane', 'silikon', 'silicone', 'polidimetilsiloksan', 'pdms', 'köpük kesici'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E901', 'Balmumu (beyaz ve sarı)', 'Beeswax (white and yellow)', 'Parlatıcı / kaplama maddesi', ['balmumu (beyaz ve sarı)', 'balmumu', 'beeswax (white and yellow)', 'beeswax', 'bal mumu'], ['non_vegan'], 'green', 'Arı ürünüdür (vegan değildir).', [], 'listed', True, 'general_knowledge', None),
    ('E902', 'Kandelilla mumu', 'Candelilla wax', 'Parlatıcı / kaplama maddesi', ['kandelilla mumu', 'candelilla wax'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E903', 'Karnauba mumu', 'Carnauba wax', 'Parlatıcı / kaplama maddesi', ['karnauba mumu', 'carnauba wax', 'karnauba', 'carnauba'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E904', 'Gomalak', 'Shellac', 'Parlatıcı / kaplama maddesi', ['gomalak', 'shellac', 'şellak', 'lak', "confectioner's glaze", 'glaze'], ['non_vegan', 'insect_derived'], 'green', 'Lak böceğinin salgısından elde edilir (vegan değildir).', [], 'listed', True, 'general_knowledge', None),
    ('E905', 'Mikrokristalin mum', 'Microcrystalline wax', 'Parlatıcı / kaplama maddesi', ['mikrokristalin mum', 'microcrystalline wax'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E907', 'Hidrojenize poli-1-deken', 'Hydrogenated poly-1-decene', 'Parlatıcı / kaplama maddesi', ['hidrojenize poli-1-deken', 'hydrogenated poly-1-decene'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E912', 'Montan asit esterleri', 'Montan acid esters', 'Parlatıcı / kaplama maddesi', ['montan asit esterleri', 'montan acid esters'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E914', 'Oksitlenmiş polietilen mumu', 'Oxidised polyethylene wax', 'Parlatıcı / kaplama maddesi', ['oksitlenmiş polietilen mumu', 'oxidised polyethylene wax'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E920', 'L-Sistein', 'L-Cysteine', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['l-sistein', 'l-cysteine', 'sistein', 'cysteine'], ['vegan_suspect', 'halal_suspect'], 'green', 'Tüy, boynuz veya bazı ülkelerde insan saçından elde edilebilir; fermantasyon veya sentetik kaynaklıları da vardır.', [], 'listed', True, 'general_knowledge', None),
    ('E924a', 'Potasyum bromat', 'Potassium bromate', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['potasyum bromat', 'potassium bromate', 'bromat', 'bromate'], ['banned_eu'], 'red', "AB'de gıda katkısı olarak izinli değil (genel bilgi; doğrulanmalı). California AB 418 ile 2027'den itibaren yasaklanıyor.", ['EU_not_listed', 'CA_AB418_2027'], 'not_listed', True, 'general_knowledge', None),
    ('E927b', 'Karbamid', 'Carbamide', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['karbamid', 'carbamide', 'üre', 'urea'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E938', 'Argon', 'Argon', 'Gaz / itici gaz', ['argon'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E939', 'Helyum', 'Helium', 'Gaz / itici gaz', ['helyum', 'helium'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E941', 'Azot', 'Nitrogen', 'Gaz / itici gaz', ['azot', 'nitrogen', 'nitrojen'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E942', 'Diazot monoksit', 'Nitrous oxide', 'Gaz / itici gaz', ['diazot monoksit', 'nitrous oxide', 'azot protoksit', 'gülme gazı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E943a', 'Bütan', 'Butane', 'Gaz / itici gaz', ['bütan', 'butane'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E943b', 'İzobütan', 'Iso-butane', 'Gaz / itici gaz', ['izobütan', 'iso-butane'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E944', 'Propan', 'Propane', 'Gaz / itici gaz', ['propan', 'propane'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E948', 'Oksijen', 'Oxygen', 'Gaz / itici gaz', ['oksijen', 'oxygen'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E949', 'Hidrojen', 'Hydrogen', 'Gaz / itici gaz', ['hidrojen', 'hydrogen'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E950', 'Asesülfam K', 'Acesulfame K', 'Tatlandırıcı', ['asesülfam k', 'acesulfame k', 'acesulfame potassium', 'asesülfam potasyum', 'asesulfam k', 'acesulfame-k', 'ace-k', 'ace k'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E951', 'Aspartam', 'Aspartame', 'Tatlandırıcı', ['aspartam', 'aspartame', 'nutrasweet'], ['iarc_listed', 'phenylalanine'], 'yellow', "IARC 2023'te aspartamı Grup 2B (olası kanserojen) olarak sınıflandırdı; JECFA ise günlük kabul edilebilir alım değerini (40 mg/kg) değiştirmedi. Fenilketonürililer için etikette “fenilalanin kaynağı içerir” uyarısı zorunludur.", ['IARC_2B_2023', 'EU_phenylalanine_label'], 'listed', True, 'general_knowledge', None),
    ('E952', 'Siklamik asit ve sodyum, kalsiyum tuzları', 'Cyclamic acid and its Na and Ca salts', 'Tatlandırıcı', ['siklamik asit ve sodyum, kalsiyum tuzları', 'cyclamic acid and its na and ca salts', 'siklamat', 'cyclamate', 'sodyum siklamat', 'sodium cyclamate', 'siklamik asit'], ['fda_banned', 'sodium'], 'red', "ABD'de 1969-1970'ten beri gıdada izinli değildir; AB'de izinlidir ve kabul edilebilir günlük alım değeri belirlenmiştir.", ['FDA_banned_1970'], 'listed', True, 'general_knowledge', None),
    ('E953', 'İzomalt', 'Isomalt', 'Tatlandırıcı', ['izomalt', 'isomalt'], ['laxative_polyols', 'fodmap'], 'yellow', "Poliol (şeker alkolü): %10'dan fazla ilave poliol içeren ürünlerde AB'de “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur; hassas bağırsak (FODMAP) diyetinde kaçınılır.", [], 'listed', True, 'general_knowledge', None),
    ('E954', 'Sakarin ve sodyum, potasyum, kalsiyum tuzları', 'Saccharin and its Na, K and Ca salts', 'Tatlandırıcı', ['sakarin ve sodyum, potasyum, kalsiyum tuzları', 'saccharin and its na, k and ca salts', 'sakarin', 'saccharin', 'sodyum sakarin', 'sodium saccharin'], ['debated', 'sodium'], 'green', "Hayvan deneylerindeki mesane tümörü bulgusunun insana uyarlanamadığı sonucuyla IARC 1999'da Grup 3'e indirdi; ABD NTP 2000'de kanserojen listesinden çıkardı.", ['IARC_3_1999'], 'listed', True, 'general_knowledge', None),
    ('E955', 'Sukraloz', 'Sucralose', 'Tatlandırıcı', ['sukraloz', 'sucralose', 'splenda'], ['debated'], 'green', 'Bağırsak mikrobiyomu ve sindirim yan ürünleri üzerine çalışmalar sürmektedir; bu listede kesin bir zarar kanıtı işaretlenmemiştir.', [], 'listed', True, 'general_knowledge', None),
    ('E957', 'Taumatin', 'Thaumatin', 'Tatlandırıcı', ['taumatin', 'thaumatin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E959', 'Neohesperidin DC', 'Neohesperidine DC', 'Tatlandırıcı', ['neohesperidin dc', 'neohesperidine dc', 'neohesperidin dihidrokalkon', 'nhdc'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E960', 'Steviol glikozitler', 'Steviol glycosides', 'Tatlandırıcı', ['steviol glikozitler', 'steviol glycosides', 'stevya', 'stevia', 'steviol glikozit', 'rebaudioside a', 'reb a', 'rebaudiosid a', 'stevia ekstresi', 'steviol glikozitleri', 'stevia yaprağı özütü', 'stevia ekstraktı', 'stevia özütü', 'stevia yaprağı ekstresi', 'stevia yaprağı ekstraktı'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E961', 'Neotam', 'Neotame', 'Tatlandırıcı', ['neotam', 'neotame'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E962', 'Aspartam-asesülfam tuzu', 'Salt of aspartame-acesulfame', 'Tatlandırıcı', ['aspartam-asesülfam tuzu', 'salt of aspartame-acesulfame', 'aspartam-asesülfam', 'aspartame-acesulfame salt'], ['iarc_listed', 'phenylalanine'], 'yellow', "Aspartam içerir: IARC 2023'te aspartamı Grup 2B (olası kanserojen) olarak sınıflandırdı. Fenilketonürililer için etikette “fenilalanin kaynağı içerir” uyarısı zorunludur.", ['IARC_2B_2023', 'EU_phenylalanine_label'], 'listed', True, 'general_knowledge', None),
    ('E964', 'Poliglisitol şurubu', 'Polyglycitol syrup', 'Tatlandırıcı', ['poliglisitol şurubu', 'polyglycitol syrup', 'hidrojenize nişasta hidrolizatı', 'hydrogenated starch hydrolysate'], ['laxative_polyols', 'fodmap'], 'yellow', "Poliol (şeker alkolü): %10'dan fazla ilave poliol içeren ürünlerde AB'de “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur; hassas bağırsak (FODMAP) diyetinde kaçınılır.", [], 'listed', True, 'general_knowledge', None),
    ('E965', 'Maltitol', 'Maltitol', 'Tatlandırıcı', ['maltitol', 'maltitol şurubu', 'maltitol syrup'], ['laxative_polyols', 'fodmap'], 'yellow', "Poliol (şeker alkolü): %10'dan fazla ilave poliol içeren ürünlerde AB'de “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur; hassas bağırsak (FODMAP) diyetinde kaçınılır.", [], 'listed', True, 'general_knowledge', None),
    ('E966', 'Laktitol', 'Lactitol', 'Tatlandırıcı', ['laktitol', 'lactitol'], ['laxative_polyols', 'fodmap'], 'yellow', "Poliol (şeker alkolü): %10'dan fazla ilave poliol içeren ürünlerde AB'de “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur; hassas bağırsak (FODMAP) diyetinde kaçınılır.", [], 'listed', True, 'general_knowledge', None),
    ('E967', 'Ksilitol', 'Xylitol', 'Tatlandırıcı', ['ksilitol', 'xylitol', 'huş ağacı şekeri'], ['laxative_polyols', 'fodmap', 'pet_risk'], 'yellow', "Poliol (şeker alkolü): %10'dan fazla ilave poliol içeren ürünlerde AB'de “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur; hassas bağırsak (FODMAP) diyetinde kaçınılır. Köpekler için çok toksiktir; evcil hayvanlara verilmemelidir.", [], 'listed', True, 'general_knowledge', None),
    ('E968', 'Eritritol', 'Erythritol', 'Tatlandırıcı', ['eritritol', 'erythritol', 'eritrit'], ['debated'], 'green', "2023'te yayımlanan çalışmalar kandaki eritritol düzeyiyle kardiyovasküler olay riski arasında ilişki bildirdi; nedensellik kanıtlanmadı.", [], 'listed', True, 'general_knowledge', None),
    ('E969', 'Advantam', 'Advantame', 'Tatlandırıcı', ['advantam', 'advantame'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E999', 'Quillaia ekstresi', 'Quillaia extract', 'Stabilizatör / dolgu', ['quillaia ekstresi', 'quillaia extract', 'quillaja', 'quillaia', 'quillaia ekstraktı', 'quillaia özütü'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1103', 'İnvertaz', 'Invertase', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['invertaz', 'invertase'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1105', 'Lizozim', 'Lysozyme', 'Koruyucu', ['lizozim', 'lysozyme', 'lisozim'], ['allergen_egg', 'non_vegan'], 'green', 'Yumurta akından elde edilir (yumurta alerjisi olanlar için önemlidir).', [], 'listed', True, 'general_knowledge', None),
    ('E1200', 'Polidekstroz', 'Polydextrose', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['polidekstroz', 'polydextrose'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1201', 'Polivinilpirolidon', 'Polyvinylpyrrolidone', 'Stabilizatör / dolgu', ['polivinilpirolidon', 'polyvinylpyrrolidone', 'pvp', 'povidon', 'povidone'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1202', 'Polivinilpolipirolidon', 'Polyvinylpolypyrrolidone', 'Stabilizatör / dolgu', ['polivinilpolipirolidon', 'polyvinylpolypyrrolidone', 'pvpp', 'krospovidon'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1203', 'Polivinil alkol', 'Polyvinyl alcohol', 'Parlatıcı / kaplama maddesi', ['polivinil alkol', 'polyvinyl alcohol', 'pva'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1204', 'Pululan', 'Pullulan', 'Kıvam artırıcı / jelleştirici', ['pululan', 'pullulan'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1205', 'Bazik metakrilat kopolimeri', 'Basic methacrylate copolymer', 'Parlatıcı / kaplama maddesi', ['bazik metakrilat kopolimeri', 'basic methacrylate copolymer'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1404', 'Okside nişasta', 'Oxidised starch', 'Modifiye nişasta', ['okside nişasta', 'oxidised starch', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1410', 'Mononişasta fosfat', 'Monostarch phosphate', 'Modifiye nişasta', ['mononişasta fosfat', 'monostarch phosphate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1412', 'Dinişasta fosfat', 'Distarch phosphate', 'Modifiye nişasta', ['dinişasta fosfat', 'distarch phosphate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1413', 'Fosfatlanmış dinişasta fosfat', 'Phosphated distarch phosphate', 'Modifiye nişasta', ['fosfatlanmış dinişasta fosfat', 'phosphated distarch phosphate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1414', 'Asetillenmiş dinişasta fosfat', 'Acetylated distarch phosphate', 'Modifiye nişasta', ['asetillenmiş dinişasta fosfat', 'acetylated distarch phosphate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1420', 'Asetillenmiş nişasta', 'Acetylated starch', 'Modifiye nişasta', ['asetillenmiş nişasta', 'acetylated starch', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1422', 'Asetillenmiş dinişasta adipat', 'Acetylated distarch adipate', 'Modifiye nişasta', ['asetillenmiş dinişasta adipat', 'acetylated distarch adipate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1440', 'Hidroksipropil nişasta', 'Hydroxypropyl starch', 'Modifiye nişasta', ['hidroksipropil nişasta', 'hydroxypropyl starch', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1442', 'Hidroksipropil dinişasta fosfat', 'Hydroxypropyl distarch phosphate', 'Modifiye nişasta', ['hidroksipropil dinişasta fosfat', 'hydroxypropyl distarch phosphate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1450', 'Nişasta sodyum oktenil süksinat', 'Starch sodium octenyl succinate', 'Modifiye nişasta', ['nişasta sodyum oktenil süksinat', 'starch sodium octenyl succinate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], ['sodium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1451', 'Asetillenmiş okside nişasta', 'Acetylated oxidised starch', 'Modifiye nişasta', ['asetillenmiş okside nişasta', 'acetylated oxidised starch', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1452', 'Nişasta alüminyum oktenil süksinat', 'Starch aluminium octenyl succinate', 'Modifiye nişasta', ['nişasta alüminyum oktenil süksinat', 'starch aluminium octenyl succinate', 'modifiye nişasta', 'modified starch', 'modifiye mısır nişastası', 'modifiye patates nişastası', 'modifiye buğday nişastası', 'modifiye tapyoka nişastası', 'modified maize starch', 'modified corn starch', 'modified potato starch', 'modified tapioca starch', 'modified wheat starch'], ['aluminium'], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1505', 'Trietil sitrat', 'Triethyl citrate', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['trietil sitrat', 'triethyl citrate'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1517', 'Gliseril diasetat', 'Glyceryl diacetate', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['gliseril diasetat', 'diasetin', 'glyceryl diacetate', 'diacetin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1518', 'Gliseril triasetat', 'Glyceryl triacetate', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['gliseril triasetat', 'triasetin', 'glyceryl triacetate', 'triacetin'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1519', 'Benzil alkol', 'Benzyl alcohol', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['benzil alkol', 'benzyl alcohol'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1520', 'Propan-1,2-diol', 'Propane-1,2-diol', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['propan-1,2-diol', 'propilen glikol', 'propane-1,2-diol', 'propylene glycol'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
    ('E1521', 'Polietilen glikol', 'Polyethylene glycol', 'Diğer (taşıyıcı, nem tutucu, çözücü vb.)', ['polietilen glikol', 'polyethylene glycol', 'peg', 'makrogol', 'macrogol'], [], 'green', None, [], 'listed', False, 'inventory_only', None),
]


# 03.10.2026 kaynak doğrulaması. Anahtar: E kodu -> {sources, isteğe bağlı reason/risk/flags/partial}.
# partial=True: iddianın bir kısmı doğrulandı (needs_review kalır). TR izin durumu belirsiz kayıtlar da needs_review kalır.
S6 = "https://cms.law/en/gbr/legal-updates/compulsory-warnings-on-colours-in-food-and-drink"
BENZ = "https://www.fda.gov/food/process-contaminants-food/questions-and-answers-occurrence-benzene-soft-drinks-and-other-beverages"
SULF = "https://www.denib.gov.tr/files/downloads/sirku_ekleri/2016-02-ek1-1.pdf"
NITR = "https://science.food.gov.uk/article/144676-safety-of-nitrates-and-nitrites-as-food-additives"
POLY = "https://www.cargill.com/food-beverage/emea/eu-labeling-and-legislation"
GLU = "https://efsa.europa.eu/en/efsajournal/pub/4910"
ASP = "https://www.who.int/news/item/14-07-2023-aspartame-hazard-and-risk-assessment-results-released"
AB418 = "https://bclplaw.com/en-US/events-insights-news/california-bans-use-of-certain-food-additives.html"
CARR = "https://pmc.ncbi.nlm.nih.gov/articles/PMC7009739"
CARR_REASON = ("Kırmızı deniz yosunundan elde edilir. EFSA 2018 yeniden değerlendirmesinde mevcut grup ADI'yi (75 mg/kg vücut ağırlığı/gün) "
               "veri eksikleri nedeniyle geçici saydı ve bazı nüfus gruplarında tahmini alımın bu değeri 10 kata kadar aşabildiğini bildirdi.")
VERIFY = {
    **{k: {"sources": [S6]} for k in ("E102", "E104", "E110", "E122", "E124", "E129")},
    "E123": {"sources": ["https://en.wikipedia.org/wiki/Amaranth_(dye)"]},
    "E128": {"sources": ["https://www.ecolex.org/details/legislation/commission-regulation-ec-no-8842007-on-emergency-measures-suspending-the-use-of-e-128-red-2g-as-food-colour-lex-faoc073000/"]},
    "E150c": {"sources": ["https://www.cfs.gov.hk/english/programme/programme_rafs/programme_rafs_fa_01_07.html"]},
    "E150d": {"sources": ["https://www.cfs.gov.hk/english/programme/programme_rafs/programme_rafs_fa_01_07.html"]},
    "E154": {"sources": ["https://en.wikipedia.org/wiki/Brown_FK"], "risk": "red", "flags": ["banned_eu"],
             "reason": "AB'de gıda katkısı olarak izinli değil: EFSA 2011'de artık kullanılmadığını bildirdi ve AB izinli listesine alınmadı."},
    "E160f": {"sources": ["https://en.wikipedia.org/wiki/Food_orange_7"], "risk": "red", "flags": ["banned_eu"],
              "reason": "AB izinli katkı listesinden Kasım 2011'de (Tüzük 1129/2011) artık üretilmediği için çıkarıldı."},
    "E161g": {"sources": ["https://efsa.europa.eu/en/efsajournal/pub/1852"],
              "reason": "Renklendirici. AB'de gıdada yalnızca Strasbourg sosisinde (saucisse de Strasbourg) izinlidir; EFSA ADI'yi 0,03 mg/kg olarak belirledi ve alımın bu değeri aşmasının olası olmadığını bildirdi."},
    "E171": {"sources": ["https://www.fsai.ie/news-and-alerts/latest-news/titanium-dioxide-is-no-longer-authorised-as-a-food"]},
    **{k: {"sources": [BENZ]} for k in ("E210", "E211", "E212", "E213")},
    "E216": {"sources": [AB418], "partial": True},
    "E217": {"sources": [AB418], "partial": True},
    "E924a": {"sources": ["https://bakeryandsnacks.com/Article/2019/09/25/Potassium-bromate-in-bread-Outlawed-in-Europe-but-considered-safe-in-America", AB418],
              "reason": "AB'de un işlem maddesi olarak izinli değil. IARC 1998'de Grup 2B (olası kanserojen) olarak sınıflandırdı. ABD California AB 418 ile 1 Ocak 2027'den itibaren yasaklanıyor."},
    **{k: {"sources": [SULF]} for k in ("E220", "E221", "E222", "E223", "E224", "E226", "E227", "E228")},
    "E230": {"sources": ["https://en.wikipedia.org/wiki/Biphenyl"], "risk": "red", "flags": ["banned_eu"],
             "reason": "AB'de gıda katkısı olarak artık izinli değil (eskiden narenciye kabuğunun taşıma sırasında korunmasında kullanılırdı)."},
    **{k: {"sources": [NITR]} for k in ("E249", "E250", "E251", "E252")},
    "E284": {"sources": ["https://decode.ipb.pt/additives/E284"]},
    "E285": {"sources": ["https://decode.ipb.pt/additives/E285"]},
    "E320": {"sources": ["https://foodadditives.net/antioxidant/butylated-hydroxyanisole-bha/"]},
    "E407": {"sources": [CARR], "risk": "yellow", "reason": CARR_REASON},
    "E407a": {"sources": [CARR], "risk": "yellow", "reason": CARR_REASON},
    **{k: {"sources": [POLY]} for k in ("E420", "E421", "E953", "E964", "E965", "E966", "E967")},
    **{k: {"sources": [GLU]} for k in ("E620", "E621", "E622", "E623", "E624", "E625")},
    "E951": {"sources": [ASP]}, "E962": {"sources": [ASP]},
    "E952": {"sources": ["https://en.wikipedia.org/wiki/Cyclamate"],
             "reason": "ABD'de 1969'da genel gıdalarda, 1970'te tamamen yasaklandı; AB'de 1996'daki yeniden değerlendirmeden sonra izinlidir ve kabul edilebilir günlük alım değeri belirlenmiştir."},
    "E954": {"sources": ["https://inchem.org/documents/iarc/vol73/73-19.html"]},
    "E955": {"sources": ["https://www.efsa.europa.eu/en/plain-language-summary/re-evaluation-sucralose-e-955-food-additive"], "flags": [],
             "reason": "EFSA 16 Şubat 2026'daki yeniden değerlendirmede ADI'yi (15 mg/kg vücut ağırlığı/gün) değiştirmedi; en yüksek tahmini alımın bile bu değerin altında olduğunu ve güvenlik endişesi olmadığını bildirdi."},
    "E968": {"sources": ["https://www.efsa.europa.eu/en/efsajournal/pub/8430", "https://fs-cpc.charite.de/en/der-kuenstliche-suessstoff-erythrit-und-das-risiko-kardiovaskulaerer-komplikationen/"],
             "risk": "yellow",
             "reason": "EFSA 2023 yeniden değerlendirmesinde ADI'yi 0,5 g/kg vücut ağırlığı/gün olarak belirledi (ishal/laksatif etki esas alındı) ve tahmini alımın bu değerin üzerinde olduğunu bildirdi. 2023'te yayımlanan bir çalışma kandaki eritritol düzeyiyle kalp-damar olayları arasında ilişki bildirdi; nedensellik kanıtlanmadı."},
}


def apply_verify(rec, review):
    v = VERIFY.get(rec["id"])
    if not v:
        return review
    rec["sources"] = v["sources"]
    if "reason" in v: rec["reason"] = v["reason"]
    if "risk" in v: rec["risk_level"] = v["risk"]
    if "flags" in v:
        keep = [f for f in rec["flags"] if f not in ("debated", "banned_eu")]
        rec["flags"] = keep + [f for f in v["flags"] if f not in keep]
    rec["verification"] = "partially_checked" if v.get("partial") else "checked_2026_10"
    return True if v.get("partial") else False


def code_aliases(eid):
    c = eid[1:].lower()
    a = ["e" + c, "e-" + c, "e " + c, "ins " + c, "ins" + c]
    m = re.match(r"^(\d+)([a-z])$", c)
    if m:
        a += ["e%s(%s)" % m.groups(), "e %s (%s)" % m.groups()]
    return a


def with_folds(names):
    extra = []
    for x in names:
        f = fold(x)
        if f != x and f not in names and f not in extra:
            extra.append(f)
    return names + extra


def build():
    tgk = load_tgk()
    seen = set()
    items = []
    for (eid, name, en, cat, names, flags, risk, reason, agencies, eu, review, verif, ctx) in ITEMS:
        assert eid not in seen, eid
        seen.add(eid)
        for f in flags:
            assert f in META["flags"], (eid, f)
        assert risk in META["risk_levels"], (eid, risk)
        assert verif in META["verification"], (eid, verif)
        names = list(names)
        if tgk:
            for a in tgk_aliases(eid, tgk.get(eid, "")):
                if a not in names:
                    names.append(a)
            if eid not in tgk and not review and eid not in TGK_NOTES and risk == "green":
                review = True            # TR izin durumu belirsiz: doğrulanana kadar işaretli
        rec = {"id": eid, "ins": eid[1:], "primary_name": name, "name_en": en, "category": cat,
               "aliases": code_aliases(eid) + with_folds(names), "flags": list(flags),
               "risk_level": risk, "reason": reason if reason is not None else DEFAULT_REASON.replace("{K}", cat),
               "agencies": list(agencies), "eu_status": eu, "needs_review": review, "verification": verif}
        tr_unknown = bool(tgk) and eid not in tgk and eid not in TGK_NOTES and rec["risk_level"] == "green"
        rec["needs_review"] = apply_verify(rec, review) or (review and eid not in VERIFY) or tr_unknown
        if eid in tgk:
            rec["tgk_name"] = tgk[eid]
        if eid in TGK_NOTES or (tgk and eid not in tgk):
            rec["tgk_note"] = TGK_NOTES.get(eid, TGK_MISSING)
        if ctx:
            rec["context_aliases"] = CONTEXT[ctx]
        items.append(rec)
    meta = dict(META)
    cnt = {"total": len(items)}
    for lv in ("green", "red", "yellow", "unrated"):
        cnt[lv] = sum(1 for i in items if i["risk_level"] == lv)
    cnt["needs_review"] = sum(1 for i in items if i["needs_review"])
    meta["counts"] = cnt
    return {"version": VERSION, "last_updated": LAST_UPDATED, "meta": meta, "ingredients": items}


def write(db, path=OUT):
    s = "{\n"
    s += '"version": ' + json.dumps(db["version"]) + ",\n"
    s += '"last_updated": ' + json.dumps(db["last_updated"]) + ",\n"
    s += '"meta": ' + json.dumps(db["meta"], ensure_ascii=False, indent=1) + ",\n"
    s += '"ingredients": [\n'
    s += ",\n".join(json.dumps(i, ensure_ascii=False) for i in db["ingredients"])
    s += "\n]\n}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


if __name__ == "__main__":
    db = build()
    write(db)
    print("Yazıldı:", OUT, db["meta"]["counts"])
