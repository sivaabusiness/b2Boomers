# Écrit PROPOSITION_CAMPAGNE.md à partir des fichiers de la campagne.
import json, sys
sys.path.insert(0, "/home/user/b2Boomers/B2Boomers/Pack_B2Boomers/google-ads-locale/scripts")
from diagnostic import longueur_affichee
r=json.load(open("rsa.json")); kws=json.load(open("mots_cles.json")); neg=json.load(open("negatifs.json")); d=json.load(open("fiches_fusion.json"))
out=["# Campagne Google Ads — Allô Paysagiste Artois","","_Version validée par l'utilisateur (23/11/2026). Création en PAUSE ; il l'active lui-même._",""]
out+=["## Réglages","| Réglage | Valeur |","|---|---|",
"| Campagne | Paysagiste Artois (Lens, Béthune, Arras) — 1 campagne, choix de l'utilisateur (secteurs voisins) |",
"| Type | Réseau de Recherche seul (ni Display, ni partenaires) |","| Statut à la création | En pause |",
"| Enchères | CPC manuel, une enchère par mot-clé (moyenne des 3 fiches) |",
"| Budget | 15 €/jour au départ (à confirmer ; palier suivant après 2 semaines) |",
"| Zone | 506 communes (42 Lens + 187 Béthune + 277 Arras), « Présence : personnes situées dans la zone », pas de rayon |",
"| Ajustements | Arras −20 % · 14 communes +15 à +25 % (fiches) |",
"| Conversions | Formulaire envoyé · Appels depuis le site · Appels depuis l'annonce |",
"| Composants | Appel 07 56 95 13 25 · liens annexes vers les 4 pages devis · accroches (Devis gratuit 24 h, Déplacement gratuit, Devis écrit, Chantier propre) |",
"| Retirés (hors positionnement du site) | béton désactivé prix m2 · allée en beton · terrasse en béton prix |",""]
for g in r["groupes"]:
    ks=[k for k in kws if k["groupe"]==g["nom"]]
    out+=[f"## Groupe « {g['nom']} »",f"Page d'arrivée : `{ks[0]['url']}` · {len(ks)} mots-clés","","| # | Titre | Caractères |","|---|---|---|"]
    for i,t in enumerate(g["titres"],1):
        tx=t["texte"] if isinstance(t,dict) else t; pin=" 📌 position 1" if isinstance(t,dict) else ""
        out.append(f"| {i} | {tx.replace('|','/')}{pin} | {longueur_affichee(tx)} |")
    out+=["","| Description | Caractères |","|---|---|"]+[f"| {x} | {len(x)} |" for x in g["descriptions"]]
    out+=["","| Mot-clé | Correspondance | Recherches/mois (3 zones) | Enchère |","|---|---|---|---|"]
    out+=[f"| {k['mot']} | {k['corr']} | {k['vol']} | {k['cpc']:.2f} € |" for k in ks]; out.append("")
out+=["## Mots exclus",f"{len(neg)} exclusions.","","| Mot | Correspondance |","|---|---|"]+[f"| {m} | {t} |" for m,t in neg]
out+=["","## Ajustements par commune","| Commune | Ajustement | Pourquoi | Fiche |","|---|---|---|---|","| Arras | −20 % | ville mixte (33 % de maisons) | Arras |"]
out+=[f"| {a[0]} | {a[1]} % | {a[2]} | {a[3].capitalize()} |" for a in d["ajust"]]
open("PROPOSITION_CAMPAGNE.md","w").write("\n".join(out)+"\n"); print("ok")
