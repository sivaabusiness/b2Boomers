# -*- coding: utf-8 -*-
"""P1 — Diagnostic de la campagne « Paysagiste Artois » (LECTURE SEULE, aucune écriture).

    python3 campagne/diagnostic_p1.py --env CHEMIN/env.local.txt

Récolte, dans l'ordre de l'audit du skill (pilotage-campagne.md, P1) :
dépense par jour, derniers changements, conversions, groupes, taux d'impressions,
mots-clés (avec le « rouge » enchère 1re page), annonces, termes de recherche.
"""
import argparse
import collections
import datetime
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ICI, "..", "B2Boomers", "Pack_B2Boomers")
sys.path.insert(0, os.path.join(PACK, "google-ads-locale", "scripts"))
from google_ads_client import GoogleAdsClient  # noqa: E402

NOM = "Paysagiste Artois"


def eur(m):
    return (int(m or 0)) / 1e6


def pct(x):
    return "n/d" if x in (None, "") else f"{round(float(x) * 100)} %"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=os.path.join(PACK, "env.local.txt"))
    a = ap.parse_args()
    cl = GoogleAdsClient(a.env)
    cid = cl.customer_id

    def q(s):
        try:
            return cl.search(cid, s)
        except RuntimeError as e:
            print("   (lecture impossible :", str(e)[:200], ")")
            return []

    camp = q("SELECT campaign.id, campaign.status, campaign.serving_status, campaign.primary_status, "
             "campaign_budget.amount_micros FROM campaign "
             f"WHERE campaign.name = '{NOM}' AND campaign.status != 'REMOVED'")
    if not camp:
        sys.exit(f"Campagne « {NOM} » introuvable.")
    c = camp[0]
    cidc = c["campaign"]["id"]
    budget = eur(c["campaignBudget"]["amountMicros"])
    print(f"== CAMPAGNE {cidc} : statut {c['campaign']['status']} · diffusion "
          f"{c['campaign'].get('servingStatus')} · état {c['campaign'].get('primaryStatus')} · budget {budget:.2f} €/j")

    print("\n== 1. DÉPENSE PAR JOUR")
    jours = q("SELECT segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, "
              "metrics.search_impression_share, metrics.search_budget_lost_impression_share, "
              "metrics.search_rank_lost_impression_share FROM campaign "
              f"WHERE campaign.id = {cidc} AND segments.date DURING LAST_30_DAYS ORDER BY segments.date")
    tot = collections.Counter()
    for r in jours:
        m = r["metrics"]
        tot["impr"] += int(m.get("impressions", 0))
        tot["clics"] += int(m.get("clicks", 0))
        tot["cout"] += eur(m.get("costMicros"))
        tot["conv"] += float(m.get("conversions", 0))
        print(f"  {r['segments']['date']} : {eur(m.get('costMicros')):5.2f} € ({eur(m.get('costMicros')) / budget * 100:3.0f} % du budget) · "
              f"{m.get('impressions', 0):>4} impr · {m.get('clicks', 0):>3} clics · {float(m.get('conversions', 0)):.1f} conv · "
              f"part impr {pct(m.get('searchImpressionShare'))} (perdue enchères {pct(m.get('searchRankLostImpressionShare'))}, "
              f"budget {pct(m.get('searchBudgetLostImpressionShare'))})")
    ctr = tot["clics"] / tot["impr"] * 100 if tot["impr"] else 0
    print(f"  TOTAL : {tot['cout']:.2f} € · {tot['impr']} impr · {tot['clics']} clics · CTR {ctr:.1f} % · "
          f"{tot['conv']:.1f} conv · CPC moyen {tot['cout'] / tot['clics'] if tot['clics'] else 0:.2f} €")

    print("\n== 1b. DERNIERS CHANGEMENTS (14 jours)")
    debut = (datetime.date.today() - datetime.timedelta(days=13)).isoformat()
    fin = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    ch = q("SELECT change_event.change_date_time, change_event.change_resource_type, "
           "change_event.resource_change_operation, change_event.changed_fields, change_event.client_type "
           f"FROM change_event WHERE change_event.change_date_time >= '{debut}' "
           f"AND change_event.change_date_time <= '{fin}' "
           "ORDER BY change_event.change_date_time DESC LIMIT 40")
    resume = collections.Counter()
    for r in ch:
        e = r["changeEvent"]
        cle = (e["changeDateTime"][:16], e["changeResourceType"], e["resourceChangeOperation"],
               e.get("changedFields", "")[:60], e.get("clientType", ""))
        resume[cle] += 1
    for (d, t, op, f, cli), n in list(resume.items())[:15]:
        print(f"  {d} · {t} · {op} ×{n} · {f} · via {cli}")

    print("\n== 2. CONVERSIONS (30 j)")
    for r in q("SELECT conversion_action.name, conversion_action.type, conversion_action.primary_for_goal, "
               "conversion_action.status, metrics.all_conversions FROM conversion_action "
               "WHERE segments.date DURING LAST_30_DAYS"):
        v = r["conversionAction"]
        print(f"  {v['name']} | {v['type']} | {'principale' if v.get('primaryForGoal') else 'secondaire'} | "
              f"{float(r['metrics'].get('allConversions', 0)):.1f}")
    appels = q("SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.call_status, "
               "call_view.caller_area_code FROM call_view")
    print(f"  Appels depuis l'annonce : {len(appels)}")
    for r in appels[:15]:
        v = r["callView"]
        print(f"    {v.get('startCallDateTime')} · {v.get('callDurationSeconds', 0)} s · {v.get('callStatus')}")

    print("\n== 3-4. GROUPES (30 j)")
    for r in q("SELECT ad_group.name, ad_group.cpc_bid_micros, metrics.impressions, metrics.clicks, metrics.cost_micros, "
               "metrics.conversions, metrics.search_impression_share, metrics.search_top_impression_share "
               f"FROM ad_group WHERE campaign.id = {cidc} AND segments.date DURING LAST_30_DAYS"):
        m = r["metrics"]
        i, k = int(m.get("impressions", 0)), int(m.get("clicks", 0))
        print(f"  {r['adGroup']['name']:28s} enchère {eur(r['adGroup'].get('cpcBidMicros')):.2f} € · {i} impr · {k} clics · "
              f"CTR {k / i * 100 if i else 0:.0f} % · {eur(m.get('costMicros')):.2f} € · {float(m.get('conversions', 0)):.1f} conv · "
              f"part impr {pct(m.get('searchImpressionShare'))} (haut {pct(m.get('searchTopImpressionShare'))})")

    print("\n== 5. MOTS-CLÉS (30 j, ceux qui ont eu des impressions)")
    kw = q("SELECT ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
           "ad_group_criterion.cpc_bid_micros, ad_group_criterion.position_estimates.first_page_cpc_micros, "
           "ad_group_criterion.system_serving_status, metrics.impressions, metrics.clicks, metrics.cost_micros, "
           "metrics.average_cpc, metrics.conversions FROM keyword_view "
           f"WHERE campaign.id = {cidc} AND segments.date DURING LAST_30_DAYS AND metrics.impressions > 0 "
           "ORDER BY metrics.impressions DESC")
    for r in kw[:25]:
        k, m = r["adGroupCriterion"], r["metrics"]
        ench = eur(k.get("cpcBidMicros"))
        p1 = eur(k.get("positionEstimates", {}).get("firstPageCpcMicros"))
        rouge = "ROUGE (1re page " + f"{p1:.2f} €)" if p1 and p1 > ench else "ok"
        print(f"  {k['keyword']['text'][:34]:34s} {k['keyword']['matchType'][:6]:6s} · enchère {ench:.2f} € · "
              f"{m.get('impressions', 0)} impr · {m.get('clicks', 0)} clics · CPC moy {eur(m.get('averageCpc')):.2f} € · "
              f"{float(m.get('conversions', 0)):.1f} conv · {rouge}")
    statut = collections.Counter()
    for r in q("SELECT ad_group_criterion.system_serving_status, ad_group_criterion.approval_status "
               f"FROM ad_group_criterion WHERE campaign.id = {cidc} AND ad_group_criterion.type = 'KEYWORD' "
               "AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status != 'REMOVED'"):
        k = r["adGroupCriterion"]
        statut[(k.get("systemServingStatus"), k.get("approvalStatus"))] += 1
    print("  État des 99 mots-clés :", dict(statut))

    print("\n== 6. ANNONCES")
    for r in q("SELECT ad_group.name, ad_group_ad.status, ad_group_ad.policy_summary.approval_status, "
               "ad_group_ad.ad_strength, metrics.impressions, metrics.clicks FROM ad_group_ad "
               f"WHERE campaign.id = {cidc} AND ad_group_ad.status != 'REMOVED' AND segments.date DURING LAST_30_DAYS"):
        g = r["adGroupAd"]
        print(f"  {r['adGroup']['name']:28s} {g['status']} · examen {g.get('policySummary', {}).get('approvalStatus')} · "
              f"efficacité {g.get('adStrength')} · {r['metrics'].get('impressions', 0)} impr · {r['metrics'].get('clicks', 0)} clics")

    print("\n== 7. TERMES DE RECHERCHE (30 j, par coût)")
    st = q("SELECT search_term_view.search_term, ad_group.name, metrics.impressions, metrics.clicks, "
           "metrics.cost_micros, metrics.conversions FROM search_term_view "
           f"WHERE campaign.id = {cidc} AND segments.date DURING LAST_30_DAYS ORDER BY metrics.cost_micros DESC")
    for r in st[:30]:
        m = r["metrics"]
        print(f"  « {r['searchTermView']['searchTerm']} » ({r['adGroup']['name'][:12]}) · {m.get('impressions', 0)} impr · "
              f"{m.get('clicks', 0)} clics · {eur(m.get('costMicros')):.2f} € · {float(m.get('conversions', 0)):.1f} conv")
    print(f"  ({len(st)} termes au total)")
    print("\nFin du diagnostic — rien n'a été modifié.")


if __name__ == "__main__":
    main()
