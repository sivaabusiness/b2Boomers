# Lit les 3 fiches Atlas et fusionne : mots-clés (volumes additionnés), négatifs, communes, ajustements.
import re, json, sys
F = {z: f"/home/user/b2Boomers/B2Boomers/Fiche_lancement_paysagiste_secteur_{z}.md" for z in ("lens","bethune","arras")}
def num(s):
    s = s.replace(" ","").replace(" ","").replace(",",".").replace("€","")
    try: return float(s)
    except: return None
data = {"mots": {}, "negatifs": {}, "communes": {}, "ajust": [], "plan": {}, "quartiers": []}
for z, path in F.items():
    txt = open(path, encoding="utf-8").read()
    # plan démarrer
    m = re.search(r"### Démarrer.*?\n(.*?)\n###", txt, re.S)
    data["plan"][z] = {l.split(" : CPC max ")[0][2:]: num(l.split("CPC max ")[1]) for l in m.group(1).splitlines() if "CPC max" in l}
    # mots-clés par service
    for bloc in re.finditer(r"### (.+?) — ~[^\n]*\n(.*?)(?=\n### |\n## )", txt, re.S):
        svc = bloc.group(1)
        for row in re.findall(r'^\| "([^"]+)" \| ([^|]+) \| ([^|]+) \| ([^|]+) \|', bloc.group(2), re.M):
            kw, vol, haut, ench = row
            d = data["mots"].setdefault(kw, {"service": svc, "vol": 0.0, "haut": haut.strip(), "ench": {}})
            d["vol"] += num(vol) or 0; d["ench"][z] = num(ench)
    neg = re.search(r"## Les mots à exclure.*?\n(\|.*?)\n\n", txt, re.S).group(1)
    for row in re.findall(r"^\| ([^|]+) \| ([^|]+) \| ([^|]+) \|", neg, re.M):
        if row[0].strip() in ("Mot-clé à exclure",) or row[0].startswith("---"): continue
        data["negatifs"].setdefault(row[0].strip(), row[1].strip())
    com = re.search(r"## Les communes à cibler.*?```\n(.*?)```", txt, re.S).group(1)
    for l in com.strip().splitlines():
        nom, insee = l.rsplit(" — ", 1); data["communes"].setdefault(insee.strip(), (nom.strip(), z))
    aj = re.search(r"## Ajustements d’enchère par commune\n(.*?)\n\n", txt, re.S).group(1)
    for row in re.findall(r"^\| ([^|]+) \| ([+−-]\d+) % \| ([^|]+) \|", aj, re.M):
        data["ajust"].append((row[0].strip(), row[1].replace("−","-"), row[2].strip(), z))
    q = re.search(r"## Les quartiers.*?\n(.*?)\n\n", txt, re.S).group(1)
    data["quartiers"] += [(z, l.strip()) for l in q.splitlines() if l.strip()]
    data.setdefault("centre", {})[z] = re.search(r"- Ville centre — ([^\n]+)", txt).group(1)
json.dump(data, open("fiches_fusion.json","w"), ensure_ascii=False, indent=1)
print("mots-clés distincts:", len(data["mots"]), "| négatifs:", len(data["negatifs"]), "| communes uniques:", len(data["communes"]))
from collections import Counter
print("communes par zone:", Counter(v[1] for v in data["communes"].values()))
print("ajustements:", data["ajust"]); print("centres:", data["centre"])
for z,p in data["plan"].items(): print(z, p)
