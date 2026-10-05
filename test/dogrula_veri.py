"""Bakanlık verisi doğrulaması (dogrula_veri.py): depodaki veri geçerli, bozuk örnekler reddedilir."""
import copy, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from dogrula_veri import dogrula_listeler, dogrula_tagsis, dogrula_arsiv, dogrula_durum, Gecersiz

t = json.load(open("data/tagsis.json", encoding="utf-8"))
dogrula_tagsis(t)
dogrula_arsiv(json.load(open("data/arsiv.json", encoding="utf-8")))
dogrula_durum(json.load(open("data/durum.json", encoding="utf-8")), t)
L = t["listeler"]


def bozuk(ad, degistir):
    d = copy.deepcopy(L)
    degistir(d)
    try:
        dogrula_listeler(d)
    except Gecersiz:
        print("  reddedildi:", ad)
        return 0
    print("  HATA, kabul edildi:", ad)
    return 1


def ilk(d):
    return d["saglik"][0]


hata = 0
hata += bozuk("boş nesne", lambda d: d.clear())
hata += bozuk("zorunlu liste yok", lambda d: d.pop("304"))
hata += bozuk("bilinmeyen liste adı", lambda d: d.__setitem__("999", d["304"]))
hata += bozuk("liste dizi değil", lambda d: d.__setitem__("305", {"x": 1}))
hata += bozuk("eksik alan", lambda d: ilk(d).pop("UrunAdi"))
hata += bozuk("boş firma adı", lambda d: ilk(d).__setitem__("FirmaAdi", "  "))
hata += bozuk("sayı olan alan", lambda d: ilk(d).__setitem__("Marka", 5))
hata += bozuk("tarih biçimi", lambda d: ilk(d).__setitem__("DuyuruTarihi", "2026-01-01"))
hata += bozuk("gelecek tarih", lambda d: ilk(d).__setitem__("DuyuruTarihi", "/Date(4102444800000)/"))
hata += bozuk("çok uzun alan", lambda d: ilk(d).__setitem__("UrunAdi", "x" * 5000))
hata += bozuk("kayıt nesne değil", lambda d: d["saglik"].__setitem__(0, "metin"))

for ad, fn in [("durum sayısı uyuşmuyor", lambda: dogrula_durum({"son_kontrol": "x", "kayit": {"saglik": 1}}, t)),
               ("arşivde eksik alan", lambda: dogrula_arsiv({"kayitlar": [{"anahtar": "a"}]}))]:
    try:
        fn(); print("  HATA, kabul edildi:", ad); hata += 1
    except Gecersiz:
        print("  reddedildi:", ad)

print("Bakanlık verisi doğrulaması:", "TAMAM" if not hata else f"{hata} HATA")
sys.exit(1 if hata else 0)
