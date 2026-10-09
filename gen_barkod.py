# -*- coding: utf-8 -*-
"""Barkodla ürün bulma verisi: data/barkod_off.json

Kaynak: kaynak/off/urunler.json (off_al.py; Open Food Facts, Open Beauty Facts, Open Products Facts'te Türkiye'de satılan ürünler).
Lisans: Open Database License (ODbL) 1.0. Atıf uygulamada her gösterimde yapılır. Bu dosya kullanıcı katkısı veritabanımızla
(Worker D1) birleştirilmez.

Biçim (küçük olsun diye dizi): {"meta": {...}, "u": {"<barkod>": [db, ad, marka, son_degisiklik_sn, {dil: içerik metni}]}}
db: food | beauty | products (uygulamada gıda | kozmetik | temizlik). İçerik metni yoksa {} (ürün adı bilinir, içerik için fotoğraf istenir).
Çalıştır: python3 gen_barkod.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
KAYNAK = os.path.join(HERE, "kaynak", "off", "urunler.json")
CIKTI = os.path.join(HERE, "data", "barkod_off.json")


def main():
    with open(KAYNAK, encoding="utf-8") as f:
        k = json.load(f)
    u = {}
    for p in k["urunler"]:
        kod = str(p["kod"]).strip()
        if not kod.isdigit() or not 8 <= len(kod) <= 14:
            continue
        metin = {d: " ".join(str(v).split())[:4000] for d, v in sorted(p.get("metin", {}).items()) if str(v).strip()}
        u[kod] = [p["db"], p.get("ad", "")[:200], p.get("marka", "")[:100], int(p.get("t") or 0), metin]
    veri = {
        "meta": {
            "surum": k["surum"],
            "kaynak": k["kaynak"],
            "lisans": k["lisans"],
            "atif": k["atif"],
            "sayi": len(u),
            "icerikli": sum(1 for v in u.values() if v[4]),
            "aciklama": "Barkod -> [db, ad, marka, son değişiklik (sn), {dil: içerik metni}]. gen_barkod.py ile kaynak/off/urunler.json'dan üretilir; elle düzenlenmez.",
        },
        "u": dict(sorted(u.items())),
    }
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print("data/barkod_off.json:", veri["meta"]["sayi"], "ürün,", veri["meta"]["icerikli"], "içerikli")


if __name__ == "__main__":
    main()
