# -*- coding: utf-8 -*-
"""Création de la campagne « Paysagiste Artois » — UNE transaction Google Ads.

    python3 campagne/creer_campagne.py --dry     -> vérification par Google, RIEN n'est créé
    python3 campagne/creer_campagne.py --apply   -> création réelle (EN PAUSE) — lancé par l'utilisateur

Options :
    python3 campagne/creer_campagne.py --communes -> seulement la recherche des communes
    --sans-images   retire les images et le logo (compte trop récent pour les images)
    --env CHEMIN    autre fichier env.local.txt

Lit : mots_cles.json, negatifs.json, rsa.json, fiches_fusion.json, images/ (dossier campagne/).
Les identifiants restent dans env.local.txt (jamais affichés, jamais sur GitHub).
"""
import argparse
import base64
import json
import os
import re
import statistics
import sys
import unicodedata
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ICI, "..", "B2Boomers", "Pack_B2Boomers")
sys.path.insert(0, os.path.join(PACK, "google-ads-locale", "scripts"))
from google_ads_client import GoogleAdsClient  # noqa: E402

NOM_CAMPAGNE = "Paysagiste Artois"
NOM_LISTE_NEG = "Mots exclus - Paysagiste Artois"
BUDGET_EUR = 15
TELEPHONE = "07 56 95 13 25"
DOMAINE = "https://allopaysagisteartois.fr/"
AJUST_ARRAS = -20                       # en %
CORR = {"Exact": "EXACT", "Expression": "PHRASE", "Large": "BROAD"}

# Chemin d'affichage (path1/path2, 15 car. max) par groupe
PATHS = {
    "Aménagement & création": ("jardin", "artois"),
    "Terrasse, allées & murets": ("terrasse", "artois"),
    "Entretien de jardin": ("entretien", "artois"),
    "Clôture & portail": ("cloture", "artois"),
}
# Service (slug ?travaux=) -> liens annexes
SITELINKS = [
    ("amenagement-jardin", "Devis Aménagement Jardin", "Création, gazon, haies, arrosage", "Devis gratuit sous 24 h"),
    ("terrasse-allee", "Devis Terrasse & Allée", "Terrasse, allée, muret, talus", "Devis gratuit sous 24 h"),
    ("entretien-jardin", "Devis Entretien Jardin", "Tonte, taille de haie, entretien", "Devis gratuit sous 24 h"),
    ("cloture-portail", "Devis Clôture & Portail", "Clôture, grillage, portail", "Devis gratuit sous 24 h"),
]
ACCROCHES = ["Devis Gratuit Sous 24 h", "Déplacement Gratuit", "Devis Écrit Avant Travaux", "Chantier Rendu Propre"]


def plat(t):
    t = unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()
    t = re.sub(r"[-'’ ]+", " ", t).strip()
    t = re.sub(r"\bst\b", "saint", t)
    return re.sub(r"\bste\b", "sainte", t)


def micros(eur):
    return str(int(round(eur * 100)) * 10_000)


def charger(nom):
    with open(os.path.join(ICI, nom), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- lectures
def lire_compte(client, cid):
    camps = client.search(cid, "SELECT campaign.id, campaign.name, campaign.status FROM campaign")
    sets = client.search(cid, "SELECT shared_set.id, shared_set.name, shared_set.status FROM shared_set")
    convs = client.search(cid, (
        "SELECT conversion_action.id, conversion_action.name, conversion_action.type, "
        "conversion_action.status, conversion_action.primary_for_goal, "
        "conversion_action.resource_name FROM conversion_action"))
    cust = client.search(cid, "SELECT customer.call_reporting_setting.call_reporting_enabled, "
                              "customer.call_reporting_setting.call_conversion_reporting_enabled, "
                              "customer.call_reporting_setting.call_conversion_action FROM customer")
    return ([r["campaign"] for r in camps], [r["sharedSet"] for r in sets],
            [r["conversionAction"] for r in convs], (cust[0]["customer"].get("callReportingSetting", {}) if cust else {}))


def geos_region(client, cid):
    """Toutes les villes et codes postaux Google des Hauts-de-France (+ départements)."""
    rows = client.search(cid, (
        "SELECT geo_target_constant.resource_name, geo_target_constant.name, "
        "geo_target_constant.canonical_name, geo_target_constant.target_type, "
        "geo_target_constant.parent_geo_target, geo_target_constant.status, "
        "geo_target_constant.country_code FROM geo_target_constant "
        "WHERE geo_target_constant.country_code = 'FR' "
        "AND geo_target_constant.canonical_name LIKE '%Hauts-de-France%' "
        "AND geo_target_constant.target_type IN ('City', 'Postal Code', 'Department') "
        "AND geo_target_constant.status = 'ENABLED'"))
    villes, postaux, depts = {}, {}, {}
    for r in rows:
        g = r["geoTargetConstant"]
        if g["targetType"] == "City":
            villes.setdefault(plat(g["name"]), []).append(g)
        elif g["targetType"] == "Postal Code":
            postaux[g["name"]] = g
        else:
            depts[g["resourceName"]] = g["name"]
    return villes, postaux, depts


DEPTS_REGION = ["62", "59", "80", "02", "60"]   # Pas-de-Calais + autres départements des Hauts-de-France


def communes_officielles():
    """Liste officielle (geo.api.gouv.fr) : nom, INSEE, codes postaux de toute la région."""
    out = {}
    for d in DEPTS_REGION:
        url = f"https://geo.api.gouv.fr/departements/{d}/communes?fields=nom,code,codesPostaux"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                out[d] = json.load(r)
        except Exception as e:
            sys.exit(f"STOP : liste officielle des communes injoignable ({e.__class__.__name__}). "
                     "Vérifie ta connexion internet et relance.")
    return out


def resoudre_communes(client, cid, communes, bavard=False):
    villes, postaux, depts = geos_region(client, cid)
    print(f"   Google connaît en Hauts-de-France : {sum(len(v) for v in villes.values())} villes, "
          f"{len(postaux)} codes postaux, {len(depts)} départements")
    if not villes:
        sys.exit("STOP : Google ne renvoie aucune ville des Hauts-de-France. Montre ce message à Claude.")
    off = communes_officielles()
    noms_region = {}                     # nom simplifié -> nb de communes de ce nom dans la région
    cp_communes, cp_de, nom_de = {}, {}, {}
    for d, lst in off.items():
        for x in lst:
            noms_region[plat(x["nom"])] = noms_region.get(plat(x["nom"]), 0) + 1
            nom_de[x["code"]] = x["nom"]
            for cp in x.get("codesPostaux", []):
                cp_communes.setdefault(cp, set()).add(x["code"])
            if d == "62":
                cp_de[x["code"]] = x.get("codesPostaux", [])
    a_cibler = set(communes)
    res, manquantes, via_cp = {}, [], []
    stats = {"ville": 0, "cp": 0}
    for insee, (nom, _zone) in communes.items():
        cands = villes.get(plat(nom), [])
        unique = noms_region.get(plat(nom), 0) == 1   # aucun homonyme dans la région
        if len(cands) == 1 and unique:
            res[insee] = cands[0]["resourceName"]
            stats["ville"] += 1
            continue
        raison = ("homonyme ailleurs dans la région" if cands and not unique else
                  "plusieurs lieux Google du même nom" if len(cands) > 1 else "pas une ville chez Google")
        cps = cp_de.get(insee, [])
        ok_cp = [cp for cp in cps if cp in postaux and cp_communes.get(cp, set()) <= a_cibler]
        if ok_cp:
            res[insee] = postaux[ok_cp[0]]["resourceName"]
            stats["cp"] += 1
            via_cp.append(f"{nom} ({insee}) -> code postal {ok_cp[0]}")
            continue
        detail = []
        for cp in cps:
            if cp not in postaux:
                detail.append(f"{cp} inconnu de Google")
            else:
                hors = sorted(nom_de.get(i, i) for i in cp_communes.get(cp, set()) - a_cibler)
                detail.append(f"{cp} déborde sur {len(hors)} commune(s) hors zone : {', '.join(hors[:6])}"
                              + ("…" if len(hors) > 6 else ""))
        manquantes.append(f"{nom} ({insee}) : {raison} ; " + ("; ".join(detail) or "pas de code postal"))
    print(f"   Par ville : {stats['ville']} · par code postal (100 % dans ta zone) : {stats['cp']}")
    return res, manquantes, via_cp


# ---------------------------------------------------------------- opérations
def construire(cid, kws, negs, rsa, fiches, geos, convs, appel_conf, images):
    C = f"customers/{cid}"
    ops = []
    budget, camp, liste = f"{C}/campaignBudgets/-1", f"{C}/campaigns/-2", f"{C}/sharedSets/-3"
    ops.append({"campaignBudgetOperation": {"create": {
        "resourceName": budget, "name": f"Budget {NOM_CAMPAGNE}", "amountMicros": micros(BUDGET_EUR),
        "deliveryMethod": "STANDARD", "explicitlyShared": False}}})
    ops.append({"campaignOperation": {"create": {
        "resourceName": camp, "name": NOM_CAMPAGNE, "status": "PAUSED",
        "advertisingChannelType": "SEARCH", "campaignBudget": budget, "manualCpc": {},
        "networkSettings": {"targetGoogleSearch": True, "targetSearchNetwork": False,
                            "targetContentNetwork": False, "targetPartnerSearchNetwork": False},
        "geoTargetTypeSetting": {"positiveGeoTargetType": "PRESENCE", "negativeGeoTargetType": "PRESENCE"},
        "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"}}})
    ops.append({"campaignCriterionOperation": {"create": {
        "campaign": camp, "language": {"languageConstant": "languageConstants/1002"}}}})

    # Zone : 1 critère par lieu, ajustements (Arras -20 %, communes de la fiche)
    nom_insee = {v[0]: k for k, v in fiches["communes"].items()}
    ajust = {nom_insee["Arras"]: AJUST_ARRAS}
    for nom, pct, _pourquoi, _z in fiches["ajust"]:
        ajust[nom_insee[nom]] = min(int(pct), 25)
    par_lieu = {}
    for insee, res in geos.items():
        par_lieu.setdefault(res, []).append(insee)
    zone = {"lieux": 0, "ajustes": [], "non_ajustes": []}
    for res, insees in par_lieu.items():
        crit = {"campaign": camp, "location": {"geoTargetConstant": res}}
        pcts = {ajust.get(i, 0) for i in insees}
        if len(pcts) == 1 and pcts != {0}:
            pct = pcts.pop()
            crit["bidModifier"] = round(1 + pct / 100, 2)
            zone["ajustes"].append((", ".join(fiches["communes"][i][0] for i in insees), pct))
        elif len(pcts) > 1:
            zone["non_ajustes"].append(", ".join(fiches["communes"][i][0] for i in insees if i in ajust))
        ops.append({"campaignCriterionOperation": {"create": crit}})
        zone["lieux"] += 1

    # Mots exclus : liste partagée liée à la campagne
    ops.append({"sharedSetOperation": {"create": {"resourceName": liste, "name": NOM_LISTE_NEG,
                                                  "type": "NEGATIVE_KEYWORDS"}}})
    for mot, corr in negs:
        ops.append({"sharedCriterionOperation": {"create": {
            "sharedSet": liste, "keyword": {"text": mot, "matchType": CORR[corr]}}}})
    ops.append({"campaignSharedSetOperation": {"create": {"campaign": camp, "sharedSet": liste}}})

    # Groupes, mots-clés (enchère = champ cpc), annonces
    groupes = {}
    for i, g in enumerate(rsa["groupes"]):
        ag = f"{C}/adGroups/{-10 - i}"
        ks = [k for k in kws if k["groupe"] == g["nom"]]
        urls = {k["url"] for k in ks}
        assert len(urls) == 1, f"plusieurs URL dans {g['nom']}"
        url = urls.pop()
        assert "?travaux=" in url and "devis-" not in url, url
        med = statistics.median(k["cpc"] for k in ks)
        groupes[g["nom"]] = {"ag": ag, "url": url, "n": len(ks), "med": med,
                             "min": min(k["cpc"] for k in ks), "max": max(k["cpc"] for k in ks),
                             "exact": sum(k["corr"] == "Exact" for k in ks)}
        ops.append({"adGroupOperation": {"create": {
            "resourceName": ag, "name": g["nom"], "campaign": camp, "status": "ENABLED",
            "type": "SEARCH_STANDARD", "cpcBidMicros": micros(med)}}})
        for k in ks:
            ops.append({"adGroupCriterionOperation": {"create": {
                "adGroup": ag, "status": "ENABLED", "cpcBidMicros": micros(k["cpc"]),
                "keyword": {"text": k["mot"], "matchType": CORR[k["corr"]]}}}})
        titres = []
        for t in g["titres"]:
            if isinstance(t, dict):
                h = {"text": t["texte"]}
                if t.get("epingle"):
                    h["pinnedField"] = "HEADLINE_1"
                titres.append(h)
            else:
                titres.append({"text": t})
        p1, p2 = PATHS[g["nom"]]
        ops.append({"adGroupAdOperation": {"create": {
            "adGroup": ag, "status": "ENABLED",
            "ad": {"finalUrls": [url], "responsiveSearchAd": {
                "headlines": titres, "descriptions": [{"text": d} for d in g["descriptions"]],
                "path1": p1, "path2": p2}}}}})

    # Composants niveau campagne
    n = [-100]

    def asset(corps):
        rn = f"{C}/assets/{n[0]}"
        n[0] -= 1
        ops.append({"assetOperation": {"create": dict(resourceName=rn, **corps)}})
        return rn

    def lier(rn, champ, ag=None):
        if ag:
            ops.append({"adGroupAssetOperation": {"create": {"adGroup": ag, "asset": rn, "fieldType": champ}}})
        else:
            ops.append({"campaignAssetOperation": {"create": {"campaign": camp, "asset": rn, "fieldType": champ}}})

    lier(asset({"callAsset": {"countryCode": "FR", "phoneNumber": TELEPHONE,
                              "callConversionReportingState": "USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION"}}), "CALL")
    for slug, texte, d1, d2 in SITELINKS:
        lier(asset({"finalUrls": [f"{DOMAINE}devis-{slug}.html"],
                    "sitelinkAsset": {"linkText": texte, "description1": d1, "description2": d2}}), "SITELINK")
    for a in ACCROCHES:
        lier(asset({"calloutAsset": {"calloutText": a}}), "CALLOUT")

    imgs = []
    if images:
        slug_groupe = {groupes[g]["url"].split("=")[-1]: groupes[g]["ag"] for g in groupes}
        for f in sorted(os.listdir(os.path.join(ICI, "images"))):
            with open(os.path.join(ICI, "images", f), "rb") as fh:
                data = base64.b64encode(fh.read()).decode()
            rn = asset({"name": f"Paysagiste Artois - {f}", "type": "IMAGE", "imageAsset": {"data": data}})
            if f == "logo.png":
                lier(rn, "BUSINESS_LOGO")
                imgs.append((f, "campagne (logo)"))
            elif f.startswith("equipe"):
                lier(rn, "AD_IMAGE")
                imgs.append((f, "campagne (équipe)"))
            else:
                slug = next(s for s in slug_groupe if s in f)
                lier(rn, "AD_IMAGE", slug_groupe[slug])
                imgs.append((f, f"groupe {slug}"))

    # Appels depuis l'annonce : relier au niveau du compte si ce n'est pas déjà fait
    modif_compte = None
    if appel_conf and appel_conf.get("besoin"):
        ops.append({"customerOperation": {"update": {
            "resourceName": C, "callReportingSetting": {
                "callReportingEnabled": True, "callConversionReportingEnabled": True,
                "callConversionAction": appel_conf["resource"]}},
            "updateMask": "callReportingSetting.callReportingEnabled,"
                          "callReportingSetting.callConversionReportingEnabled,"
                          "callReportingSetting.callConversionAction"}})
        modif_compte = f"relier les appels depuis l'annonce à « {appel_conf['nom']} »"
    return ops, groupes, zone, imgs, modif_compte


# ---------------------------------------------------------------- programme
def main():
    ap = argparse.ArgumentParser()
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--dry", action="store_true")
    m.add_argument("--apply", action="store_true")
    m.add_argument("--communes", action="store_true", help="seulement la recherche des communes (rien n'est envoyé)")
    ap.add_argument("--sans-images", action="store_true")
    ap.add_argument("--env", default=os.path.join(PACK, "env.local.txt"))
    a = ap.parse_args()

    kws, negs, rsa, fiches = (charger("mots_cles.json"), charger("negatifs.json"),
                              charger("rsa.json"), charger("fiches_fusion.json"))
    client = GoogleAdsClient(a.env)
    cid = client.customer_id

    print("1) Lecture du compte…")
    camps, sets, convs, call_set = lire_compte(client, cid)
    if any(c["name"] == NOM_CAMPAGNE and c.get("status") != "REMOVED" for c in camps):
        sys.exit(f"STOP : une campagne « {NOM_CAMPAGNE} » existe déjà dans le compte. Rien n'est fait.")
    if any(s["name"] == NOM_LISTE_NEG and s.get("status") != "REMOVED" for s in sets):
        sys.exit(f"STOP : la liste « {NOM_LISTE_NEG} » existe déjà. Rien n'est fait.")
    print(f"   Campagnes existantes : {len(camps)}")
    print("   Conversions du compte :")
    for c in convs:
        print(f"     - {c['name']} | {c['type']} | {c['status']} | "
              f"{'principale' if c.get('primaryForGoal') else 'secondaire'}")
    actives = [c for c in convs if c["status"] == "ENABLED"]
    attendues = {"formulaire envoye": None, "appels depuis le site": None, "appels depuis l annonce": None}
    for c in actives:
        if plat(c["name"]) in attendues:
            attendues[plat(c["name"])] = c
    manque = [k for k, v in attendues.items() if v is None]
    if manque:
        print(f"   ATTENTION : conversion(s) introuvable(s) sous ce nom : {', '.join(manque)}")
    clics = [c for c in actives if c["type"] == "CLICK_TO_CALL" and c.get("primaryForGoal")]
    if clics:
        print("   ATTENTION : une conversion « clic sur le numéro » est principale "
              "(à passer en secondaire — rien n'est changé ici sans ton accord).")
    annonce = attendues["appels depuis l annonce"]
    appel_conf = None
    if annonce:
        deja = (call_set.get("callConversionAction") == annonce["resourceName"]
                and call_set.get("callConversionReportingEnabled"))
        print(f"   Appels depuis l'annonce reliés au compte : {'oui' if deja else 'NON'}")
        appel_conf = {"besoin": not deja, "resource": annonce["resourceName"], "nom": annonce["name"]}

    print("2) Recherche des 506 communes chez Google (Pas-de-Calais, code INSEE)…")
    geos, manquantes, via_cp = resoudre_communes(client, cid, fiches["communes"], bavard=a.communes)
    print(f"   Trouvées : {len(geos)} / {len(fiches['communes'])}")
    for v in via_cp:
        print(f"   via code postal : {v}")
    if manquantes:
        print("   NON TROUVÉES (elles ne seraient pas ciblées) :")
        for v in manquantes:
            print(f"     - {v}")
        if not a.dry:
            sys.exit("STOP : des communes ne sont pas trouvées. Montre ce message à Claude. Rien n'est créé.")

    if a.communes:
        print("\nOK : toutes les communes sont trouvées. (Mode --communes : rien n'est envoyé.)")
        return
    ops, groupes, zone, imgs, modif = construire(cid, kws, negs, rsa, fiches, geos, convs,
                                                 appel_conf, not a.sans_images)

    print("\n=========== RÉCAPITULATIF ===========")
    print(f"Campagne        : {NOM_CAMPAGNE} — EN PAUSE — Réseau de Recherche seul — CPC manuel")
    print(f"Budget          : {BUDGET_EUR} €/jour")
    print(f"Zone            : {zone['lieux']} lieux ciblés (présence) pour {len(geos)} communes, pas de rayon")
    for nom, pct in zone["ajustes"]:
        print(f"   ajustement   : {nom} {pct:+d} %")
    for nom in zone["non_ajustes"]:
        print(f"   PAS d'ajustement pour {nom} : son code postal couvre aussi des communes sans ajustement")
    print(f"Mots exclus     : {len(negs)} dans la liste « {NOM_LISTE_NEG} »")
    for g, d in groupes.items():
        print(f"Groupe « {g} » : {d['n']} mots-clés ({d['exact']} exact) — enchères {d['min']:.2f} à "
              f"{d['max']:.2f} € (groupe {d['med']:.2f} €) — {d['url']}")
    print(f"Annonces        : {len(groupes)} RSA (15 titres, 4 descriptions chacune)")
    print(f"Composants      : appel {TELEPHONE}, {len(SITELINKS)} liens annexes, {len(ACCROCHES)} accroches")
    print(f"Images          : {len(imgs) if imgs else 'aucune (--sans-images)'}")
    med = statistics.median(k["cpc"] for k in kws)
    print(f"Clics/jour      : ~{BUDGET_EUR / med:.0f} (15 € / enchère médiane {med:.2f} €)")
    if modif:
        print(f"MODIF DU COMPTE : {modif} (réglage d'appels du compte)")
    print(f"Opérations      : {len(ops)} dans UNE transaction")

    mode = "VÉRIFICATION (--dry, rien n'est créé)" if a.dry else "CRÉATION RÉELLE (--apply)"
    print(f"\n3) Envoi à Google : {mode}…")
    try:
        rep = client.mutate(cid, ops, validate_only=a.dry)
    except RuntimeError as e:
        print("\nGOOGLE A REFUSÉ (rien n'a été créé). Détail :")
        print(str(e))
        sys.exit(1)
    if a.dry:
        print("OK : Google a validé toute la transaction. Rien n'a été créé.")
    else:
        res = rep.get("mutateOperationResponses", [])
        print(f"OK : {len(res)} éléments créés. La campagne est EN PAUSE.")
        for r in res[:2]:
            print("  ", json.dumps(r))


if __name__ == "__main__":
    main()
