# -*- coding: utf-8 -*-
"""
"Birlikte dikkat" eşleşmelerini üretir: data/eslesmeler.json

Kullanım:  python3 gen_eslesmeler.py   (önce gen_e_kodlari.py ve gen_kozmetik.py çalışmış olmalı)

İki tür kural var:
  - "cift":   iki grubun her birinden en az bir madde aynı listede (ör. benzoat + C vitamini)
  - "toplam": aynı gruptan en az iki farklı madde (AB'nin "toplam" sınırı ya da grup ADI'si olan maddeler)
Her kural resmi bir kaynağa dayanır. Kaynağı olmayan "şu ikisi birlikte zehir olur" türü iddialar eklenmez.
Metinler risk değil olasılık bildirir; miktar etiketten bilinemez.
Kozmetik INCI listeleri kozmetik.json'daki AB koşul metinlerinden üretilir (nitrozamin, florür toplamı).
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "eslesmeler.json")
VERSION = "0.1.0"
LAST_UPDATED = "2026-10-03"

FDA_BENZ = "https://www.fda.gov/food/process-contaminants-food/questions-and-answers-occurrence-benzene-soft-drinks-and-other-beverages"
HC_BENZ = "https://www.canada.ca/en/health-canada/services/food-nutrition/food-safety/chemical-contaminants/food-processing-induced-chemicals/benzene.html"
BFR_SOUTH = "https://www.bfr.bund.de/cm/349/hyperactivity_and_additives_is_there_an_association.pdf"
POLY = "https://www.cargill.com/food-beverage/emea/eu-labeling-and-legislation"
PHOS = "https://www.foodingredientsfirst.com/news/EFSA-issues-new-EU-phosphates-limits-advice-warns-that-safe-levels-may-be-being-exceeded.html"
ALU = "https://www.nutraingredients.com/Article/2008/07/16/efsa-sets-new-intake-level-for-aluminium-in-food/"
SULF = "https://www.denib.gov.tr/files/downloads/sirku_ekleri/2016-02-ek1-1.pdf"
COSING = "https://single-market-economy.ec.europa.eu/sectors/cosmetics/cosmetic-ingredient-database_en"
FORM = "https://cosmetic.chemlinked.com/news/cosmetic-news/eu-lowers-the-labelling-threshold-for-formaldehyde-releasers-in-cosmetics-regulation"


def food_rules(edb):
    alu = sorted(i["id"] for i in edb["ingredients"] if "aluminium" in i["flags"])
    return [
        {"id": "benzen", "mode": "gida", "type": "cift", "level": "yellow",
         "title": "Birlikte dikkat: benzoat + C vitamini",
         "groups": [{"label": "Benzoat", "ids": ["E210", "E211", "E212", "E213"]},
                    {"label": "C vitamini", "ids": ["E300", "E301", "E302"]}],
         "text": "Benzoatlı koruyucu ile C vitamini (askorbik asit) birlikte bulunduğunda ısı, ışık ve metal iyonlarının etkisiyle eser miktarda benzen oluşabilir. Benzen kanserojen bir maddedir. Kanada'nın 2007 taramasında 139 içeceğin çoğunda miktar içme suyu sınırının (5 µg/L) altında kaldı; üreticiler formüllerini buna göre düzenledi. Ürünü serin ve karanlık yerde saklamak oluşumu azaltır.",
         "sources": [HC_BENZ, FDA_BENZ]},
        {"id": "southampton", "mode": "gida", "type": "cift", "level": "yellow",
         "title": "Birlikte dikkat: Southampton renklendiricileri + sodyum benzoat",
         "groups": [{"label": "Renklendirici", "ids": ["E102", "E104", "E110", "E122", "E124", "E129"]},
                    {"label": "Sodyum benzoat", "ids": ["E211"]}],
         "text": "2007'deki Southampton çalışmasında çocuklara bu renklendiriciler sodyum benzoatla birlikte karışım olarak verildi ve davranış üzerinde olası bir etki görüldü. Bu üründe aynı ikili var. Etkinin hangi maddeden geldiği ayırt edilemedi; Alman BfR açık bir neden-sonuç kanıtı olmadığını belirtti. AB, renklendiriciler için uyarı etiketini zorunlu tuttu.",
         "sources": [BFR_SOUTH]},
        {"id": "polioller", "mode": "gida", "type": "toplam", "level": "yellow", "min": 2,
         "title": "Birlikte dikkat: birden fazla poliol (şeker alkolü)",
         "groups": [{"label": "Poliol", "ids": ["E420", "E421", "E953", "E964", "E965", "E966", "E967", "E968"]}],
         "text": "Poliollerin laksatif (ishal yapıcı) etkisi toplam miktara bağlıdır. AB kuralına göre eklenen poliollerin toplamı %10'u aşarsa etikette “aşırı tüketimi laksatif etki yapabilir” uyarısı zorunludur.",
         "sources": [POLY]},
        {"id": "fosfatlar", "mode": "gida", "type": "toplam", "level": "yellow", "min": 2,
         "title": "Birlikte dikkat: birden fazla fosfat katkısı",
         "groups": [{"label": "Fosfat", "ids": ["E338", "E339", "E340", "E341", "E343", "E450", "E451", "E452"]}],
         "text": "EFSA 2019'da fosfat katkıları için fosfor cinsinden ortak bir günlük alım sınırı (40 mg/kg vücut ağırlığı) belirledi ve bebek, çocuk ve fosfatlı gıdaları çok tüketen gençlerde bu sınırın aşılabileceğini bildirdi. Sınır tüm fosfat katkılarının toplamı içindir.",
         "sources": [PHOS]},
        {"id": "aluminyum", "mode": "gida", "type": "toplam", "level": "yellow", "min": 2,
         "title": "Birlikte dikkat: birden fazla alüminyumlu katkı",
         "groups": [{"label": "Alüminyumlu katkı", "ids": alu}],
         "text": "EFSA 2008'de alüminyum için haftalık alım sınırını 1 mg/kg vücut ağırlığı olarak belirledi ve çok tüketen kişilerde bu sınırın aşılabileceğini bildirdi. Sınır tüm kaynakların toplamı içindir.",
         "sources": [ALU]},
        {"id": "sulfitler", "mode": "gida", "type": "toplam", "level": "yellow", "min": 2,
         "title": "Birlikte dikkat: birden fazla sülfit",
         "groups": [{"label": "Sülfit", "ids": ["E220", "E221", "E222", "E223", "E224", "E226", "E227", "E228"]}],
         "text": "Sülfit alerjeni için eşik tek tek maddelere değil toplama bakar: toplam kükürt dioksit 10 mg/kg (ya da 10 mg/L) üzerindeyse alerjen olarak etikette belirtilmesi zorunludur.",
         "sources": [SULF]},
    ]


def cos_rules(kdb):
    amines, nitros, fluor = set(), set(), set()
    for e in kdb["entries"]:
        t = " ".join([e.get("product_type", ""), e.get("max", ""), e.get("conditions_en", "")])
        if e["annex"] == "III" and re.search(r"use with nitro\s?sating|nitrosating (agents|systems)", t, re.I):
            amines.update(e["inci"])
        if re.search(r"Avoid formation of nitrosamines|Not to be used with secondary and/or tertiary amines", t, re.I):
            nitros.update(e["inci"])
        if re.search(r"total F concentration", t, re.I):
            fluor.update(a for a in e["inci"] if "FLUOR" in a)
    fr = sorted({a for e in kdb["entries"] if "formaldehyde_releaser" in e["flags"] for a in e["inci"]})
    par = sorted({a for e in kdb["entries"] if e["id"] in ("V/12", "V/12a") for a in e["inci"]
                  if re.search(r"PARABEN$", a) and "/" not in a})
    return [
        {"id": "nitrozamin", "mode": "koz", "type": "cift", "level": "yellow",
         "title": "Birlikte dikkat: nitrozamin oluşturabilecek ikili",
         "groups": [{"label": "Nitrozamin oluşturan maddelerle birlikte kullanılmaması gereken madde", "inci": sorted(amines - nitros)},
                    {"label": "Nitrozamin oluşturabilen madde", "inci": sorted(nitros)}],
         "text": "Bazı aminler, nitrit ya da bronopol gibi maddelerle birlikte nitrozamin oluşturabilir; nitrozaminlerin bir kısmı kanserojendir. AB kozmetik yönetmeliği bu yüzden bu aminlerin “nitrozamin oluşturan sistemlerle birlikte kullanılmamasını” şart koşar. Bu üründe iki grup birlikte görünüyor.",
         "sources": [COSING]},
        {"id": "formaldehit", "mode": "koz", "type": "toplam", "level": "yellow", "min": 2,
         "title": "Birlikte dikkat: birden fazla formaldehit salıcı",
         "groups": [{"label": "Formaldehit salıcı", "inci": fr}],
         "text": "AB'de etiket uyarısı (“releases formaldehyde”) tek bir koruyucuya değil, üründe salınabilecek toplam formaldehite bakar: toplam %0,001'i aşarsa uyarı zorunludur. Birden fazla salıcı bu toplamı artırır.",
         "sources": [FORM]},
        {"id": "parabenler", "mode": "koz", "type": "toplam", "level": "yellow", "min": 2,
         "title": "Birlikte dikkat: birden fazla paraben",
         "groups": [{"label": "Paraben", "inci": par}],
         "text": "AB'de parabenlerin tek tek sınırının yanında toplam sınırı da vardır: propil ve bütil paraben toplamı %0,14'ü, tüm parabenlerin toplamı %0,8'i geçemez.",
         "sources": [COSING]},
        {"id": "florurler", "mode": "koz", "type": "toplam", "level": "yellow", "min": 2,
         "title": "Birlikte dikkat: birden fazla florür",
         "groups": [{"label": "Florür", "inci": sorted(fluor)}],
         "text": "AB'de ağız bakım ürünlerinde florür bileşikleri birlikte kullanılırsa toplam flor %0,15'i geçemez. 6 yaş altı çocuklar için diş macununda özel uyarılar vardır; çocuklar için ayrıca etikete bakın.",
         "sources": [COSING]},
    ]


def main():
    edb = json.load(open(os.path.join(HERE, "data", "e_kodlari.json"), encoding="utf-8"))
    kdb = json.load(open(os.path.join(HERE, "data", "kozmetik.json"), encoding="utf-8"))
    rules = food_rules(edb) + cos_rules(kdb)
    known = {i["id"] for i in edb["ingredients"]}
    for r in rules:
        for g in r["groups"]:
            for i in g.get("ids", []):
                assert i in known, (r["id"], i)
            assert g.get("ids") or g.get("inci"), (r["id"], g["label"])
    out = {"version": VERSION, "last_updated": LAST_UPDATED,
           "meta": {"description": "Birlikte bulunduğunda ayrıca dikkat gerektiren madde eşleşmeleri. cift: iki grubun her birinden en az biri; toplam: aynı gruptan en az 'min' farklı madde.",
                    "note": "Metinler olasılık bildirir; miktar etiketten bilinmez. Her kural resmi bir kaynağa dayanır."},
           "rules": rules}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("eslesmeler.json: %d kural" % len(rules), {r["id"]: sum(len(g.get("ids", g.get("inci", []))) for g in r["groups"]) for r in rules})


if __name__ == "__main__":
    main()
