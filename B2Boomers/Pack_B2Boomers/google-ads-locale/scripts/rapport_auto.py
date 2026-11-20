# -*- coding: utf-8 -*-
"""Installe l'envoi QUOTIDIEN automatique du rapport (12h30, tous les jours).

A lancer UNE fois depuis le dossier du pack :
    Windows :  python  google-ads-locale/scripts/rapport_auto.py
    Mac     :  python3 google-ads-locale/scripts/rapport_auto.py

Options :  --voir     montre ce qui serait installe, sans rien installer
           --retirer  desinstalle la tache

Windows : tache planifiee « B2Boomers Rapport » (Planificateur de taches).
Mac     : agent launchd com.b2boomers.rapport (~/Library/LaunchAgents).
Si l'ordinateur est eteint a 12h30, le rapport part a la prochaine occasion
(chaque envoi contient de toute facon les 14 derniers jours, jour par jour :
aucun trou dans les donnees).
"""
import os
import plistlib
import subprocess
import sys

PACK = os.getcwd()
PY = sys.executable
SCRIPT = os.path.join(PACK, "google-ads-locale", "scripts", "rapport.py")
HEURE = "12:30"

NOM_WIN = "B2Boomers Rapport"
NOM_MAC = "com.b2boomers.rapport"


def verifier():
    if not os.path.exists(SCRIPT):
        sys.exit("Lance cette commande depuis le dossier du pack "
                 "(rapport.py introuvable ici).")
    if not os.path.exists(os.path.join(PACK, "env.local.txt")):
        sys.exit("env.local.txt introuvable : termine d'abord le guide "
                 "(parties E a H), puis relance cette commande.")


def chemin_demarrage():
    return os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows",
                        "Start Menu", "Programs", "Startup",
                        "B2Boomers Rapport.vbs")


def chemin_lanceur():
    """Lanceur court (chemin < 100 caracteres) pour la tache planifiee : schtasks
    refuse une commande de plus de 261 caracteres, ce qui arrive avec un pack
    dans OneDrive + un Python dans AppData (bug vu chez un membre)."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "B2Boomers", "rapport.vbs")


def _contenu_vbs(pack, py):
    script = os.path.join(pack, "google-ads-locale", "scripts", "rapport.py")
    return ('CreateObject("WScript.Shell").Run "cmd /c cd /d ""' + pack +
            '"" && ""' + py + '"" ""' + script + '""", 0, False\r\n')


def _ecrire_si_different(chemin, contenu):
    try:
        with open(chemin, encoding="utf-8") as f:
            if f.read() == contenu:
                return
    except OSError:
        pass
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)


def assurer_demarrage(pack=None, py=None):
    """Pose (ou repose) le lanceur silencieux du dossier Demarrage : le rapport
    part a chaque allumage du PC, SANS droits administrateur (schtasks ONLOGON
    les exige — c'etait le bug 'Acces refuse'). Appele aussi par rapport.py a
    chaque envoi : auto-reparant. Pose aussi le lanceur court de la tache
    quotidienne."""
    pack = pack or PACK
    py = py or PY
    contenu = _contenu_vbs(pack, py)
    _ecrire_si_different(chemin_demarrage(), contenu)
    _ecrire_si_different(chemin_lanceur(), contenu)
    return True


def windows(voir, retirer):
    if retirer:
        subprocess.run(["schtasks", "/Delete", "/TN", NOM_WIN, "/F"])
        subprocess.run(["schtasks", "/Delete", "/TN", NOM_WIN + " (session)", "/F"])
        for c in (chemin_demarrage(), chemin_lanceur()):
            try:
                os.remove(c)
            except OSError:
                pass
        print("Taches retirees.")
        return
    # 1) lanceur du dossier Demarrage : marche toujours, aucun droit requis
    assurer_demarrage()
    # 2) tache quotidienne a HEURE, via le lanceur court (commande < 261 caracteres)
    commande = f'wscript.exe "{chemin_lanceur()}"'
    args = ["schtasks", "/Create", "/F", "/SC", "DAILY", "/ST", HEURE,
            "/TN", NOM_WIN, "/TR", commande]
    if voir:
        print("Serait installe :", " ".join(args))
        print("Serait ecrit :", chemin_demarrage(), "et", chemin_lanceur())
        return
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        # pas bloquant : l'envoi a chaque allumage du PC est deja en place
        print("Envoi a chaque allumage du PC : installe.")
        print("Tache quotidienne 12h30 : pas installee (" + (r.stderr or r.stdout).strip() + ")")
        print("Ce n'est pas grave : le rapport part a chaque demarrage de l'ordinateur.")
        return
    print(f"Installe : rapport envoye chaque jour a {HEURE} ET a chaque "
          "allumage du PC. Aucun droit special requis.")


def mac(voir, retirer):
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{NOM_MAC}.plist")
    if retirer:
        subprocess.run(["launchctl", "unload", plist_path])
        if os.path.exists(plist_path):
            os.remove(plist_path)
        print("Agent quotidien retire.")
        return
    h, m = (int(x) for x in HEURE.split(":"))
    contenu = {
        "Label": NOM_MAC,
        "ProgramArguments": [PY, SCRIPT],
        "WorkingDirectory": PACK,
        "StartCalendarInterval": {"Hour": h, "Minute": m},
        # Mac eteint a l'heure dite : l'envoi part aussi a l'ouverture de
        # session (le serveur garde un rapport par jour, pas de doublon).
        "RunAtLoad": True,
    }
    if voir:
        print("Serait ecrit dans", plist_path, ":", contenu)
        return
    os.makedirs(os.path.dirname(plist_path), exist_ok=True)
    with open(plist_path, "wb") as f:
        plistlib.dump(contenu, f)
    subprocess.run(["launchctl", "unload", plist_path], capture_output=True)
    r = subprocess.run(["launchctl", "load", plist_path], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"Installe : rapport envoye chaque jour a {HEURE} (agent launchd).")
    else:
        sys.exit("Echec du chargement launchd : " + (r.stderr or r.stdout))


def main():
    voir = "--voir" in sys.argv
    retirer = "--retirer" in sys.argv
    if not retirer:
        verifier()
    if os.name == "nt":
        windows(voir, retirer)
    elif sys.platform == "darwin":
        mac(voir, retirer)
    else:
        sys.exit("Systeme non reconnu (Windows ou Mac attendu).")


if __name__ == "__main__":
    main()
