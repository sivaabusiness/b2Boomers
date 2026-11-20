# -*- coding: utf-8 -*-
"""Recupere le kit mots-cles de ta zone depuis l'espace membre B2Boomers.

Le kit est prepare a partir de l'atlas B2Boomers (inventaire Keyword Planner
ville par ville) : mots-cles de service classes par sous-service, volumes et
CPC mesures pour ta ville, correspondance suggeree, et les mots-cles a exclure
trouves dans ta zone. Il n'existe que pour une zone VALIDEE (onglet Zones).

Usage :
    python google-ads-locale/scripts/kit.py              # ta zone (si une seule)
    python google-ads-locale/scripts/kit.py --zone <id>  # si tu en as plusieurs
Ecrit dans kit/ : kit_<niche>_<ville>.json (lu par le skill) + 2 CSV pour Excel.
Lecture seule : rien n'est modifie sur ton compte Google Ads.
"""
import argparse
import csv
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from google_ads_client import load_env  # noqa: E402

ENV_PATH = os.path.join(os.getcwd(), "env.local.txt")
URL = os.environ.get("B2B_URL", "https://b2boomers-espace.vercel.app") + "/api/kit"
DOSSIER = os.path.join(os.getcwd(), "kit")


def appeler(code, params=None):
    url = URL + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + code})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit("L'espace membre refuse ton code (B2B_CODE_MEMBRE dans env.local.txt) "
                     "— verifie-le dans ton espace, ou ecris a Leo.")
        try:
            return json.load(e)
        except Exception:
            return {"ok": False, "error": f"HTTP {e.code}"}


def slug(texte):
    t = unicodedata.normalize("NFD", texte.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-") or "zone"


def cpc(x):
    return "n/d" if not x else f"{x:.2f}".replace(".", ",")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone", help="identifiant de la zone (le script les liste)")
    args = ap.parse_args()

    if not os.path.exists(ENV_PATH):
        sys.exit("env.local.txt introuvable : lance le script depuis ton dossier de "
                 "travail (celui ou tu as installe le pack).")
    code = load_env(ENV_PATH).get("B2B_CODE_MEMBRE", "").strip().upper()
    if not code.startswith("B2B-"):
        sys.exit("Il manque B2B_CODE_MEMBRE dans env.local.txt (ton code membre, ex. B2B-XXXXX).")

    zones = appeler(code).get("zones") or []
    if not zones:
        sys.exit("Aucune zone validee pour l'instant : reserve ta zone dans l'onglet Zones de "
                 "l'espace membre ; des que Leo la valide, relance ce script.")
    choix = [z for z in zones if z["id"] == args.zone] if args.zone else \
        (zones if len(zones) == 1 else [])
    if not choix:
        print("Tu as plusieurs zones ouvertes — relance avec --zone <id> :")
        for z in zones:
            etat = "kit pret" if z.get("kit") else "pas encore de kit"
            print(f"  --zone {z['id']}   {z['niche']} · {z['ville']} ({z['dept']}) — {etat}")
        sys.exit(1)
    z = choix[0]
    if not z.get("kit"):
        sys.exit(f"Pas encore de kit pour {z['niche']} · {z['ville']} : previens Leo, il le "
                 "prepare. En attendant, aucun chiffre ne s'invente.")

    rep = appeler(code, {"zone": z["id"]})
    if not rep.get("ok"):
        sys.exit(f"L'espace membre n'a pas pu fournir le kit : {rep.get('error')}")
    kit = rep["kit"]
    os.makedirs(DOSSIER, exist_ok=True)
    base = f"{kit['niche']}_{slug(z['ville'])}"

    chemin_json = os.path.join(DOSSIER, f"kit_{base}.json")
    with open(chemin_json, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DOSSIER, f"kit_{base}.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Sous-service", "Mot-clé", f"Volume/mois ({kit['reference']})",
                    "CPC bas (€)", "CPC haut (€)", "Correspondance suggérée"])
        for m in kit["mots_cles"]:
            w.writerow([m["sous_service"], m["mot_cle"], m["volume"], cpc(m["cpc_bas"]),
                        cpc(m["cpc_haut"]), m["correspondance"]])
    with open(os.path.join(DOSSIER, f"negatifs_{base}.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Mot-clé à exclure", "Catégorie", "Volume/mois"])
        for n in kit["negatifs"]:
            w.writerow([n["mot_cle"], n["categorie"], n["volume"]])
    # la zone à cibler : les communes du secteur (ajout groupé de lieux), ou tout le département
    communes, secteur = rep.get("communes") or [], rep.get("secteur") or {}
    if communes:
        with open(os.path.join(DOSSIER, f"communes_{base}.csv"), "w", newline="",
                  encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Code INSEE", "Commune", "Département"])
            for c in communes:
                w.writerow([c["insee"], c["nom"], secteur.get("dept") or z["dept"]])

    sous_services = sorted({m["sous_service"] for m in kit["mots_cles"]})
    print(f"Kit recupere : {kit['niche_label']} · {z['ville']} ({z['dept']})")
    print(f"  {len(kit['mots_cles'])} mots-cles de service, volumes mesures : {kit['reference']}")
    print(f"  sous-services : {', '.join(sous_services)}")
    print(f"  {len(kit['negatifs'])} mots-cles a exclure trouves dans la zone")
    if communes:
        print(f"  zone : secteur de {secteur.get('nom')} ({len(communes)} communes a cibler, pas de rayon)")
    elif rep.get("tout_dept"):
        print(f"  zone : tout le departement {rep.get('zone', {}).get('dept') or z['dept']} (pas de rayon)")
    print(f"  -> {chemin_json} (+ les CSV pour Excel dans {DOSSIER})")


if __name__ == "__main__":
    main()
