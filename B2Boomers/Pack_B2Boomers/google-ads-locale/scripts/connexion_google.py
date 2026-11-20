# -*- coding: utf-8 -*-
"""Connexion de ton compte Google — a lancer UNE SEULE FOIS.

Ce script ouvre ton navigateur sur la page d'autorisation Google, recupere
l'autorisation, et enregistre la cle de connexion (refresh token) dans ton
fichier env.local.txt. Aucune dependance a installer (Python standard).

Usage :
    python google-ads-locale/scripts/connexion_google.py

Il attend un fichier env.local.txt dans le dossier courant contenant deja :
    GOOGLE_ADS_OAUTH_CLIENT_ID=...
    GOOGLE_ADS_OAUTH_CLIENT_SECRET=...
"""
import json
import os
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

ENV_PATH = os.path.join(os.getcwd(), "env.local.txt")
PORT = 8765
REDIRECT = f"http://localhost:{PORT}"
SCOPE = "https://www.googleapis.com/auth/adwords"

PAGE_OK = """<html><meta charset="utf-8"><body style="font-family:sans-serif;
text-align:center;padding-top:80px"><h1 style="color:#1a7f37">Connexion reussie</h1>
<p>Tu peux fermer cet onglet et retourner dans le terminal.</p></body></html>"""
PAGE_KO = """<html><meta charset="utf-8"><body style="font-family:sans-serif;
text-align:center;padding-top:80px"><h1 style="color:#b91c1c">Echec de la connexion</h1>
<p>Retourne dans le terminal et relance le script.</p></body></html>"""


def load_env(path):
    env = {}
    if not os.path.exists(path):
        sys.exit(f"Fichier introuvable : {path}\n"
                 "Copie env.exemple.txt en env.local.txt et remplis les 2 "
                 "premieres lignes (voir le guide, partie E).")
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def save_refresh_token(path, token):
    with open(path, "r", encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    out, done = [], False
    for line in lines:
        if line.strip().startswith("GOOGLE_ADS_REFRESH_TOKEN="):
            out.append(f"GOOGLE_ADS_REFRESH_TOKEN={token}")
            done = True
        else:
            out.append(line)
    if not done:
        out.append(f"GOOGLE_ADS_REFRESH_TOKEN={token}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def main():
    env = load_env(ENV_PATH)
    client_id = env.get("GOOGLE_ADS_OAUTH_CLIENT_ID", "")
    client_secret = env.get("GOOGLE_ADS_OAUTH_CLIENT_SECRET", "")
    if not client_id or not client_secret or "COLLE_ICI" in client_id:
        sys.exit("Remplis d'abord GOOGLE_ADS_OAUTH_CLIENT_ID et "
                 "GOOGLE_ADS_OAUTH_CLIENT_SECRET dans env.local.txt "
                 "(voir le guide, partie E).")

    state = secrets.token_urlsafe(16)
    received = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            ok = "code" in q and q.get("state", [""])[0] == state
            if ok:
                received["code"] = q["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write((PAGE_OK if ok else PAGE_KO).encode())

        def log_message(self, *a):
            pass

    server = HTTPServer(("localhost", PORT), Handler)
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    })
    print("Ouverture du navigateur… Si rien ne s'ouvre, copie cette adresse :")
    print(auth_url + "\n")
    threading.Timer(1.0, webbrowser.open, [auth_url]).start()
    print("En attente de ton autorisation dans le navigateur…")
    while "code" not in received:
        server.handle_request()
    server.server_close()

    data = urllib.parse.urlencode({
        "code": received["code"],
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        tok = json.load(r)
    refresh = tok.get("refresh_token")
    if not refresh:
        sys.exit("Google n'a pas renvoye de cle de connexion. Relance le script "
                 "(l'ecran Google doit redemander l'autorisation complete).")
    save_refresh_token(ENV_PATH, refresh)
    print("\nConnexion enregistree dans env.local.txt.")
    print("Etape suivante : python google-ads-locale/scripts/test_connexion.py")


if __name__ == "__main__":
    main()
