# -*- coding: utf-8 -*-
"""Client REST Google Ads generique (aucune dependance externe).

Couvre : auth par refresh token, backoff 429/5xx, search GAQL, mutate
(avec validateOnly), Keyword Planner (ideas + historical metrics),
suggestion de geo target constants.

Usage :
    from google_ads_client import GoogleAdsClient
    client = GoogleAdsClient("chemin/vers/env.local.txt")
    rows = client.search("1234567890", "SELECT campaign.id FROM campaign")
    resp = client.mutate("1234567890", ops, validate_only=True)

Cles attendues dans le fichier env (format K=V, une par ligne) :
    GOOGLE_ADS_OAUTH_CLIENT_ID, GOOGLE_ADS_OAUTH_CLIENT_SECRET,
    GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID
Optionnelles (anciens montages) :
    GOOGLE_ADS_DEVELOPER_TOKEN  — supprime par Google le 2026-09-09, ignore
    GOOGLE_ADS_LOGIN_CUSTOMER_ID — seulement si compte manager (MCC)
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Verifiee active en 2026-08. Si UNSUPPORTED_VERSION : re-sonder v(N+1), v(N+2)...
API_VERSION = "v25"

LANG_FR = "languageConstants/1002"
NETWORK = "GOOGLE_SEARCH"


def load_env(path):
    env = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


class GoogleAdsClient:
    def __init__(self, env_path):
        env = load_env(env_path)
        # CGU du pack : le code membre B2Boomers est requis. L'utiliser,
        # c'est accepter la remontee des statistiques (scripts/rapport.py).
        self.code_membre = env.get("B2B_CODE_MEMBRE", "").strip()
        if not self.code_membre.upper().startswith("B2B-"):
            raise SystemExit(
                "Il manque B2B_CODE_MEMBRE dans env.local.txt (ton code membre, "
                "celui de l'espace B2Boomers, ex. B2B-XXXXX).\n"
                "Rappel des CGU : utiliser le pack = accepter la remontee de tes "
                "statistiques de campagne vers l'espace membre.")
        self.client_id = env["GOOGLE_ADS_OAUTH_CLIENT_ID"]
        self.client_secret = env["GOOGLE_ADS_OAUTH_CLIENT_SECRET"]
        self.refresh_token = env["GOOGLE_ADS_REFRESH_TOKEN"]
        self.customer_id = env.get("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")
        # Optionnels : dev token (supprime depuis 2026-09-09) et manager (MCC)
        self.dev_token = env.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")
        self.login_cid = (env.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
                          .replace("-", "") or self.customer_id)
        self._access_token = None
        self._token_ts = 0

    # ---- auth ----
    def access_token(self):
        if self._access_token and time.time() - self._token_ts < 3000:
            return self._access_token
        data = urllib.parse.urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }).encode()
        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
        with urllib.request.urlopen(req, timeout=30) as r:
            tok = json.load(r)
        self._access_token = tok["access_token"]
        self._token_ts = time.time()
        return self._access_token

    # ---- transport avec backoff ----
    def post(self, path, body, max_retries=5):
        url = f"https://googleads.googleapis.com/{API_VERSION}/{path}"
        payload = json.dumps(body).encode()
        delay = 5.0
        for attempt in range(max_retries + 1):
            headers = {
                "Authorization": f"Bearer {self.access_token()}",
                "Content-Type": "application/json",
            }
            if self.dev_token:
                headers["developer-token"] = self.dev_token
            if self.login_cid:
                headers["login-customer-id"] = self.login_cid
            req = urllib.request.Request(url, data=payload, method="POST",
                                         headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                try:
                    err = json.load(e)
                except Exception:
                    err = {"raw": e.read().decode(errors="replace")}
                text = json.dumps(err)
                retriable = e.code == 429 or "RESOURCE_EXHAUSTED" in text or e.code >= 500
                if retriable and attempt < max_retries:
                    print(f"    [backoff] HTTP {e.code}, retry dans {delay:.0f}s",
                          file=sys.stderr)
                    time.sleep(delay)
                    delay = min(delay * 2, 120)
                    continue
                raise RuntimeError(
                    f"HTTP {e.code} sur {path}: {json.dumps(err, indent=2)[:3000]}")

    # ---- lecture ----
    def search(self, customer_id, query):
        """GAQL. NB: pas de pageSize (PAGE_SIZE_NOT_SUPPORTED) ; tout champ en
        WHERE doit figurer dans le SELECT. Suit la pagination."""
        results = []
        body = {"query": query}
        while True:
            resp = self.post(f"customers/{customer_id}/googleAds:search", body)
            results.extend(resp.get("results", []))
            token = resp.get("nextPageToken")
            if not token:
                return results
            body["pageToken"] = token

    def list_accounts(self):
        """Comptes sous le manager : id, nom, devise, statut."""
        q = ("SELECT customer_client.id, customer_client.descriptive_name, "
             "customer_client.currency_code, customer_client.status, "
             "customer_client.manager, customer_client.level FROM customer_client")
        return [r["customerClient"] for r in self.search(self.login_cid, q)]

    # ---- ecriture (une transaction, ids temporaires) ----
    def mutate(self, customer_id, operations, validate_only=True,
               partial_failure=False):
        """googleAds:mutate. Laisser validate_only=True pour le dry-run ;
        l'execution reelle (--apply) doit etre lancee par l'utilisateur."""
        return self.post(f"customers/{customer_id}/googleAds:mutate", {
            "mutateOperations": operations,
            "partialFailure": partial_failure,
            "validateOnly": validate_only,
        })

    # ---- Keyword Planner ----
    def suggest_geos(self, names, country="FR", locale="fr"):
        """-> {searchTerm: {resource, name, type, canonical}} (1er FR par nom).
        Rappel : les types Postal Code sont refuses par le Keyword Planner."""
        resp = self.post("geoTargetConstants:suggest", {
            "locale": locale, "countryCode": country,
            "locationNames": {"names": names}})
        out = {}
        for s in resp.get("geoTargetConstantSuggestions", []):
            g = s.get("geoTargetConstant", {})
            term = s.get("searchTerm", "")
            if g.get("countryCode") != country or term in out:
                continue
            out[term] = {"resource": g.get("resourceName"), "name": g.get("name"),
                         "type": g.get("targetType"),
                         "canonical": g.get("canonicalName")}
        return out

    def generate_ideas(self, customer_id, geo_resources, keywords=None, url=None,
                       language=LANG_FR, max_pages=5, pause=2.0):
        body = {
            "language": language, "geoTargetConstants": geo_resources,
            "keywordPlanNetwork": NETWORK, "includeAdultKeywords": False,
            "pageSize": 1000,
        }
        if keywords and url:
            body["keywordAndUrlSeed"] = {"url": url, "keywords": keywords}
        elif keywords:
            body["keywordSeed"] = {"keywords": keywords}
        elif url:
            body["urlSeed"] = {"url": url}
        else:
            raise ValueError("keywords ou url requis")
        results, token = [], None
        for _ in range(max_pages):
            if token:
                body["pageToken"] = token
            resp = self.post(f"customers/{customer_id}:generateKeywordIdeas", body)
            results.extend(resp.get("results", []))
            token = resp.get("nextPageToken")
            if not token:
                break
            time.sleep(pause)
        return results

    def historical_metrics(self, customer_id, keywords, geo_resources,
                           language=LANG_FR, pause=2.0):
        out = []
        for i in range(0, len(keywords), 200):
            resp = self.post(
                f"customers/{customer_id}:generateKeywordHistoricalMetrics", {
                    "keywords": keywords[i:i + 200], "language": language,
                    "geoTargetConstants": geo_resources,
                    "keywordPlanNetwork": NETWORK})
            out.extend(resp.get("results", []))
            time.sleep(pause)
        return out


def micros_to_eur(v):
    return round(int(v) / 1_000_000, 2) if v not in (None, "") else None
