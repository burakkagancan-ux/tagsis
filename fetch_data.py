"""Bakanlığın taklit/tağşiş listelerini çekip data/tagsis.json dosyasına yazar."""
import json, os, sys, time, datetime
import urllib.parse, urllib.request

from dogrula_veri import dogrula_listeler, Gecersiz

URL = os.environ.get("TAGSIS_URL", "https://guvenilirgida.tarimorman.gov.tr/GuvenilirGida/GKD/DataTablesList")
REFERER = "https://guvenilirgida.tarimorman.gov.tr/GuvenilirGida/gkd/TaklitVeyaTagsisListe1?siteYayinDurumu=True"
OUT = "data/tagsis.json"
DURUM = "data/durum.json"   # her başarılı çalışmada yazılır: son kontrol zamanı
COLS = ["DuyuruTarihi", "FirmaAdi", "Marka", "UrunAdi", "Uygunsuzluk", "PartiSeriNo", "FirmaIlce", "FirmaIl", "UrunGrupAdi"]
IDS = [""] + [str(i) for i in range(300, 321)]   # "" = sağlığı tehlikeye düşürecek liste
NAMES = {"": "saglik"}


def fetch(list_id):
    f = {"draw": "1"}
    for i, c in enumerate(COLS):
        f[f"columns[{i}][data]"] = c
        f[f"columns[{i}][name]"] = c
        f[f"columns[{i}][searchable]"] = "true"
        f[f"columns[{i}][orderable]"] = "true"
        f[f"columns[{i}][search][value]"] = ""
        f[f"columns[{i}][search][regex]"] = "false"
    f.update({
        "order[0][column]": "0", "order[0][dir]": "desc",
        "start": "0", "length": "-1",          # -1 = "Hepsi": sayfalama yok, tüm kayıtlar tek istekte
        "search[value]": "", "search[regex]": "false",
        "KamuoyuDuyuruAra.ListeTurId": list_id,
        "SiteYayinDurumu": "True",
        "Order[0][column]": "DuyuruTarihi", "Order[0][dir]": "desc",
    })
    req = urllib.request.Request(URL, data=urllib.parse.urlencode(f).encode(), headers={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": REFERER,
        "Origin": "https://guvenilirgida.tarimorman.gov.tr",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    os.makedirs("data", exist_ok=True)
    listeler = {}
    for lid in IDS:
        for _ in range(3):
            try:
                j = fetch(lid)
                break
            except Exception as e:
                print(f"ListeTurId {lid!r} denemesi başarısız: {e}")
                time.sleep(5)
        else:
            sys.exit(f"HATA: ListeTurId {lid!r} alınamadı")
        data = j.get("data", [])
        total = j.get("recordsTotal", len(data))
        if len(data) != total:   # tüm kayıtlar gelmediyse yayınlama
            sys.exit(f"HATA: ListeTurId {lid!r}: {len(data)} kayıt geldi, sunucu {total} diyor")
        if data:
            listeler[NAMES.get(lid, lid)] = data
            print(f"{NAMES.get(lid, lid)}: {len(data)} kayıt")
        time.sleep(0.5)

    try:
        dogrula_listeler(listeler)       # zorunlu listeler, alanlar, tarih biçimi
    except Gecersiz as e:
        sys.exit(f"HATA: gelen veri geçersiz, dosya değiştirilmedi: {e}")

    yeni = sum(len(v) for v in listeler.values())
    if os.path.exists(OUT):
        onceki = json.load(open(OUT, encoding="utf-8"))
        eski = sum(len(v) for v in onceki["listeler"].values())
        if yeni < eski * 0.5:
            sys.exit(f"HATA: kayıt sayısı {eski} -> {yeni} düştü, dosya değiştirilmedi")
        if onceki["listeler"] == listeler:
            print("Değişiklik yok.")
            durum_yaz(onceki.get("guncelleme"), listeler)
            return
    simdi = datetime.datetime.now(datetime.timezone.utc).isoformat()
    yaz_json(OUT, {"guncelleme": simdi, "listeler": listeler})
    print(f"Yazıldı: toplam {yeni} kayıt")
    durum_yaz(simdi, listeler)


def durum_yaz(son_degisiklik, listeler):
    """Liste değişmese de 'son kontrol' zamanını kaydeder; ekranda 'son kontrol' olarak gösterilir."""
    yaz_json(DURUM, {"son_kontrol": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     "son_degisiklik": son_degisiklik,
                     "kayit": {k: len(v) for k, v in listeler.items()}}, indent=1)


def yaz_json(yol, veri, indent=None):
    """Önce geçici dosyaya yazar, sonra yerine koyar: yarıda kalan yazma bozuk dosya bırakmaz."""
    gecici = yol + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=indent)
    os.replace(gecici, yol)


if __name__ == "__main__":
    main()
