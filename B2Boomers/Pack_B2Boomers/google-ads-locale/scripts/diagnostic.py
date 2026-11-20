# -*- coding: utf-8 -*-
"""Diagnostic automatique d'une campagne — LECTURE SEULE, aucune écriture.

Applique les seuils de references/pilotage-campagne.md (règles des coachings
de Léo, n°2 → n°7, la session la plus récente gagne) aux données que
rapport.py a déjà collectées, pour chaque campagne active :
  - le stade (0 bloquée, 1 ne dépense pas, 2 trop tôt, 3 on lit, 4 on optimise)
  - des alertes codées, chacune avec un chiffre et la procédure à lancer
    (dont les règles de coupe d'une zone, le plafond de budget atteint,
    les titres interdits et la conversion « clic sur le numéro »).

Fonction pure (testable sans Google) : diagnostiquer(rapport, aujourd_hui).
`verifier_urls` est la seule à toucher le réseau (un HEAD sur les URL
finales des annonces, pour repérer une 404) ; rapport.py l'appelle avant.
"""
import datetime
import re
import urllib.request

STADES = {
    0: "bloquée", 1: "ne dépense pas", 2: "trop tôt",
    3: "on lit", 4: "on optimise",
}
# Les seuils du skill (pilotage-campagne.md, coachings n°2 → n°7 ; la session
# la plus récente gagne)
JOURS_PLEINS_MIN = 1        # n°7 : « trois heures après je paie déjà mes clics » —
                            # dès le 1er jour plein sans dépense, ce sont les enchères
JOURS_LUS = 3               # on lit au plus les 3 derniers jours pleins
PART_BUDGET_MIN = 0.50      # n°6 (audit) : jour sous 50 % du budget = ne dépense pas
IMPR_QUASI_NULLES = 10      # moins de 10 impressions/jour en moyenne (n°4 : 8 en un jour → monter)
IMPR_MIN_CTR = 100          # on juge un CTR à partir de 100 impressions
CTR_FAIBLE = 10.0           # en % — n°6 : CTR < 10 % → réécrire (7 % = « à chier »)
TITRE_MAX = 28              # caractères (texte de secours des insertions compris) : on vise
                            # 25, mais « Devis & Déplacement Gratuits » (28, validé n°6) passe
COUT_TERME_HORS_SUJET = 5.0 # € dépensés sans conversion
CLICS_SANS_CONV = 30
CLICS_DECISION = 100
DEMANDES_OPTI = 10
GROUPES_MAX = 4             # n°6 : 3-4 groupes d'annonces maximum
COUPE_SANS_DEMANDE = 60.0   # n°7 : > 60 € dépensés sans demande → on coupe la zone
COUPE_COUT_DEMANDE = 50.0   # n°7 : > 50 € la demande au début → on coupe
COUPE_DEPENSE_MIN = 100.0   # n°7 : 1 demande puis 100-150 € sans 2e → on coupe
PLAFOND_PART = 0.90         # n°7 : plafond tapé tous les jours → +5 € de budget
# Titres interdits (n°2, n°6, décision du 07/11 : on est l'entreprise, jamais
# un intermédiaire ; les gens veulent quelqu'un qui se déplace)
TITRES_BANNIS = (
    (r"humain vous r[ée]pond", "« Un humain vous répond »"),
    (r"mise en relation", "« mise en relation »"),
    (r"partenaire", "« partenaire »"),
    (r"devis par t[ée]l[ée]phone", "« devis par téléphone »"),
)
# Conversion « clic sur le numéro » : à retirer (n°6 : on ne compte que les vraies demandes)
CONV_CLIC_TEL = re.compile(r"clic.*(num|t[ée]l)|click.*call", re.I)

STATUTS_BLOQUES = ("NOT_ELIGIBLE", "MISCONFIGURED", "PENDING")
APPROBATIONS_KO = ("DISAPPROVED", "AREA_OF_INTEREST_ONLY")

PROCEDURES = {
    "P1": "diagnostic", "P2": "kickstart", "P3": "titres",
    "P4": "mots-clés négatifs", "P5": "enchères", "P6": "conversions et URL",
    "P7": "site",
}


def _f(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _date(s):
    try:
        return datetime.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


_INSERTION = re.compile(r"\{[^{}]*?:([^{}]*)\}")


def longueur_affichee(titre):
    """Longueur d'un titre tel que Google l'affiche au pire : chaque insertion
    {LOCATION(City):Belfort}, {KeyWord:Élagage}, {=IF(...):texte} compte pour
    son texte de secours (après les deux-points), comme le fait Google."""
    t = str(titre or "")
    if "{" not in t:
        return len(t)
    # un IF : la branche la plus longue compte
    for m in re.finditer(r"\{=IF\([^,]*,([^)]*)\):([^{}]*)\}", t):
        plus_long = max(m.group(1), m.group(2), key=len)
        t = t.replace(m.group(0), plus_long)
    return len(_INSERTION.sub(lambda m: m.group(1), t))


def _alerte(code, procedure, message, valeur=None, details=None):
    a = {"code": code, "procedure": procedure, "message": message}
    if valeur is not None:
        a["valeur"] = valeur
    if details:
        a["details"] = details
    return a


def _eur(x):
    return f"{x:.2f}".replace(".", ",") + " €"


def _pct(x):
    return f"{x:.1f}".replace(".", ",") + " %"


def _de(c):
    """`de` la campagne, ou par nom : les groupes/annonces/mots-clés/termes
    portent le nom de la campagne (champ `campagne`)."""
    return lambda x: (x.get("campagne") or "") == c.get("nom")


def diagnostiquer(rapport, aujourd_hui=None):
    """rapport : le dict construit par rapport.collecter(). Renvoie
    {"version": 1, "date": "AAAA-MM-JJ", "campagnes": [...]}."""
    auj = aujourd_hui or datetime.date.today()
    if isinstance(auj, str):
        auj = _date(auj)
    par_jour = {}
    for j in rapport.get("campagnes_jours") or []:
        par_jour.setdefault(str(j.get("campagne_id", "")), {})[str(j.get("date", ""))[:10]] = j

    resultats = []
    for c in rapport.get("campagnes") or []:
        if c.get("statut") != "ENABLED":
            continue
        groupes = [g for g in rapport.get("groupes") or [] if _de(c)(g)]
        annonces = [a for a in rapport.get("annonces") or [] if _de(c)(a)]
        mots = [k for k in rapport.get("mots_cles") or [] if _de(c)(k)]
        termes = [t for t in rapport.get("termes") or [] if _de(c)(t)]
        jours = par_jour.get(str(c.get("id", "")), {})

        # --- jours pleins depuis le lancement (aujourd'hui ne compte pas) ---
        debut = _date(c.get("debut"))
        dates_actives = sorted(d for d, j in jours.items()
                               if _f(j.get("impressions")) > 0 and _date(d))
        if not debut and dates_actives:
            debut = _date(dates_actives[0])
        jours_pleins = (auj - debut).days if debut and debut < auj else 0
        jours_pleins = max(0, jours_pleins)

        clics = int(_f(c.get("clics")))
        conv = _f(c.get("conversions"))
        budget = _f(c.get("budget_jour"))
        alertes = []

        # --- stade ---
        stade = None
        raison = ""
        statut_p = str(c.get("statut_diffusion") or "").upper()
        approb = [str(a.get("approbation") or "").upper() for a in annonces]
        if statut_p in STATUTS_BLOQUES:
            stade, raison = 0, f"Google ne diffuse pas ({statut_p.lower().replace('_', ' ')})"
        elif annonces and all(x in APPROBATIONS_KO for x in approb):
            stade, raison = 0, "toutes les annonces sont refusées"
        elif jours_pleins >= JOURS_PLEINS_MIN:
            # les derniers jours pleins (3 au plus) : une campagne dépense dès
            # les premières heures (n°7), sinon ce sont les enchères
            n = min(JOURS_LUS, jours_pleins)
            derniers = [(auj - datetime.timedelta(days=i)).isoformat() for i in range(1, n + 1)]
            imp3 = sum(_f(jours.get(d, {}).get("impressions")) for d in derniers)
            cout3 = sum(_f(jours.get(d, {}).get("cout_eur")) for d in derniers)
            if not jours and jours_pleins <= 7:
                # pas de détail par jour (ancien format) : on lit les totaux
                imp3 = _f(c.get("impressions")) * n / max(jours_pleins, 1)
                cout3 = _f(c.get("cout_eur")) * n / max(jours_pleins, 1)
            quasi_nulles = imp3 < IMPR_QUASI_NULLES * n
            sous_budget = budget > 0 and cout3 < PART_BUDGET_MIN * budget * n
            if quasi_nulles or sous_budget:
                stade = 1
                periode = "le dernier jour" if n == 1 else f"les {n} derniers jours"
                if quasi_nulles:
                    raison = f"{int(imp3)} impressions sur {periode}"
                    valeur = int(imp3)
                else:
                    raison = (f"{_eur(cout3 / n)}/jour dépensés pour "
                              f"{_eur(budget)}/jour de budget")
                    valeur = round(cout3 / n, 2)
                pleins = "1 jour plein" if jours_pleins == 1 else f"{jours_pleins} jours pleins"
                alertes.append(_alerte(
                    "ne_depense_pas", "P2",
                    f"après {pleins}, {raison} : enchères trop basses", valeur))
        if stade is None:
            if jours_pleins < JOURS_PLEINS_MIN:
                stade, raison = 2, ("lancée aujourd'hui : elle doit dépenser dans les "
                                    "heures qui viennent, on regarde demain")
            elif clics < CLICS_DECISION:
                stade, raison = 2, f"{clics} clics cumulés (< {CLICS_DECISION})"
            elif conv < DEMANDES_OPTI:
                stade, raison = 3, f"{clics} clics, {conv:g} conversion(s) Google (< {DEMANDES_OPTI})"
            else:
                stade, raison = 4, f"{clics} clics, {conv:g} conversions Google"

        # --- alertes indépendantes du stade ---
        # CTR faible par groupe (≥ 100 impressions)
        for g in groupes:
            imp, cl = _f(g.get("impressions")), _f(g.get("clics"))
            if imp >= IMPR_MIN_CTR:
                ctr = 100.0 * cl / imp
                if ctr < CTR_FAIBLE:
                    alertes.append(_alerte(
                        "ctr_faible", "P3",
                        f"groupe « {g.get('nom', '')} » : CTR {_pct(ctr)} sur {int(imp)} impressions",
                        round(ctr, 1), [g.get("nom", "")]))
        # Titres trop longs (> TITRE_MAX = 28 caractères), jugés dès le jour 1
        longs = []
        for a in annonces:
            for t in a.get("titres_liste") or []:
                if longueur_affichee(t) > TITRE_MAX and t not in longs:
                    longs.append(t)
        if longs:
            alertes.append(_alerte(
                "titres_longs", "P3",
                f"{len(longs)} titre(s) de plus de {TITRE_MAX} caractères, ex. « {longs[0]} » "
                f"({longueur_affichee(longs[0])})",
                len(longs), longs[:5]))
        # Titres interdits (n°2, n°6, 07/11) : intermédiaire, téléphone, « humain »
        bannis = []
        for a in annonces:
            for t in a.get("titres_liste") or []:
                if t not in bannis and any(re.search(m, t, re.I) for m, _ in TITRES_BANNIS):
                    bannis.append(t)
        if bannis:
            alertes.append(_alerte(
                "titres_bannis", "P3",
                f"{len(bannis)} titre(s) interdit(s), ex. « {bannis[0]} » : on est l'entreprise "
                "qui se déplace, jamais un intermédiaire",
                len(bannis), bannis[:5]))
        # Pas d'insertion de la ville (n°4, n°6 : le personnalisateur, « un banger »)
        tous_titres = [t for a in annonces for t in (a.get("titres_liste") or [])]
        if tous_titres and not any("{location(" in t.lower() for t in tous_titres):
            alertes.append(_alerte(
                "sans_personnalisateur", "P3",
                "aucun titre n'affiche la ville de la personne ({LOCATION(City)}) : "
                "ajoute le personnalisateur en titre épinglé n°1",
                len(annonces)))
        # Trop de groupes actifs : budget dilué (n°6 : 3-4 maximum, on met en veille)
        actifs = [g for g in groupes if str(g.get("statut") or "ENABLED").upper() == "ENABLED"]
        if len(actifs) > GROUPES_MAX:
            alertes.append(_alerte(
                "groupes_dilues", "P1",
                f"{len(actifs)} groupes d'annonces actifs : le budget se dilue, garde les 3-4 "
                "qui rapportent le plus et mets les autres en pause (sans rien supprimer)",
                len(actifs), [g.get("nom", "") for g in actifs][:5]))
        # Termes de recherche hors sujet : coûtent > 5 € sans convertir
        chers = sorted([t for t in termes
                        if _f(t.get("conversions")) == 0 and _f(t.get("cout_eur")) > COUT_TERME_HORS_SUJET],
                       key=lambda t: -_f(t.get("cout_eur")))
        if chers:
            total = sum(_f(t.get("cout_eur")) for t in chers)
            alertes.append(_alerte(
                "termes_hors_sujet", "P4",
                f"{len(chers)} terme(s) à {_eur(total)} sans aucune conversion, ex. "
                + ", ".join("« %s » (%s)" % (t.get("terme", ""), _eur(_f(t.get("cout_eur")))) for t in chers[:5]),
                round(total, 2), [t.get("terme", "") for t in chers[:5]]))
        # Conversions absentes : ≥ 30 clics et 0 conversion Google
        if clics >= CLICS_SANS_CONV and conv == 0:
            alertes.append(_alerte(
                "conversions_absentes", "P6",
                f"{clics} clics et 0 conversion comptée par Google (balise ou appels non suivis ?)",
                clics))
        # Règles de coupe d'une zone (n°7, budget serré) : vérifiées sur les
        # conversions Google, à recouper avec les vraies demandes (Telegram)
        cout = _f(c.get("cout_eur"))
        if conv == 0 and cout > COUPE_SANS_DEMANDE:
            alertes.append(_alerte(
                "seuil_coupe", "P1",
                f"{_eur(cout)} dépensés sans aucune conversion Google : si tu n'as reçu aucune "
                f"vraie demande (Telegram), la règle des {COUPE_SANS_DEMANDE:.0f} € dit de couper "
                "cette zone (mise en pause, rien de supprimé)",
                round(cout, 2)))
        elif conv >= 1 and cout >= COUPE_DEPENSE_MIN and cout / conv > COUPE_COUT_DEMANDE:
            alertes.append(_alerte(
                "cout_demande_eleve", "P1",
                f"{_eur(cout / conv)} par conversion Google ({_eur(cout)} pour {conv:g}) : "
                f"au-delà de {COUPE_COUT_DEMANDE:.0f} € la demande, la règle dit de couper "
                "(vérifie d'abord tes vraies demandes)",
                round(cout / conv, 2)))
        # Campagne saine qui tape son plafond : +5 € de budget, pas les enchères (n°7)
        if budget > 0 and conv >= 1 and stade >= 2 and jours_pleins >= JOURS_LUS:
            derniers = [(auj - datetime.timedelta(days=i)).isoformat() for i in range(1, JOURS_LUS + 1)]
            if all(_f(jours.get(d, {}).get("cout_eur")) >= PLAFOND_PART * budget for d in derniers):
                alertes.append(_alerte(
                    "plafond_atteint", "P1",
                    f"elle dépense tout son budget ({_eur(budget)}/jour) depuis {JOURS_LUS} jours avec "
                    f"{conv:g} conversion(s) : monte le budget de 5 €/jour, ne touche pas aux enchères",
                    budget))
        # Conversion « clic sur le numéro » encore comptée comme demande (n°6)
        clic_tel = [x.get("nom", "") for x in rapport.get("conversions_actions") or []
                    if x.get("principale", True) and (str(x.get("type", "")).upper() == "CLICK_TO_CALL"
                                                      or CONV_CLIC_TEL.search(str(x.get("nom", ""))))]
        if clic_tel:
            alertes.append(_alerte(
                "conversion_clic_tel", "P6",
                f"la conversion « {clic_tel[0]} » compte un clic sur le numéro comme une demande : "
                "passe-la en secondaire, seuls les formulaires et les vrais appels comptent",
                len(clic_tel), clic_tel[:5]))
        # URL finale vers une page tunnel ou une 404
        urls_ko = []
        for a in annonces:
            u = str(a.get("url_finale") or "")
            st = a.get("url_statut")
            if u and ("devis-" in u.lower() or (isinstance(st, int) and st >= 400)):
                if u not in urls_ko:
                    urls_ko.append(u)
        if urls_ko:
            alertes.append(_alerte(
                "url_finale_tunnel", "P6",
                f"{len(urls_ko)} URL finale(s) vers une page tunnel ou introuvable, ex. {urls_ko[0]}",
                len(urls_ko), urls_ko[:5]))
        # Mot-clé en requête large
        larges = [k.get("mot", "") for k in mots if str(k.get("corresp", "")).upper() == "BROAD"]
        if larges:
            alertes.append(_alerte(
                "mot_cle_large", "P4",
                f"{len(larges)} mot(s)-clé(s) en requête large, ex. « {larges[0]} » → passer en expression/exact",
                len(larges), larges[:5]))

        resultats.append({
            "id": str(c.get("id", "")), "nom": c.get("nom", ""),
            "stade": stade, "stade_libelle": STADES[stade], "raison": raison,
            "jours_pleins": jours_pleins, "clics": clics, "conversions": conv,
            "alertes": alertes,
        })
    return {"version": 1, "date": auj.isoformat(), "campagnes": resultats}


def verifier_urls(annonces, timeout=6):
    """Pose `url_statut` (code HTTP) sur chaque annonce dont l'URL finale
    répond ; silencieux en cas d'échec réseau. Lecture seule (HEAD puis GET)."""
    cache = {}
    for a in annonces:
        u = str(a.get("url_finale") or "").strip()
        if not u or not re.match(r"^https?://", u):
            continue
        if u not in cache:
            cache[u] = None
            for methode in ("HEAD", "GET"):
                try:
                    req = urllib.request.Request(u, method=methode,
                                                 headers={"User-Agent": "B2Boomers-rapport"})
                    with urllib.request.urlopen(req, timeout=timeout) as r:
                        cache[u] = r.status
                    break
                except urllib.error.HTTPError as e:
                    cache[u] = e.code
                    if e.code != 405:
                        break
                except Exception:
                    break
        if cache[u] is not None:
            a["url_statut"] = cache[u]
    return annonces


def resume(diag):
    """Une ligne par campagne, pour l'affichage console de rapport.py."""
    lignes = []
    for c in diag.get("campagnes") or []:
        lignes.append(f"  - {c['nom']} : stade {c['stade']} ({c['stade_libelle']}) — {c['raison']}")
        for a in c["alertes"]:
            lignes.append(f"      ! {a['code']} : {a['message']} -> {a['procedure']} ({PROCEDURES.get(a['procedure'], '')})")
    return "\n".join(lignes)
