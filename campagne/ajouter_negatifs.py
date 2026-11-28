# -*- coding: utf-8 -*-
"""P4 — Ajoute des mots exclus à la liste « Mots exclus - Paysagiste Artois ».

    python3 campagne/ajouter_negatifs.py FICHIER.json --dry   --env CHEMIN/env.local.txt
    python3 campagne/ajouter_negatifs.py FICHIER.json --apply --env CHEMIN/env.local.txt

FICHIER.json : [["mot", "Large" | "Expression" | "Exact"], ...]
Refuse tout mot exclu qui bloquerait un mot-clé de la campagne ; ignore ceux déjà dans la liste.
"""
import argparse
import json
import os
import sys
import unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ICI, "..", "B2Boomers", "Pack_B2Boomers")
sys.path.insert(0, os.path.join(PACK, "google-ads-locale", "scripts"))
from google_ads_client import GoogleAdsClient  # noqa: E402

LISTE = "Mots exclus - Paysagiste Artois"
NOM = "Paysagiste Artois"
CORR = {"Large": "BROAD", "Expression": "PHRASE", "Exact": "EXACT"}


def mots(t):
    return unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode().replace("'", " ").split()


def bloque(neg, corr, kw):
    n, k = mots(neg), mots(kw)
    if corr == "BROAD":
        return all(w in k for w in n)
    if corr == "PHRASE":
        return " ".join(n) in " ".join(k)
    return n == k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier")
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--dry", action="store_true")
    m.add_argument("--apply", action="store_true")
    ap.add_argument("--env", default=os.path.join(PACK, "env.local.txt"))
    a = ap.parse_args()
    with open(a.fichier if os.path.isabs(a.fichier) else os.path.join(os.getcwd(), a.fichier), encoding="utf-8") as f:
        ajouts = [(t, CORR[c]) for t, c in json.load(f)]

    cl = GoogleAdsClient(a.env)
    cid = cl.customer_id
    ss = cl.search(cid, "SELECT shared_set.resource_name, shared_set.name, shared_set.status FROM shared_set "
                        f"WHERE shared_set.name = '{LISTE}' AND shared_set.status = 'ENABLED'")
    if len(ss) != 1:
        sys.exit(f"STOP : liste « {LISTE} » introuvable.")
    rn = ss[0]["sharedSet"]["resourceName"]
    deja = {(r["sharedCriterion"]["keyword"]["text"].lower(), r["sharedCriterion"]["keyword"]["matchType"])
            for r in cl.search(cid, "SELECT shared_set.name, shared_criterion.keyword.text, "
                                    "shared_criterion.keyword.match_type FROM shared_criterion "
                                    f"WHERE shared_set.name = '{LISTE}'")}
    kws = [r["adGroupCriterion"]["keyword"]["text"] for r in cl.search(cid, (
        "SELECT ad_group_criterion.keyword.text, campaign.name FROM ad_group_criterion "
        f"WHERE campaign.name = '{NOM}' AND ad_group_criterion.type = 'KEYWORD' "
        "AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status != 'REMOVED'"))]

    ops, ignores = [], []
    for t, c in ajouts:
        if (t.lower(), c) in deja:
            ignores.append(f"{t} (déjà dans la liste)")
            continue
        conflit = [k for k in kws if bloque(t, c, k)]
        if conflit:
            sys.exit(f"STOP : « {t} » ({c}) bloquerait le mot-clé « {conflit[0]} ». Rien n'est fait.")
        ops.append({"sharedCriterionOperation": {"create": {"sharedSet": rn,
                                                            "keyword": {"text": t, "matchType": c}}}})
        print(f"  + {t} ({c})")
    for i in ignores:
        print("  =", i)
    print(f"{len(ops)} mot(s) exclu(s) à ajouter · aucun conflit avec les {len(kws)} mots-clés")
    if not ops:
        return
    print("Envoi à Google :", "VÉRIFICATION (--dry, rien ne change)" if a.dry else "AJOUT RÉEL (--apply)")
    try:
        cl.mutate(cid, ops, validate_only=a.dry)
    except RuntimeError as e:
        print("GOOGLE A REFUSÉ (rien n'a changé) :\n" + str(e))
        sys.exit(1)
    print("OK : Google a validé. Rien n'a changé." if a.dry else "OK : mots exclus ajoutés.")


if __name__ == "__main__":
    main()
