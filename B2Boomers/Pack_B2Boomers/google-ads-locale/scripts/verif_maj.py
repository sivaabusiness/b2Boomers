# -*- coding: utf-8 -*-
"""Vérification des mises à jour du pack — Python pur, aucune dépendance.

Chaque zip de mise à jour est signé par Léo (clé privée sur son ordinateur).
Ce fichier contient la clé PUBLIQUE : il permet de vérifier qu'un zip vient
bien de lui, jamais d'en signer un. Si le serveur était piraté, un zip
modifié serait refusé ici, avant toute extraction.

    from verif_maj import telecharger_verifie
    contenu = telecharger_verifie(code_membre)   # bytes du zip, ou MiseAJourRefusee
"""
import base64
import hashlib
import hmac
import os
import urllib.request

# Clé publique RSA-3072 de Léo (écrite par signer.py, côté Léo).
N = 0xc639a838e9dc0bce6cf0906849e94a729116601975d91d8c8f4074e135d7ab884ed56b6aff7039eacdf37cb8d9e03217d1bd4ad4bb483e35d006d0886846aea9553eb77dfb608785352f5bf0c801fb77c53d47d46a88145f37a75338182cd3f55be685d004beee8ccce14eb920e7261827959e442f98aa0cfe12345030909862cbbcc705c9e36f0ba915e563f420256b591877d9d27f1df2dc89a67a8ac8fd8c25f11b85a65c1f47ec968dd6788572371b5304bb7bd069f750968a925d5fd97d0afbad0c980c5e1c92708e4508b340a7a1e487b701b21ce77a63e9dd151d2cd97563b05bec63deb2b3f5e16547250df0e4b3503c0b75c15111d5f5ff0273965ebbb68b4aba9babcc3942658f8505f3080d1e6cceefc739b230591f6f825ff9ab219051e879e3fb359d835da34f7e1581bf08adc1e1b367e9834d6785b86155ebdfeef5341c5bb63423716d7d273b48efd614124fa839a1234581d69f5959687d9f9ee677173a78f96c01967b9d01b3c2ebe1e805855b3b7dd9d1b538c00742c7
E = 65537

_DIGEST_INFO_SHA256 = bytes.fromhex("3031300d060960864801650304020105000420")


class MiseAJourRefusee(Exception):
    pass


def verifier(donnees, signature_b64):
    """True si `donnees` est signé (RSA PKCS#1 v1.5, SHA-256) par la clé privée de Léo."""
    try:
        s = int.from_bytes(base64.b64decode(signature_b64.strip()), "big")
    except Exception:
        return False
    if N <= 1 or s <= 0 or s >= N:
        return False
    k = (N.bit_length() + 7) // 8
    em = pow(s, E, N).to_bytes(k, "big")
    t = _DIGEST_INFO_SHA256 + hashlib.sha256(donnees).digest()
    if k < len(t) + 11:
        return False
    attendu = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    return hmac.compare_digest(em, attendu)


def _get(url, code_membre, timeout=60):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + code_membre})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def telecharger_verifie(code_membre, nom="Skill_Google_Ads_Local.zip"):
    """Télécharge le zip et sa signature ; renvoie le zip seulement si la signature est bonne."""
    base = os.environ.get("B2B_URL", "https://b2boomers-espace.vercel.app")
    contenu = _get(f"{base}/api/fichier?f={nom}", code_membre)
    try:
        sig = _get(f"{base}/api/fichier?f={nom}.sig", code_membre, timeout=30).decode("ascii")
    except Exception as e:
        raise MiseAJourRefusee(f"signature absente ({e})")
    if not verifier(contenu, sig):
        raise MiseAJourRefusee("signature invalide : ce fichier ne vient pas de Leo, "
                               "rien n'a ete installe. Previens-le sur WhatsApp.")
    return contenu


def noms_surs(z, dossier="google-ads-locale"):
    """Entrées du zip autorisées à l'extraction : sous `dossier/`, sans '..' ni chemin absolu."""
    ok = []
    for nom in z.namelist():
        n = nom.replace("\\", "/")
        if not n.startswith(dossier + "/") or n.endswith("/"):
            continue
        parties = n.split("/")
        if any(p in ("", ".", "..") for p in parties) or n.startswith("/") or ":" in n:
            raise MiseAJourRefusee(f"chemin suspect dans le zip : {nom}")
        ok.append(nom)
    return ok
