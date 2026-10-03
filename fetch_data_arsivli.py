"""Bakanlık listesini çeker (fetch_data.py) ve listeden kalkan kayıtları data/arsiv.json'da saklar.

Bakanlık, bir kaydı belli bir süre sonra listeden kaldırıyor. Bu betik her çalıştığında
önceki data/tagsis.json ile yeni listeyi karşılaştırır:
  - önceki listede olup yeni listede olmayan kayıt -> arşive eklenir (kaldırılma tarihiyle),
  - arşivdeki bir kayıt listeye geri dönerse -> arşivden çıkarılır.
data/tagsis.json'un biçimi değişmez; arşiv ayrı bir dosyadır.

Kullanım:  python3 fetch_data_arsivli.py
Arşiv yalnızca betik çalışmaya başladığı günden itibaren dolar; daha önce kalkan kayıtlar bilinemez.
"""
import json, os, sys, hashlib, datetime

import fetch_data

OUT = fetch_data.OUT
ARSIV = "data/arsiv.json"
ANAHTAR_ALANLAR = ["DuyuruTarihi", "FirmaAdi", "Marka", "UrunAdi", "PartiSeriNo", "Uygunsuzluk"]


def anahtar(liste, kayit):
    """Bir kaydı listeler arasında tekil tanımlayan kısa özet (alanlardaki boşluk farkları yok sayılır)."""
    parca = [liste] + [" ".join(str(kayit.get(a) or "").split()) for a in ANAHTAR_ALANLAR]
    return hashlib.sha1("\x1f".join(parca).encode("utf-8")).hexdigest()[:16]


def oku(yol, bos):
    if not os.path.exists(yol):
        return bos
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def arsivi_guncelle(onceki, yeni, arsiv, bugun):
    """onceki/yeni: {liste_adi: [kayit, ...]}; arsiv: {"kayitlar": [...]}. Yeni arşivi ve özet döndürür."""
    yeni_anahtarlar = {anahtar(l, k) for l, v in yeni.items() for k in v}
    kayitlar = []
    geri_donen = 0
    for a in arsiv.get("kayitlar", []):
        if a["anahtar"] in yeni_anahtarlar:
            geri_donen += 1          # listeye geri döndü: arşivde tutma
        else:
            kayitlar.append(a)
    arsivdekiler = {a["anahtar"] for a in kayitlar}
    eklenen = 0
    for liste, v in onceki.items():
        for k in v:
            h = anahtar(liste, k)
            if h in yeni_anahtarlar or h in arsivdekiler:
                continue
            kayitlar.append({"anahtar": h, "liste": liste, "kaldirilma": bugun, "kayit": k})
            arsivdekiler.add(h)
            eklenen += 1
    kayitlar.sort(key=lambda a: (a["kaldirilma"], a["anahtar"]), reverse=True)
    return {"guncelleme": bugun, "aciklama": "Bakanlık listesinden kaldırılan kayıtlar. 'kaldirilma', kaydın listede görülmediği ilk gündür.",
            "kayitlar": kayitlar}, {"eklenen": eklenen, "geri_donen": geri_donen, "toplam": len(kayitlar)}


def main():
    onceki = oku(OUT, {"listeler": {}}).get("listeler", {})
    fetch_data.main()                      # hata olursa burada sys.exit ile durur; arşive dokunulmaz
    yeni = oku(OUT, {"listeler": {}}).get("listeler", {})
    if not yeni:
        sys.exit("HATA: yeni liste okunamadı, arşiv değiştirilmedi")
    bugun = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    arsiv = oku(ARSIV, {"kayitlar": []})
    yeni_arsiv, ozet = arsivi_guncelle(onceki, yeni, arsiv, bugun)
    if ozet["eklenen"] == 0 and ozet["geri_donen"] == 0 and os.path.exists(ARSIV):
        print("Arşivde değişiklik yok.")
        return
    with open(ARSIV, "w", encoding="utf-8") as f:
        json.dump(yeni_arsiv, f, ensure_ascii=False)
    print(f"Arşiv: {ozet['eklenen']} eklendi, {ozet['geri_donen']} listeye geri döndü, toplam {ozet['toplam']}")


if __name__ == "__main__":
    main()
