import csv

in_csv = r"c:\hijaiyyah-codex\MH-28-v1.0.csv"
out_in = r"c:\hijaiyyah-codex\MH_18x28.in"

letters_order = ["ا","ب","ت","ث","ج","ح","خ","د","ذ","ر","ز","س","ش","ص","ض","ط","ظ","ع","غ","ف","ق","ك","ل","م","ن","و","هـ","ي"]

rows = {}
with open(in_csv, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows[r["letter"]] = r

def to_int(r, key): 
    return int(r[key])

with open(out_in, "w", encoding="utf-8") as g:
    g.write("amb_space 18\n")
    g.write("monoid 28\n")
    for L in letters_order:
        r = rows[L]
        ThetaHat = to_int(r,"ThetaHat")
        nt,nf,nm = to_int(r,"nt"),to_int(r,"nf"),to_int(r,"nm")
        km,kt,kd,ka,kz = to_int(r,"km"),to_int(r,"kt"),to_int(r,"kd"),to_int(r,"ka"),to_int(r,"kz")
        qa,qt,qd,qs,qz = to_int(r,"qa"),to_int(r,"qt"),to_int(r,"qd"),to_int(r,"qs"),to_int(r,"qz")

        AN = nt+nf+nm
        AK = km+kt+kd+ka+kz
        AQ = qa+qt+qd+qs+qz

        H = 1 if L=="ك" else 0

        v18 = [ThetaHat, nt,nf,nm, km,kt,kd,ka,kz, qa,qt,qd,qs,qz, AN,AK,AQ, H]
        g.write(" ".join(map(str,v18))+"\n")

print("Wrote:", out_in)
