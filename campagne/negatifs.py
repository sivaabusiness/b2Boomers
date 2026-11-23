import json, unicodedata, re
d = json.load(open("fiches_fusion.json")); kws = json.load(open("mots_cles.json"))
def plat(t): return unicodedata.normalize("NFD", t.lower()).encode("ascii","ignore").decode()
# 1) mots seuls en "Large" : personne qui ne cherche pas une entreprise
LARGE = ["emploi","emplois","salaire","formation","stage","alternance","recrutement","embauche","offre","cv","cap","bts","école","cours",
 "tuto","tutoriel","comment","diy","soi-même","idée","idées","photo","photos","image","images","dessin","pdf","définition","logiciel","application",
 "leroy","merlin","castorama","brico","bricomarché","bricodepot","gamm","lapeyre","amazon","ikea","gifi","jardiland","truffaut","botanic",
 "occasion","location","louer","suisse","belgique","moquet","courtin","o2","cesu","sap","piscine","balcon","véranda","appartement",
 "synthétique","pvc","résine","bambou","bonsai","palmier","jardinière","jardinières","lampe","lampes","éclairage","luminaire","solaire",
 "motorisation","moteur","tondeuse","robot","lambourde","lambourdes","lame","lames","kit","notice","gravier","cailloux"]
# 2) locutions en "Expression"
EXPR = ["béton désactivé","béton ciré","que faire","faire soi meme","pas japonais","facile à faire","sans entretien","tondre le dimanche","daniel moquet","bois composite"]
# 3) les requêtes produit/curiosité de la fiche, en "Exact" (bloque la requête exacte sans bloquer nos mots-clés)
EXACT = sorted(d["negatifs"].keys())
neg = [(m,"Large") for m in LARGE] + [(m,"Expression") for m in EXPR] + [(m,"Exact") for m in EXACT]
# doublon sans accent
out = []
for m,t in neg:
    for v in {m, plat(m)}:
        if (v,t) not in out: out.append((v,t))
# simulation de conflit avec les mots-clés retenus
def mots(t): return plat(t).replace("'"," ").split()
conf = []
for k in kws:
    kw = mots(k["mot"])
    for m,t in out:
        mm = mots(m)
        if t == "Large" and all(w in kw for w in mm): conf.append((k["mot"], m, t))
        if t == "Expression" and " ".join(mm) in " ".join(kw): conf.append((k["mot"], m, t))
        if t == "Exact" and mm == kw: conf.append((k["mot"], m, t))
print("négatifs:", len(out), "| Large", sum(t=="Large" for _,t in out), "| Expression", sum(t=="Expression" for _,t in out), "| Exact", sum(t=="Exact" for _,t in out))
print("conflits:", conf or "aucun")
json.dump(out, open("negatifs.json","w"), ensure_ascii=False, indent=0)
