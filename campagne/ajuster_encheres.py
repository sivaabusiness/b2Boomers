# -*- coding: utf-8 -*-
"""Hausse (ou baisse) des enchères de la campagne « Paysagiste Artois » — P2 du skill.

    python3 campagne/ajuster_encheres.py --pct 30 --dry  --env CHEMIN/env.local.txt   -> montre, ne change rien
    python3 campagne/ajuster_encheres.py --pct 30 --apply --env CHEMIN/env.local.txt  -> applique (lancé par l'utilisateur)

Règle du skill : +20 à +30 % maximum par palier (jamais ×2), puis 72 h sans toucher.
Avant toute écriture, les enchères actuelles sont enregistrées dans
campagne/journal_encheres_<date>.json (pour pouvoir revenir en arrière).
"""
import argparse
import datetime
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ICI, "..", "B2Boomers", "Pack_B2Boomers")
sys.path.insert(0, os.path.join(PACK, "google-ads-locale", "scripts"))
from google_ads_client import GoogleAdsClient, micros_to_eur  # noqa: E402

NOM = "Paysagiste Artois"
PLAFOND_PCT = 30


def arrondi_micros(micros):
    return str(max(10_000, int(round(micros / 10_000)) * 10_000))   # au centime, 0,01 € minimum


def main():
    ap = argparse.ArgumentParser()
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--dry", action="store_true")
    m.add_argument("--apply", action="store_true")
    ap.add_argument("--pct", type=float, required=True, help="ex. 30 pour +30 %, -20 pour -20 %")
    ap.add_argument("--env", default=os.path.join(PACK, "env.local.txt"))
    a = ap.parse_args()
    if a.pct > PLAFOND_PCT:
        sys.exit(f"STOP : +{a.pct:g} % dépasse la règle du skill (+{PLAFOND_PCT} % maximum par palier).")
    facteur = 1 + a.pct / 100

    cl = GoogleAdsClient(a.env)
    cid = cl.customer_id
    q = lambda s: cl.search(cid, s)  # noqa: E731

    camp = q("SELECT campaign.id, campaign.name, campaign.status FROM campaign "
             f"WHERE campaign.name = '{NOM}' AND campaign.status != 'REMOVED'")
    if len(camp) != 1:
        sys.exit(f"STOP : campagne « {NOM} » introuvable.")
    c = camp[0]["campaign"]
    print(f"Campagne {c['id']} — statut {c['status']}")

    # Les chiffres depuis le lancement : pour vérifier que la hausse est justifiée (P2)
    stats = q("SELECT metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, "
              "metrics.search_impression_share, campaign.id FROM campaign "
              f"WHERE campaign.id = {c['id']} AND segments.date DURING LAST_30_DAYS")
    if stats:
        s = stats[0]["metrics"]
        part = s.get("searchImpressionShare")
        print(f"30 derniers jours : {s.get('impressions', 0)} impressions · {s.get('clicks', 0)} clics · "
              f"{micros_to_eur(s.get('costMicros', 0)) or 0:.2f} € · {s.get('conversions', 0)} conversions · "
              f"taux d'impressions {round(part * 100) if part else 'n/d'} %")

    kws = q("SELECT ad_group.name, ad_group_criterion.resource_name, ad_group_criterion.keyword.text, "
            "ad_group_criterion.keyword.match_type, ad_group_criterion.cpc_bid_micros, "
            "ad_group_criterion.negative, campaign.id FROM ad_group_criterion "
            f"WHERE campaign.id = {c['id']} AND ad_group_criterion.type = 'KEYWORD' "
            "AND ad_group_criterion.status != 'REMOVED' AND ad_group_criterion.negative = FALSE")
    ags = q("SELECT ad_group.resource_name, ad_group.name, ad_group.cpc_bid_micros, campaign.id FROM ad_group "
            f"WHERE campaign.id = {c['id']} AND ad_group.status != 'REMOVED'")

    journal, ops = {"date": datetime.datetime.now().isoformat(timespec="seconds"), "pct": a.pct,
                    "mots_cles": [], "groupes": []}, []
    print(f"\nEnchères {a.pct:+g} % :")
    for r in ags:
        g = r["adGroup"]
        avant = int(g.get("cpcBidMicros", 0))
        apres = arrondi_micros(avant * facteur)
        journal["groupes"].append({"resource": g["resourceName"], "nom": g["name"], "avant_micros": avant})
        ops.append({"adGroupOperation": {"update": {"resourceName": g["resourceName"], "cpcBidMicros": apres},
                                         "updateMask": "cpc_bid_micros"}})
        print(f"  groupe {g['name']:28s} {avant / 1e6:5.2f} € -> {int(apres) / 1e6:5.2f} €")
    mini, maxi = None, None
    for r in kws:
        k = r["adGroupCriterion"]
        avant = int(k.get("cpcBidMicros", 0))
        if not avant:
            continue   # pas d'enchère propre : il suit celle du groupe
        apres = arrondi_micros(avant * facteur)
        journal["mots_cles"].append({"resource": k["resourceName"], "mot": k["keyword"]["text"],
                                     "corr": k["keyword"]["matchType"], "avant_micros": avant})
        ops.append({"adGroupCriterionOperation": {"update": {"resourceName": k["resourceName"],
                                                             "cpcBidMicros": apres},
                                                  "updateMask": "cpc_bid_micros"}})
        mini = min(mini or avant, avant)
        maxi = max(maxi or avant, avant)
    if mini is None:
        sys.exit("STOP : aucun mot-clé avec une enchère propre trouvé.")
    print(f"  {len(journal['mots_cles'])} mots-clés : de {mini / 1e6:.2f}–{maxi / 1e6:.2f} € "
          f"à {mini * facteur / 1e6:.2f}–{maxi * facteur / 1e6:.2f} €")
    print(f"Opérations : {len(ops)} dans UNE transaction")

    if a.apply:
        chemin = os.path.join(ICI, f"journal_encheres_{datetime.date.today().isoformat()}.json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(journal, f, ensure_ascii=False, indent=1)
        print(f"Enchères d'avant enregistrées : {chemin}")

    print("\nEnvoi à Google :", "VÉRIFICATION (--dry, rien ne change)" if a.dry else "MODIFICATION RÉELLE (--apply)")
    try:
        cl.mutate(cid, ops, validate_only=a.dry)
    except RuntimeError as e:
        print("GOOGLE A REFUSÉ (rien n'a changé) :\n" + str(e))
        sys.exit(1)
    print("OK : Google a validé. Rien n'a changé." if a.dry
          else "OK : enchères modifiées. Ne plus y toucher pendant 72 h.")


if __name__ == "__main__":
    main()
