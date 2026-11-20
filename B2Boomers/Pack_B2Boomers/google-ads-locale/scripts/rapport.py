# -*- coding: utf-8 -*-
"""Remontee des statistiques de campagne vers l'espace membre B2Boomers.

Fait partie des CGU du pack : en installant le pack, tu acceptes l'envoi
de ces metriques business (campagnes, couts, termes de recherche — fenetre
glissante de 3 mois, et l'historique complet du compte au premier envoi).
Elles alimentent le classement mutualise des zones dont tu profites
toi-meme. Aucun identifiant, aucun mot de passe, aucune donnee personnelle
n'est envoye.

Usage :
    python google-ads-locale/scripts/rapport.py
Lance automatiquement par le skill en fin de session de travail.
"""
import datetime
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from google_ads_client import GoogleAdsClient, micros_to_eur  # noqa: E402
import diagnostic  # noqa: E402  — stade + alertes par campagne, lecture seule

ENV_PATH = os.path.join(os.getcwd(), "env.local.txt")
URL = os.environ.get("B2B_URL", "https://b2boomers-espace.vercel.app") + "/api/rapport"
VERSION_PACK = "2.8.0"
FENETRE_JOURS = 92        # 3 mois pleins a chaque envoi
DEBUT_HISTORIQUE = "2018-01-01"  # premier envoi : tout l'historique du compte


def collecter(client, depuis=None):
    cid = client.customer_id
    jusqua = datetime.date.today().isoformat()
    if not depuis:
        depuis = (datetime.date.today()
                  - datetime.timedelta(days=FENETRE_JOURS)).isoformat()
    plage = f"segments.date BETWEEN '{depuis}' AND '{jusqua}'"
    campagnes = []
    totaux = {"impressions": 0, "clics": 0, "cout_eur": 0.0, "conversions": 0.0}
    # La requête principale a un mode dégradé : si Google refuse un champ
    # (renommé/retiré d'une version de l'API — c'est arrivé avec
    # campaign.start_date le 2026-10-20 et ça a planté tout le parc), on
    # réessaie avec le noyau minimal plutôt que de perdre le rapport du jour.
    try:
        rows = client.search(cid, (
            "SELECT campaign.id, campaign.name, campaign.status, "
            "campaign_budget.amount_micros, metrics.impressions, "
            "metrics.clicks, metrics.cost_micros, metrics.conversions "
            f"FROM campaign WHERE {plage}"))
    except RuntimeError as e:
        print(f"(requete campagnes refusee, repli minimal : {str(e)[:120]})")
        rows = client.search(cid, (
            "SELECT campaign.id, campaign.name, campaign.status, "
            "metrics.impressions, metrics.clicks, metrics.cost_micros, "
            "metrics.conversions "
            f"FROM campaign WHERE {plage}"))
    for r in rows:
        c, met = r.get("campaign", {}), r.get("metrics", {})
        cout = micros_to_eur(met.get("costMicros")) or 0
        ligne = {
            "id": str(c.get("id", "")), "nom": c.get("name", ""),
            "statut": c.get("status", ""),
            "debut": "",  # rempli par la requete isolee ci-dessous
            "budget_jour": micros_to_eur(
                (r.get("campaignBudget") or {}).get("amountMicros")) or 0,
            "impressions": int(met.get("impressions", 0) or 0),
            "clics": int(met.get("clicks", 0) or 0),
            "cout_eur": cout,
            "conversions": float(met.get("conversions", 0) or 0),
        }
        campagnes.append(ligne)
        totaux["impressions"] += ligne["impressions"]
        totaux["clics"] += ligne["clics"]
        totaux["cout_eur"] = round(totaux["cout_eur"] + cout, 2)
        totaux["conversions"] += ligne["conversions"]

    # La date de début de chaque campagne : requête ISOLÉE (le champ
    # campaign.start_date a été refusé par l'API le 2026-10-20 — s'il
    # redevient valide on la récupère, sinon le diagnostic se rabat sur le
    # premier jour actif, sans rien casser).
    try:
        rows = client.search(cid, (
            "SELECT campaign.id, campaign.start_date FROM campaign"))
        debuts = {str((r.get("campaign") or {}).get("id", "")):
                  str((r.get("campaign") or {}).get("startDate", ""))[:10]
                  for r in rows}
        for ligne in campagnes:
            ligne["debut"] = debuts.get(ligne["id"], "")
    except Exception:
        pass

    # Pourquoi Google diffuse (ou pas) : requête à part, pour ne pas casser
    # la liste des campagnes si le champ change de nom dans l'API
    try:
        rows = client.search(cid, (
            "SELECT campaign.id, campaign.primary_status FROM campaign"))
        statuts = {str((r.get("campaign") or {}).get("id", "")):
                   (r.get("campaign") or {}).get("primaryStatus", "") for r in rows}
        for ligne in campagnes:
            ligne["statut_diffusion"] = statuts.get(ligne["id"], "")
    except Exception:
        pass

    # Chaque campagne jour par jour : le diagnostic lit les 3 derniers jours
    campagnes_jours = []
    try:
        rows = client.search(cid, (
            "SELECT campaign.id, segments.date, metrics.impressions, "
            "metrics.clicks, metrics.cost_micros, metrics.conversions "
            f"FROM campaign WHERE {plage} AND campaign.status = 'ENABLED'"))
        for r in rows:
            met = r.get("metrics", {})
            campagnes_jours.append({
                "campagne_id": str((r.get("campaign") or {}).get("id", "")),
                "date": (r.get("segments", {}) or {}).get("date", ""),
                "impressions": int(met.get("impressions", 0) or 0),
                "clics": int(met.get("clicks", 0) or 0),
                "cout_eur": micros_to_eur(met.get("costMicros")) or 0,
                "conversions": float(met.get("conversions", 0) or 0),
            })
    except Exception:
        pass

    jours = []
    try:
        rows = client.search(cid, (
            "SELECT segments.date, metrics.impressions, metrics.clicks, "
            "metrics.cost_micros, metrics.conversions "
            f"FROM customer WHERE {plage}"))
        for r in rows:
            met = r.get("metrics", {})
            jours.append({
                "date": (r.get("segments", {}) or {}).get("date", ""),
                "impressions": int(met.get("impressions", 0) or 0),
                "clics": int(met.get("clicks", 0) or 0),
                "cout_eur": micros_to_eur(met.get("costMicros")) or 0,
                "conversions": float(met.get("conversions", 0) or 0),
            })
        jours.sort(key=lambda j: j["date"])
    except Exception:
        pass

    termes = []
    try:
        rows = client.search(cid, (
            "SELECT search_term_view.search_term, ad_group.name, campaign.name, "
            "metrics.clicks, metrics.impressions, metrics.cost_micros, "
            "metrics.conversions "
            f"FROM search_term_view WHERE {plage} "
            "ORDER BY metrics.clicks DESC LIMIT 50"))
        for r in rows:
            met = r.get("metrics", {}) or {}
            termes.append({
                "terme": (r.get("searchTermView", {}) or {}).get("searchTerm", ""),
                "groupe": (r.get("adGroup") or {}).get("name", ""),
                "campagne": (r.get("campaign") or {}).get("name", ""),
                "clics": int(met.get("clicks", 0) or 0),
                "impressions": int(met.get("impressions", 0) or 0),
                "cout_eur": micros_to_eur(met.get("costMicros")) or 0,
                "conversions": float(met.get("conversions", 0) or 0),
            })
    except Exception:
        pass  # compte sans campagne active : pas de termes, pas grave

    # Les groupes d'annonces : l'étage entre campagne et mots-clés
    groupes = []
    try:
        rows = client.search(cid, (
            "SELECT campaign.name, ad_group.name, ad_group.status, "
            "ad_group.cpc_bid_micros, metrics.impressions, metrics.clicks, "
            "metrics.cost_micros, metrics.conversions "
            f"FROM ad_group WHERE {plage} "
            "ORDER BY metrics.cost_micros DESC LIMIT 100"))
        for r in rows:
            g, met = r.get("adGroup") or {}, r.get("metrics", {})
            groupes.append({
                "campagne": (r.get("campaign") or {}).get("name", ""),
                "nom": g.get("name", ""), "statut": g.get("status", ""),
                "enchere_defaut": micros_to_eur(g.get("cpcBidMicros")) or 0,
                "impressions": int(met.get("impressions", 0) or 0),
                "clics": int(met.get("clicks", 0) or 0),
                "cout_eur": micros_to_eur(met.get("costMicros")) or 0,
                "conversions": float(met.get("conversions", 0) or 0),
            })
    except Exception:
        pass

    # Les annonces (RSA) : les 3 premiers titres + leurs perfs
    annonces = []
    try:
        rows = client.search(cid, (
            "SELECT ad_group.name, campaign.name, ad_group_ad.status, "
            "ad_group_ad.ad.responsive_search_ad.headlines, "
            "ad_group_ad.ad.final_urls, "
            "ad_group_ad.policy_summary.approval_status, "
            "metrics.impressions, metrics.clicks, metrics.cost_micros, "
            "metrics.conversions "
            f"FROM ad_group_ad WHERE {plage} LIMIT 50"))
        for r in rows:
            aga = r.get("adGroupAd") or {}
            ad = aga.get("ad") or {}
            rsa = ad.get("responsiveSearchAd") or {}
            liste = [str(h.get("text", ""))[:60] for h in (rsa.get("headlines") or [])]
            titres = " · ".join(liste[:3])
            met = r.get("metrics", {})
            annonces.append({
                "groupe": (r.get("adGroup") or {}).get("name", ""),
                "campagne": (r.get("campaign") or {}).get("name", ""),
                "statut": aga.get("status", ""),
                "titres": titres[:200],
                "titres_liste": liste[:15],
                "url_finale": str((ad.get("finalUrls") or [""])[0])[:200],
                "approbation": (aga.get("policySummary") or {}).get("approvalStatus", ""),
                "impressions": int(met.get("impressions", 0) or 0),
                "clics": int(met.get("clicks", 0) or 0),
                "cout_eur": micros_to_eur(met.get("costMicros")) or 0,
                "conversions": float(met.get("conversions", 0) or 0),
            })
    except Exception:
        pass

    mots_cles = []
    try:
        rows = client.search(cid, (
            "SELECT ad_group.name, campaign.name, ad_group_criterion.keyword.text, "
            "ad_group_criterion.keyword.match_type, "
            "ad_group_criterion.quality_info.quality_score, "
            "ad_group_criterion.effective_cpc_bid_micros, "
            "metrics.impressions, metrics.clicks, metrics.cost_micros, "
            "metrics.conversions, metrics.average_cpc "
            f"FROM keyword_view WHERE {plage} "
            "ORDER BY metrics.cost_micros DESC LIMIT 100"))
        for r in rows:
            crit = r.get("adGroupCriterion") or {}
            met = r.get("metrics", {})
            mots_cles.append({
                "mot": (crit.get("keyword") or {}).get("text", ""),
                "corresp": (crit.get("keyword") or {}).get("matchType", ""),
                "groupe": (r.get("adGroup") or {}).get("name", ""),
                "campagne": (r.get("campaign") or {}).get("name", ""),
                "qs": int((crit.get("qualityInfo") or {}).get("qualityScore", 0) or 0),
                "enchere_max": micros_to_eur(
                    crit.get("effectiveCpcBidMicros")) or 0,
                "impressions": int(met.get("impressions", 0) or 0),
                "clics": int(met.get("clicks", 0) or 0),
                "cout_eur": micros_to_eur(met.get("costMicros")) or 0,
                "conversions": float(met.get("conversions", 0) or 0),
                "cpc_moy": micros_to_eur(met.get("averageCpc")) or 0,
            })
    except Exception:
        pass

    # Les conversions du compte : le diagnostic repère une conversion « clic
    # sur le numéro » encore comptée comme demande (coaching n°6). Lecture seule.
    conversions_actions = []
    try:
        rows = client.search(cid, (
            "SELECT conversion_action.name, conversion_action.type, "
            "conversion_action.status, conversion_action.primary_for_goal "
            "FROM conversion_action WHERE conversion_action.status = 'ENABLED'"))
        for r in rows:
            ca = r.get("conversionAction") or {}
            conversions_actions.append({
                "nom": str(ca.get("name", ""))[:80],
                "type": ca.get("type", ""),
                "principale": bool(ca.get("primaryForGoal", True)),
            })
    except Exception:
        pass  # champ refusé ou droits : pas d'alerte, pas grave

    # Historique des modifications du compte (Google ne garde que 30 jours)
    modifs = []
    try:
        d28 = (datetime.date.today() - datetime.timedelta(days=28)).isoformat()
        rows = client.search(cid, (
            "SELECT change_event.change_date_time, "
            "change_event.change_resource_type, change_event.client_type, "
            "change_event.changed_fields "
            "FROM change_event "
            f"WHERE change_event.change_date_time >= '{d28} 00:00:00' "
            "ORDER BY change_event.change_date_time DESC LIMIT 50"))
        for r in rows:
            e = r.get("changeEvent") or {}
            champs = e.get("changedFields", "")
            if isinstance(champs, dict):
                champs = ",".join(champs.get("paths", []))
            modifs.append({
                "quand": str(e.get("changeDateTime", ""))[:19],
                "type": e.get("changeResourceType", ""),
                "outil": e.get("clientType", ""),
                "champs": str(champs)[:200],
            })
    except Exception:
        pass  # droits ou compte neuf : pas d'historique, pas grave

    rapport = {
        "customer_id": cid,
        "periode": {"depuis": depuis, "jusqua": jusqua},
        "totaux": totaux,
        "campagnes": campagnes[:50],
        "groupes": groupes[:100],
        "annonces": annonces[:50],
        "termes": termes[:50],
        "mots_cles": mots_cles[:100],
        "modifs": modifs[:50],
        "jours": jours[:2000],
        "campagnes_jours": campagnes_jours[:5000],
        "conversions_actions": conversions_actions[:30],
        "version_pack": VERSION_PACK,
    }
    # Le diagnostic (stade + alertes par campagne active) : lecture seule.
    # Les anciens serveurs ignorent simplement la clé.
    try:
        diagnostic.verifier_urls(rapport["annonces"])
        rapport["diagnostic"] = diagnostic.diagnostiquer(rapport)
    except Exception as e:
        rapport["diagnostic"] = {"version": 1, "erreur": str(e)[:200], "campagnes": []}
    return rapport


def envoyer(code_membre, rapport):
    req = urllib.request.Request(URL, data=json.dumps(rapport).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + code_membre,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def notifier_membre(texte):
    """Envoie `texte` sur le Telegram du membre, avec SON bot (les deux mêmes
    variables que sur son site Vercel, recopiées dans env.local.txt).
    Variables absentes = rien n'est envoyé, le message reste affiché à l'écran."""
    from google_ads_client import load_env
    env = load_env(ENV_PATH)
    token, chat = env.get("TELEGRAM_TOKEN", "").strip(), env.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        return False
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat, "text": texte,
                         "disable_web_page_preview": True}).encode(),
        method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status == 200


def _version(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except ValueError:
        return (0,)


def maj_auto(code_membre, pack_actuel):
    """Le pack se met à jour quand l'espace publie une version plus récente.
    Sécurité : le zip est téléchargé AVEC sa signature et vérifié avec la clé
    publique de Léo (scripts/verif_maj.py) avant toute extraction — un fichier
    modifié sur le serveur est refusé. env.local.txt n'est jamais touché.
    Option : B2B_MAJ_AUTO=non dans env.local.txt → on prévient seulement,
    l'installation se fait à la main avec mettre_a_jour.py."""
    if not pack_actuel or _version(pack_actuel) <= _version(VERSION_PACK):
        return
    try:
        from google_ads_client import load_env
        auto = load_env(ENV_PATH).get("B2B_MAJ_AUTO", "oui").strip().lower()
    except Exception:
        auto = "oui"
    if auto in ("non", "no", "0", "false"):
        print(f"Nouvelle version du pack disponible ({VERSION_PACK} -> {pack_actuel}). "
              "Installation automatique desactivee (B2B_MAJ_AUTO=non) : "
              "lance mettre_a_jour.py quand tu veux.")
        return
    print(f"Nouvelle version du pack disponible ({VERSION_PACK} -> {pack_actuel}), "
          "verification de la signature puis mise a jour…")
    import io
    import zipfile
    from verif_maj import telecharger_verifie, noms_surs
    contenu = telecharger_verifie(code_membre)   # MiseAJourRefusee si signature absente/invalide

    pack = os.getcwd()
    with zipfile.ZipFile(io.BytesIO(contenu)) as z:
        noms = noms_surs(z)   # valide TOUT le zip avant de toucher au dossier
        installer_dossier(z, noms, pack)
    print(f"Pack mis a jour en v{pack_actuel} (signature verifiee, actif au prochain lancement).")


def installer_dossier(z, noms, pack, dossier="google-ads-locale"):
    """Extrait les `noms` du zip dans un dossier temporaire puis copie fichier par fichier
    dans `pack/<dossier>` (ecrase). Marche meme si le dossier est verrouille par OneDrive,
    un terminal ou Claude Code : seul un fichier reellement ouvert peut bloquer, et on
    reessaie 5 fois avant d'abandonner en nommant le fichier."""
    import shutil
    import stat
    import time
    tmp = os.path.join(pack, dossier + ".nouveau")
    if os.path.isdir(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    for nom in noms:
        z.extract(nom, tmp)
    src = os.path.join(tmp, dossier)
    cible = os.path.join(pack, dossier)
    for racine, _dirs, fichiers in os.walk(src):
        rel = os.path.relpath(racine, src)
        dest = os.path.join(cible, rel) if rel != "." else cible
        os.makedirs(dest, exist_ok=True)
        for f in fichiers:
            a, b = os.path.join(racine, f), os.path.join(dest, f)
            for essai in range(5):
                try:
                    if os.path.exists(b):
                        os.chmod(b, stat.S_IWRITE)
                    shutil.copy2(a, b)
                    break
                except PermissionError:
                    if essai == 4:
                        raise PermissionError(
                            f"le fichier {os.path.relpath(b, pack)} est utilise par un autre "
                            "programme (ferme Claude Code / le terminal ouvert dans le pack, puis relance)")
                    time.sleep(1.5)
    # caches Python de l'ancienne version
    for racine, dirs, _f in os.walk(cible):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(racine, d), ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    # console Windows en cp1252 : un nom de campagne exotique ne doit pas planter l'envoi
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    client = GoogleAdsClient(ENV_PATH)
    # Si la collecte plante (ex. : champ refusé par une nouvelle version de
    # l'API Google, 2026-10-20), on vérifie QUAND MÊME la mise à jour du pack
    # — sinon un bug qui casse la collecte empêcherait aussi sa propre
    # correction d'arriver, et tout le parc resterait en panne.
    try:
        rapport = collecter(client)
    except Exception as e:
        print(f"Collecte impossible aujourd'hui : {e}")
        print("Verification de mise a jour du pack malgre tout…")
        try:
            base = os.environ.get("B2B_URL", "https://b2boomers-espace.vercel.app")
            req = urllib.request.Request(
                base + "/api/fichier?f=pack.version",
                headers={"Authorization": "Bearer " + client.code_membre})
            with urllib.request.urlopen(req, timeout=30) as r:
                en_ligne = r.read().decode("utf-8", errors="replace").strip()
            maj_auto(client.code_membre, en_ligne)
        except Exception as e2:
            print(f"(verification reportee : {e2})")
        return
    reponse = envoyer(client.code_membre, rapport)
    if not reponse.get("ok"):
        print("L'espace membre a refuse le rapport :", reponse)
        return
    print(f"Rapport envoye : {len(rapport['campagnes'])} campagne(s), "
          f"{rapport['totaux']['clics']} clics sur 3 mois.")
    lignes = diagnostic.resume(rapport.get("diagnostic") or {})
    if lignes:
        print("Diagnostic du jour (lecture seule) :\n" + lignes)
    # Les messages que l'espace a décidé d'envoyer (nouvelle alerte, routine
    # hebdo) : l'espace ne connaît pas ton Telegram, c'est TON bot (celui
    # du site, TELEGRAM_TOKEN + TELEGRAM_CHAT_ID dans env.local.txt) qui sonne.
    for texte in reponse.get("notifs") or []:
        print("\n" + texte)
        try:
            notifier_membre(texte)
        except Exception as e:
            print(f"(notif Telegram non envoyee : {e})")
    if reponse.get("premier"):
        # premier envoi : on complete avec l'historique entier du compte
        print("Premier rapport — envoi de l'historique complet du compte…")
        complet = collecter(client, depuis=DEBUT_HISTORIQUE)
        if envoyer(client.code_membre, complet).get("ok"):
            print(f"Historique envoye ({len(complet['jours'])} jours de donnees). "
                  "Ton compte est relie a l'espace membre.")
    # auto-mise-a-jour : si l'espace publie une version plus recente du pack
    try:
        maj_auto(client.code_membre, reponse.get("pack_actuel"))
    except Exception as e:
        print(f"(mise a jour automatique reportee : {e})")
    # auto-reparation du lanceur « a l'allumage du PC » (Windows, sans admin)
    if os.name == "nt":
        try:
            import rapport_auto
            rapport_auto.assurer_demarrage(os.getcwd())
        except Exception:
            pass


if __name__ == "__main__":
    main()
