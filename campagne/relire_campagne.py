# -*- coding: utf-8 -*-
"""Relecture du compte après création (LECTURE SEULE) : recompte tout.

    python campagne/relire_campagne.py
"""
import collections
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ICI, "..", "B2Boomers", "Pack_B2Boomers")
sys.path.insert(0, os.path.join(PACK, "google-ads-locale", "scripts"))
from google_ads_client import GoogleAdsClient, micros_to_eur  # noqa: E402

NOM = "Paysagiste Artois"
LISTE = "Mots exclus - Paysagiste Artois"


def ok(cond, txt):
    print(("  [OK]  " if cond else "  [!!]  ") + txt)
    return cond


def main():
    env = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PACK, "env.local.txt")
    cl = GoogleAdsClient(env)
    cid = cl.customer_id
    q = lambda s: cl.search(cid, s)  # noqa: E731
    attendu_kw = json.load(open(os.path.join(ICI, "mots_cles.json"), encoding="utf-8"))
    attendu_neg = json.load(open(os.path.join(ICI, "negatifs.json"), encoding="utf-8"))

    c = q("SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type, "
          "campaign.advertising_channel_type, campaign.network_settings.target_google_search, "
          "campaign.network_settings.target_search_network, campaign.network_settings.target_content_network, "
          "campaign.geo_target_type_setting.positive_geo_target_type, campaign_budget.amount_micros "
          f"FROM campaign WHERE campaign.name = '{NOM}' AND campaign.status != 'REMOVED'")
    if not ok(len(c) == 1, f"campagne « {NOM} » trouvée ({len(c)})"):
        return
    r = c[0]
    camp, ns = r["campaign"], r["campaign"]["networkSettings"]
    cid_c = camp["id"]
    print(f"\nCampagne {cid_c}")
    ok(camp["status"] == "PAUSED", f"statut : {camp['status']}")
    ok(camp["biddingStrategyType"] == "MANUAL_CPC", f"enchères : {camp['biddingStrategyType']}")
    ok(micros_to_eur(r["campaignBudget"]["amountMicros"]) == 15.0,
       f"budget : {micros_to_eur(r['campaignBudget']['amountMicros'])} €/jour")
    ok(ns.get("targetGoogleSearch") and not ns.get("targetSearchNetwork") and not ns.get("targetContentNetwork"),
       "Réseau de Recherche seul (ni partenaires ni Display)")
    ok(camp["geoTargetTypeSetting"]["positiveGeoTargetType"] == "PRESENCE", "présence : personnes situées dans la zone")

    crit = q("SELECT campaign_criterion.type, campaign_criterion.negative, campaign_criterion.bid_modifier, "
             "campaign_criterion.location.geo_target_constant, campaign.id FROM campaign_criterion "
             f"WHERE campaign.id = {cid_c}")
    types = collections.Counter(x["campaignCriterion"]["type"] for x in crit)
    lieux = [x["campaignCriterion"] for x in crit if x["campaignCriterion"]["type"] == "LOCATION"]
    ajustes = [x for x in lieux if "bidModifier" in x and abs(x["bidModifier"] - 1) > 1e-6]
    print("\nZone")
    ok(types.get("PROXIMITY", 0) == 0, "aucun rayon")
    print(f"  lieux ciblés : {len(lieux)} · langue : {types.get('LANGUAGE', 0)} · ajustements : {len(ajustes)}")
    for x in sorted(ajustes, key=lambda x: x["bidModifier"]):
        print(f"     {x['location']['geoTargetConstant']} : {round((x['bidModifier'] - 1) * 100):+d} %")

    print("\nGroupes et mots-clés")
    ag = q("SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.cpc_bid_micros, campaign.id "
           f"FROM ad_group WHERE campaign.id = {cid_c} AND ad_group.status != 'REMOVED'")
    ok(len(ag) == 4, f"{len(ag)} groupes")
    kw = q("SELECT ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
           "ad_group_criterion.cpc_bid_micros, ad_group_criterion.negative, campaign.id FROM ad_group_criterion "
           f"WHERE campaign.id = {cid_c} AND ad_group_criterion.type = 'KEYWORD' "
           "AND ad_group_criterion.status != 'REMOVED'")
    pos = [x for x in kw if not x["adGroupCriterion"].get("negative")]
    ok(len(pos) == len(attendu_kw), f"{len(pos)} mots-clés (attendu {len(attendu_kw)})")
    att = {(k["groupe"], k["mot"], {"Exact": "EXACT", "Expression": "PHRASE"}[k["corr"]]): k["cpc"] for k in attendu_kw}
    ecarts = []
    for x in pos:
        k = (x["adGroup"]["name"], x["adGroupCriterion"]["keyword"]["text"], x["adGroupCriterion"]["keyword"]["matchType"])
        bid = micros_to_eur(x["adGroupCriterion"].get("cpcBidMicros"))
        if k not in att or abs(att[k] - (bid or 0)) > 0.005:
            ecarts.append((k, bid))
    ok(not ecarts, f"enchère de chaque mot-clé = champ cpc ({len(ecarts)} écart(s))")
    for e in ecarts[:10]:
        print("     ", e)
    for g, n in collections.Counter((x["adGroup"]["name"], x["adGroupCriterion"]["keyword"]["matchType"]) for x in pos).items():
        print(f"     {g[0]} · {g[1]} : {n}")

    print("\nAnnonces")
    ads = q("SELECT ad_group.name, ad_group_ad.status, ad_group_ad.ad.final_urls, "
            "ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions, "
            "ad_group_ad.policy_summary.approval_status, campaign.id FROM ad_group_ad "
            f"WHERE campaign.id = {cid_c} AND ad_group_ad.status != 'REMOVED'")
    ok(len(ads) == 4, f"{len(ads)} annonces RSA")
    for x in ads:
        a = x["adGroupAd"]["ad"]
        rsa = a["responsiveSearchAd"]
        pins = sum(1 for h in rsa["headlines"] if h.get("pinnedField") == "HEADLINE_1")
        print(f"     {x['adGroup']['name']} : {len(rsa['headlines'])} titres ({pins} épinglés), "
              f"{len(rsa['descriptions'])} descr., {a['finalUrls'][0]} — examen : "
              f"{x['adGroupAd'].get('policySummary', {}).get('approvalStatus', '?')}")

    print("\nMots exclus")
    neg = q("SELECT shared_set.name, shared_criterion.keyword.text, shared_criterion.keyword.match_type "
            f"FROM shared_criterion WHERE shared_set.name = '{LISTE}'")
    ok(len(neg) == len(attendu_neg), f"{len(neg)} mots exclus (attendu {len(attendu_neg)})")
    lien = q("SELECT campaign_shared_set.shared_set, campaign_shared_set.status, campaign.id FROM campaign_shared_set "
             f"WHERE campaign.id = {cid_c}")
    ok(len(lien) >= 1, "liste reliée à la campagne")

    print("\nComposants")
    ca = q("SELECT campaign_asset.field_type, campaign_asset.status, campaign.id FROM campaign_asset "
           f"WHERE campaign.id = {cid_c} AND campaign_asset.status != 'REMOVED'")
    print("     campagne :", dict(collections.Counter(x["campaignAsset"]["fieldType"] for x in ca)))
    ga = q("SELECT ad_group.name, ad_group_asset.field_type, ad_group_asset.status, campaign.id FROM ad_group_asset "
           f"WHERE campaign.id = {cid_c} AND ad_group_asset.status != 'REMOVED'")
    print("     groupes  :", dict(collections.Counter((x["adGroup"]["name"], x["adGroupAsset"]["fieldType"]) for x in ga)))

    print("\nConversions")
    conv = q("SELECT conversion_action.name, conversion_action.type, conversion_action.status, "
             "conversion_action.primary_for_goal FROM conversion_action WHERE conversion_action.status = 'ENABLED'")
    for x in conv:
        v = x["conversionAction"]
        print(f"     {v['name']} | {v['type']} | {'principale' if v.get('primaryForGoal') else 'secondaire'}")
    cs = q("SELECT customer.call_reporting_setting.call_conversion_action, "
           "customer.call_reporting_setting.call_conversion_reporting_enabled FROM customer")
    print("     appels depuis l'annonce reliés :", json.dumps(cs[0]["customer"].get("callReportingSetting", {})))


if __name__ == "__main__":
    main()
