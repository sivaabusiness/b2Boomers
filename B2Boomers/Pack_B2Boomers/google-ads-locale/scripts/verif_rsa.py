# -*- coding: utf-8 -*-
"""Vérifie les annonces (RSA) AVANT de les montrer à l'utilisateur et avant
tout --dry : les règles de references/rsa-et-assets.md (coachings de Léo
n°2, n°4, n°6, décisions du 07/11), par script, pas à l'œil.

    python google-ads-locale/scripts/verif_rsa.py <client>/rsa.json

rsa.json :
{
  "villes": ["Belfort", "Delle", ...],          # communes de la zone (kit) : jamais en dur
  "groupes": [
    {"nom": "Élagage", "mot_cle_principal": "élagage",
     "mots_cles": ["élagage belfort", "prix élagage", ...],
     "titres": [{"texte": "Élagage {LOCATION(City):Belfort}", "epingle": true},
                "Devis & Déplacement Gratuits", ...],
     "descriptions": ["...", ...]}
  ]
}
Sortie : ERREUR (à corriger, code de sortie 1) / ATTENTION (à regarder).
Lecture seule, aucun appel réseau.
"""
import json
import re
import sys
import unicodedata
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagnostic import longueur_affichee, TITRES_BANNIS  # noqa: E402

TITRE_VISE, TITRE_MAX, DESC_MAX = 25, 28, 90
BATEAU = r"\b(qualit[ée]|s[ée]rieux|professionnel\w*|savoir[- ]faire|[àa] votre service|votre expert|confiance|meilleur\w*)\b"
TECHNIQUE = r"\b(corde|nacelle|[ée]t[êe]tage|rognage|broy[ée]e?s?|b[ûu]ches?|bois mort retir[ée])\b"
TELEPHONE = r"\d{2}[\s.]?\d{2}[\s.]?\d{2}[\s.]?\d{2}"
PRIX = r"\b(prix|tarifs?)\b"


def plat(t):
    t = unicodedata.normalize("NFD", str(t).lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sans_insertions(t):
    """Le texte hors accolades (les villes du personnalisateur ne comptent pas)."""
    return re.sub(r"\{[^{}]*\}", " ", str(t))


def verifier_groupe(g, villes):
    erreurs, alertes = [], []
    titres = [x if isinstance(x, dict) else {"texte": x} for x in g.get("titres") or []]
    textes = [str(t.get("texte", "")) for t in titres]
    nom = g.get("nom", "?")

    if len(textes) < 15:
        alertes.append(f"{len(textes)} titres sur 15 : remplis les 15 (plus de combinaisons)")
    vus = set()
    for t in textes:
        n = longueur_affichee(t)
        if n > TITRE_MAX:
            erreurs.append(f"« {t} » : {n} caractères (> {TITRE_MAX})")
        elif n > TITRE_VISE:
            alertes.append(f"« {t} » : {n} caractères (vise ≤ {TITRE_VISE})")
        cle = plat(sans_insertions(t)) or plat(t)
        if cle in vus:
            erreurs.append(f"« {t} » : doublon")
        vus.add(cle)
        if "!" in t:
            erreurs.append(f"« {t} » : « ! » interdit dans un titre")
        lettres = re.sub(r"[^A-Za-zÀ-ÿ]", "", sans_insertions(t))
        if len(lettres) > 3 and lettres.isupper():
            erreurs.append(f"« {t} » : tout en majuscules (refus Google)")
        if re.search(TELEPHONE, t):
            erreurs.append(f"« {t} » : numéro de téléphone dans le texte (passe par l'asset d'appel)")
        for motif, libelle in TITRES_BANNIS:
            if re.search(motif, t, re.I):
                erreurs.append(f"« {t} » : {libelle} est interdit (on est l'entreprise qui se déplace)")
        if re.search(BATEAU, t, re.I):
            erreurs.append(f"« {t} » : vocabulaire bateau")
        if re.search(TECHNIQUE, t, re.I):
            erreurs.append(f"« {t} » : titre technique sans apport pour le client")
        if re.search(r"\bet\b", sans_insertions(t), re.I):
            alertes.append(f"« {t} » : écris « & » au lieu de « et »")
        for mot in re.findall(r"[A-Za-zÀ-ÿ][\wÀ-ÿ'’-]*", sans_insertions(t)):
            if len(mot) > 1 and mot[0].islower():
                alertes.append(f"« {t} » : une majuscule à chaque mot (« {mot} »)")
                break
        hors = " " + plat(sans_insertions(t)) + " "
        for v in villes:
            pv = plat(v)
            if pv and len(pv) > 2 and f" {pv} " in hors:
                erreurs.append(f"« {t} » : ville en dur ({v}) — le personnalisateur s'en charge")
                break

    if not any("{location(" in t.lower() for t in textes):
        erreurs.append("aucun titre avec {LOCATION(City):<ville>} (le titre épinglé n°1)")
    epingles = [t for t in titres if t.get("epingle")]
    if not epingles:
        erreurs.append("aucun titre épinglé en position 1 (service + {LOCATION(City):…})")
    elif len(epingles) > 2:
        erreurs.append(f"{len(epingles)} titres épinglés : 1 ou 2 maximum")
    for t in epingles:
        if "{location(" not in str(t.get("texte", "")).lower():
            alertes.append(f"« {t.get('texte')} » épinglé sans la ville de la personne")
    if sum(1 for t in textes if t.strip().endswith("?")) > 1:
        erreurs.append("plus d'une question dans les titres")

    principal = plat(g.get("mot_cle_principal", ""))
    if principal:
        rep = [t.get("texte") for t in titres
               if not t.get("epingle") and f" {principal} " in " " + plat(sans_insertions(t.get("texte", ""))) + " "]
        if rep:
            alertes.append(f"le mot-clé « {g.get('mot_cle_principal')} » est répété hors du titre "
                           f"épinglé : {', '.join('« %s »' % x for x in rep[:3])}")
    if any(re.search(PRIX, plat(m)) for m in g.get("mots_cles") or []) and \
            not any(re.search(PRIX, plat(t)) for t in textes):
        erreurs.append("des mots-clés parlent de prix/tarif : il faut un titre « Obtenez Un Prix » / « Prix … »")

    descs = [str(d) for d in g.get("descriptions") or []]
    if len(descs) < 4:
        alertes.append(f"{len(descs)} descriptions sur 4")
    for d in descs:
        if len(d) > DESC_MAX:
            erreurs.append(f"description de {len(d)} caractères (> {DESC_MAX}) : « {d[:40]}… »")
        if d.count("!") > 1:
            erreurs.append(f"description avec plus d'un « ! » : « {d[:40]}… »")
        if re.search(TELEPHONE, d):
            erreurs.append(f"numéro de téléphone dans une description : « {d[:40]}… »")
        for motif, libelle in TITRES_BANNIS:
            if re.search(motif, d, re.I):
                erreurs.append(f"description : {libelle} est interdit : « {d[:40]}… »")
    return [f"[{nom}] ERREUR : {e}" for e in erreurs], [f"[{nom}] ATTENTION : {a}" for a in alertes]


def verifier(donnees):
    villes = donnees.get("villes") or []
    erreurs, alertes = [], []
    groupes = donnees.get("groupes") or []
    if len(groupes) > 4:
        erreurs.append(f"{len(groupes)} groupes d'annonces : 3-4 maximum (regroupe les sous-services)")
    for g in groupes:
        e, a = verifier_groupe(g, villes)
        erreurs += e
        alertes += a
    return erreurs, alertes


def main():
    try:
        sys.stdout.reconfigure(errors="replace")  # console Windows (cp1252)
    except Exception:
        pass
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        donnees = json.load(f)
    erreurs, alertes = verifier(donnees)
    for ligne in erreurs + alertes:
        print(ligne)
    print(f"\n{len(erreurs)} erreur(s), {len(alertes)} point(s) d'attention.")
    if not erreurs:
        print("RSA conformes aux règles : montre-les à l'utilisateur avant le --dry.")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
