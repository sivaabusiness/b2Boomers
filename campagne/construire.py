# Construit la proposition de campagne à partir des 3 fiches fusionnées.
import json, unicodedata, re
d = json.load(open("fiches_fusion.json"))
M = d["mots"]
DOM = "https://allopaysagisteartois.fr/?travaux="
# (mot-clé, correspondance)  E = exact, P = expression
GROUPES = {
 "Aménagement & création": ("amenagement-jardin", [
   ("paysagiste","E"),("paysagiste","P"),("entreprise paysagiste","P"),("aménagement jardin","E"),("aménagement jardin","P"),
   ("aménagement extérieur jardin","P"),("amenagement exterieur","P"),("aménagement paysager","P"),("entreprise aménagement extérieur","P"),
   ("aménagement extérieur devant maison","P"),("amenagement devant maison","P"),("aménagement extérieur maison","P"),("aménagement jardin en pente","P"),
   ("amenagement terrain en pente","P"),("maçon paysagiste","P"),("espace vert paysagiste","P"),("paysagiste nord pas de calais","P"),("prix paysagiste","P"),
   ("pose gazon en rouleau","P"),("poseur de gazon en rouleau","P"),("engazonnement","P"),("prix engazonnement au m2","P"),("prix m2 gazon paysagiste","P"),
   ("plantation haie","P"),("creation de massif","P"),
   ("arrosage automatique installation","P"),("installation arrosage automatique enterré","P"),("entreprise arrosage automatique","P"),
   ("installateur arrosage automatique jardin","P"),("pose arrosage automatique","P"),("prix arrosage automatique","P"),("installation arrosage enterré","P"),
   ("création bassin jardin","P"),("paysagiste bassin aquatique","P"),("amenagement d un bassin exterieur","P")]),
 "Terrasse, allées & murets": ("terrasse-allee", [
   ("amenagement terrasse","P"),("amenagement terrasse exterieur","P"),("aménagement terrasse jardin","P"),("aménagement terrasse devant maison","P"),
   ("pose terrasse bois","P"),("pose terrasse composite","P"),("pose terrasse sur plot","P"),("pose dalle sur plot","P"),("devis terrasse en bois","P"),
   ("artisan terrasse","P"),("terrasse en béton prix","P"),
   ("allée carrossable","P"),("allée de jardin","P"),("pose de pavé pour passage voiture","P"),("aménagement allée entrée maison","P"),
   ("aménagement cour extérieur","P"),("amenagement cour","P"),("allée en beton","P"),("béton désactivé prix m2","P"),("allée goudron prix au m2","P"),
   ("mur de soutènement","P"),("enrochement","P"),("muret jardin","P"),("talus aménagement","P"),("aménagement talus moderne","P")]),
 "Entretien de jardin": ("entretien-jardin", [
   ("jardinier autour de moi","P"),("jardinier paysagiste","P"),("entretien espace vert","P"),("entretien jardin","E"),("entretien jardin","P"),
   ("jardinier professionnel","P"),("jardinier à domicile","P"),("jardinier entreprise","P"),("entreprise entretien espace vert","P"),
   ("entreprise entretien jardin","P"),("entretien de jardin particulier","P"),("devis jardinier","P"),("tarif jardinier","P"),("prix jardinier","P"),
   ("recherche jardinier","P"),("tarif entretien jardin à l année","P"),("prix entretien jardin","P"),("entreprise de jardinage","P"),
   ("petit travaux de jardinage chez particulier","P"),("tonte pelouse","P"),("entreprise tonte de pelouse","P"),("tarif tonte pelouse","P"),
   ("entreprise taille haie","P"),("tarif taille de haie 3 faces","P"),("devis pour tailler une haie","P"),("jardinier taille haie","P"),("entretien haie","P")]),
 "Clôture & portail": ("cloture-portail", [
   ("pose cloture","P"),("pose grillage","P"),("installation cloture","P"),("installation grillage rigide","P"),("poseur de cloture","P"),
   ("prix pose cloture rigide","P"),("pose portail","P"),("installation portail coulissant","P"),("installation portail battant","P"),
   ("installateur portail","P"),("poseur de portail","P"),("entreprise pose portail et clôture","P"),("prix portail alu avec pose","P"),
   ("brise vue pose","P"),("installateur brise vue","P")]),
}
POIDS = {"lens": 0.0, "bethune": 0.0, "arras": 0.0}
lignes = []
for g, (slug, kws) in GROUPES.items():
    for kw, mt in kws:
        v = M[kw]
        e = [x for x in v["ench"].values() if x]
        bid = round(sum(e) / len(e), 2)          # moyenne des enchères conseillées des 3 fiches
        lignes.append(dict(groupe=g, url=DOM + slug, mot=kw, corr="Exact" if mt == "E" else "Expression",
                           vol=round(v["vol"], 1), haut=v["haut"], cpc=bid, service_fiche=v["service"]))
# contrôle : doublons
vus = set()
for l in lignes:
    k = (l["mot"], l["corr"]); assert k not in vus, k; vus.add(k)
json.dump(lignes, open("mots_cles.json", "w"), ensure_ascii=False, indent=1)
from collections import defaultdict
s = defaultdict(lambda: [0, 0.0, []])
for l in lignes:
    if l["corr"] == "Exact" and (l["mot"], "Expression") in vus: pass
    s[l["groupe"]][0] += 1; s[l["groupe"]][2].append(l["cpc"])
    if not (l["corr"] == "Exact" and (l["mot"], "Expression") in vus): s[l["groupe"]][1] += l["vol"]
tot = 0
for g, (n, vol, c) in s.items():
    c = sorted(c); print(f"{g:28s} {n:3d} mots-clés | ~{vol:5.0f} recherches/mois | CPC médian {c[len(c)//2]:.2f} €"); tot += n
print("TOTAL mots-clés:", tot)
