# -*- coding: utf-8 -*-
"""
E kodu olmayan bileşenler listesini (data/bilesenler.json) üretir.
Faz 1 kapsamı: gizli şeker, palm yağı, 14 yasal alerjen (gluten dahil),
laktoz, hayvansal kaynak (vegan/vejetaryen), ultra işlenmiş gıda (UPF) işaretleri.

Kullanım:  python3 gen_bilesenler.py   (data/e_kodlari.json ile aynı depoda)
- e_kodlari.json içinde zaten bulunan isimler (jelatin, karmin, soya lesitini...)
  burada tekrar edilmez; çakışan eş anlamlılar atılır ve ekrana yazılır.
"""
import json, re, os, datetime

VERSION = "0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "bilesenler.json")
EDB = os.path.join(HERE, "data", "e_kodlari.json")

TR = str.maketrans("çğıöşüâîû", "cgiosuaiu")
def norm(s):
    s = s.replace("İ", "i").replace("I", "ı").lower().translate(TR)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

FLAGS = {
    "sugar": "Şeker kaynağı",
    "sugar_hidden": "Gizli şeker (adında 'şeker' geçmiyor)",
    "palm": "Palm yağı",
    "allergen_gluten": "Gluten içeren tahıl",
    "allergen_crustacean": "Kabuklu deniz ürünü",
    "allergen_egg": "Yumurta",
    "allergen_fish": "Balık",
    "allergen_peanut": "Yer fıstığı",
    "allergen_soy": "Soya",
    "allergen_milk": "Süt",
    "allergen_nuts": "Sert kabuklu meyve",
    "allergen_celery": "Kereviz",
    "allergen_mustard": "Hardal",
    "allergen_sesame": "Susam",
    "allergen_sulphite": "Sülfit",
    "allergen_lupin": "Acı bakla (lupin)",
    "allergen_mollusc": "Yumuşakça",
    "lactose": "Laktoz içerir",
    "lactose_low": "Laktoz düşük olabilir",
    "non_vegan": "Hayvansal kaynaklı (vegan değil)",
    "vegan_suspect": "Kaynak bitkisel veya hayvansal olabilir",
    "non_vegetarian": "Et/balık/kesim yan ürünü (vejetaryen değil)",
    "vegetarian_suspect": "Vejetaryen uygunluğu belirsiz",
    "upf": "Ultra işlenmiş gıda işareti (NOVA)",
}

# Profil ekranındaki alerjen listesi (TGK Etiketleme Yönetmeliği Ek-1 sırası)
ALLERGENS = [
    ["allergen_gluten", "Gluten (çölyak)"], ["allergen_crustacean", "Kabuklu deniz ürünleri"],
    ["allergen_egg", "Yumurta"], ["allergen_fish", "Balık"], ["allergen_peanut", "Yer fıstığı"],
    ["allergen_soy", "Soya"], ["allergen_milk", "Süt"], ["allergen_nuts", "Sert kabuklu meyveler"],
    ["allergen_celery", "Kereviz"], ["allergen_mustard", "Hardal"], ["allergen_sesame", "Susam"],
    ["allergen_sulphite", "Sülfit"], ["allergen_lupin", "Acı bakla (lupin)"], ["allergen_mollusc", "Yumuşakçalar"],
]

# E kodu kategorisi -> UPF işaret sınıfı (NOVA'daki "kozmetik katkılar")
UPF_E_CATEGORIES = {
    "Renklendirici": "renklendirici", "Lezzet artırıcı": "lezzet artırıcı",
    "Tatlandırıcı": "tatlandırıcı", "Emülgatör": "emülgatör",
    "Kıvam artırıcı / jelleştirici": "kıvam artırıcı", "Modifiye nişasta": "modifiye nişasta",
    "Parlatıcı / kaplama maddesi": "parlatıcı",
}

S, H, U = "sugar", "sugar_hidden", "upf"
GL, MI, LA, NV = "allergen_gluten", "allergen_milk", "lactose", "non_vegan"
NVG = "non_vegetarian"

# (id, ad, [eş anlamlılar], [bayraklar], not, ek alanlar)
# ek: upf_class = UPF sınıfı adı; short_ok = 3 harften kısa eş anlamlıya izin
ITEMS = [
    # ---------- ŞEKER ----------
    ("seker", "Şeker", ["şeker", "toz şeker", "kristal şeker", "pudra şekeri", "esmer şeker", "kahverengi şeker", "küp şeker", "şeker şurubu", "karamelize şeker", "beyaz şeker", "rafine şeker", "sakaroz", "sakkaroz", "sukroz"], [S], "", {}),
    ("glukoz_surubu", "Glukoz şurubu", ["glukoz şurubu", "glikoz şurubu", "glukoz", "glikoz", "kurutulmuş glukoz şurubu", "glukoz şurubu tozu", "nişasta şurubu"], [S, H, U], "", {"upf_class": "şeker türevi şurup"}),
    ("gfs", "Glukoz-fruktoz şurubu", ["glukoz fruktoz şurubu", "glikoz fruktoz şurubu", "fruktoz glukoz şurubu", "fruktoz glikoz şurubu", "fruktoz şurubu", "mısır şurubu", "yüksek fruktozlu mısır şurubu", "nişasta bazlı şeker", "nbş", "izoglukoz"], [S, H, U], "Nişasta bazlı şeker (NBŞ) olarak da bilinir.", {"upf_class": "şeker türevi şurup"}),
    ("invert", "İnvert şeker", ["invert şeker", "invert şeker şurubu", "invert şurup", "invert şurubu"], [S, U], "", {"upf_class": "şeker türevi şurup"}),
    ("dekstroz", "Dekstroz", ["dekstroz", "dekstroz monohidrat"], [S, H, U], "", {"upf_class": "şeker türevi şurup"}),
    ("fruktoz", "Fruktoz", ["fruktoz", "meyve şekeri", "kristal fruktoz"], [S, U], "", {"upf_class": "şeker türevi şurup"}),
    ("maltoz", "Maltoz", ["maltoz", "maltoz şurubu"], [S, H], "", {}),
    ("maltodekstrin", "Maltodekstrin", ["maltodekstrin"], [S, H, U], "Kimyasal olarak şeker sayılmaz ama kan şekerini hızla yükselten bir nişasta türevidir.", {"upf_class": "şeker türevi şurup"}),
    ("laktoz", "Laktoz (süt şekeri)", ["laktoz", "süt şekeri"], [S, H, U, MI, LA, NV], "", {"upf_class": "şeker türevi şurup"}),
    ("bal", "Bal", ["bal", "çiçek balı", "süzme bal"], [S, H, NV], "", {}),
    ("pekmez", "Pekmez", ["pekmez", "üzüm pekmezi", "dut pekmezi", "keçiboynuzu pekmezi", "harnup pekmezi"], [S, H], "", {}),
    ("melas", "Melas", ["melas", "şeker kamışı melası", "şeker pancarı melası"], [S, H], "", {}),
    ("surup_diger", "Bitkisel şurup", ["agave şurubu", "akçaağaç şurubu", "hurma şurubu", "pirinç şurubu", "esmer pirinç şurubu", "agave", "hurma özü"], [S, H], "", {}),
    ("meyve_konsantre", "Meyve suyu konsantresi", ["meyve suyu konsantresi", "konsantre meyve suyu", "elma suyu konsantresi", "üzüm suyu konsantresi", "meyve konsantresi", "konsantre elma suyu", "konsantre üzüm suyu"], [S, H, U], "Eklenen meyve suyu konsantresi DSÖ tanımına göre serbest şekerdir.", {"upf_class": "şeker türevi şurup"}),
    ("malt", "Malt ekstraktı", ["malt ekstraktı", "malt özütü", "arpa malt ekstraktı", "arpa maltı ekstraktı", "malt şurubu", "arpa malt özütü"], [S, H, GL], "Genellikle arpadan elde edilir; gluten içerir.", {}),
    # Yönetmelik muafiyeti: buğday/arpa bazlı glukoz şurubu, maltodekstrin gluten alerjeni sayılmaz
    ("bugday_glukoz", "Buğday glukoz şurubu", ["buğday glukoz şurubu", "buğday glikoz şurubu", "buğday bazlı glukoz şurubu", "buğday kaynaklı glukoz şurubu", "buğday glukoz fruktoz şurubu", "buğday maltodekstrini", "buğday maltodekstrin", "buğday dekstrozu", "arpa glukoz şurubu"], [S, H, U], "Yönetmelik muafiyeti: buğday veya arpa bazlı glukoz şurubu ve maltodekstrin gluten alerjeni sayılmaz.", {"upf_class": "şeker türevi şurup"}),

    # ---------- PALM ----------
    ("palm", "Palm yağı", ["palm yağı", "palmiye yağı", "palm", "rafine palm yağı", "palm stearin", "palm stearini", "palm olein", "palm oleini", "fraksiyone palm yağı", "palm yağları"], ["palm"], "", {}),
    ("palm_cekirdek", "Palm çekirdek yağı", ["palm çekirdek yağı", "palm çekirdeği yağı", "palmiye çekirdeği yağı", "palm kernel"], ["palm"], "", {}),

    # ---------- GLUTEN ----------
    ("bugday", "Buğday", ["buğday", "buğday unu", "tam buğday unu", "tam buğday", "irmik", "buğday irmiği", "bulgur", "firik", "kuskus", "galeta unu", "ekmek kırıntısı", "buğday kepeği", "buğday ruşeymi", "buğday nişastası", "buğday proteini", "durum buğdayı", "durum buğdayı irmiği", "siyez", "siyez unu", "kavılca", "yufka"], [GL], "", {}),
    ("un", "Un", ["un", "ekmeklik un", "beyaz un", "tip 550 un", "pastalık un"], [GL], "Türü belirtilmemiş 'un' genellikle buğday unudur.", {"short_ok": True}),
    ("gluten", "Gluten", ["gluten", "buğday gluteni", "vital gluten", "glüten"], [GL, U], "", {"upf_class": "protein izolatı"}),
    ("arpa", "Arpa", ["arpa", "arpa unu", "arpa maltı", "malt", "kavrulmuş arpa", "arpa şehriye"], [GL], "", {}),
    ("cavdar", "Çavdar", ["çavdar", "çavdar unu", "tam çavdar unu"], [GL], "", {}),
    ("yulaf", "Yulaf", ["yulaf", "yulaf ezmesi", "yulaf unu", "yulaf kepeği", "yulaf lifi", "yulaf sütü", "yulaf içeceği"], [GL], "Yulaf yönetmelikte gluten içeren tahıllar arasındadır; 'glutensiz yulaf' ibaresini etikette kontrol edin.", {}),
    ("spelt", "Kavuzlu buğday", ["kavuzlu buğday", "spelt", "spelt unu", "kamut", "kamut unu", "einkorn", "emmer"], [GL], "", {}),

    # ---------- KABUKLU / YUMUŞAKÇA / BALIK ----------
    ("kabuklu", "Kabuklu deniz ürünleri", ["karides", "ıstakoz", "yengeç", "kerevit", "kabuklular", "karides özü", "kabuklu deniz ürünleri"], ["allergen_crustacean", NV, NVG], "", {}),
    ("yumusakca", "Yumuşakçalar", ["midye", "kalamar", "ahtapot", "istiridye", "salyangoz", "mürekkep balığı", "deniz tarağı", "yumuşakçalar"], ["allergen_mollusc", NV, NVG], "", {}),
    ("deniz_urunu", "Deniz ürünleri", ["deniz ürünleri", "deniz mahsulleri"], ["allergen_crustacean", "allergen_mollusc", "allergen_fish", NV, NVG], "Türü belirtilmemiş; kabuklu, yumuşakça ve balık olabilir.", {}),
    ("balik", "Balık", ["balık", "balık eti", "balık yağı", "balık sosu", "ançüez", "hamsi", "ton balığı", "somon", "sardalya", "uskumru", "balık unu", "balık özü", "balık jelatini", "balık kolajeni"], ["allergen_fish", NV, NVG], "", {}),

    # ---------- YUMURTA ----------
    ("yumurta", "Yumurta", ["yumurta", "yumurta tozu", "tam yumurta tozu", "yumurta akı", "yumurta akı tozu", "yumurta sarısı", "yumurta sarısı tozu", "pastörize yumurta", "sıvı yumurta", "albümin", "yumurta albümini", "ovalbümin"], ["allergen_egg", NV], "", {}),

    # ---------- YER FISTIĞI / KABUKLU MEYVELER ----------
    ("yer_fistigi", "Yer fıstığı", ["yer fıstığı", "yerfıstığı", "yer fıstığı ezmesi", "fıstık ezmesi", "yer fıstığı yağı", "yer fıstığı unu", "fıstık yağı"], ["allergen_peanut"], "", {}),
    ("fistik", "Fıstık (türü belirtilmemiş)", ["fıstık", "fıstıklı"], ["allergen_peanut", "allergen_nuts"], "Yer fıstığı veya Antep fıstığı olabilir.", {}),
    ("badem", "Badem", ["badem", "badem unu", "badem ezmesi", "badem sütü", "badem içeceği", "badem yağı", "badem parçaları", "marzipan", "acıbadem", "acı badem"], ["allergen_nuts"], "", {}),
    ("findik", "Fındık", ["fındık", "fındık ezmesi", "fındık püresi", "fındık içi", "fındık parçaları", "fındık unu", "fındık yağı", "kavrulmuş fındık", "pralin"], ["allergen_nuts"], "", {}),
    ("ceviz", "Ceviz", ["ceviz", "ceviz içi", "ceviz parçaları"], ["allergen_nuts"], "", {}),
    ("kaju", "Kaju", ["kaju", "kaju fıstığı"], ["allergen_nuts"], "", {}),
    ("antep", "Antep fıstığı", ["antep fıstığı", "şam fıstığı", "boz içi", "bozici"], ["allergen_nuts"], "", {}),
    ("pikan", "Pikan / Brezilya cevizi / makadamya", ["pikan cevizi", "pekan cevizi", "pikan", "pekan", "brezilya cevizi", "makadamya", "makadamya fındığı", "queensland cevizi"], ["allergen_nuts"], "", {}),

    # ---------- SOYA ----------
    ("soya", "Soya", ["soya", "soya fasulyesi", "soya unu", "soya proteini", "soya sütü", "soya içeceği", "soya sosu", "tofu", "edamame", "soya kırığı", "soya kepeği", "teksturize soya proteini"], ["allergen_soy"], "Soya sosu çoğunlukla buğday da içerir; etikete bakın.", {}),
    ("soya_izolat", "Soya protein izolatı", ["soya protein izolatı", "izole soya proteini", "soya izolatı", "soya protein konsantresi"], ["allergen_soy", U], "", {"upf_class": "protein izolatı"}),
    ("soya_yagi", "Soya yağı", ["soya yağı", "rafine soya yağı"], [], "Yönetmelik muafiyeti: tamamen rafine soya yağı soya alerjeni sayılmaz.", {}),

    # ---------- SÜT ----------
    ("sut", "Süt", ["süt", "inek sütü", "keçi sütü", "koyun sütü", "manda sütü", "çiğ süt", "pastörize süt", "tam yağlı süt", "yarım yağlı süt", "yağsız süt", "sütü"], [MI, LA, NV], "", {}),
    ("sut_tozu", "Süt tozu", ["süt tozu", "yağsız süt tozu", "tam yağlı süt tozu", "yarım yağlı süt tozu", "inek sütü tozu", "keçi sütü tozu"], [MI, LA, NV], "", {}),
    ("pas", "Peynir altı suyu", ["peynir altı suyu", "peyniraltı suyu", "peynir altı suyu tozu", "peyniraltı suyu tozu", "demineralize peynir altı suyu tozu", "laktoserum", "whey", "peynir suyu tozu"], [MI, LA, NV, U], "", {"upf_class": "protein izolatı"}),
    ("pas_protein", "Süt / peynir altı suyu proteini", ["peynir altı suyu proteini", "peyniraltı suyu proteini", "whey protein", "peynir altı suyu protein konsantresi", "süt proteini", "süt protein konsantresi", "süt proteini konsantresi", "laktalbümin", "süt mineralleri"], [MI, NV, U], "", {"upf_class": "protein izolatı"}),
    ("kazein", "Kazein / kazeinat", ["kazein", "kazeinat", "sodyum kazeinat", "kalsiyum kazeinat", "potasyum kazeinat", "süt kazeini", "kazeinatlar"], [MI, NV, U, "lactose_low"], "Laktoz miktarı çok düşüktür ama süt alerjisinde sorun yaratır.", {"upf_class": "protein izolatı"}),
    ("krema", "Krema / kaymak", ["krema", "süt kreması", "kaymak", "çiğ krema", "krema tozu", "kaymak tozu", "ekşi krema"], [MI, LA, NV], "", {}),
    ("tereyagi", "Tereyağı / süt yağı", ["tereyağı", "tereyağ", "sade yağ", "süt yağı", "tereyağı yağı", "anhidr süt yağı", "tereyağı tozu"], [MI, NV, "lactose_low"], "Laktoz miktarı düşüktür; süt alerjisinde sorun yaratır.", {}),
    ("yogurt", "Yoğurt / ayran / kefir", ["yoğurt", "yoğurt tozu", "süzme yoğurt", "ayran", "kefir", "yoğurt kültürü"], [MI, LA, NV], "", {}),
    ("peynir", "Peynir", ["peynir", "beyaz peynir", "kaşar", "kaşar peyniri", "lor", "lor peyniri", "çökelek", "tulum peyniri", "krem peynir", "eritme peynir", "peynir tozu", "mozzarella", "çedar", "cheddar", "parmesan", "labne", "lorlu"], [MI, LA, NV], "Olgunlaştırılmış sert peynirlerde laktoz çok düşüktür.", {}),

    # ---------- KEREVİZ / HARDAL / SUSAM / LUPİN / SÜLFİT ----------
    ("kereviz", "Kereviz", ["kereviz", "kereviz sapı", "kereviz kökü", "kereviz tohumu", "kereviz tozu", "kereviz yaprağı"], ["allergen_celery"], "", {}),
    ("hardal", "Hardal", ["hardal", "hardal tohumu", "hardal unu", "hardal tozu", "hardal yağı", "dijon hardalı"], ["allergen_mustard"], "", {}),
    ("susam", "Susam", ["susam", "susam tohumu", "tahin", "susam yağı", "susam ezmesi", "kavrulmuş susam"], ["allergen_sesame"], "", {}),
    ("lupin", "Acı bakla (lupin)", ["acı bakla", "lupin", "lupin unu", "termiye", "termiye unu"], ["allergen_lupin"], "", {}),
    ("sulfit", "Sülfit", ["sülfit", "sülfitler", "kükürt dioksit", "sülfür dioksit", "sodyum metabisülfit", "potasyum metabisülfit", "sodyum bisülfit"], ["allergen_sulphite"], "10 mg/kg üzerindeki sülfit alerjen olarak bildirilmek zorundadır.", {}),

    # ---------- HAYVANSAL (vegan / vejetaryen) ----------
    ("et", "Et", ["et", "kırmızı et", "sığır eti", "dana eti", "kuzu eti", "koyun eti", "keçi eti", "manda eti", "sığır", "dana", "kuzu", "mekanik ayrılmış et", "mekanik ayrılmış kanatlı eti", "et suyu", "et suyu tozu", "et ekstraktı", "et özü", "kemik suyu", "sakatat", "işkembe", "jambon", "bacon", "salam", "sucuk", "sosis", "pastırma", "kavurma"], [NV, NVG], "", {"short_ok": True}),
    ("tavuk", "Tavuk / hindi", ["tavuk", "tavuk eti", "tavuk göğsü", "hindi", "hindi eti", "kanatlı eti", "tavuk suyu", "tavuk suyu tozu", "tavuk yağı", "tavuk derisi", "tavuk ekstraktı"], [NV, NVG], "", {}),
    ("domuz", "Domuz", ["domuz", "domuz eti", "domuz yağı", "domuz jelatini", "domuz derisi"], [NV, NVG], "", {}),
    ("hayvansal_yag", "Hayvansal yağ", ["hayvansal yağ", "iç yağı", "kuyruk yağı", "donyağı", "don yağı", "sığır yağı", "hayvansal yağlar"], [NV, NVG], "", {}),
    ("kolajen", "Kolajen", ["kolajen", "kolajen peptidi", "hidrolize kolajen", "sığır kolajeni", "sığır jelatini"], [NV, NVG], "", {}),
    ("peynir_mayasi", "Peynir mayası", ["peynir mayası", "şirden mayası", "buzağı şirdeni", "renin", "rennet"], [NV, "vegetarian_suspect"], "Hayvansal (şirden) ya da mikrobiyal olabilir; mikrobiyal maya vejetaryene uygundur.", {}),
    ("mikrobiyal_maya", "Mikrobiyal peynir mayası", ["mikrobiyal peynir mayası", "mikrobiyal maya", "bitkisel peynir mayası", "mikrobiyal renin"], [], "Hayvansal kaynaklı değildir.", {}),
    ("ari_urunu", "Arı ürünleri", ["arı sütü", "propolis", "polen", "arı poleni"], [NV], "", {}),
    ("lanolin", "Lanolin", ["lanolin", "yün yağı"], [NV], "", {}),

    # ---------- UPF İŞARETLERİ (E kodsuz) ----------
    ("aroma", "Aroma verici", ["aroma", "aroma verici", "aroma vericiler", "aromalar", "doğal aroma", "doğal aroma verici", "doğala özdeş aroma", "doğal özdeş aroma", "yapay aroma", "aroma verici preparat", "vanilin", "etil vanilin", "vanilya aroması", "duman aroması", "tütsü aroması", "aroma maddesi", "aroma verici madde", "aroması", "aromalı", "aromaları", "esansı", "esans"], [U, "vegan_suspect"], "Aroma vericilerin kaynağı etikette genellikle yazmaz.", {"upf_class": "aroma verici"}),
    ("hidrolize_protein", "Hidrolize protein", ["hidrolize protein", "hidrolize bitkisel protein", "hidrolize soya proteini", "hidrolize buğday proteini", "protein hidrolizatı", "maya özütü", "maya ekstraktı", "otolize maya"], [U], "Doğal glutamat kaynağıdır; 'lezzet artırıcı içermez' etiketlerinde sık kullanılır.", {"upf_class": "lezzet artırıcı"}),
    ("hidrojenize", "Hidrojenize / interesterifiye yağ", ["hidrojenize yağ", "hidrojenize bitkisel yağ", "kısmen hidrojenize", "kısmen hidrojenize yağ", "tamamen hidrojenize yağ", "interesterifiye yağ", "interesterifiye bitkisel yağ", "hidrojenize", "margarin"], [U], "", {"upf_class": "hidrojenize yağ"}),
    ("upf_sinif_emulgator", "Emülgatör", ["emülgatör", "emülgatörler", "emülsifiye edici", "emülsiyon verici", "eritme tuzu", "eritme tuzları"], [U], "", {"upf_class": "emülgatör"}),
    ("upf_sinif_kivam", "Kıvam artırıcı", ["kıvam artırıcı", "kıvam arttırıcı", "kıvam artırıcılar", "jelleştirici", "jelleştirici madde", "stabilizör", "stabilizatör", "stabilizatörler"], [U], "", {"upf_class": "kıvam artırıcı"}),
    ("upf_sinif_renk", "Renklendirici", ["renklendirici", "renklendiriciler", "renk verici", "gıda boyası"], [U], "", {"upf_class": "renklendirici"}),
    ("upf_sinif_tatlandirici", "Tatlandırıcı", ["tatlandırıcı", "tatlandırıcılar", "yapay tatlandırıcı"], [U], "", {"upf_class": "tatlandırıcı"}),
    ("upf_sinif_lezzet", "Lezzet artırıcı", ["lezzet artırıcı", "lezzet arttırıcı", "lezzet artırıcılar", "lezzet güçlendirici"], [U], "", {"upf_class": "lezzet artırıcı"}),
    ("upf_sinif_parlatici", "Parlatıcı", ["parlatıcı", "parlatıcı madde", "kaplama maddesi", "kaplama ajanı"], [U], "", {"upf_class": "parlatıcı"}),
    ("upf_sinif_kopuk", "Köpük önleyici / kabartıcı", ["köpük önleyici", "köpürtücü", "dolgu maddesi", "hacim artırıcı"], [U], "", {"upf_class": "köpük/dolgu maddesi"}),

    # ---------- NÖTR (yanlış eşleşmeyi önleyen) ----------
    ("n_hindistan", "Hindistan cevizi", ["hindistan cevizi", "hindistan cevizi sütü", "hindistan cevizi kreması", "hindistan cevizi yağı", "hindistan cevizi unu", "rendelenmiş hindistan cevizi"], [], "Yönetmelikteki sert kabuklu meyveler listesinde yoktur.", {}),
    ("n_muskat", "Muskat", ["muskat", "muskat cevizi", "küçük hindistan cevizi"], [], "", {}),
    ("n_cam_fistigi", "Çam fıstığı", ["çam fıstığı", "dolmalık fıstık"], [], "Yönetmelikteki sert kabuklu meyveler listesinde yoktur; ayrı bir alerji olabilir.", {}),
    ("n_kakao", "Kakao yağı", ["kakao yağı", "kakao tereyağı"], [], "Süt ürünü değildir.", {}),
    ("n_bitkisel_krema", "Bitkisel krema", ["bitkisel krema", "bitkisel krem şanti", "bitkisel kaymak", "bitkisel bazlı krema"], [U], "Süt kreması değildir; genellikle bitkisel yağ ve katkılarla yapılır.", {"upf_class": "hidrojenize yağ"}),
    ("n_pirinc_sutu", "Pirinç sütü", ["pirinç sütü", "pirinç içeceği"], [], "", {}),
    ("n_balkabagi", "Bal kabağı", ["bal kabağı", "balkabağı", "bal kabağı çekirdeği"], [], "", {}),
    ("n_sut_aroma", "Süt ürünü aroması", ["kaymak aroması", "süt aroması", "tereyağı aroması", "peynir aroması", "yoğurt aroması"], [U, "vegan_suspect"], "Aroma olarak geçiyor; süt içerip içermediği belirsiz.", {"upf_class": "aroma verici"}),
    ("n_glutensiz_un", "Glutensiz un / nişasta", ["mısır unu", "pirinç unu", "nohut unu", "karabuğday", "karabuğday unu", "patates unu", "keçiboynuzu unu", "tapyoka", "tapyoka nişastası", "mısır nişastası", "patates nişastası", "pirinç nişastası", "mısır irmiği", "kinoa", "kinoa unu", "tef unu", "darı", "darı unu"], [], "Gluten içeren tahıllardan değildir; çapraz bulaşma için etikete bakın.", {}),
    ("n_hamur_mayasi", "Maya", ["maya", "ekmek mayası", "kuru maya", "yaş maya", "instant maya", "aktif kuru maya"], [], "", {}),
]

# Cümle düzeyinde "eser miktarda içerebilir" tetikleyicileri (normalize edilmiş)
MAY_TRIGGERS = ["icerebilir", "iceribilir", "eser", "ayni tesiste", "ayni hatta", "ayni uretim", "bulunabilir"]
NEGATIONS = ["icermez", "yoktur", "icermemektedir", "ilave edilmemistir", "katilmamistir"]
AROMA_NEXT = ["aromasi", "aromali", "aroma", "esansi"]

def main():
    edb = json.load(open(EDB, encoding="utf-8"))
    e_aliases = {}
    for it in edb["ingredients"]:
        for a in it["aliases"]:
            e_aliases[norm(a)] = it["id"]
    seen, items, dropped = {}, [], []
    for (iid, name, aliases, flags, note, extra) in ITEMS:
        for f in flags:
            assert f in FLAGS, (iid, f)
        keep = []
        for a in aliases:
            n = norm(a)
            if not n: continue
            if len(n) < 3 and not extra.get("short_ok"):
                dropped.append((iid, a, "çok kısa")); continue
            if n in e_aliases:
                dropped.append((iid, a, "e_kodlari.json'da var: " + e_aliases[n])); continue
            if seen.get(n) == iid:
                continue
            if n in seen:
                raise SystemExit("Aynı eş anlamlı iki maddede: %s (%s, %s)" % (a, seen[n], iid))
            seen[n] = iid
            keep.append(a)
        rec = {"id": iid, "name": name, "aliases": keep, "flags": flags}
        if note: rec["note"] = note
        if extra.get("upf_class"): rec["upf_class"] = extra["upf_class"]
        if extra.get("short_ok"): rec["short_ok"] = True
        items.append(rec)
    out = {
        "meta": {
            "version": VERSION,
            "generated": datetime.date.today().isoformat(),
            "description": "E kodu olmayan bileşenler: gizli şeker, palm yağı, 14 yasal alerjen, laktoz, hayvansal kaynak, ultra işlenmiş gıda (UPF) işaretleri.",
            "flags": FLAGS,
            "allergens": ALLERGENS,
            "upf_e_categories": UPF_E_CATEGORIES,
            "may_triggers": MAY_TRIGGERS,
            "negations": NEGATIONS,
            "aroma_next": AROMA_NEXT,
            "sources": [
                {"name": "TGK Gıda Etiketleme ve Tüketicileri Bilgilendirme Yönetmeliği, Ek-1 (alerjenler)", "ref": "Resmî Gazete 26.01.2017, sayı 29960 (1. mükerrer); son değişiklik 06.04.2024",
                 "note": "Ek-1'in metni bu çalışmada birebir okunamadı; liste ve muafiyetler, Ek-1'in uyumlaştırıldığı AB Tüzüğü 1169/2011 Ek II'den alındı. Yayından önce Ek-1 ile karşılaştırılmalı."},
                {"name": "DSÖ (WHO) Guideline: Sugars intake for adults and children (2015)", "note": "'Serbest şeker' tanımı: eklenen şekerler + bal, şuruplar, meyve suyu ve konsantreleri."},
                {"name": "Monteiro ve ark., Ultra-processed foods, diet quality, and health using the NOVA classification system (FAO, 2019)", "note": "UPF işaretleri: aroma vericiler, lezzet artırıcılar, renklendiriciler, emülgatörler, tatlandırıcılar, kıvam artırıcılar; invert şeker, maltodekstrin, dekstroz, laktoz, yüksek fruktozlu mısır şurubu, meyve suyu konsantresi; hidrojenize/interesterifiye yağlar; hidrolize proteinler, soya protein izolatı, gluten, kazein, peynir altı suyu proteini, mekanik ayrılmış et."},
            ],
            "caveats": [
                "Bileşen eşleştirme yalnızca etiketteki 'İçindekiler' yazısına dayanır; miktar bilgisi yoktur.",
                "Alerjen sonucu bir onay değildir: 'tespit edilmedi' ürünün güvenli olduğu anlamına gelmez.",
                "UPF işaretleri bir puan değildir; NOVA'nın tanımladığı işaret maddelerinin listesidir.",
                "Vegan/vejetaryen sonucu yalnızca içerik adlarına dayanır; üretim süreci ve çapraz bulaşma bilinmez.",
            ],
            "counts": {"items": len(items), "aliases": sum(len(i["aliases"]) for i in items)},
        },
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Yazıldı:", OUT, out["meta"]["counts"])
    for d in dropped: print("  atıldı:", d)

if __name__ == "__main__":
    main()
