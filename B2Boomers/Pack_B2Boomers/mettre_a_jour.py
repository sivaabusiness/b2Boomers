# -*- coding: utf-8 -*-
"""Mise a jour du pack B2Boomers — un double-clic et c'est tout.

Ce fichier :
  1. retrouve ton dossier du pack sur l'ordinateur (celui qui contient
     env.local.txt) ;
  2. telecharge la derniere version du pack depuis ton espace membre
     (avec TON code membre, rien d'autre) ;
  3. remplace le dossier google-ads-locale — ton env.local.txt n'est
     jamais touche ;
  4. relance le test de connexion (qui envoie tes stats a l'espace) et
     reinstalle l'envoi automatique quotidien.

Windows : double-clique ce fichier.
Mac     : ouvre le Terminal, tape  python3  (avec un espace), glisse ce
          fichier dans la fenetre, touche Entree.
"""
import io
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

URL = "https://b2boomers-espace.vercel.app/api/fichier?f=Skill_Google_Ads_Local.zip"
DOSSIER_PACK = "google-ads-locale"
PROFOND_MAX = 4
IGNORES = {"AppData", "Library", "node_modules", ".git", "Windows",
           "Program Files", "Program Files (x86)", "$Recycle.Bin",
           "Applications", "Musique", "Music", "Pictures", "Images", "Movies"}


def _rmtree_force(chemin):
    """Suppression qui force les fichiers en lecture seule (piege Windows :
    rmtree echoue en 'Acces refuse' sur un fichier read-only)."""
    import stat
    def forcer(fonction, p, _exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            fonction(p)
        except OSError:
            pass
    shutil.rmtree(chemin, onerror=forcer)


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


def pause_puis_sortir(code=0):
    try:
        input("\nAppuie sur Entree pour fermer cette fenetre…")
    except EOFError:
        pass
    sys.exit(code)


def trouver_packs():
    maison = os.path.expanduser("~")
    racines = [os.path.join(maison, d) for d in
               ("Desktop", "Bureau", "Documents", "Downloads", "Téléchargements",
                "OneDrive")] + [maison]
    vus, trouves = set(), []
    for racine in racines:
        if not os.path.isdir(racine) or racine in vus:
            continue
        vus.add(racine)
        base = racine.rstrip(os.sep).count(os.sep)
        for chemin, dossiers, fichiers in os.walk(racine):
            dossiers[:] = [d for d in dossiers
                           if d not in IGNORES and not d.startswith(".")]
            if chemin.count(os.sep) - base >= PROFOND_MAX:
                dossiers[:] = []
            if "env.local.txt" in fichiers and DOSSIER_PACK in dossiers:
                if chemin not in trouves:
                    trouves.append(chemin)
    return trouves


def lire_env(pack):
    env = {}
    try:
        with open(os.path.join(pack, "env.local.txt"), encoding="utf-8-sig") as f:
            for ligne in f:
                if "=" in ligne and not ligne.strip().startswith("#"):
                    k, v = ligne.split("=", 1)
                    env[k.strip()] = v.strip()
    except OSError:
        pass
    return env


def etat_pack(pack):
    """(pack, configure?, code, date de env.local.txt)"""
    env = lire_env(pack)
    configure = bool(env.get("GOOGLE_ADS_REFRESH_TOKEN")) and \
        "COLLE_ICI" not in env.get("GOOGLE_ADS_OAUTH_CLIENT_ID", "COLLE_ICI")
    try:
        import datetime
        quand = datetime.date.fromtimestamp(
            os.path.getmtime(os.path.join(pack, "env.local.txt"))).isoformat()
    except OSError:
        quand = "?"
    return {"chemin": pack, "configure": configure,
            "code": env.get("B2B_CODE_MEMBRE", ""), "date": quand}


def telecharger(code, pack):
    """Telecharge le zip ET sa signature ; refuse tout zip qui ne vient pas de Leo
    (verification avec la cle publique du pack deja installe, scripts/verif_maj.py).
    Vieux pack sans verif_maj.py : on verifie quand meme avec la copie embarquee ci-dessous."""
    req = urllib.request.Request(URL, headers={"Authorization": "Bearer " + code})
    with urllib.request.urlopen(req, timeout=60) as r:
        contenu = r.read()
    req = urllib.request.Request(URL + ".sig", headers={"Authorization": "Bearer " + code})
    with urllib.request.urlopen(req, timeout=30) as r:
        sig = r.read().decode("ascii")
    sys.path.insert(0, os.path.join(pack, DOSSIER_PACK, "scripts"))
    try:
        from verif_maj import verifier
    except ImportError:
        verifier = _verifier_embarque
    if not verifier(contenu, sig):
        raise RuntimeError("signature invalide : ce fichier ne vient pas de Leo, rien n'est installe")
    return contenu


# Copie de la verification (cle publique de Leo) pour les packs anterieurs a la 2.6.0.
_N = 0xc639a838e9dc0bce6cf0906849e94a729116601975d91d8c8f4074e135d7ab884ed56b6aff7039eacdf37cb8d9e03217d1bd4ad4bb483e35d006d0886846aea9553eb77dfb608785352f5bf0c801fb77c53d47d46a88145f37a75338182cd3f55be685d004beee8ccce14eb920e7261827959e442f98aa0cfe12345030909862cbbcc705c9e36f0ba915e563f420256b591877d9d27f1df2dc89a67a8ac8fd8c25f11b85a65c1f47ec968dd6788572371b5304bb7bd069f750968a925d5fd97d0afbad0c980c5e1c92708e4508b340a7a1e487b701b21ce77a63e9dd151d2cd97563b05bec63deb2b3f5e16547250df0e4b3503c0b75c15111d5f5ff0273965ebbb68b4aba9babcc3942658f8505f3080d1e6cceefc739b230591f6f825ff9ab219051e879e3fb359d835da34f7e1581bf08adc1e1b367e9834d6785b86155ebdfeef5341c5bb63423716d7d273b48efd614124fa839a1234581d69f5959687d9f9ee677173a78f96c01967b9d01b3c2ebe1e805855b3b7dd9d1b538c00742c7
_E = 65537


def _verifier_embarque(donnees, signature_b64):
    import base64
    import hashlib
    import hmac
    try:
        s = int.from_bytes(base64.b64decode(signature_b64.strip()), "big")
    except Exception:
        return False
    if _N <= 1 or s <= 0 or s >= _N:
        return False
    k = (_N.bit_length() + 7) // 8
    em = pow(s, _E, _N).to_bytes(k, "big")
    t = bytes.fromhex("3031300d060960864801650304020105000420") + hashlib.sha256(donnees).digest()
    attendu = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    return hmac.compare_digest(em, attendu)


def main():
    print("=== Mise a jour du pack B2Boomers ===\n")
    packs = [os.path.realpath(p) for p in trouver_packs()]
    packs = sorted(set(packs))
    if not packs:
        print("Je ne trouve pas ton dossier du pack (celui qui contient env.local.txt).")
        chemin = input("Colle ici son chemin complet puis Entree : ").strip().strip('"')
        if not os.path.isfile(os.path.join(chemin, "env.local.txt")):
            print("env.local.txt introuvable la non plus. Ecris a Leo sur WhatsApp.")
            pause_puis_sortir(1)
        packs = [chemin]

    etats = [etat_pack(p) for p in packs]
    configures = [e for e in etats if e["configure"]]

    if len(packs) == 1:
        pack = packs[0]
    elif len(configures) == 1:
        # un seul pack reellement branche : c'est lui, sans question
        pack = configures[0]["chemin"]
        autres = [e["chemin"] for e in etats if e["chemin"] != pack]
        print("ATTENTION : j'ai trouve d'autres copies du pack, NON configurees :")
        for a in autres:
            print(f"   - {a}")
        print("Elles ne servent a rien et sement la confusion : supprime-les")
        print("quand tu as une minute. Je mets a jour le bon :")
    else:
        # zero ou plusieurs packs configures : on fait choisir, avec les infos
        print("ATTENTION : plusieurs dossiers du pack sur cet ordinateur :")
        for i, e in enumerate(etats, 1):
            etat = "CONFIGURE (connexion Google faite)" if e["configure"] \
                else "pas configure"
            print(f"  {i}. {e['chemin']}")
            print(f"     -> {etat} · modifie le {e['date']}"
                  + (f" · code {e['code']}" if e["code"] else ""))
        print("Le bon, c'est celui dans lequel tu travailles avec Claude Code.")
        choix = input(f"Lequel mettre a jour ? (1-{len(etats)}) : ").strip()
        if not (choix.isdigit() and 1 <= int(choix) <= len(etats)):
            print("Reponse non comprise — relance et tape juste le numero.")
            pause_puis_sortir(1)
        pack = etats[int(choix) - 1]["chemin"]
        print("Pense a SUPPRIMER les autres copies apres : l'envoi automatique")
        print("ne doit viser qu'un seul dossier.")
    print(f"\nDossier du pack : {pack}")

    code = lire_env(pack).get("B2B_CODE_MEMBRE", "")
    if not code.upper().startswith("B2B-"):
        print("Ton code membre (B2B-XXXXX) manque dans env.local.txt — ajoute-le,")
        print("enregistre, puis relance ce fichier.")
        pause_puis_sortir(1)

    print("Telechargement de la derniere version et verification de sa signature…")
    try:
        contenu = telecharger(code, pack)
    except Exception as e:
        print(f"Echec du telechargement ({e}).")
        print("Verifie ta connexion internet et ton code membre, puis relance. "
              "Si le message parle de signature, ecris a Leo : n'installe rien a la main.")
        pause_puis_sortir(1)

    print("Mise a jour du dossier google-ads-locale (env.local.txt non touche)…")
    try:
        with zipfile.ZipFile(io.BytesIO(contenu)) as z:
            noms = []
            for nom in z.namelist():
                n = nom.replace("\\", "/")
                if not n.startswith(DOSSIER_PACK + "/") or n.endswith("/"):
                    continue
                if any(p in ("", ".", "..") for p in n.split("/")) or ":" in n:
                    raise RuntimeError("chemin suspect dans le zip : " + nom)
                noms.append(nom)
            installer_dossier(z, noms, pack, DOSSIER_PACK)
    except Exception as e:
        print(f"Echec de la mise a jour ({e}).")
        print("Ferme Claude Code et tout terminal ouvert dans le dossier du pack, puis relance ce fichier.")
        pause_puis_sortir(1)
    print("Pack a jour.\n")

    scripts = os.path.join(pack, DOSSIER_PACK, "scripts")
    print("--- Test de connexion (envoie tes stats a l'espace) ---")
    subprocess.run([sys.executable, os.path.join(scripts, "test_connexion.py")],
                   cwd=pack)
    print("\n--- Envoi automatique quotidien ---")
    subprocess.run([sys.executable, os.path.join(scripts, "rapport_auto.py")],
                   cwd=pack)

    print("\n=== Termine. Tu peux fermer cette fenetre. ===")
    pause_puis_sortir(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:  # jamais de fenetre qui disparait sans explication
        print(f"\nErreur inattendue : {e}\nEnvoie une capture de cette fenetre a Leo.")
        pause_puis_sortir(1)
