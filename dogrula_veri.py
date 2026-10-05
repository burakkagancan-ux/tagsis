"""Bakanlık verisini (data/tagsis.json, data/arsiv.json, data/durum.json) doğrular.

İki yerde kullanılır:
  - fetch_data.py yeni listeyi yazmadan önce dogrula_listeler() çağırır; geçersizse dosyaya dokunmaz.
  - .github/workflows/update.yml commit'ten önce `python dogrula_veri.py` çalıştırır; hata varsa iş durur, hiçbir şey gönderilmez.
Geçersiz veri sessizce düzeltilmez; hata mesajı yazılır ve çıkış kodu 1 olur.
"""
import json, re, sys, datetime

TAGSIS = "data/tagsis.json"
ARSIV = "data/arsiv.json"
DURUM = "data/durum.json"
LISTE_ADLARI = {"saglik"} | {str(i) for i in range(300, 321)}
ZORUNLU_LISTELER = ("saglik", "304", "305")
ALANLAR = ["DuyuruTarihi", "FirmaAdi", "Marka", "UrunAdi", "Uygunsuzluk", "PartiSeriNo", "FirmaIlce", "FirmaIl", "UrunGrupAdi"]
DOLU_OLMALI = ("FirmaAdi", "UrunAdi", "Uygunsuzluk")
EN_UZUN = 2000                     # tek alan için üst sınır (bugün en uzunu ~200 karakter)
TARIH = re.compile(r"^/Date\((\d{10,13})\)/$")
EN_ESKI = datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc)
ISO_GUN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Gecersiz(Exception):
    pass


def _kayit(kayit, yer, simdi):
    if not isinstance(kayit, dict):
        raise Gecersiz(f"{yer}: kayıt nesne değil")
    eksik = [a for a in ALANLAR if a not in kayit]
    if eksik:
        raise Gecersiz(f"{yer}: eksik alan {eksik}")
    for a in ALANLAR:
        v = kayit[a]
        if v is not None and not isinstance(v, str):
            raise Gecersiz(f"{yer}: {a} metin değil ({type(v).__name__})")
        if v and len(v) > EN_UZUN:
            raise Gecersiz(f"{yer}: {a} çok uzun ({len(v)} karakter)")
    for a in DOLU_OLMALI:
        if not (kayit[a] or "").strip():
            raise Gecersiz(f"{yer}: {a} boş")
    m = TARIH.match(kayit["DuyuruTarihi"] or "")
    if not m:
        raise Gecersiz(f"{yer}: DuyuruTarihi biçimi tanınmadı: {kayit['DuyuruTarihi']!r}")
    t = datetime.datetime.fromtimestamp(int(m.group(1)) / 1000, datetime.timezone.utc)
    if not (EN_ESKI <= t <= simdi + datetime.timedelta(days=2)):
        raise Gecersiz(f"{yer}: DuyuruTarihi olası aralıkta değil: {t.date()}")


def dogrula_listeler(listeler, simdi=None):
    """{liste_adi: [kayit, ...]} yapısını doğrular; sorun varsa Gecersiz fırlatır."""
    simdi = simdi or datetime.datetime.now(datetime.timezone.utc)
    if not isinstance(listeler, dict) or not listeler:
        raise Gecersiz("listeler boş ya da nesne değil")
    for ad, kayitlar in listeler.items():
        if ad not in LISTE_ADLARI:
            raise Gecersiz(f"beklenmeyen liste adı: {ad!r}")
        if not isinstance(kayitlar, list) or not kayitlar:
            raise Gecersiz(f"{ad}: liste boş ya da dizi değil")
        for i, k in enumerate(kayitlar):
            _kayit(k, f"{ad}[{i}]", simdi)
    for z in ZORUNLU_LISTELER:
        if z not in listeler:
            raise Gecersiz(f"beklenen liste yok: {z}")


def dogrula_tagsis(j):
    if not isinstance(j, dict) or not isinstance(j.get("guncelleme"), str):
        raise Gecersiz("tagsis.json: 'guncelleme' yok")
    dogrula_listeler(j.get("listeler"))


def dogrula_arsiv(j):
    if not isinstance(j, dict) or not isinstance(j.get("kayitlar"), list):
        raise Gecersiz("arsiv.json: 'kayitlar' dizisi yok")
    simdi = datetime.datetime.now(datetime.timezone.utc)
    goruldu = set()
    for i, a in enumerate(j["kayitlar"]):
        yer = f"arsiv[{i}]"
        if not isinstance(a, dict) or not all(x in a for x in ("anahtar", "liste", "kaldirilma", "kayit")):
            raise Gecersiz(f"{yer}: eksik alan")
        if a["liste"] not in LISTE_ADLARI:
            raise Gecersiz(f"{yer}: beklenmeyen liste adı {a['liste']!r}")
        if not ISO_GUN.match(str(a["kaldirilma"])):
            raise Gecersiz(f"{yer}: kaldirilma tarihi biçimi yanlış")
        if a["anahtar"] in goruldu:
            raise Gecersiz(f"{yer}: aynı anahtar iki kez")
        goruldu.add(a["anahtar"])
        _kayit(a["kayit"], yer, simdi)


def dogrula_durum(j, tagsis):
    if not isinstance(j, dict) or not isinstance(j.get("son_kontrol"), str):
        raise Gecersiz("durum.json: 'son_kontrol' yok")
    sayilar = {k: len(v) for k, v in tagsis["listeler"].items()}
    if j.get("kayit") != sayilar:
        raise Gecersiz(f"durum.json kayıt sayıları tagsis.json ile uyuşmuyor: {j.get('kayit')} / {sayilar}")


def main():
    try:
        oku = lambda y: json.load(open(y, encoding="utf-8"))
        t = oku(TAGSIS)
        dogrula_tagsis(t)
        dogrula_arsiv(oku(ARSIV))
        dogrula_durum(oku(DURUM), t)
    except (Gecersiz, OSError, ValueError) as e:
        sys.exit(f"HATA: veri doğrulanamadı: {e}")
    print(f"Veri geçerli: {sum(len(v) for v in t['listeler'].values())} kayıt")


if __name__ == "__main__":
    main()
