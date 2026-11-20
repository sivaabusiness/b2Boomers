# -*- coding: utf-8 -*-
"""Verifie que tout est branche : identifiants, connexion Google, compte Ads.

Usage :
    python google-ads-locale/scripts/test_connexion.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from google_ads_client import GoogleAdsClient  # noqa: E402

ENV_PATH = os.path.join(os.getcwd(), "env.local.txt")


def main():
    client = GoogleAdsClient(ENV_PATH)
    if not client.customer_id:
        sys.exit("Il manque GOOGLE_ADS_CUSTOMER_ID dans env.local.txt "
                 "(voir le guide, partie G).")
    rows = client.search(client.customer_id, (
        "SELECT customer.descriptive_name, customer.currency_code, "
        "customer.status FROM customer"))
    c = rows[0]["customer"] if rows else {}
    print("Connexion OK !")
    print(f"  Compte  : {c.get('descriptiveName', '(sans nom)')}")
    print(f"  Numero  : {client.customer_id}")
    print(f"  Devise  : {c.get('currencyCode', '?')}")
    print(f"  Statut  : {c.get('status', '?')}")
    camps = client.search(client.customer_id, (
        "SELECT campaign.id, campaign.name, campaign.status FROM campaign "
        "ORDER BY campaign.id"))
    print(f"  Campagnes existantes : {len(camps)}")

    # Etre « connecte » = etre visible dans l'espace membre : le test envoie
    # le premier rapport de donnees tout de suite (CGU du pack).
    print("\nEnvoi du rapport de donnees vers l'espace membre…")
    try:
        import rapport
        rep = rapport.envoyer(client.code_membre, rapport.collecter(client))
        if rep.get("ok"):
            print("  Rapport envoye.")
            if rep.get("premier"):
                print("  Premier rapport : l'historique complet du compte part aussi…")
                rapport.envoyer(client.code_membre,
                                rapport.collecter(client, depuis=rapport.DEBUT_HISTORIQUE))
                print("  Compte relie a l'espace membre.")
        else:
            print("  L'espace membre a refuse le rapport :", rep)
    except Exception as e:
        print(f"  (envoi impossible pour l'instant : {e} — relance ce test plus tard)")

    print("\nTout est pret. Tu peux passer a la creation de ta campagne.")


if __name__ == "__main__":
    main()
