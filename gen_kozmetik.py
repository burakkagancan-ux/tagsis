# -*- coding: utf-8 -*-
"""
Kozmetik bileşen veri tabanını üretir:
  data/kozmetik.json       AB kozmetik yönetmeliği (1223/2009) eklerindeki düzenlenmiş maddeler
  data/kozmetik_inci.json  CosIng INCI ad listesi (işlev + hayvansal kaynak / PFAS bayrakları)

Kullanım:
  git clone https://github.com/inhouse-work/cosing ../cosing && git -C ../cosing checkout 268e3cd
  python3 gen_kozmetik.py [--cosing ../cosing/data]

- JSON dosyalarını elle düzenlemeyin; değişikliği bu betikte ya da kaynak/kozmetik_guncellemeler.tsv'de yapın.
- Ham veri: Avrupa Komisyonu CosIng veritabanı (Komisyon içeriği 2011/833/AB kararıyla kaynak
  gösterilerek yeniden kullanılabilir). CSV biçimine dönüştürülmüş anlık görüntü inhouse-work/cosing
  deposundan (MIT lisansı) alınır. Anlık görüntü 2024 başına aittir; sonraki AB değişiklikleri
  kaynak/kozmetik_guncellemeler.tsv ile elle eklenir.
- Türkiye: Kozmetik Ürünler Yönetmeliği (RG 08.05.2023, 32184 mük.) ekleri AB ekleriyle uyumludur.
  Madde madde karşılaştırma henüz yapılmadı (TEKNIK_BORC.md).
"""
import argparse, csv, json, os, re, sys
from collections import defaultdict

VERSION = "0.1.0"
LAST_UPDATED = "2026-10-03"
COSING_COMMIT = "268e3cd"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "kozmetik.json")
OUT_INCI = os.path.join(HERE, "data", "kozmetik_inci.json")
UPD = os.path.join(HERE, "kaynak", "kozmetik_guncellemeler.tsv")

# CSV başlıklarında "regulated_by" sütunu var ama satırlarda yok; satırlar bir sütun eksik.
H2 = ["ref", "inn", "cas", "ec", "regulation", "other_regulations", "sccs", "chemical_name",
      "identified", "cmr", "update_date"]
H3 = ["ref", "inn", "common", "cas", "ec", "product_type", "max", "other", "wording", "regulation",
      "other_regulations", "sccs", "chemical_name", "identified", "cmr", "update_date"]
H4 = ["ref", "inn", "ci", "cas", "ec", "colour", "product_type", "max", "other", "wording",
      "regulation", "other_regulations", "sccs", "chemical_name", "identified", "cmr", "update_date"]
HEADERS = {"II": H2, "III": H3, "IV": H4, "V": H3, "VI": H3}

LEVELS = {
    "red": "AB kozmetik yönetmeliği Ek II'de (yasaklı maddeler) yer alıyor.",
    "orange": "Resmi bir tehlike sınıflaması var (ör. AB'de CMR kategori 2) ya da büyük bir pazarda yasak.",
    "yellow": "Yasal sınırla izinli (Ek III kısıtlaması) ya da bilinen bir alerjen/formaldehit salıcı.",
    "info": "İzinli listede (renklendirici, koruyucu, UV filtresi) ya da yalnızca profil için önemli. 'Güvenli' anlamına gelmez.",
}

FLAGS = {
    "allergen_fragrance": "Koku alerjeni (etikette adıyla yazılması zorunlu)",
    "allergen_hairdye": "Saç boyası alerjeni",
    "allergen_preservative": "Bilinen koruyucu alerjeni",
    "formaldehyde_releaser": "Formaldehit salıcı koruyucu",
    "cmr2": "AB'de CMR kategori 2 (şüpheli kanserojen/mutajen/üreme toksiği)",
    "cmr_ban": "CMR (kanserojen, mutajen, üreme toksiği) sınıflaması nedeniyle yasak",
    "nano": "Nano biçim",
    "pfas": "PFAS (florlu, doğada kalıcı madde grubu)",
    "non_vegan": "Hayvansal kaynaklı",
    "non_veg": "Kesim ya da böcek kaynaklı (vejetaryen değil)",
    "vegan_unsure": "Kaynağı bitkisel, sentetik ya da hayvansal olabilir",
}

# Formaldehit salıcılar: 2022/1181 ile "releases formaldehyde" uyarısı getirilen Ek V koruyucuları.
FORMALDEHYDE_RELEASERS = [
    "DMDM HYDANTOIN", "IMIDAZOLIDINYL UREA", "DIAZOLIDINYL UREA", "QUATERNIUM-15",
    "2-BROMO-2-NITROPROPANE-1,3-DIOL", "BRONOPOL", "SODIUM HYDROXYMETHYLGLYCINATE", "METHENAMINE",
    "5-BROMO-5-NITRO-1,3-DIOXANE", "BENZYLHEMIFORMAL", "METHENAMINE 3-CHLOROALLYLOCHLORIDE",
    "POLYMETHOXY BICYCLIC OXAZOLIDINE",
]
PRESERVATIVE_ALLERGENS = ["METHYLISOTHIAZOLINONE", "METHYLCHLOROISOTHIAZOLINONE",
                          "METHYLCHLOROISOTHIAZOLINONE AND METHYLISOTHIAZOLINONE", "METHYLDIBROMO GLUTARONITRILE"]

# Hayvansal kaynak (INCI adında sözcük olarak geçerse). non_veg = kesim/böcek; non_vegan = hayvandan elde.
NON_VEG_WORDS = ["TALLOW", "TALLOWATE", "TALLOWAMIDE", "GELATIN", "COLLAGEN", "ELASTIN", "PLACENTAL",
                 "PLACENTA", "MINK", "MINKATE", "SHARK", "FISH", "CAVIAR", "GUANINE", "CIVETONE",
                 "VIVERRA", "CASTOREUM", "BOVINE", "PORCINE", "KERATIN", "SNAIL", "SPERMACETI", "CETACEUM",
                 "CI 75470", "CARMINE", "ANIMAL"]
NON_VEGAN_WORDS = ["LANOLIN", "CERA ALBA", "BEESWAX", "SILK", "SERICIN", "LACTIS", "MILK", "SHELLAC",
                   "MEL", "HONEY", "PROPOLIS", "ROYAL JELLY", "CASEIN", "EGG", "OVUM", "LACTOSE", "WHEY"]
VEGAN_UNSURE = ["SQUALENE", "SQUALANE", "CHOLESTEROL", "CHITOSAN", "AMBERGRIS", "HYALURONIC ACID",
                "SODIUM HYALURONATE", "STEARIC ACID", "GLYCERIN", "LACTIC ACID", "PANTHENOL", "ALLANTOIN"]
# Sözcük eşleşmesine rağmen hayvansal olmayanlar
ANIMAL_EXCEPT = re.compile(r"HONEYSUCKLE|GELATINUM|COCONUT MILK|ALMOND MILK|OAT MILK|SOY MILK|RICE MILK|"
                           r"MILK THISTLE|MILKWEED|EGGPLANT|^R-|\bRH-|\bSH-|RECOMBINANT|MILK VETCH|"
                           r"FISH MINT|STARFISH|SHELLFISH")
PFAS_RE = re.compile(r"PERFLUOR|POLYPERFLUOR|\bPTFE\b|TETRAFLUOROETHYLENE|TRIFLUORO|NONAFLUORO|"
                     r"TRIDECAFLUORO|HEPTADECAFLUORO|CHLOROTRIFLUOROETHYLENE|FLUOROALKYL")

# CosIng işlev adlarının Türkçesi
FUNC_TR = {
    "ABRASIVE": "Aşındırıcı", "ABSORBENT": "Emici", "ADHESIVE": "Yapıştırıcı",
    "ANTI-SEBORRHEIC": "Seboreye karşı", "ANTISEBORRHOEIC": "Seboreye karşı", "ANTI-SEBUM": "Yağlanmaya karşı",
    "ANTICAKING": "Topaklanma önleyici", "ANTICORROSIVE": "Korozyon önleyici", "ANTIDANDRUFF": "Kepeğe karşı",
    "ANTIFOAMING": "Köpük önleyici", "ANTIMICROBIAL": "Antimikrobiyal", "ANTIOXIDANT": "Antioksidan",
    "ANTIPERSPIRANT": "Ter önleyici", "ANTIPLAQUE": "Diş plağına karşı", "ANTISTATIC": "Antistatik",
    "ASTRINGENT": "Büzücü", "BINDING": "Bağlayıcı", "BLEACHING": "Ağartıcı", "BUFFERING": "Tampon (pH)",
    "BULKING": "Dolgu", "CHELATING": "Şelatlayıcı", "CLEANSING": "Temizleyici", "COLORANT": "Renklendirici",
    "COSMETIC COLORANT": "Renklendirici", "DENATURANT": "Denatüre edici", "DEODORANT": "Deodorant",
    "DEPILATORY": "Tüy dökücü", "DETANGLING": "Kolay tarama", "DISPERSING NON-SURFACTANT": "Dağıtıcı",
    "EMOLLIENT": "Yumuşatıcı", "EMULSIFYING": "Emülgatör", "EMULSION STABILISING": "Emülsiyon dengeleyici",
    "EPILATING": "Ağda", "EXFOLIATING": "Peeling", "EYELASH CONDITIONING": "Kirpik bakımı",
    "FILM FORMING": "Film oluşturucu", "FLAVOURING": "Aroma verici", "FOAMING": "Köpürtücü",
    "FRAGRANCE": "Koku", "GEL FORMING": "Jel yapıcı", "HAIR CONDITIONING": "Saç bakımı",
    "HAIR DYEING": "Saç boyası", "HAIR FIXING": "Saç sabitleyici",
    "HAIR WAVING OR STRAIGHTENING": "Saç kıvırma/düzleştirme", "HUMECTANT": "Nem tutucu",
    "KERATOLYTIC": "Keratolitik", "LIGHT STABILIZER": "Işık dengeleyici", "LYTIC": "Çözücü (litik)",
    "MASKING": "Koku maskeleyici", "MOISTURISING": "Nemlendirici", "NAIL CONDITIONING": "Tırnak bakımı",
    "NAIL SCULPTING": "Tırnak şekillendirme", "OPACIFYING": "Matlaştırıcı", "ORAL CARE": "Ağız bakımı",
    "OXIDISING": "Oksitleyici", "PEARLESCENT": "Sedef parlaklığı", "PERFUMING": "Parfüm",
    "PLASTICISER": "Plastikleştirici", "PRESERVATIVE": "Koruyucu", "PROPELLANT": "İtici gaz",
    "REDUCING": "İndirgeyici", "REFATTING": "Yağ kazandırıcı", "REFRESHING": "Ferahlatıcı",
    "SKIN CONDITIONING": "Cilt bakımı", "SKIN CONDITIONING - EMOLLIENT": "Cilt bakımı (yumuşatıcı)",
    "SKIN CONDITIONING - HUMECTANT": "Cilt bakımı (nem tutucu)",
    "SKIN CONDITIONING - MISCELLANEOUS": "Cilt bakımı", "SKIN CONDITIONING - OCCLUSIVE": "Cilt bakımı (örtücü)",
    "SKIN PROTECTING": "Cilt koruyucu", "SLIP MODIFIER": "Kayganlık verici", "SMOOTHING": "Pürüzsüzleştirici",
    "SOLVENT": "Çözücü", "SOOTHING": "Yatıştırıcı", "STABILISING": "Dengeleyici",
    "SURFACE MODIFIER": "Yüzey düzenleyici", "SURFACTANT": "Yüzey aktif madde",
    "SURFACTANT - CLEANSING": "Yüzey aktif (temizleyici)", "SURFACTANT - DISPERSING": "Yüzey aktif (dağıtıcı)",
    "SURFACTANT - EMULSIFYING": "Yüzey aktif (emülgatör)", "SURFACTANT - FOAM BOOSTING": "Köpük artırıcı",
    "SURFACTANT - HYDROTROPE": "Hidrotrop", "SURFACTANT - SOLUBILIZING": "Çözündürücü",
    "TANNING": "Bronzlaştırıcı", "TONIC": "Tonik", "UV ABSORBER": "UV emici", "UV FILTER": "UV filtresi",
    "VISCOSITY CONTROLLING": "Kıvam düzenleyici", "pH ADJUSTERS": "pH düzenleyici", "NOT REPORTED": None,
}


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


def norm_alias(s):
    s = clean(s).upper().strip(" ,;.*-")
    s = re.sub(r"\s*\(\s*NANO\s*\)", " (NANO)", s)
    s = re.sub(r"\s*/\s*", "/", s)
    if s.count("(") < s.count(")"):
        s = s.replace(")", "")
    return s


def split_names(s, comma=True):
    """INCI listesini böler. "1,2-HEXANEDIOL" gibi rakam arası virgüller bölünmez."""
    s = clean(s)
    if not s:
        return []
    parts = re.split(r"\s*;\s*|\s+/\s+" + (r"|,(?!\d)|(?<!\d)," if comma else ""), s)
    out = []
    for p in parts:
        p = norm_alias(p)
        if len(p) >= 3 and p not in ("MOVED OR DELETED",) and not re.fullmatch(r"[\d\-/ .]+", p):
            out.append(p)
    return out


def split_cas(s):
    return [c for c in re.findall(r"\d{2,7}-\d{2}-\d", s or "")]


def trim(s, n=400):
    s = clean(s)
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


CHEM_STOP = {"INN", "ISO", "INNM", "NANO", "INCI", "CAS", "SALTS", "ESTERS", "ISOMERS", "ETHYL", "METHYL",
             "PROPYL", "BUTYL", "FRUIT", "COAL", "ACID", "OILS", "WATER", "EXTRACT", "POWDER"}
# Bir kayda yanlışlıkla bağlanan genel adlar (kayıt id -> çıkarılacak adlar)
ALIAS_EXCLUDE = {"V/59": {"CITRIC ACID"}}


def short_chem(s):
    """Kimyasal addan eş anlamlı olarak kullanılabilecek kısa adları çıkarır (liste).
    "2,6-Dihydroxy-4-methylbenzaldehyde (Atranol)" -> ["ATRANOL"]; "Mercury and its compounds" -> ["MERCURY"]."""
    out = []
    s = clean(s)
    paren = [p for p in re.findall(r"(?:^|\s)\(([^()]{4,30})\)", s) if re.fullmatch(r"[A-Za-z][A-Za-z\- ]+", p)]
    s = re.sub(r"\((INN|ISO|INNM)\)", "", s, flags=re.I)
    for part in re.split(r"\s*;\s*", s) + paren:
        part = re.sub(r",? (and|its|or) (its |their )?(salts|esters|ethers|isomers|derivatives|compounds|mixtures).*$", "", part, flags=re.I)
        part = clean(re.sub(r"[\[\]]", "", part)).strip(" ,;")
        if 4 <= len(part) <= 40 and re.search(r"[A-Za-z]{3}", part) and part.upper() not in CHEM_STOP \
                and not re.fullmatch(r"[\d\s,.\-]+", part) and "(" not in part:
            out.append(norm_alias(part))
    return list(dict.fromkeys(out))


def read_annex(cdir, annex):
    path = os.path.join(cdir, "annex.%s.csv" % annex)
    rows = list(csv.reader(open(path, encoding="utf-8")))[1:]
    H = HEADERS[annex]
    out = []
    for r in rows:
        if len(r) != len(H):
            print("uyarı: Ek %s satır sütun sayısı beklenmedik (%d): %s" % (annex, len(r), r[:2]), file=sys.stderr)
            continue
        d = dict(zip(H, r))
        if "moved or deleted" in d["inn"].lower() or clean(d["inn"]) in ("", "-"):
            if not clean(d.get("identified")):
                continue
        out.append(d)
    return out


def level_reason(e):
    a, f = e["annex"], set(e["flags"])
    reg = e.get("regulation") or ""
    if a == "II":
        r = "AB kozmetik yönetmeliği Ek II'de yasaklı maddeler arasında (giriş %s%s)." % (e["ref"], ", " + reg if reg else "")
        if "cmr_ban" in f:
            r += " Kanserojen, mutajen ya da üreme için toksik (CMR) sınıflaması nedeniyle yasaklandı."
        return r + " Etikette görülmesi okuma hatası ya da AB/Türkiye dışı bir ürün olduğunu gösterebilir."
    parts = []
    if a == "III":
        if "allergen_fragrance" in f and not e.get("max"):
            parts.append("Koku alerjeni: AB'de durulanmayan üründe %0,001, durulanan üründe %0,01'in üzerindeyse etikette adıyla yazılması zorunlu.")
        else:
            parts.append("AB Ek III'te kısıtlı madde: yalnızca belirli ürün tiplerinde ve üst sınırla kullanılabilir.")
            if "allergen_fragrance" in f:
                parts.append("Aynı zamanda etikette adıyla yazılması zorunlu bir koku alerjenidir.")
    elif a == "IV":
        parts.append("İzinli renklendirici (AB Ek IV).")
    elif a == "V":
        parts.append("İzinli koruyucu (AB Ek V), üst sınırla.")
    elif a == "VI":
        parts.append("İzinli UV filtresi (AB Ek VI), üst sınırla.")
    if "cmr2" in f:
        parts.append("AB'de CMR kategori 2 (şüpheli) sınıflaması var; bu yüzden yalnızca sınırlı kullanıma izin veriliyor.")
    if "formaldehyde_releaser" in f:
        parts.append("Formaldehit salabilir. Formaldehit AB'de kanserojen (1B) sınıfındadır ve yaygın bir alerjendir; toplam formaldehit %0,001'i aşarsa etikette \"releases formaldehyde\" yazılması zorunludur.")
    if "allergen_preservative" in f:
        parts.append("Temas alerjisine sık yol açan bir koruyucu; AB'de kullanım koşulları bu yüzden daraltıldı.")
    if "allergen_hairdye" in f:
        parts.append("Saç boyası maddesi; ciddi alerjik reaksiyonlara yol açabileceği için etikette uyarı zorunludur.")
    if e["annex"] in ("III", "V", "VI") and e.get("max"):
        parts.append("Etikette yüzde yazmadığı için sınırın aşılıp aşılmadığı anlaşılamaz.")
    return " ".join(parts)


def compute_level(e):
    f = set(e["flags"])
    if e["annex"] == "II":
        return "red"
    if "cmr2" in f:
        return "orange"
    if e["annex"] == "III":
        if "allergen_fragrance" in f and not e.get("max"):
            return "info"
        return "yellow"
    if f & {"formaldehyde_releaser", "allergen_preservative"}:
        return "yellow"
    return "info"


def build(cdir):
    entries = {}
    alias_from_ingredients = defaultdict(set)

    # INCI listesi -> ek referansları (ör. "III/60")
    ing = list(csv.DictReader(open(os.path.join(cdir, "ingredients.csv"), encoding="utf-8")))
    for r in ing:
        for m in re.finditer(r"\b(II|III|IV|V|VI)\s*/\s*(\d+[a-z]?)", r["restriction"] or ""):
            alias_from_ingredients["%s/%s" % (m.group(1), m.group(2))].add(norm_alias(r["inci_name"]))

    for annex in ["II", "III", "IV", "V", "VI"]:
        for d in read_annex(cdir, annex):
            eid = "%s/%s" % (annex, d["ref"])
            inci = []
            for k in ("common", "identified"):
                if d.get(k):
                    inci += split_names(d[k])
            if annex == "IV" and clean(d.get("ci")):
                inci.append(norm_alias(d["ci"]))
            inci += sorted(alias_from_ingredients.get(eid, []))
            chem = clean(d.get("chemical_name")) or clean(d["inn"])
            if not inci or annex == "II":
                inci += short_chem(d["inn"])
            # Koku alerjenlerinin etikette yazılacak toplu adı (ör. 'Lavandula Oil/Extract', 'Rose Flower Oil/Extract')
            for q in re.findall(r"indicated (?:as )?[\u2018'\"]([^\u2019'\"]{3,60})[\u2019'\"]", d.get("other", "") + " " + d.get("wording", "")):
                inci.append(norm_alias(q))
            inci = list(dict.fromkeys(a for a in inci if a and a not in ALIAS_EXCLUDE.get(eid, ())
                                      and a not in CHEM_STOP))
            if not inci:
                continue
            flags = []
            cmr = clean(d.get("cmr"))
            if annex != "II" and re.search(r"(Carcinogenic|Mutagenic|Reprotoxic)", cmr):
                flags.append("cmr2")
            txt = " ".join(clean(d.get(k)) for k in ("product_type", "max", "other", "wording"))
            if annex == "III" and re.search(r"(shall|must) be indicated", txt, re.I):
                flags.append("allergen_fragrance")
            if annex == "III" and re.search(r"allergic reaction", txt, re.I):
                flags.append("allergen_hairdye")
            if any("(NANO)" in a for a in inci):
                flags.append("nano")
            e = {
                "id": eid, "annex": annex, "ref": d["ref"],
                "name": inci[0] if inci and not inci[0].startswith(("CI ",)) else trim(chem, 90),
                "inci": inci, "cas": split_cas(d["cas"])[:6],
                "flags": flags, "regulation": clean(d["regulation"]),
            }
            if annex != "II":
                if clean(d.get("product_type")): e["product_type"] = trim(d["product_type"], 300)
                if clean(d.get("max")).strip("-") : e["max"] = trim(d["max"], 200)
                cond = " ".join(x for x in (clean(d.get("other")), clean(d.get("wording"))) if x)
                if cond: e["conditions_en"] = trim(cond, 400)
            entries[eid] = e
    return entries, ing


def apply_updates(entries):
    if not os.path.exists(UPD):
        return []
    log = []
    by_inci = defaultdict(list)
    for e in entries.values():
        for a in e["inci"]:
            by_inci[a].append(e["id"])
    head = None
    auto = 0
    for line in open(UPD, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        cols = line.rstrip("\n").split("\t")
        if head is None:
            head = cols
            continue
        cols += [""] * (len(head) - len(cols))
        r = dict(zip(head, cols))
        op, annex, ref = r["islem"], r["ek"], r["ref"]
        inci = split_names(r["inci"], comma=False)
        upd = {"regulation": r["yonetmelik"], "applies_from": r["uygulama"], "note_tr": r["not_tr"], "source": r["kaynak"]}
        if op == "sil":
            eid = "%s/%s" % (annex, ref)
            if entries.pop(eid, None):
                log.append("sil " + eid)
            continue
        if op == "guncelle":
            eid = "%s/%s" % (annex, ref)
            if eid not in entries and inci:
                ids = [i for a in inci for i in by_inci.get(a, []) if i.startswith(annex + "/")]
                eid = ids[0] if ids else eid
            if eid not in entries:
                print("uyarı: güncellenecek kayıt yok: %s %s" % (eid, inci), file=sys.stderr)
                continue
            e = entries[eid]
            e.setdefault("updates", []).append(upd)
            if r["inceleme"] == "1": e["needs_review"] = True
            log.append("guncelle " + eid)
            continue
        if op == "ekle":
            if ref == "?":
                auto += 1
                ref = "y%d" % auto
            eid = "%s/%s" % (annex, ref)
            names = inci[:] or []
            if not names:  # INCI verilmemişse kimyasal addan kısa ad üret (Türkçe açıklamalardan değil)
                names = short_chem(r["ad"])
            e = {"id": eid, "annex": annex, "ref": ref if not ref.startswith("y") else "?",
                 "name": names[0] if names else r["ad"], "inci": names, "cas": split_cas(r["cas"]),
                 "flags": [], "regulation": r["yonetmelik"], "applies_from": r["uygulama"],
                 "note_tr": r["not_tr"], "source": r["kaynak"]}
            if annex == "II" and "CMR" in r["not_tr"]:
                e["flags"].append("cmr_ban")
            if any("(NANO)" in a for a in names):
                e["flags"].append("nano")
            if r["inceleme"] == "1":
                e["needs_review"] = True
            # Aynı INCI başka ekte eski kayıtla duruyorsa (ör. TPO Ek III'ten Ek II'ye) eski kayıt kalkar
            for a in names:
                for old in by_inci.get(a, []):
                    if old in entries and old != eid and entries[old]["annex"] != annex and annex == "II":
                        entries.pop(old, None)
                        log.append("taşındı %s -> %s" % (old, eid))
            entries[eid] = e
            for a in names:
                by_inci[a].append(eid)
            log.append("ekle " + eid)
    return log


def finalize(entries):
    fr = set(FORMALDEHYDE_RELEASERS)
    pa = set(PRESERVATIVE_ALLERGENS)
    for e in entries.values():
        s = set(e["inci"])
        if e["annex"] in ("V", "III") and s & fr: e["flags"].append("formaldehyde_releaser")
        if e["annex"] == "V" and s & pa: e["flags"].append("allergen_preservative")
        if any(PFAS_RE.search(a) for a in e["inci"]): e["flags"].append("pfas")
        e["flags"] = list(dict.fromkeys(e["flags"]))

    # Aynı ad hem yasaklı (II) hem izinli bir ekte geçiyorsa: II'deki ad o maddenin başka bir
    # biçimine/kullanımına aittir (ör. bir tuzu, bir ürün tipi). Ad II kaydından çıkarılır.
    allowed = defaultdict(set)
    for e in entries.values():
        if e["annex"] != "II":
            for a in e["inci"]:
                allowed[a].add(e["id"])
    dropped = 0
    for eid in list(entries):
        e = entries[eid]
        if e["annex"] != "II":
            continue
        keep = [a for a in e["inci"] if a not in allowed]
        if len(keep) != len(e["inci"]):
            e["partly_allowed"] = sorted({i for a in e["inci"] if a in allowed for i in allowed[a]})
            dropped += len(e["inci"]) - len(keep)
            e["inci"] = keep
            if not keep:
                del entries[eid]
                continue
            if e["name"] not in keep:
                e["name"] = keep[0]
    for e in entries.values():
        e["level"] = compute_level(e)
        e["reason"] = level_reason(e)
    return dropped


def inci_file(ing):
    funcs, fidx, items = [], {}, []
    for r in ing:
        name = norm_alias(r["inci_name"])
        if not name:
            continue
        fl = []
        for f in (r["functions"] or "").split(","):
            f = clean(f)
            tr = FUNC_TR.get(f)
            if not tr:
                continue
            if tr not in fidx:
                fidx[tr] = len(funcs); funcs.append(tr)
            if fidx[tr] not in fl:
                fl.append(fidx[tr])
        flags = []
        if not ANIMAL_EXCEPT.search(name):
            if any(re.search(r"\b%s\b" % re.escape(w), name) for w in NON_VEG_WORDS):
                flags.append("non_veg")
            elif any(re.search(r"\b%s\b" % re.escape(w), name) for w in NON_VEGAN_WORDS):
                flags.append("non_vegan")
            elif name in VEGAN_UNSURE:
                flags.append("vegan_unsure")
        if PFAS_RE.search(name):
            flags.append("pfas")
        it = [name, fl]
        if flags:
            it.append(flags)
        items.append(it)
    items.sort(key=lambda x: x[0])
    return funcs, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cosing", default=os.environ.get("COSING_DIR", os.path.join(HERE, "..", "cosing", "data")))
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.cosing, "annex.II.csv")):
        sys.exit("CosIng verisi bulunamadı: %s (betiğin başındaki kullanım notuna bakın)" % a.cosing)
    entries, ing = build(a.cosing)
    log = apply_updates(entries)
    dropped = finalize(entries)
    order = {"II": 0, "III": 1, "V": 2, "VI": 3, "IV": 4}
    def rk(e):
        m = re.match(r"(\d+)", e["ref"]); return (order[e["annex"]], int(m.group(1)) if m else 99999, e["ref"])
    lst = sorted(entries.values(), key=rk)
    counts = defaultdict(int)
    for e in lst:
        counts["annex_" + e["annex"]] += 1; counts["level_" + e["level"]] += 1
        for f in e["flags"]: counts["flag_" + f] += 1
    out = {
        "version": VERSION, "last_updated": LAST_UPDATED,
        "meta": {
            "description": "AB kozmetik yönetmeliği (EC) 1223/2009 eklerindeki düzenlenmiş maddeler. Türkiye Kozmetik Ürünler Yönetmeliği ekleri AB ile uyumludur.",
            "source": "Avrupa Komisyonu CosIng veritabanı (anlık görüntü: inhouse-work/cosing @%s, 2024 başı) + kaynak/kozmetik_guncellemeler.tsv (2024-2026 değişiklikleri)." % COSING_COMMIT,
            "license": "CosIng içeriği Komisyon'un 2011/833/AB kararıyla kaynak gösterilerek yeniden kullanılabilir.",
            "tr_status": "Türkiye ekleriyle madde madde karşılaştırma yapılmadı; AB ile uyumlu varsayıldı.",
            "match": "inci alanındaki adlar büyük harfle, etiketteki INCI adlarıyla eşleştirilir.",
            "levels": LEVELS, "flags": FLAGS,
            "inci_flag_levels": {"pfas": "orange"},
            "inci_flag_reasons": {
                "pfas": "PFAS grubundan (florlu, doğada parçalanmayan madde). Fransa'da 1 Ocak 2026'dan itibaren kozmetikte yasak (Kanun 2025-188); ABD'de Kaliforniya 2025'ten itibaren bazı PFAS'ları yasakladı; AB'de genel kısıtlama önerisi değerlendiriliyor. AB/Türkiye'de şu an yasak değil.",
                "non_vegan": "Hayvandan elde edilen bir bileşen.",
                "non_veg": "Kesim, balık ya da böcek kaynaklı bir bileşen.",
                "vegan_unsure": "Bitkisel, sentetik ya da hayvansal kaynaklı olabilir; etikette kaynak yazmaz."},
            "known_gaps": [
                "(EU) 2026/78 ile Ek II'ye eklenen 15 CMR maddesinin adları henüz eklenmedi.",
                "(EU) 2026/909: alüminyum içeren bileşenler, suda çözünen çinko tuzları, DHHB ve 4 yeni saç boyası eklenmedi.",
                "2026 sonu taslak: benzofenon-1/-2, BHA, paraben ve CBD kısıtlamaları (henüz yayımlanmadı).",
            ],
            "counts": dict(sorted(counts.items())),
            "updates_applied": len(log), "aliases_dropped_ii_conflict": dropped,
        },
        "entries": lst,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    funcs, items = inci_file(ing)
    with open(OUT_INCI, "w", encoding="utf-8") as f:
        json.dump({"version": VERSION, "last_updated": LAST_UPDATED,
                   "meta": {"source": "Avrupa Komisyonu CosIng INCI listesi (inhouse-work/cosing @%s)" % COSING_COMMIT,
                            "item": "[INCI adı, [işlev indeksleri], [bayraklar]?]", "flags": {k: FLAGS[k] for k in ("non_vegan", "non_veg", "vegan_unsure", "pfas")}},
                   "functions": funcs, "items": items}, f, ensure_ascii=False, separators=(",", ":"))
    print("kozmetik.json: %d kayıt %s" % (len(lst), json.dumps(dict(counts), ensure_ascii=False)))
    print("kozmetik_inci.json: %d INCI adı, %d işlev" % (len(items), len(funcs)))
    print("güncellemeler: %d işlem; II çakışmasıyla çıkarılan ad: %d" % (len(log), dropped))


if __name__ == "__main__":
    main()
