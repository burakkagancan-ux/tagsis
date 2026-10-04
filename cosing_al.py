# -*- coding: utf-8 -*-
"""
CosIng verisinin gen_kozmetik.py'nin kullandığı kısmını depoya (kaynak/cosing/) alır.

Kullanım:
  python3 cosing_al.py                      # inhouse-work/cosing deposunu sabit sürümüyle (COMMIT) indirir
  python3 cosing_al.py --commit <hash>      # başka bir sürüm
  python3 cosing_al.py --kaynak ../cosing   # elde var olan bir kopyadan (ağ gerekmez)

Yazılanlar:
  kaynak/cosing/annex.II.csv ... annex.VI.csv  AB 1223/2009 Ek II-VI (değiştirilmeden)
  kaynak/cosing/ingredients.csv                INCI listesi; yalnızca inci_name, restriction, functions sütunları
  kaynak/cosing/LICENSE.txt                    inhouse-work/cosing lisansı (MIT)
  kaynak/cosing/surum.txt                      kaynak deponun commit kimliği (gen_kozmetik.py meta alanına yazar)
Sonra: python3 gen_kozmetik.py && python3 gen_eslesmeler.py && python3 gen_temizlik.py
"""
import argparse, csv, os, shutil, subprocess, sys, tempfile

REPO = "https://github.com/inhouse-work/cosing"
COMMIT = "268e3cd368c2aa581046beb914b72f70093480fd"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "kaynak", "cosing")
ANNEXES = ["II", "III", "IV", "V", "VI"]
ING_COLS = ["inci_name", "restriction", "functions"]


def copy_from(root, commit):
    data = os.path.join(root, "data")
    os.makedirs(OUT, exist_ok=True)
    for a in ANNEXES:
        shutil.copyfile(os.path.join(data, "annex.%s.csv" % a), os.path.join(OUT, "annex.%s.csv" % a))
    csv.field_size_limit(10 ** 9)
    with open(os.path.join(data, "ingredients.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(OUT, "ingredients.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(ING_COLS)
        for r in rows:
            w.writerow([r[c] for c in ING_COLS])
    if os.path.exists(os.path.join(root, "LICENSE.txt")):
        shutil.copyfile(os.path.join(root, "LICENSE.txt"), os.path.join(OUT, "LICENSE.txt"))
    with open(os.path.join(OUT, "surum.txt"), "w", encoding="utf-8") as f:
        f.write("%s %s\n" % (REPO, commit))
    print("kaynak/cosing yazıldı: %d INCI, commit %s" % (len(rows), commit))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", default=COMMIT)
    ap.add_argument("--kaynak", help="inhouse-work/cosing deposunun yerel kopyası (verilirse indirilmez)")
    a = ap.parse_args()
    if a.kaynak:
        commit = subprocess.run(["git", "-C", a.kaynak, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or a.commit
        return copy_from(a.kaynak, commit)
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "cosing")
        subprocess.run(["git", "clone", "-q", REPO, root], check=True)
        subprocess.run(["git", "-C", root, "checkout", "-q", a.commit], check=True)
        copy_from(root, a.commit)


if __name__ == "__main__":
    sys.exit(main())
