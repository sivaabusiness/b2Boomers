# Génère les pages du site Allô Paysagiste Artois (prompt A du guide B2Boomers).
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services_seo import PAGES
BASE = "https://allopaysagisteartois.fr"

OUT = sys.argv[1]

NOM = "Allô Paysagiste Artois"
TEL_AFF = "07 56 95 13 25"
TEL_LIEN = "+33756951325"
VILLES = "Lens, Béthune, Arras"

SERVICES = [
    dict(slug="amenagement-jardin", nom="Aménagement de jardin", bouton="Aménagement, plantations",
         court="Aménagement", benefice="le jardin qui vous ressemble",
         intro="Création complète ou nouveau coin de jardin : on dessine, on prépare le sol, on plante.",
         cas=["Création de jardin complète : plan, terrassement, apport de terre, plantations",
              "Massifs et haies : charmille, photinia, laurier, troène, hêtre",
              "Engazonnement : semis ou gazon en rouleau, sol préparé et nivelé",
              "Arrosage automatique enterré, programmé selon les saisons",
              "Bassin, point d'eau et éclairage du jardin"],
         question="Votre projet ?",
         reponses=[("jardin", "Créer ou refaire tout le jardin"), ("haie", "Plantations, massifs, haie"),
                   ("gazon", "Gazon, pelouse"), ("eau", "Arrosage ou bassin")],
         exemple="ex. jardin de 300 m² derrière la maison, pelouse et haie à créer, idéalement au printemps…",
         avant="terrain nu et boueux, aucune plantation", apres="jardin créé : pelouse, massifs, haie plantée"),
    dict(slug="terrasse-allee", nom="Terrasse et allées", bouton="Terrasse, allée, muret",
         court="Terrasse", benefice="du solide, fait pour durer",
         intro="Terrasse, allée, cour ou muret : des fondations sérieuses et des finitions nettes.",
         cas=["Terrasse en bois ou en composite, sur plots ou lambourdes",
              "Terrasse en dallage, carrelage extérieur ou pierre naturelle",
              "Allée, cour, entrée de garage : pavés, enrobé, gravier stabilisé",
              "Bordures, marches et raccords avec la maison",
              "Murets, enrochement, soutènement de talus"],
         question="Quel chantier ?",
         reponses=[("terrasse", "Terrasse bois ou composite"), ("dalles", "Terrasse dallage ou pierre"),
                   ("allee", "Allée, cour, entrée de garage"), ("muret", "Muret, enrochement, talus")],
         exemple="ex. terrasse d'environ 25 m² le long de la maison, accès par le côté, pour cet été…",
         avant="coin de jardin en terre et herbe abîmée", apres="terrasse en dalles posée, propre et de niveau"),
    dict(slug="entretien-jardin", focus="center 8%", nom="Entretien de jardin", bouton="Entretien, taille de haies",
         court="Entretien", benefice="un jardin net toute l'année",
         intro="Taille, tonte, remise en état : ponctuel ou à l'année, votre jardin reste impeccable.",
         cas=["Taille de haies et d'arbustes, déchets ramassés",
              "Tonte et entretien régulier, à la saison ou à l'année",
              "Remise en état d'un jardin laissé à l'abandon",
              "Débroussaillage, désherbage des allées et massifs",
              "Ramassage des feuilles et évacuation des déchets verts"],
         question="Quel entretien ?",
         reponses=[("taille", "Taille de haies"), ("tonte", "Tonte, entretien régulier"),
                   ("remise", "Remise en état d'un jardin négligé"), ("debroussaillage", "Débroussaillage, évacuation")],
         urgent=("Urgent : jardin à sécuriser", "haie ou clôture tombée, jardin à sécuriser"),
         exemple="ex. haie de thuyas d'environ 20 m, 2 m de haut, à tailler avant l'hiver, puis entretien à l'année…",
         avant="haie débordante et pelouse trop haute", apres="haie taillée au cordeau, pelouse tondue"),
    dict(slug="cloture-portail", nom="Clôture et portail", bouton="Clôture, portail",
         court="Clôture", benefice="chez vous, à l'abri des regards",
         intro="Panneaux, bois, brise-vue ou portail : une clôture droite, solide, bien ancrée.",
         cas=["Clôture en panneaux rigides ou grillage, poteaux scellés",
              "Clôture bois ou composite, brise-vue occultant",
              "Portail et portillon, pose des piliers",
              "Remplacement d'une clôture abîmée par le vent",
              "Clôture doublée d'une haie, pour un jardin à l'abri des regards"],
         question="Votre besoin ?",
         reponses=[("cloture", "Clôture neuve"), ("portail", "Portail ou portillon"),
                   ("reparation", "Remplacer une clôture abîmée")],
         urgent=("Urgent : dégâts, tempête", "clôture ou portail abîmé (tempête, dégâts)"),
         autre="Plusieurs travaux / je ne sais pas",
         exemple="ex. environ 30 m de clôture côté voisin, ancien grillage à enlever, assez pressé…",
         avant="vieux grillage affaissé et rouillé", apres="clôture neuve en panneaux, droite et propre"),
]

COMMUNES = ["Lens", "Béthune", "Arras", "Liévin", "Hénin-Beaumont", "Bruay-la-Buissière", "Carvin", "Avion",
            "Bully-les-Mines", "Harnes", "Nœux-les-Mines", "Lillers", "Beuvry", "Méricourt", "Achicourt",
            "Beaurains", "Saint-Laurent-Blangy", "Vimy"]

def FOC(s):
    return f' style="object-position:{s["focus"]}"' if s.get('focus') else ''

TEL_IC = '<svg class="i-tel" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>'

def tel(cls="", txt=None):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="tel:{TEL_LIEN}">{txt or TEL_AFF}</a>'

FONTS = ''
FONT_FACE = ("@font-face{font-family:'Inter';font-style:normal;font-weight:400 700;font-display:swap;src:url(/fonts/inter-latin.woff2) format('woff2')}"
             "@font-face{font-family:'Bricolage Grotesque';font-style:normal;font-weight:700 800;font-display:swap;src:url(/fonts/bricolage-grotesque-latin.woff2) format('woff2')}")

LOGO = '<img class="logo" src="photos/logo.webp" alt="" width="44" height="44">'

def ic(path):
    return ('<span class="ico" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" '
            f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{path}</svg></span>')

ICONES = {
    "rappel": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "gratuit": '<path d="M4 7h16v13H4z"/><path d="M8 7V4h8v3"/><path d="M9 13l2 2 4-4"/>',
    "assure": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "propre": '<path d="M4 20h16"/><path d="M7 20l3-12h4l3 12"/><path d="M12 4v4"/>',
    "distance": '<path d="M3 12h18"/><path d="M6 9l-3 3 3 3"/><path d="M18 9l3 3-3 3"/><path d="M12 4v4M12 16v4"/>',
    "autorisation": '<path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="M10 13l2 2 4-4"/>',
    "securite": '<path d="M12 2l9 18H3z"/><path d="M12 9v5M12 17v.5"/>',
}

# Icônes au trait des choix (masques SVG, couleur = var(--sauge))
ICONES_CHOIX = {
    'jardin': '<path d="M2 11l5-4.5 5 4.5"/><path d="M3.5 10v10h7V10"/><path d="M6 20v-4h2v4"/><path d="M2 20.5h20"/><circle cx="17.5" cy="9" r="3.5"/><path d="M17.5 12.5v8"/><path d="M13 20.5v-3M22 20.5v-3M13 18h9"/>',
    'haie': '<path d="M12 21v-9"/><circle cx="12" cy="7" r="2"/><path d="M12 5V3.5M14 7h1.5M12 9v.5M10 7H8.5M13.5 5.5l1-1M13.5 8.5l1 1M10.5 8.5l-1 1M10.5 5.5l-1-1"/><path d="M12 17c0-2.5 2-4 5-4 0 2.5-2 4-5 4z"/><path d="M12 15c0-2-1.6-3.5-4.5-3.5 0 2 1.6 3.5 4.5 3.5z"/><path d="M5 21h14"/>',
    'gazon': '<path d="M2 20h20"/><path d="M4 20l1.5-7L7 20"/><path d="M9 20l1.5-10L12 20"/><path d="M14 20l1.5-8L17 20"/><path d="M18.5 20l1-5 1 5"/>',
    'eau': '<path d="M3 10h11v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M14 13l5-5"/><path d="M6 10V7.5A2.5 2.5 0 0 1 8.5 5h0A2.5 2.5 0 0 1 11 7.5V10"/><path d="M21 4v1.5"/><path d="M18 3v1.5"/><path d="M21.5 8.5h.01"/>',
    'terrasse': '<rect x="3" y="4" width="18" height="16" rx="1.5"/><path d="M3 8h18M3 12h18M3 16h18"/><path d="M9 4v4M15 8v4M7 12v4M14 16v4"/>',
    'dalles': '<rect x="3" y="3.5" width="18" height="17" rx="2"/><path d="M3 11h7l3-2.5"/><path d="M13 8.5V3.5"/><path d="M10 11l1.5 9.5"/><path d="M11.8 14.5H21"/>',
    'allee': '<path d="M3 9l9-5.5L21 9"/><path d="M5 8v8"/><path d="M19 8v8"/><path d="M8 16v-5.5h8V16"/><path d="M8 13.2h8"/><rect x="2.5" y="18" width="19" height="3.5" rx=".5"/><path d="M7 18v3.5M12 18v3.5M17 18v3.5"/>',
    'muret': '<path d="M2 8.5h8"/><path d="M2 8.5c0 4 4 6 8 6"/><rect x="10" y="6" width="7" height="15" rx=".5"/><path d="M10 11h7M10 16h7M13.5 6v5M13.5 16v5"/><path d="M17 21h5"/><path d="M5 8.5V5"/><path d="M5 6c0-1.7 1.3-2.5 3-2.5 0 1.7-1.3 2.5-3 2.5z"/>',
    'taille': '<circle cx="6" cy="7" r="3"/><circle cx="6" cy="17" r="3"/><path d="M8.5 8.5L20 19"/><path d="M8.5 15.5L20 5"/>',
    'tonte': '<path d="M3 16h13l1.5-4H4.5z"/><path d="M16.5 12L20 4"/><path d="M18.5 4H21.5"/><circle cx="6.5" cy="18.5" r="2"/><circle cx="14" cy="18.5" r="2"/>',
    'remise': '<path d="M2 20h20"/><path d="M3 20L2 13"/><path d="M5 20l1-9"/><path d="M7.5 20L5.5 14"/><path d="M10 14.5h4"/><path d="M12.5 12.5l2 2-2 2"/><path d="M16.5 20v-2.5M19 20v-2.5M21.5 20v-2.5"/>',
    'debroussaillage': '<path d="M2.5 9h14l-3 6.5H6z"/><path d="M16.5 9l4.5-2.5"/><circle cx="10" cy="18.5" r="2"/><path d="M6 15.5L5 20"/><path d="M7 9L5.5 5"/><path d="M11 9l.5-5"/><path d="M14 9l2-3"/>',
    'cloture': '<path d="M2 11h20"/><path d="M2 17h20"/><path d="M4 21V7l1.5-2L7 7v14"/><path d="M10.5 21V7L12 5l1.5 2v14"/><path d="M17 21V7l1.5-2L20 7v14"/>',
    'portail': '<path d="M3 21V5"/><path d="M21 21V5"/><path d="M1.5 5h3"/><path d="M19.5 5h3"/><path d="M3 10c6-3.5 12-3.5 18 0"/><path d="M3 19h18"/><path d="M7.5 8.6V19"/><path d="M12 7.5V19"/><path d="M16.5 8.6V19"/>',
    'reparation': '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L4 17l3 3 5.3-5.3a4 4 0 0 0 5.4-5.4l-2.3 2.3-2.4-.6-.6-2.4z"/>',
    'urgent': '<path d="M12 3l10 18H2z"/><path d="M12 10v5"/><path d="M12 18v.5"/>',
    'autre': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5v.7"/><path d="M12 17.5v.5"/>',
}
def _ic_url(d):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + d + '</svg>'
    return svg.replace('"', '%22').replace('<', '%3C').replace('>', '%3E').replace('#', '%23')
ICCSS = "".join(f'[data-ic="{k}"]{{--ic:url("data:image/svg+xml,{_ic_url(d)}")}}' for k, d in ICONES_CHOIX.items())
CSS_BASE = FONT_FACE + """

.prog{height:6px;border-radius:6px;background:#E7E2D6;overflow:hidden;margin:0 0 12px}
.prog i{display:block;height:100%;width:50%;border-radius:6px;background:linear-gradient(90deg,var(--sauge),var(--brique))}
[data-etape="2"] .prog i{width:100%}
.local{margin:-2px 0 12px;font-size:15px;color:var(--gris)}
.resume{display:flex;flex-wrap:wrap;align-items:center;gap:4px 12px;background:#F2F6F1;border:1.5px solid #CFE0D2;border-radius:14px;padding:12px 14px;margin:0 0 6px;font-family:Inter,sans-serif!important;font-size:17px!important;letter-spacing:0!important}
.resume-lab{flex-basis:100%;font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--sauge)}
.resume b{flex:1;min-width:0;color:var(--sauge-n)}
.resume [data-retour]{flex:none;padding:7px 14px;border-radius:10px;border:1.5px solid var(--sauge);background:#fff;color:var(--sauge-n);font:600 15px Inter,sans-serif;text-decoration:none;cursor:pointer;transition:background .3s ease,color .3s ease}
.resume [data-retour]:hover{background:var(--sauge);color:#fff}
.form-ok::after{content:"La suite\\A 1. On vous rappelle pour préciser votre projet.\\A 2. On fixe la visite, au jour qui vous arrange.\\A 3. Vous recevez un devis écrit et gratuit, et vous décidez.";display:block;white-space:pre-line;margin-top:18px;padding-top:14px;border-top:1px solid #CFE0D2;font-size:15.5px;line-height:1.7;color:var(--sauge-f)}

.btn{transition:background .3s ease,transform .3s cubic-bezier(.22,.61,.36,1),box-shadow .3s ease}
@media(hover:hover){.btn:hover{transform:translateY(-1px);box-shadow:0 10px 22px -12px rgba(135,59,37,.7)}}
.btn:active{transform:scale(.98)}
.i-tel{flex:none}
.choix a,.choix button{min-width:0;hyphens:manual;-webkit-hyphens:manual;overflow-wrap:break-word}
.choix a,.choix button{transition:border-color .35s cubic-bezier(.22,.61,.36,1),box-shadow .35s cubic-bezier(.22,.61,.36,1),transform .35s cubic-bezier(.22,.61,.36,1),background .35s ease}
@media(hover:hover){.choix a:hover,.choix button:hover{transform:translateY(-2px);border-color:var(--sauge);background:#FBFAF6}}
.choix a:active,.choix button:active{transform:scale(.98);border-color:var(--brique);box-shadow:0 0 0 2px var(--brique)}
.choix a:focus-visible,.choix button:focus-visible,.btn:focus-visible{outline:3px solid var(--brique);outline-offset:2px}
.choix button.urgent{border-color:#E3B9A8;background:#FBF1EC;color:#6E2E1B}
.choix button.urgent::before{background:var(--brique)}
input[name=tel]:not(:placeholder-shown):valid{border-color:#3F8F55;padding-right:46px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233F8F55' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 13l4 4L19 7'/%3E%3C/svg%3E") right 14px center/20px no-repeat}
input[name=tel]:not(:placeholder-shown):not(:focus):invalid{border-color:#C0392B;padding-right:46px;background:#FDF2F0 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23C0392B' stroke-width='3' stroke-linecap='round'%3E%3Cpath d='M6 6l12 12M18 6L6 18'/%3E%3C/svg%3E") no-repeat right 14px center/20px;box-shadow:0 0 0 3px rgba(192,57,43,.12)}
.aide-tel{display:none;font-size:14px;font-weight:600;color:#B3261E;margin-top:6px;line-height:1.4}
input[name=tel]:not(:placeholder-shown):not(:focus):invalid + .aide-tel{display:block}
.form-ok{background:#EEF5EF;color:var(--sauge-n);border:1.5px solid #BFD8C5;border-radius:16px;padding:24px 22px;font-size:17px;line-height:1.6;box-shadow:0 14px 34px -22px rgba(34,42,36,.45);animation:okv .35s ease both}
.form-ok b:first-child{display:block;font-family:"Bricolage Grotesque",Inter,sans-serif;font-size:23px;letter-spacing:-.02em;line-height:1.2;margin-bottom:2px}
.form-ok b:first-child + br,.form-ok b:first-child + br + br{display:none}
.form-ok a{display:inline-flex;align-items:center;min-height:50px;margin-top:6px;padding:0 20px;border-radius:12px;background:var(--brique);color:#fff;text-decoration:none;font-weight:700}
@keyframes okv{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
:root{interpolate-size:allow-keywords}
details::details-content{block-size:0;overflow:hidden;transition:block-size .3s ease,content-visibility .3s allow-discrete}
details[open]::details-content{block-size:auto}
summary::after{transition:transform .25s}
details[open] summary::after{transform:rotate(180deg)}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
:root{--creme:#F4EFE6;--sable:#E9E1D1;--sauge:#4A5D4F;--sauge-f:#2F3B33;--sauge-n:#222A24;--brique:#A04A30;--brique-f:#873B25;--brique-c:#F3E2D8;--texte:#2B2B2B;--gris:#5F5F58;--filet:#DDD5C5;--blanc:#fff;--ombre:0 18px 50px -18px rgba(34,42,36,.28);--r:18px}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--creme);color:var(--texte);font:400 17px/1.6 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
img{max-width:100%;height:auto;display:block}
a{color:inherit}
h1,h2,h3{font-family:"Bricolage Grotesque",Inter,sans-serif;font-weight:800;letter-spacing:-.03em;line-height:1.05;margin:0}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:56px;padding:0 26px;border-radius:12px;background:var(--brique);color:#fff;font-weight:700;font-size:17px;text-decoration:none;border:0;cursor:pointer;font-family:inherit;transition:background .15s}
.btn:hover{background:var(--brique-f)}
.btn-2{background:var(--sauge)}.btn-2:hover{background:var(--sauge-f)}
.btn-blanc{background:#fff;color:var(--sauge-n)}.btn-blanc:hover{background:var(--creme)}
.confiance{display:grid;gap:6px;margin-top:16px;font-size:15px;color:var(--gris)}
.confiance div{padding-left:26px;position:relative}
.confiance div::before{content:"✓";position:absolute;left:0;top:0;color:var(--sauge);font-weight:800}
.choix{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.choix a,.choix button{display:flex;align-items:center;gap:10px;min-height:60px;padding:8px 12px;border:1.5px solid var(--filet);border-radius:12px;background:#fff;color:var(--texte);font:600 16px/1.25 Inter,sans-serif;text-decoration:none;text-align:left;cursor:pointer;transition:border-color .15s,box-shadow .15s}
.choix a:hover,.choix button:hover{border-color:var(--sauge);box-shadow:0 6px 18px -10px rgba(34,42,36,.4)}
.choix img{width:46px;height:46px;border-radius:9px;object-fit:cover;flex:none}
.choix .tuile.choisie{border-color:var(--brique);box-shadow:0 0 0 2px var(--brique)}
[data-ic]::before{content:"";flex:none;width:26px;height:26px;background:var(--sauge);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}
"""+ICCSS+"""
.question{font-family:"Bricolage Grotesque",Inter,sans-serif;font-weight:800;font-size:24px;letter-spacing:-.02em;margin:0 0 14px}
@media(max-width:480px){
 .choix a:has(img){flex-direction:column;align-items:stretch;padding:0;overflow:hidden;gap:0}
 .choix a:has(img) img{width:100%;height:74px;border-radius:0}
 .choix a:has(img) span{padding:9px 10px;font-size:15px}
}
"""

CSS_ACCUEIL = """
.pc{}

.mo{display:none}
.carte-s,.sv-var article,.regle{transition:transform .5s cubic-bezier(.22,.61,.36,1),box-shadow .5s cubic-bezier(.22,.61,.36,1)}
.carte-s .img img,.sv-var img{transition:transform .8s cubic-bezier(.22,.61,.36,1)}
@media(hover:hover){.carte-s:hover .img img,.sv-var article:hover .ph img{transform:scale(1.04)}}
@media(hover:hover){.carte-s:hover,.sv-var article:hover,.regle:hover{transform:translateY(-4px);box-shadow:0 28px 60px -24px rgba(34,42,36,.4)}}
.final-act{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}
.final .btn-blanc{font-size:18px;min-height:62px}
.pres .visu .carte{background:rgba(255,255,255,.7);-webkit-backdrop-filter:blur(12px) saturate(1.4);backdrop-filter:blur(12px) saturate(1.4);border:1px solid rgba(255,255,255,.6)}
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){.pres .visu .carte{background:#fff}}
.saison{display:none}
header.top{position:sticky;top:0;z-index:50;background:rgba(244,239,230,.92);backdrop-filter:blur(8px);border-bottom:1px solid rgba(0,0,0,.06)}
header.top .wrap{display:flex;align-items:center;gap:28px;min-height:76px}
.marque{display:flex;align-items:center;gap:10px;font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:21px;letter-spacing:-.02em;text-decoration:none;color:var(--sauge-n)}
.logo{width:44px;height:44px;border-radius:50%;flex:none;background:#F6F3E9}
nav.ancres{display:flex;gap:22px;margin-left:auto;font-size:15px;font-weight:500}
nav.ancres a{text-decoration:none;color:var(--gris)}nav.ancres a:hover{color:var(--texte)}
.h-tel{display:flex;flex-direction:column;line-height:1.2;font-size:13px;color:var(--gris)}
.h-tel a{font-weight:700;font-size:17px;color:var(--sauge-n);text-decoration:none}
header.top .btn{min-height:48px;padding:0 20px;font-size:16px}
/* HERO */
.hero{position:relative;background:var(--sauge-f) url("photos/action-amenagement-jardin.webp") center/cover no-repeat;color:#fff}
.hero::before{content:"";position:absolute;inset:0;background:linear-gradient(100deg,rgba(34,42,36,.92) 0%,rgba(34,42,36,.72) 45%,rgba(34,42,36,.25) 100%)}
.hero .wrap{position:relative;display:grid;grid-template-columns:1.12fr .88fr;gap:56px;align-items:center;min-height:640px;padding-top:60px;padding-bottom:60px}
.hero h1{font-size:clamp(40px,5.6vw,68px)}
.hero h1 [data-titre-travaux]{color:#F2B9A2}
.hero .phrase{font-size:21px;font-weight:600;margin:22px 0 8px;max-width:560px}
.hero .sous{color:rgba(255,255,255,.82);margin:0 0 26px;max-width:520px}
.hero .btn-blanc{font-size:18px;min-height:58px}
.puces{display:flex;flex-wrap:wrap;gap:10px 26px;margin:30px 0 0;padding:22px 0 0;border-top:1px solid rgba(255,255,255,.22);list-style:none;font-size:15px;color:rgba(255,255,255,.88)}
.puces li::before{content:"✓ ";color:#F2B9A2;font-weight:800}
.form-card{background:#fff;color:var(--texte);border-radius:20px;padding:28px;box-shadow:0 30px 70px -25px rgba(0,0,0,.55)}
.form-card h2{font-size:26px;margin-bottom:6px;color:var(--sauge-n)}
.form-card .question{font-size:19px;color:var(--gris);font-family:Inter,sans-serif;font-weight:600;letter-spacing:0;margin-bottom:12px}
.choix .tuile:last-child{grid-column:1/-1;justify-content:center;min-height:52px}
@media(min-width:821px){.hero[style*="action-entretien-jardin"]{background-position:center 10%}}
/* SECTIONS */
section.s{padding:100px 0}
.kicker{display:flex;align-items:center;gap:10px;text-transform:uppercase;letter-spacing:.14em;font-size:13px;font-weight:700;color:var(--sauge);margin:0 0 14px}
.kicker::before{content:"";width:26px;height:2px;background:var(--brique)}
.sombre .kicker{color:#C9D6CB}
h2.t{font-size:clamp(30px,3.9vw,48px);color:var(--sauge-n);max-width:760px}
.sombre h2.t{color:#fff}
.intro{color:var(--gris);font-size:18px;max-width:640px;margin:16px 0 0}
.sombre .intro{color:rgba(255,255,255,.75)}
.sable{background:var(--sable)}
.sombre{background:var(--sauge-n);color:#fff}
.remonte{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:14px 22px;margin-top:46px;text-align:center;font-weight:600}
/* AVANT APRES */
.aa{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:44px}
.paire{background:#fff;border-radius:var(--r);padding:12px;box-shadow:var(--ombre);margin:0}
.paire .photos{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.paire .ph{position:relative}
.paire img{aspect-ratio:1/1;object-fit:cover;border-radius:12px;width:100%;background:var(--sable)}
.badge{position:absolute;top:10px;left:10px;padding:6px 12px;border-radius:8px;font-weight:800;font-size:14px;letter-spacing:.08em;color:#fff}
.badge.av{background:#B5583A}.badge.ap{background:var(--sauge)}
.paire figcaption{padding:14px 6px 6px;font-size:16px;color:var(--gris)}
.paire figcaption b{color:var(--texte)}
/* ENGAGEMENTS */
.eng{display:grid;grid-template-columns:repeat(4,1fr);margin-top:50px;border-top:1px solid rgba(255,255,255,.14)}
.eng div{padding:30px 26px 6px;border-left:1px solid rgba(255,255,255,.14)}
.eng div:first-child{border-left:0;padding-left:0}
.ico{width:46px;height:46px;border-radius:12px;display:grid;place-items:center;background:rgba(255,255,255,.08);color:#F2B9A2;margin-bottom:18px}
.eng h3{font-size:21px;letter-spacing:-.02em}
.eng p{color:rgba(255,255,255,.72);margin:10px 0 0;font-size:16px}
/* PRESENTATION */
.pres{display:grid;grid-template-columns:1.05fr .95fr;gap:70px;align-items:center}
.pres .visu{position:relative;padding-bottom:70px}
.pres .visu .grande{border-radius:var(--r);box-shadow:var(--ombre);aspect-ratio:4/3;object-fit:cover;width:100%}
.pres .visu .petite{position:absolute;right:-18px;bottom:0;width:46%;border-radius:16px;border:6px solid var(--creme);box-shadow:var(--ombre);aspect-ratio:4/3;object-fit:cover}
.pres .visu .carte{position:absolute;left:22px;bottom:30px;background:#fff;border-radius:14px;padding:14px 18px;box-shadow:var(--ombre);font-weight:700;display:flex;gap:10px;align-items:center;font-size:15px}
.pres .visu .carte::before{content:"✓";width:28px;height:28px;border-radius:50%;background:var(--sauge);color:#fff;display:grid;place-items:center;font-size:14px}
.pres p{margin:0 0 16px}
.garanties{display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;margin:26px 0 0;padding:24px 0 0;border-top:1px solid var(--filet);list-style:none;font-weight:600;font-size:16px}
.garanties li{padding-left:26px;position:relative}
.garanties li::before{content:"✓";position:absolute;left:0;color:var(--brique);font-weight:800}
/* PRESTATIONS */
.presta{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:50px}
.carte-s{background:#fff;border-radius:20px;overflow:hidden;box-shadow:var(--ombre);display:flex;flex-direction:column;position:relative;cursor:pointer}
.carte-s .lien-plus::after{content:"";position:absolute;inset:0;z-index:1}
.carte-s .btn{position:relative;z-index:2}
.carte-s:hover .lien-plus{text-decoration:underline}
.carte-s .img{position:relative;overflow:hidden;isolation:isolate}
.carte-s .img img,.sv-var .ph img{display:block;backface-visibility:hidden}
.sv-var .ph{overflow:hidden;isolation:isolate}
.carte-s .img img{aspect-ratio:16/10;object-fit:cover;object-position:center 40%;width:100%;background:var(--sauge)}
.carte-s .img .leg{position:absolute;inset:auto 0 0 0;padding:70px 26px 22px;background:linear-gradient(to top,rgba(34,42,36,.92),rgba(34,42,36,0));color:#fff}
.carte-s h3{font-size:27px}
.carte-s .leg p{margin:8px 0 0;color:rgba(255,255,255,.88);font-size:16px}
.carte-s ul{list-style:none;margin:0;padding:10px 26px 0}
.carte-s li{padding:12px 0 12px 22px;border-bottom:1px solid var(--filet);position:relative;font-size:16px}
.carte-s li::before{content:"";position:absolute;left:2px;top:20px;width:7px;height:7px;border-radius:50%;background:var(--brique)}
.carte-s .btn{margin:22px 26px 10px;align-self:flex-start}
.lien-plus{margin:0 26px 24px;font-weight:600;font-size:15px;color:var(--sauge)}
.detail{margin-top:44px;background:#fff;border-radius:var(--r);padding:26px 28px;box-shadow:var(--ombre)}
.detail h3{font-size:22px;color:var(--sauge-n);letter-spacing:-.02em;margin-bottom:14px}
.detail ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:8px 24px}
.detail a{display:block;padding:10px 0;border-bottom:1px solid var(--filet);font-weight:600;text-decoration:none;color:var(--texte)}
.detail a::after{content:' →';color:var(--brique)}
/* BANDE PHOTO */
.bande{position:relative;min-height:440px;display:flex;align-items:flex-end;background:var(--sauge-f);color:#fff;overflow:hidden}
.fond{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bande::before,.final::before{z-index:1}
.bande .wrap,.final .wrap{z-index:2}
.bande::before{content:"";position:absolute;inset:0;background:linear-gradient(to bottom,rgba(34,42,36,.1) 20%,rgba(34,42,36,.88))}
.bande .wrap{position:relative;padding-bottom:64px;width:100%}
.bande p.gros{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;letter-spacing:-.035em;line-height:1.02;font-size:clamp(36px,5.4vw,70px);margin:0;max-width:900px}
.bande p.gros em{font-style:normal;color:#F2B9A2}
.bande p.ctx{margin:16px 0 0;color:rgba(255,255,255,.8);font-size:18px}
/* RAPPEL EXPRESS */
.express{background:#fff;padding:42px 0;border-bottom:1px solid var(--filet)}
.express .wrap{display:flex;align-items:center;gap:40px}
.express h2{font-size:30px;color:var(--sauge-n)}
.express .txt p{margin:6px 0 0;color:var(--gris)}
.rappel-express{display:flex;gap:12px;align-items:flex-end;margin-left:auto;flex:1;max-width:640px}
.rappel-express .champ{flex:1}
label{display:block;font-weight:600;font-size:16px;margin:0 0 6px}
input,textarea{width:100%;min-height:54px;border:1.5px solid var(--filet);border-radius:12px;padding:12px 14px;font:400 17px Inter,sans-serif;color:var(--texte);background:#fff}
input:focus,textarea:focus{outline:none;border-color:var(--sauge);box-shadow:0 0 0 3px rgba(74,93,79,.18)}
.rappel-express button{min-height:56px;padding:0 24px;border-radius:12px;border:0;background:var(--brique);color:#fff;font:700 17px Inter,sans-serif;cursor:pointer;white-space:nowrap}
/* URGENCE */
.urgence{background:var(--brique-c);padding:70px 0}
.urgence .wrap{display:grid;grid-template-columns:1.3fr .7fr;gap:40px;align-items:center}
.urgence h2{font-size:clamp(28px,3.4vw,42px);color:#6E2E1B}
.urgence p{margin:14px 0 0;font-size:18px}
.urgence .act{display:flex;flex-direction:column;gap:12px;align-items:flex-start}
.urgence .act .btn{font-size:19px;min-height:62px}
.urgence .act a.lien{color:#6E2E1B;font-weight:600}
/* METHODE */
.methode{display:grid;grid-template-columns:.9fr 1.1fr;gap:70px;align-items:center}
.methode .photo img{border-radius:var(--r);box-shadow:var(--ombre);aspect-ratio:4/5;object-fit:cover;width:100%}
.etapes{list-style:none;margin:34px 0 0;padding:0}
.etapes li{display:grid;grid-template-columns:76px 1fr;gap:10px;padding:22px 0;border-top:1px solid var(--filet)}
.etapes .n{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:40px;color:var(--brique);line-height:1}
.etapes h3{font-size:22px;letter-spacing:-.02em}
.etapes p{margin:6px 0 0;color:var(--gris);font-size:16px}
/* REGLEMENTATION */
.regles{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:46px}
.regle{background:#fff;border-radius:var(--r);padding:30px;box-shadow:var(--ombre)}
.regle .ico{background:var(--creme);color:var(--sauge)}
.regle h3{font-size:21px;letter-spacing:-.02em;color:var(--sauge-n)}
.regle p{margin:10px 0 0;color:var(--gris);font-size:16px}
/* ZONE */
.zone{background:var(--sauge);color:#fff}
.zone .grille{display:grid;grid-template-columns:1.5fr 1fr;gap:50px;margin-top:46px;align-items:start}
.communes{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);column-gap:28px}
.communes li{padding:13px 0;border-bottom:1px solid rgba(255,255,255,.2);font-weight:600}
.zone .encart{background:#fff;color:var(--texte);border-radius:var(--r);padding:30px;box-shadow:0 30px 60px -30px rgba(0,0,0,.5)}
.zone .encart h3{font-size:24px;color:var(--sauge-n)}
.zone .encart p{color:var(--gris);margin:10px 0 20px}
/* FAQ */
.faq{display:grid;grid-template-columns:.8fr 1.2fr;gap:70px}
.faq .gauche .btn{margin-top:28px}
details{border-bottom:1px solid var(--filet)}
details:first-child{border-top:1px solid var(--filet)}
summary{list-style:none;cursor:pointer;padding:20px 40px 20px 0;font-weight:700;font-size:18px;position:relative}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";position:absolute;right:4px;top:14px;font-size:28px;font-weight:400;color:var(--brique)}
details[open] summary::after{content:"–"}
details p{margin:0 0 20px;color:var(--gris)}
/* CTA FINAL */
.final{position:relative;background:var(--sauge-f);color:#fff;text-align:center;padding:130px 0;overflow:hidden}
.final::before{content:"";position:absolute;inset:0;background:rgba(34,42,36,.74)}
.final .wrap{position:relative}
.final h2{font-size:clamp(34px,4.6vw,58px);max-width:820px;margin:0 auto}
.final p{font-size:19px;color:rgba(255,255,255,.85);margin:18px 0 32px}
.final .btn{font-size:19px;min-height:62px;padding:0 34px}
.final .ou{display:block;margin-top:20px;font-size:18px}
.final .ou a{font-weight:700;color:#fff}
/* FOOTER */
footer.pied{background:var(--sauge-n);color:rgba(255,255,255,.75);padding:70px 0 30px;font-size:15px}
.cols{display:grid;grid-template-columns:1.3fr 1fr 1fr 1fr;gap:40px}
.cols h4{color:#fff;font-size:15px;margin:0 0 14px;text-transform:uppercase;letter-spacing:.1em}
.cols ul{list-style:none;margin:0;padding:0}.cols li{margin:0 0 8px}
.cols a{text-decoration:none}.cols a:hover{color:#fff}
footer.pied .marque{color:#fff;margin-bottom:12px}
footer.pied .tel a{color:#fff;font-weight:700;font-size:19px;text-decoration:none}
.bas{margin-top:46px;padding-top:22px;border-top:1px solid rgba(255,255,255,.12);display:flex;flex-wrap:wrap;gap:10px 24px;justify-content:space-between;font-size:14px}
.bas a{text-decoration:none}
.barre{display:none}
/* TELEPHONE */
@media(max-width:1000px){nav.ancres{display:none}}
@media(max-width:820px){
 .pc{display:none!important}
 body{font-size:16.5px}
 section.s{padding:40px 0}
 .wrap{padding:0 16px}
 header.top{position:static;background:var(--creme)}
 header.top .wrap{min-height:58px}
 header.top .btn,.h-tel{display:none}
 .marque{font-size:19px}
 .logo{width:38px;height:38px}
 .hero{background-size:100% auto;background-position:top center}
 .hero::before{background:linear-gradient(to bottom,rgba(34,42,36,0) 0,rgba(34,42,36,.2) 80px,rgba(34,42,36,.88) 160px,var(--sauge-f) 215px)}
 .hero .wrap{grid-template-columns:1fr;min-height:0;gap:22px;padding-top:128px;padding-bottom:30px}
 .hero h1{font-size:31px}
 .hero .phrase{font-size:18px;margin:12px 0 16px}
 .hero .btn-blanc{width:100%;min-height:58px}
 .form-card{padding:16px;border-radius:16px}
 .form-card h2{display:none}
 .form-card .question{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:22px;color:var(--texte);letter-spacing:-.02em}
 .form-card .confiance{font-size:14px}
 .intro{font-size:16.5px}
 .mo{display:inline}
 p.mo{display:block;margin:4px 0 0;font-size:15px;color:var(--gris)}
 .final-act .btn{width:100%}
 .pied-presta{margin:18px 0 6px}
 .pied-presta ul{columns:2;column-gap:16px}
 .pied-presta li{break-inside:avoid}
 h2.t{font-size:30px}
 .aa{grid-template-columns:1fr;gap:16px;margin-top:24px}
 .badge{font-size:12px;padding:4px 8px;top:7px;left:7px}
 .paire{padding:8px}.paire figcaption{padding:10px 4px 2px;font-size:15px}
 .remonte{margin-top:26px}.remonte .btn{width:100%}
 .eng{grid-template-columns:1fr 1fr;margin-top:26px;border-top:0;gap:12px}
 .eng div,.eng div:first-child{padding:18px;border:1px solid rgba(255,255,255,.14);border-radius:14px}
 .eng h3{font-size:17px}.ico{margin-bottom:10px;width:40px;height:40px}
 .pres,.methode,.faq,.zone .grille,.urgence .wrap{grid-template-columns:1fr;gap:26px}
 .pres .visu{padding-bottom:0}
 .pres .visu .grande{aspect-ratio:3/2}
 .pres .visu .carte{left:12px;bottom:12px;font-size:14px}
 .garanties{grid-template-columns:1fr}
 .presta{grid-template-columns:1fr;gap:18px;margin-top:24px}
 .carte-s .img img{aspect-ratio:2/1}
 .carte-s .img .leg{padding:50px 18px 14px}
 .carte-s h3{font-size:22px}.carte-s .leg p{font-size:15px}
 .carte-s .btn{margin:16px 18px 18px;align-self:stretch}
 .bande{min-height:260px}.bande .wrap{padding-bottom:34px}.bande p.gros{font-size:34px}.bande p.ctx{font-size:16px}
 .express{padding:34px 0}.express .wrap{flex-direction:column;align-items:stretch;gap:18px}.express h2{font-size:26px}
 .rappel-express{flex-direction:column;align-items:stretch;max-width:none;margin-left:0;width:100%}
 .urgence{padding:40px 0}.urgence .act .btn{width:100%}
 .methode .photo img{aspect-ratio:2/1}
 .etapes{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:22px}
 .etapes li{grid-template-columns:1fr;padding:16px;border:1px solid var(--filet);border-radius:14px;gap:6px;background:#fff}
 .etapes .n{font-size:28px}.etapes h3{font-size:17px}
 .regles{grid-template-columns:1fr;gap:12px;margin-top:24px}
 .regle{padding:14px 16px;display:flex;gap:14px;align-items:center}.regle .ico{margin:0;flex:none}.regle h3{font-size:18px}
 .communes{grid-template-columns:1fr 1fr}
 .final{padding:56px 0}.final .btn{width:100%}
 .cols{grid-template-columns:1fr;gap:0}
 footer.pied{padding:40px 0 100px}
 section.s{padding:32px 0}
 .kicker{margin-bottom:8px}
 .intro{margin-top:10px}
 .aa{gap:12px;margin-top:18px}
 .remonte{margin-top:18px;gap:10px}
 .eng{margin-top:18px}.eng div,.eng div:first-child{padding:14px}
 .presta{gap:14px;margin-top:18px}
 .carte-s .img .leg{padding:40px 16px 10px}
 .carte-s .btn{margin:12px 16px 6px;min-height:52px}
 .lien-plus{margin:0 16px 14px}
 .detail{margin-top:20px;padding:18px}
 .detail ul{grid-template-columns:1fr}
 .bande{min-height:220px}.bande .wrap{padding-bottom:26px}.bande p.gros{font-size:30px}
 .express{padding:26px 0}.express .wrap{gap:12px}.express .txt p{margin-top:2px}
 .rappel-express{gap:10px}
 .urgence{padding:30px 0}.urgence .wrap{gap:16px}
 .methode{gap:18px}.methode .photo img{aspect-ratio:5/2}
 .etapes{margin-top:16px}.etapes li{padding:12px}
 .regles{margin-top:16px;gap:10px}
 .zone .grille{margin-top:18px;gap:18px}.communes li{padding:10px 0}
 .zone .encart{padding:18px}.zone .encart p{margin:6px 0 12px}
 .faq{gap:16px}.faq .gauche .btn{margin-top:14px}
 summary{padding:14px 36px 14px 0;font-size:17px}summary::after{top:8px}
 .final{padding:44px 0}.final p{margin:10px 0 20px}
 footer.pied{padding:30px 0 96px}.bas{margin-top:24px}
 .pres{gap:18px}
 .hero .wrap{padding-top:176px}
 .hero::before{background:linear-gradient(to bottom,rgba(34,42,36,0) 0,rgba(34,42,36,0) 120px,rgba(34,42,36,.75) 205px,var(--sauge-f) 265px)}
 .choix img{object-position:center 45%}
 .carte-s .img img{object-position:center 40%}
 .carte-s .img .leg{position:static;background:none;color:var(--texte);padding:14px 16px 0}
 .carte-s h3{color:var(--sauge-n);font-size:21px}
 .carte-s .leg p{color:var(--gris);margin-top:6px}
 .pres .visu .grande{aspect-ratio:4/3;object-position:center 45%}
 .methode .photo img{aspect-ratio:4/3;object-position:center 22%}
 .paire img{object-position:center}
 .barre{display:block;position:fixed;left:0;right:0;bottom:0;z-index:60;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:rgba(244,239,230,.7);-webkit-backdrop-filter:blur(14px) saturate(1.3);backdrop-filter:blur(14px) saturate(1.3);border-top:1px solid rgba(255,255,255,.55);box-shadow:0 -6px 20px rgba(0,0,0,.08)}
 @supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){.barre{background:rgba(244,239,230,.96)}}
 .barre .btn{width:100%}
}
"""

CSS_TUNNEL = """
.entete{background:var(--sauge-n);color:#fff}
.entete .wrap{display:flex;align-items:center;min-height:52px;position:relative;font-size:15px;white-space:nowrap}
.entete a{color:#fff;text-decoration:none;font-weight:600;position:relative;z-index:1}
.entete .nom{position:absolute;left:0;right:0;text-align:center;font-family:"Bricolage Grotesque",sans-serif;font-weight:800;letter-spacing:-.01em}
.bandeau{position:relative;height:255px;background:var(--sauge-f) center/cover no-repeat;color:#fff;display:flex;align-items:flex-end}
.bandeau::before{content:"";position:absolute;inset:0;background:linear-gradient(to bottom,rgba(34,42,36,.05) 20%,rgba(34,42,36,.9))}
.bandeau .wrap{position:relative;width:100%;padding-bottom:62px}
.bandeau h1{font-size:clamp(27px,4vw,44px);max-width:760px}
.bandeau p{margin:8px 0 0;font-weight:600;color:rgba(255,255,255,.9)}
main.t{max-width:720px;margin:-44px auto 0;padding:0 16px;position:relative}
.carte-form{background:#fff;border-radius:20px;padding:26px;box-shadow:0 26px 60px -24px rgba(34,42,36,.4)}
.pas{margin:0 0 6px;font-size:14px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--brique)}
.choix button:last-child:nth-child(odd),.choix > :last-child:nth-child(odd){grid-column:1/-1}
label{display:block;font-weight:600;font-size:17px;margin:16px 0 6px}
label small{font-weight:400;color:var(--gris)}
input,textarea{width:100%;min-height:54px;border:1.5px solid var(--filet);border-radius:12px;padding:12px 14px;font:400 17px Inter,sans-serif;color:var(--texte);background:#fff}
textarea{min-height:96px;resize:vertical}
input:focus,textarea:focus{outline:none;border-color:var(--sauge);box-shadow:0 0 0 3px rgba(74,93,79,.18)}
form button[type=submit]{width:100%;min-height:58px;margin-top:20px;border:0;border-radius:12px;background:var(--brique);color:#fff;font:700 18px Inter,sans-serif;cursor:pointer}
form button[type=submit]:hover{background:var(--brique-f)}
[data-retour]{background:none;border:0;padding:0;color:var(--sauge);text-decoration:underline;font:inherit;cursor:pointer}
[data-etape="2"] .question{font-size:18px;font-family:Inter,sans-serif;font-weight:500;letter-spacing:0}
.paire{background:#fff;border-radius:var(--r);padding:10px;box-shadow:var(--ombre);margin:26px 0 0}
.paire .photos{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.paire .ph{position:relative}
.paire img{aspect-ratio:1/1;object-fit:cover;border-radius:12px;width:100%;background:var(--sable)}
.badge{position:absolute;top:8px;left:8px;padding:5px 10px;border-radius:8px;font-weight:800;font-size:13px;letter-spacing:.08em;color:#fff}
.badge.av{background:#B5583A}.badge.ap{background:var(--sauge)}
.paire figcaption{padding:10px 4px 2px;font-size:15px;color:var(--gris)}.paire figcaption b{color:var(--texte)}
.mini{text-align:center;font-size:14px;color:var(--gris);padding:30px 16px 40px}
.mini a{color:var(--gris)}
@media(max-width:600px){.carte-form{padding:18px}.bandeau h1{font-size:26px}.entete .nom{font-size:14px}}
"""

CONFIANCE = """  <div class="confiance">
    <div>Gratuit et sans engagement</div>
    <div>Un seul appel, le nôtre, jamais de démarchage</div>
    <div>Vos coordonnées ne sont jamais revendues</div>
  </div>"""

def head(title, desc, preload, noindex=False, css="", canon=None, ld=None):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>if(/iP(hone|ad|od)/.test(navigator.userAgent))document.querySelector('meta[name=viewport]').content+=',maximum-scale=1'</script>
<title>{title}</title>
<meta name="description" content="{desc}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<script src="/api/suivi" defer></script>
{f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ''}
{f'<link rel="canonical" href="{canon}">' if canon else ''}
{'<meta name="google-site-verification" content="P5RxZg88_1tas69ONUdvt3Xgm-PLqyDkRmdZM7QwzhM">' if canon == BASE + "/" else ''}
{OG(title, desc, canon) if canon else ''}
{('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>') if ld else ''}
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<style>{CSS_BASE}{css}</style>
</head>
"""

def OG(title, desc, url):
    return (f'<meta property="og:type" content="website">\n<meta property="og:locale" content="fr_FR">\n'
            f'<meta property="og:site_name" content="{NOM}">\n<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{BASE}/og-image.jpg">\n<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">')

VILLES_LD = ["Lens", "Béthune", "Arras", "Liévin", "Hénin-Beaumont", "Bruay-la-Buissière", "Carvin", "Avion"]
ENTREPRISE_LD = {"@type": "HomeAndConstructionBusiness", "@id": BASE + "/#entreprise", "name": "Allô Paysagiste Artois",
                 "url": BASE + "/", "telephone": "+33756951325", "logo": BASE + "/photos/logo.webp", "image": BASE + "/og-image.jpg",
                 "priceRange": "Devis gratuit",
                 "areaServed": [{"@type": "City", "name": v} for v in VILLES_LD]}
PAGE_DE = {"amenagement-jardin": "creation-jardin", "terrasse-allee": "terrasses",
           "entretien-jardin": "entretien-jardin", "cloture-portail": "clotures-portails"}

def liens_detail():
    return "".join(f'<li><a href="{q["slug"]}.html">{q["nom"]}</a></li>' for q in PAGES)

def paire(s, lazy=True, cls=""):
    ld = ' loading="lazy"' if lazy else ""
    c = f' class="paire {cls}"' if cls else ' class="paire"'
    return f"""<figure{c}>
  <div class="photos">
    <div class="ph"><img src="photos/avant-{s['slug']}.webp" alt="Avant : {s['avant']}" width="600" height="600"{ld}><span class="badge av">AVANT</span></div>
    <div class="ph"><img src="photos/apres-{s['slug']}.webp" alt="Après : {s['apres']}" width="600" height="600"{ld}><span class="badge ap">APRÈS</span></div>
  </div>
  <figcaption><b>{s['nom']}</b><span class="pc"> : {s['apres']}.</span></figcaption>
</figure>"""

# ---------------------------------------------------------------- ACCUEIL
def accueil():
    tuiles = "\n".join(
        f'    <a class="tuile" href="devis-{s["slug"]}.html" data-travaux="{s["slug"]}" data-nom="{s["nom"]}">'
        f'<img src="photos/action-{s["slug"]}.webp" alt="" width="46" height="46"{FOC(s)}><span>{s["bouton"]}</span></a>'
        for s in SERVICES)
    paires = "\n".join(paire(s, cls="pc" if i == 3 else "") for i, s in enumerate(SERVICES))
    cartes = "\n".join(f"""<article class="carte-s">
  <div class="img"><img src="photos/action-{s['slug']}.webp" alt="{s['nom']} en cours, près de Lens" width="1600" height="1000" loading="lazy"{FOC(s)}>
    <div class="leg"><h3>{s['nom']}</h3><p>{s['intro']}</p></div></div>
  <ul class="pc">{''.join(f'<li>{c}</li>' for c in s['cas'])}</ul>
  <a class="btn" href="devis-{s['slug']}.html">Devis {s['court'].lower()} →</a>
  <a class="lien-plus" href="{PAGE_DE[s['slug']]}.html">En savoir plus sur {s['nom'].lower()}</a>
</article>""" for s in SERVICES)
    communes = "".join(f'<li{" class=\"pc\"" if i >= 8 else ""}>{c}</li>' for i, c in enumerate(COMMUNES))
    faq = [
        ("Vais-je être harcelé de coups de fil ?",
         "Non. Vous recevez un seul appel : celui de la personne qui fera votre devis. Vos coordonnées ne sont jamais revendues ni partagées."),
        ("Le devis est-il vraiment gratuit ?",
         "Oui. Le déplacement et le devis sont gratuits et sans engagement. Vous recevez un devis écrit et détaillé, et vous décidez tranquillement."),
        ("Sous quel délai pouvez-vous intervenir ?",
         "On vous rappelle sous 24 h pour fixer la visite, que vous soyez à Lens, Béthune, Arras ou Liévin. La date des travaux dépend de la saison et de l'ampleur du chantier : elle est fixée avec vous et écrite sur le devis."),
        ("Que deviennent les déchets verts et la terre ?",
         "On les évacue. Branches, tontes, souches, terre en trop : tout est ramassé et le chantier est rendu propre. C'est précisé sur le devis."),
        ("Faut-il une autorisation pour une clôture ou une terrasse ?",
         "Ça dépend de votre commune. Une clôture, un mur ou une terrasse surélevée peuvent demander une déclaration préalable en mairie. On regarde avec vous ce que prévoit votre commune avant les travaux."),
        ("Quelle est la meilleure période ?",
         "Les plantations se font idéalement de l'automne au début du printemps, hors gel. Le gazon se sème au printemps ou en début d'automne. Terrasses, allées et clôtures se font presque toute l'année, hors grosses pluies et gel."),
        ("Mon jardin est difficile d'accès, c'est possible ?",
         "Le plus souvent, oui : passage étroit, jardin à l'arrière, pas d'accès camion… On regarde tout ça lors de la visite et on adapte le matériel."),
        ("Qui réalise les travaux ?",
         "Des professionnels du métier, du secteur, assurés. La même équipe vous rappelle, passe voir votre jardin, fait le devis et réalise les travaux."),
    ]
    faq_html = "\n".join(f"<details name=\"faq\"><summary>{q}</summary><p>{r}</p></details>" for q, r in faq)
    prest_footer = liens_detail()

    return head("Paysagiste Lens, Béthune, Arras | Allô Paysagiste Artois",
                "Paysagiste à Lens, Béthune, Arras : aménagement, terrasse, entretien, clôture. On vous rappelle sous 24 h, devis et déplacement gratuits.",
                "photos/action-amenagement-jardin.webp", css=CSS_ACCUEIL, canon=BASE + "/",
                ld={"@context": "https://schema.org", "@graph": [dict(ENTREPRISE_LD, description="Création, aménagement et entretien de jardins, terrasses, allées et clôtures à Lens, Béthune, Arras et alentours. Devis et déplacement gratuits."),
                    {"@type": "WebSite", "name": NOM, "url": BASE + "/"}]}) + f"""<body>

<header class="top">
  <div class="wrap">
    <a class="marque" href="index.html">{LOGO}{NOM}</a>
    <nav class="ancres" aria-label="Sections"><a href="#avant-apres">Avant / après</a><a href="#prestations">Prestations</a><a href="#zone">Zone</a><a href="#faq">FAQ</a></nav>
    <div class="h-tel">Appelez-nous{tel()}</div>
    <a class="btn" href="devis.html">Devis gratuit</a>
  </div>
</header>

<main>
<section class="hero" data-photo-travaux>
  <div class="wrap">
    <div>
      <h1><span data-titre-travaux>Paysagiste</span> à {VILLES} et alentours</h1>
      <p class="phrase">On vous rappelle : devis et déplacement gratuits sous 24 h.</p>
      <p class="sous pc">Décrivez vos travaux en deux clics. Sans engagement, et sans démarchage derrière.</p>
      {tel("btn btn-blanc", TEL_IC + "Appeler le " + TEL_AFF)}
      <ul class="puces pc"><li>Professionnels assurés</li><li>Devis écrit avant travaux</li><li>Chantier rendu propre</li></ul>
    </div>
<div class="form-card" id="devis-bloc" data-cacher-barre>
  <h2>Recevez votre devis gratuit</h2>
  <p class="question">Quels travaux ?</p>
  <div class="choix">
{tuiles}
    <a class="tuile" href="devis.html">Autre / je ne sais pas</a>
  </div>
{CONFIANCE}
</div>
  </div>
</section>

<section class="s" id="avant-apres">
  <div class="wrap">
    <p class="kicker">La preuve en images</p>
    <h2 class="t">Avant, après : la différence se voit tout de suite</h2>
    <p class="intro"><span class="pc">Un aperçu de ce qu'on fait dans les jardins du secteur : création, terrasse, entretien, clôture.</span><span class="mo">Création, terrasse, entretien, clôture : le résultat en images.</span></p>
    <div class="aa">
{paires}
    </div>
    <div class="remonte"><span>Votre jardin pourrait être le prochain.</span><a class="btn" href="devis.html">Recevoir mon devis gratuit →</a></div>
  </div>
</section>

<section class="s sombre">
  <div class="wrap">
    <p class="kicker">Nos engagements</p>
    <h2 class="t">Votre jardin entre de bonnes mains</h2>
    <div class="eng">
      <div>{ic(ICONES['rappel'])}<h3>Rappel sous 24 h</h3><p class="pc">Vous laissez votre demande, on vous rappelle dans la journée, au plus tard le lendemain.</p></div>
      <div>{ic(ICONES['gratuit'])}<h3>Devis et déplacement gratuits</h3><p class="pc">On vient voir le terrain, on mesure, on vous conseille. Sans engagement.</p></div>
      <div>{ic(ICONES['assure'])}<h3>Assurés et équipés</h3><p class="pc">Mini-pelle, plaque vibrante, taille-haie, broyeur : le bon outil pour chaque chantier.</p></div>
      <div>{ic(ICONES['propre'])}<h3>Chantier rendu propre</h3><p class="pc">Déchets verts et gravats évacués, allées balayées. Vous retrouvez un jardin net.</p></div>
    </div>
  </div>
</section>

<section class="s">
  <div class="wrap pres">
    <div class="visu">
      <img class="grande" src="photos/equipe.webp" alt="L'équipe de paysagistes devant son camion" width="1600" height="1200" loading="lazy">
      <img class="petite pc" src="photos/chantier-propre.webp" alt="Chantier de jardin nettoyé en fin de journée" width="800" height="600" loading="lazy">
      <div class="carte">Professionnels assurés</div>
    </div>
    <div>
      <p class="kicker">Travail d'artisan</p>
      <h2 class="t">Un jardin bien pensé, posé dans les règles</h2>
      <p class="intro"><span class="pc">Avant de planter ou de poser quoi que ce soit, on regarde votre terrain : la terre, l'eau, le soleil, l'usage que vous voulez en faire.</span><span class="mo">On étudie votre terrain avant de planter ou de poser quoi que ce soit.</span></p>
      <div class="pc" style="margin-top:18px">
        <p>Dans le Pas-de-Calais, les sols sont souvent lourds et gorgés d'eau l'hiver. On prépare donc le terrain en conséquence : décaissement, drainage si besoin, apport de terre végétale, fondations stables pour les terrasses et les allées.</p>
        <p>Pour les haies et les massifs, on choisit des végétaux qui tiennent dans la région : charmille, hêtre, photinia, laurier, troène, arbustes à fleurs. Et on vous explique comment les entretenir.</p>
        <p>À la fin, le chantier est nettoyé : déchets verts, terre en trop et gravats sont évacués.</p>
      </div>
      <ul class="garanties pc">
        <li>Devis écrit et détaillé</li><li>Déplacement gratuit</li>
        <li>Végétaux adaptés à votre sol</li><li>Matériel adapté à chaque chantier</li>
        <li>Déchets verts évacués</li><li>Chantier rendu propre</li>
      </ul>
    </div>
  </div>
</section>

<section class="s sable" id="prestations">
  <div class="wrap">
    <p class="kicker">Nos prestations</p>
    <h2 class="t">De la création à l'entretien, tout votre extérieur</h2>
    <p class="intro"><span class="pc">Quatre métiers, une seule équipe à Lens, Béthune, Arras et alentours : un seul interlocuteur, du premier appel à la fin du chantier.</span><span class="mo">Quatre métiers, une seule équipe, un seul interlocuteur.</span></p>
    <div class="presta">
{cartes}
    </div>
    <div class="detail"><h3>Toutes nos prestations en détail</h3><ul>{liens_detail()}</ul></div>
  </div>
</section>

<section class="bande" aria-label="Notre façon de travailler">
  <img class="fond" src="photos/materiel.webp" alt="" width="1600" height="1000" loading="lazy">
  <div class="wrap">
    <p class="gros">Un jardin bien fait, ça se voit <em>des années</em> après.</p>
    <p class="ctx">Fondations, drainage, finitions : on ne bâcle aucune étape, même celles qu'on ne voit plus.</p>
  </div>
</section>

<section class="express" aria-label="Rappel express">
  <div class="wrap">
    <div class="txt"><h2>Pas le temps d'écrire ?</h2><p>Laissez votre numéro : on vous rappelle, gratuitement.</p></div>
<form class="rappel-express" data-moteur="rappel" data-service="Paysagiste" novalidate>
  <div class="champ"><label for="r-nom">Votre prénom</label>
    <input id="r-nom" type="text" name="nom" autocomplete="given-name" required></div>
  <div class="champ"><label for="r-tel">Votre téléphone</label>
    <input id="r-tel" type="tel" name="tel" inputmode="tel" autocomplete="tel"
      placeholder="06 12 34 56 78" pattern="[\\s.\\-\\(\\)]*(?:\\+[1-9](?:[\\s.\\-\\(\\)]*[0-9]){{7,14}}|0[\\s.\\-\\(\\)]*[1-9](?:[\\s.\\-\\(\\)]*[0-9]){{8}})[\\s.\\-\\(\\)]*" required><small class="aide-tel">Il manque des chiffres : 10 chiffres, par exemple 06 12 34 56 78</small></div>
  <input type="text" name="site_web" tabindex="-1" autocomplete="off"
    style="position:absolute;left:-6000px">
  <button type="submit">Être rappelé →</button>
</form>
  </div>
</section>

<section class="urgence">
  <div class="wrap">
    <div>
      <h2>Clôture couchée par le vent, arbre tombé dans le jardin ?</h2>
      <p>Appelez-nous, ou commencez votre message par URGENT : on vous rappelle en priorité.</p>
    </div>
    <div class="act">
      {tel("btn", TEL_IC + "Appeler maintenant")}
      <a class="lien" href="devis.html">ou décrire la situation par écrit →</a>
    </div>
  </div>
</section>

<section class="s">
  <div class="wrap methode">
    <div class="photo"><img src="photos/conseil-client.webp" alt="Le paysagiste conseille un propriétaire dans son jardin" width="1200" height="1500" loading="lazy"></div>
    <div>
      <p class="kicker">Notre méthode</p>
      <h2 class="t">Quatre étapes, sans surprise</h2>
      <p class="intro"><span class="pc">Vous savez à chaque moment ce qui va se passer, et combien ça coûte.</span><span class="mo">À chaque étape, vous savez ce qui se passe et ce que ça coûte.</span></p>
      <ol class="etapes">
        <li><span class="n">01</span><div><h3>Vous décrivez votre projet</h3><p class="pc">Deux clics sur le site, ou un appel. Quelques lignes suffisent.</p></div></li>
        <li><span class="n">02</span><div><h3>On vous rappelle sous 24 h</h3><p class="pc">On pose les bonnes questions et on fixe une visite chez vous.</p></div></li>
        <li><span class="n">03</span><div><h3>Devis écrit avant travaux</h3><p class="pc">Un devis détaillé, poste par poste. Vous prenez le temps de décider.</p></div></li>
        <li><span class="n">04</span><div><h3>Travaux soignés, chantier propre</h3><p class="pc">On réalise le chantier comme prévu, puis on nettoie tout avant de partir.</p></div></li>
      </ol>
    </div>
  </div>
</section>

<section class="s sable">
  <div class="wrap">
    <p class="kicker">On vous guide</p>
    <h2 class="t">Les règles à connaître, on s'en occupe</h2>
    <p class="intro"><span class="pc">Planter, clôturer, construire une terrasse : quelques règles s'appliquent. On vous les explique avant de commencer.</span><span class="mo">Haie, clôture, terrasse : on vérifie les règles avant de commencer.</span></p>
    <div class="regles">
      <div class="regle">{ic(ICONES['distance'])}<div><h3>Distances de plantation</h3><p class="pc">Une haie de plus de 2 m de haut se plante à 2 m au moins de la limite du voisin, sinon à 50 cm (Code civil). On en tient compte dès le plan.</p><p class="mo">On plante à la bonne distance du voisin.</p></div></div>
      <div class="regle">{ic(ICONES['autorisation'])}<div><h3>Autorisations en mairie</h3><p class="pc">Clôture, mur, terrasse surélevée : selon votre commune, une déclaration préalable peut être demandée. On vérifie avec vous.</p><p class="mo">On vérifie ce que demande votre commune.</p></div></div>
      <div class="regle">{ic(ICONES['securite'])}<div><h3>Sécurité du chantier</h3><p class="pc">Réseaux enterrés repérés avant de creuser, zone de travail balisée, matériel rangé chaque soir.</p><p class="mo">Réseaux repérés, chantier balisé.</p></div></div>
    </div>
    <div class="remonte"><span>Une question sur votre projet ?</span><a class="btn" href="devis.html">Recevoir mon devis gratuit →</a></div>
  </div>
</section>

<section class="s zone sombre" id="zone">
  <div class="wrap">
    <p class="kicker">Zone d'intervention</p>
    <h2 class="t">Lens, Béthune, Arras et tout l'Artois</h2>
    <p class="intro"><span class="pc">On intervient dans le bassin de Lens, autour de Béthune et dans l'Arrageois.</span><span class="mo">Bassin de Lens, Béthunois et Arrageois.</span></p>
    <div class="grille">
      <ul class="communes">{communes}</ul>
      <div class="encart">
        <h3>Votre commune n'y est pas ?</h3>
        <p>Si vous êtes entre Béthune, Lens et Arras, ou à moins de 20 km de l'une d'elles, c'est dans la zone.</p>
        <a class="btn" href="devis.html">Recevoir mon devis gratuit</a>
      </div>
    </div>
  </div>
</section>

<section class="s" id="faq">
  <div class="wrap faq">
    <div class="gauche">
      <p class="kicker">Questions fréquentes</p>
      <h2 class="t">Vos questions, nos réponses</h2>
      <p class="intro"><span class="pc">Une autre question ? Le plus simple, c'est d'en parler de vive voix.</span><span class="mo">Une autre question ? Parlons-en de vive voix.</span></p>
      <a class="btn btn-2" href="devis.html">Être rappelé gratuitement</a>
    </div>
    <div>
{faq_html}
    </div>
  </div>
</section>

<section class="final">
  <img class="fond" src="photos/equipe.webp" alt="" width="1600" height="1000" loading="lazy">
  <div class="wrap">
    <h2>Un devis clair, un chantier propre, un seul interlocuteur</h2>
    <p>Devis et déplacement gratuits, sans engagement. On vous rappelle sous 24 h.</p>
    <div class="final-act"><a class="btn" href="devis.html">Recevoir mon devis gratuit</a>{tel("btn btn-blanc", TEL_IC + "Appeler le " + TEL_AFF)}</div>
  </div>
</section>
</main>

<footer class="pied">
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="marque" href="index.html">{LOGO}{NOM}</a>
        <p class="pc">Création, aménagement et entretien de jardins à Lens, Béthune, Arras et alentours.</p>
        <p class="tel">{tel()}</p>
      </div>
      <div class="pied-presta"><h4>Prestations</h4><ul>{prest_footer}</ul></div>
      <div class="pc"><h4>Zone</h4><ul><li>Lens, Liévin, Hénin-Beaumont</li><li>Béthune, Bruay-la-Buissière</li><li>Arras, Achicourt, Beaurains</li><li>Carvin, Avion, Lillers</li></ul></div>
      <div><h4>Informations</h4><ul><li class="pc"><a href="devis.html">Devis gratuit</a></li><li><a href="mentions-legales.html">Mentions légales</a></li><li><a href="confidentialite.html">Confidentialité</a></li></ul></div>
    </div>
    <div class="bas"><span>Travaux réalisés par des professionnels assurés. Photos d'illustration.</span><span>© {NOM}</span></div>
  </div>
</footer>

<div class="barre" data-barre><a class="btn" href="devis.html">Devis gratuit →</a></div>
</body>
</html>
"""

# ---------------------------------------------------------------- TUNNEL
def entete():
    return f"""<header class="entete"><div class="wrap"><a href="index.html">← Retour</a><span class="nom">{NOM}</span></div></header>"""

def mini():
    return """<footer class="mini">Travaux réalisés par des professionnels assurés. Photos d'illustration.<br>
<a href="mentions-legales.html">Mentions légales</a> · <a href="confidentialite.html">Confidentialité</a></footer>"""

def etape2(exemple, visible=False, choisi=""):
    return f"""  <div data-etape="2"{"" if visible else " hidden"}>
    <div class="prog" aria-hidden="true"><i></i></div>
    <p class="pas">Étape 2 sur 2 · c'est presque fini</p>
    <p class="question resume"><span class="resume-lab">Votre projet</span> <b data-choisi>{choisi}</b>
      <button type="button" data-retour>Modifier</button></p>
    <input type="hidden" name="service" value="{choisi}">
    <label for="f-nom">Votre nom</label>
    <input id="f-nom" type="text" name="nom" autocomplete="name" required>
    <label for="f-tel">Votre téléphone</label>
    <input id="f-tel" type="tel" name="tel" inputmode="tel" autocomplete="tel"
      placeholder="06 12 34 56 78" pattern="[\\s.\\-\\(\\)]*(?:\\+[1-9](?:[\\s.\\-\\(\\)]*[0-9]){{7,14}}|0[\\s.\\-\\(\\)]*[1-9](?:[\\s.\\-\\(\\)]*[0-9]){{8}})[\\s.\\-\\(\\)]*" required>
    <small class="aide-tel">Il manque des chiffres : 10 chiffres, par exemple 06 12 34 56 78</small>
    <label for="f-commune">Votre commune</label>
    <input id="f-commune" type="text" name="commune" placeholder="ex. Liévin, Béthune, Arras…" required>
    <label for="f-desc">Un mot sur le chantier et vos délais <small>(facultatif)</small></label>
    <textarea id="f-desc" name="description"
      placeholder="{exemple}"></textarea>
    <input type="text" name="site_web" tabindex="-1" autocomplete="off"
      style="position:absolute;left:-6000px">
    <button type="submit">Recevoir mon devis gratuit</button>
  </div>"""

def tunnel(s):
    photo = f"photos/action-{s['slug']}.webp"
    rep = "\n".join(f'      <button type="button" data-service="{s["nom"]} — {r}" data-ic="{i}">{r}</button>' for i, r in s["reponses"])
    if s.get("urgent"):
        rep += f'\n      <button type="button" class="urgent" data-service="URGENT — {s["nom"]} — {s["urgent"][1]}" data-ic="urgent">{s["urgent"][0]}</button>'
    return head(f"{s['nom']} en Artois : devis gratuit sous 24 h | {NOM}",
                f"{s['nom']} à {VILLES} : décrivez votre projet en 2 étapes, on vous rappelle sous 24 h. Devis et déplacement gratuits.",
                photo, noindex=True, css=CSS_TUNNEL) + f"""<body>
{entete()}
<div class="bandeau" style="background-image:url('{photo}');background-position:{s.get('focus','center')}">
  <div class="wrap">
    <h1>{s['nom']} en Artois : {s['benefice']}</h1>
    <p>On vous rappelle : devis et déplacement gratuits sous 24 h</p>
  </div>
</div>
<main class="t">
<div class="carte-form">
<form id="devis" data-moteur="devis" data-tel="{TEL_LIEN}" novalidate>
  <div data-etape="1">
    <div class="prog" aria-hidden="true"><i></i></div>
    <p class="pas">Étape 1 sur 2</p>
    <p class="local">Votre projet dans le Pas-de-Calais : Lens, Béthune, Arras et alentours.</p>
    <p class="question">{s['question']}</p>
    <div class="choix">
{rep}
      <button type="button" data-service="{s['nom']}" data-ic="autre">{s.get('autre', 'Autre / je ne sais pas')}</button>
    </div>
  </div>
{etape2(s['exemple'])}
{CONFIANCE}
</form>
</div>
{paire(s)}
</main>
{mini()}
</body>
</html>
"""

def devis():
    photo = "photos/equipe.webp"
    liens = "\n".join(f'      <a href="devis-{s["slug"]}.html"><img src="photos/action-{s["slug"]}.webp" alt="" width="46" height="46"{FOC(s)}><span>{s["bouton"]}</span></a>' for s in SERVICES)
    return head(f"Paysagiste en Artois : devis gratuit sous 24 h | {NOM}",
                f"Votre devis paysagiste gratuit à {VILLES} : 2 étapes, on vous rappelle sous 24 h.",
                photo, noindex=True, css=CSS_TUNNEL) + f"""<body>
{entete()}
<div class="bandeau" style="background-image:url('{photo}')">
  <div class="wrap">
    <h1>Votre devis gratuit, en 1 minute</h1>
    <p>On vous rappelle : devis et déplacement gratuits sous 24 h</p>
  </div>
</div>
<main class="t">
<div class="carte-form">
<form id="devis" data-moteur="devis" data-tel="{TEL_LIEN}" novalidate>
  <div data-etape="1">
    <div class="prog" aria-hidden="true"><i></i></div>
    <p class="pas">Étape 1 sur 2</p>
    <p class="local">Votre projet dans le Pas-de-Calais : Lens, Béthune, Arras et alentours.</p>
    <p class="question">Quels travaux ?</p>
    <div class="choix">
{liens}
      <button type="button" data-service="Autre" data-ic="autre">Autre / je ne sais pas</button>
    </div>
  </div>
{etape2("ex. jardin d'environ 200 m², terrasse et haie à faire, pour le printemps…")}
{CONFIANCE}
</form>
</div>
</main>
{mini()}
</body>
</html>
"""

# ---------------------------------------------------------------- LÉGAL
CSS_LEGAL = """
.entete{background:var(--sauge-n);color:#fff}.entete .wrap{display:flex;align-items:center;gap:20px;min-height:56px}
.entete a{color:#fff;text-decoration:none;font-weight:600}
.legal{max-width:820px;margin:0 auto;padding:50px 22px 70px}
.legal h1{font-size:clamp(32px,4vw,46px);color:var(--sauge-n);margin-bottom:26px}
.legal h2{font-size:24px;color:var(--sauge-n);margin:36px 0 10px;letter-spacing:-.02em}
.legal p,.legal li{color:#3a3a36}
.legal .todo{background:#FCEFD9;padding:1px 5px;border-radius:4px;font-weight:600}
.mini{text-align:center;font-size:14px;color:var(--gris);padding:0 16px 40px}.mini a{color:var(--gris)}
"""

def legal(title, h1, corps):
    return head(f"{h1} | {NOM}", f"{h1} du site {NOM}.", None, css=CSS_LEGAL, canon=f"{BASE}/{title}.html") + f"""<body>
<header class="entete"><div class="wrap"><a href="index.html">← {NOM}</a></div></header>
<main class="legal">
<h1>{h1}</h1>
{corps}
</main>
<footer class="mini"><a href="mentions-legales.html">Mentions légales</a> · <a href="confidentialite.html">Confidentialité</a></footer>
</body>
</html>
"""

T = lambda s: f'<span class="todo">[À COMPLÉTER : {s}]</span>'

MENTIONS = f"""
<h2>Éditeur du site</h2>
<p>Le site <b>allopaysagisteartois.fr</b> (« {NOM} ») est édité par :<br>
Koffi James Eklou, particulier (personne physique)<br>
Adresse : 174b avenue des 2 Gares, 74970 Marignier<br>
E-mail : <a href="mailto:k.eklou.contact@gmail.com">k.eklou.contact@gmail.com</a> · Téléphone : {TEL_AFF}<br>
Directeur de la publication : Koffi James Eklou</p>

<h2>Qui réalise les travaux</h2>
<p>{NOM} est le nom de ce site. Les devis et les travaux sont assurés par une entreprise locale indépendante du secteur, assurée pour son activité, à qui votre demande est transmise. Le nom de cette entreprise vous est communiqué lors de notre appel et figure sur le devis. Le devis vous est remis directement par cette entreprise, qui en est seule responsable.</p>

<h2>Hébergement</h2>
<p>Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, États-Unis (vercel.com).<br>
Les demandes envoyées par le formulaire sont stockées chez Upstash (base de données hébergée dans l'Union européenne).</p>

<h2>Propriété intellectuelle</h2>
<p>Les textes et la mise en page de ce site sont la propriété de l'éditeur. Les photos présentes sur le site sont des photos d'illustration.</p>

<h2>Données personnelles</h2>
<p>Voir notre <a href="confidentialite.html">politique de confidentialité</a>.</p>
"""

CONFID = f"""
<h2>Qui est responsable de vos données</h2>
<p>L'éditeur du site : Koffi James Eklou, 174b avenue des 2 Gares, 74970 Marignier, <a href="mailto:k.eklou.contact@gmail.com">k.eklou.contact@gmail.com</a>.</p>

<h2>Ce que nous collectons, et pourquoi</h2>
<p>Quand vous remplissez un formulaire : votre nom (ou prénom), votre téléphone, votre commune, le type de travaux et, si vous le souhaitez, quelques mots sur votre chantier. Ces informations servent uniquement à vous rappeler et à établir votre devis. Base légale : votre demande de devis (mesures précontractuelles).</p>

<h2>Qui reçoit vos données</h2>
<p>Seulement l'éditeur du site et l'entreprise qui réalise les travaux dans votre zone, une entreprise locale indépendante et assurée à qui votre demande est transmise pour vous rappeler et faire votre devis. Vos coordonnées ne sont jamais revendues ni partagées avec d'autres. Prestataires techniques : Vercel (hébergement du site), Upstash (stockage des demandes, dans l'Union européenne) et une messagerie de notification utilisée par l'éditeur pour être prévenu de chaque demande.</p>

<h2>Combien de temps nous les gardons</h2>
<p>3 ans après notre dernier échange, puis elles sont supprimées.</p>

<h2>Mesure d'audience et cookies</h2>
<p>Ce site n'utilise <b>aucun outil de mesure d'audience</b>.</p>
<p>Les clics sur notre numéro de téléphone sont comptés <b>sans cookie</b> (page, heure, type d'appareil), pour vérifier les appels reçus.</p>
<p>Si les annonces Google Ads sont mesurées (formulaire envoyé, appels), une petite barre vous demande d'abord votre accord. Sans accord, aucun cookie publicitaire n'est déposé. Avec votre accord, les cookies de Google sont conservés 13 mois au plus ; votre choix est gardé 6 mois. Pour en savoir plus sur Google : <a href="https://policies.google.com/privacy" rel="noopener">policies.google.com/privacy</a>.</p>

<h2>Vos droits</h2>
<p>Vous pouvez demander à consulter, corriger ou supprimer vos données, ou vous opposer à leur utilisation, en écrivant à <a href="mailto:k.eklou.contact@gmail.com">k.eklou.contact@gmail.com</a>. Si vous estimez que vos droits ne sont pas respectés, vous pouvez saisir la CNIL (cnil.fr).</p>
"""


# ---------------------------------------------------------------- PAGES SERVICES (référencement naturel)
CSS_SERVICE = """
.ariane{font-size:14px;color:var(--gris);padding-top:16px;padding-bottom:16px}
.ariane a{color:var(--gris);text-decoration:none}.ariane a:hover{color:var(--texte)}
.ariane span{color:var(--texte);font-weight:600}
.sv-hero{position:relative;min-height:470px;display:flex;align-items:flex-end;background:var(--sauge-f) center/cover no-repeat;color:#fff}
.sv-hero::before{content:"";position:absolute;inset:0;background:linear-gradient(100deg,rgba(34,42,36,.9) 0%,rgba(34,42,36,.65) 55%,rgba(34,42,36,.25) 100%)}
.sv-hero .wrap{position:relative;width:100%;padding-top:70px;padding-bottom:60px}
.sv-hero .kicker{color:#C9D6CB}
.sv-hero h1{font-size:clamp(34px,4.8vw,58px);max-width:820px}
.sv-hero .phrase{font-size:20px;font-weight:600;margin:18px 0 6px}
.sv-hero .sous{color:rgba(255,255,255,.85);max-width:620px;margin:0 0 24px}
.sv-hero .act{display:flex;flex-wrap:wrap;gap:12px}
.sv-intro{display:grid;grid-template-columns:1.25fr .75fr;gap:60px;align-items:start}
.sv-intro p{margin:0 0 16px}
.carte-devis{position:sticky;top:100px;background:#fff;border-radius:var(--r);padding:26px;box-shadow:var(--ombre)}
.carte-devis h3{font-size:24px;color:var(--sauge-n);letter-spacing:-.02em}
.carte-devis p{color:var(--gris);margin:8px 0 18px;font-size:16px}
.carte-devis .btn{width:100%}
.carte-devis form label{display:block;font-weight:600;font-size:17px;margin:14px 0 6px}
.carte-devis label small{font-weight:400;color:var(--gris)}
.carte-devis textarea{min-height:90px;resize:vertical}
.carte-devis .pas{margin:0 0 6px;font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--brique)}
.carte-devis .question{font-size:20px}
.carte-devis button[type=submit]{width:100%;min-height:58px;margin-top:18px;border:0;border-radius:12px;background:var(--brique);color:#fff;font:700 18px Inter,sans-serif;cursor:pointer;transition:background .3s ease}
.carte-devis button[type=submit]:hover{background:var(--brique-f)}
.carte-devis .choix{grid-template-columns:1fr}
.carte-devis .question{color:var(--texte)}
.form-ok::after{font-weight:500}
.carte-devis .tel{display:block;text-align:center;margin-top:12px;font-weight:700;color:var(--sauge-n);text-decoration:none}
.sv-var{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px}
.sv-var article{background:#fff;border-radius:var(--r);overflow:hidden;box-shadow:var(--ombre);display:flex;flex-direction:column}
.sv-var img{aspect-ratio:4/3;object-fit:cover;width:100%}
.sv-var h3{font-size:21px;color:var(--sauge-n);letter-spacing:-.02em;margin:18px 20px 6px}
.sv-var p{margin:0 20px 14px;color:var(--gris);font-size:16px}
.sv-var a{margin:auto 20px 20px;font-weight:700;color:var(--brique);text-decoration:none}
.sv-inclus{display:grid;grid-template-columns:.9fr 1.1fr;gap:50px;align-items:center}
.sombre .garanties{border-top-color:rgba(255,255,255,.18);color:#fff}
.sombre .garanties li::before{color:#F2B9A2}
.sv-autres ul{list-style:none;margin:30px 0 0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.sv-autres a{display:block;height:100%;background:#fff;border-radius:14px;padding:18px;font-weight:700;text-decoration:none;color:var(--sauge-n);box-shadow:var(--ombre)}
.sv-autres a::after{content:" →";color:var(--brique)}
.sv-zone .zone-txt{max-width:820px;color:var(--gris);font-size:18px;margin:16px 0 0}
.conseils{grid-template-columns:repeat(2,1fr)}
@media(max-width:820px){
 .sv-hero{min-height:0}.sv-hero .wrap{padding-top:150px;padding-bottom:30px}
 .sv-hero::before{background:linear-gradient(to bottom,rgba(34,42,36,.15) 0,rgba(34,42,36,.85) 150px,var(--sauge-f) 230px)}
 .sv-hero h1{font-size:29px}.sv-hero .phrase{font-size:17px}.sv-hero .act .btn{width:100%}
 .sv-intro,.sv-inclus{grid-template-columns:1fr;gap:24px}
 .carte-devis{position:static;order:-1}
 .sv-var{grid-template-columns:1fr;gap:16px;margin-top:20px}
 .sv-autres ul{grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}
 .regles .regle{display:block}
 .conseils{grid-template-columns:1fr}
 .sv-zone .zone-txt{font-size:16.5px}
}
"""

def entete_site(devis_href):
    return f"""<header class="top">
  <div class="wrap">
    <a class="marque" href="index.html">{LOGO}{NOM}</a>
    <nav class="ancres" aria-label="Sections"><a href="index.html#avant-apres">Avant / après</a><a href="index.html#prestations">Prestations</a><a href="index.html#zone">Zone</a><a href="index.html#faq">FAQ</a></nav>
    <div class="h-tel">Appelez-nous{tel()}</div>
    <a class="btn" href="{devis_href}">Devis gratuit</a>
  </div>
</header>"""

def pied_site(devis_href):
    return f"""<footer class="pied">
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="marque" href="index.html">{LOGO}{NOM}</a>
        <p class="pc">Création, aménagement et entretien de jardins à Lens, Béthune, Arras et alentours.</p>
        <p class="tel">{tel()}</p>
      </div>
      <div class="pied-presta"><h4>Prestations</h4><ul>{liens_detail()}</ul></div>
      <div class="pc"><h4>Zone</h4><ul><li>Lens, Liévin, Hénin-Beaumont</li><li>Béthune, Bruay-la-Buissière</li><li>Arras, Achicourt, Beaurains</li><li>Carvin, Avion, Lillers</li></ul></div>
      <div><h4>Informations</h4><ul><li class="pc"><a href="{devis_href}">Devis gratuit</a></li><li><a href="mentions-legales.html">Mentions légales</a></li><li><a href="confidentialite.html">Confidentialité</a></li></ul></div>
    </div>
    <div class="bas"><span>Travaux réalisés par des professionnels assurés. Photos d'illustration.</span><span>© {NOM}</span></div>
  </div>
</footer>
<div class="barre" data-barre><a class="btn" href="{devis_href}">Devis gratuit →</a></div>"""

def page_service(q):
    url = f"{BASE}/{q['slug']}.html"
    devis_href = "#devis"
    sv = {x["slug"]: x for x in SERVICES}[q["tunnel"]]
    rep_sv = "\n".join(f'      <button type="button" data-service="{sv["nom"]} — {r}" data-ic="{i}">{r}</button>' for i, r in sv["reponses"])
    if sv.get("urgent"):
        rep_sv += f'\n      <button type="button" class="urgent" data-service="URGENT — {sv["nom"]} — {sv["urgent"][1]}" data-ic="urgent">{sv["urgent"][0]}</button>'
    rep_sv += f'\n      <button type="button" data-service="{sv["nom"]}" data-ic="autre">{sv.get("autre", "Autre / je ne sais pas")}</button>'
    focus = q.get("focus", "center")
    par = "".join(f"<p>{x}</p>" for x in q["intro"])
    var = "".join(f"""<article><div class="ph"><img src="photos/{ph}.webp" alt="{t}" width="800" height="600" loading="lazy"{' style="object-position:' + focus + '"' if ph == q['photo'] and q.get('focus') else ''}></div>
  <h3>{t}</h3><p>{d}</p><a href="{devis_href}">Demander un devis gratuit →</a></article>""" for ph, t, d in q["variantes"])
    inclus = "".join(f"<li>{x}</li>" for x in q["inclus"])
    conseils = "".join(f'<div class="regle"><h3>{t}</h3><p>{d}</p></div>' for t, d in q["conseils"])
    faq = "\n".join(f"<details name=\"faq\"><summary>{a}</summary><p>{b}</p></details>" for a, b in q["faq"])
    par_slug = {x["slug"]: x for x in PAGES}
    autres = "".join(f'<li><a href="{l}.html">{par_slug[l]["nom"]}</a></li>' for l in q["liens"])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "name": q["nom"], "serviceType": q["nom"], "description": q["desc"], "url": url,
         "provider": ENTREPRISE_LD, "areaServed": [{"@type": "City", "name": v} for v in VILLES_LD]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Prestations", "item": BASE + "/#prestations"},
            {"@type": "ListItem", "position": 3, "name": q["nom"], "item": url}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": a, "acceptedAnswer": {"@type": "Answer", "text": b}} for a, b in q["faq"]]},
    ]}
    return head(q["title"], q["desc"], f"photos/{q['photo']}.webp", css=CSS_ACCUEIL + CSS_SERVICE, canon=url, ld=ld) + f"""<body>
{entete_site(devis_href)}
<nav class="ariane wrap" aria-label="Fil d'Ariane"><a href="index.html">Accueil</a> › <a href="index.html#prestations">Prestations</a> › <span>{q['nom']}</span></nav>
<main>
<section class="sv-hero" style="background-image:url('photos/{q['photo']}.webp');background-position:{focus}">
  <div class="wrap">
    <p class="kicker">{q['cat']}</p>
    <h1>{q['h1']}</h1>
    <p class="phrase">On vous rappelle : devis et déplacement gratuits sous 24 h.</p>
    <p class="sous">{q['accroche']}</p>
    <div class="act"><a class="btn" href="{devis_href}">Recevoir mon devis gratuit</a>{tel("btn btn-blanc", TEL_IC + "Appeler le " + TEL_AFF)}</div>
  </div>
</section>

<section class="s">
  <div class="wrap sv-intro">
    <div>
      <p class="kicker">Ce que nous faisons</p>
      <h2 class="t">{q['nom']} : notre façon de travailler</h2>
      <div style="margin-top:22px">{par}</div>
    </div>
    <aside class="carte-devis">
      <h3>Votre devis gratuit</h3>
      <p>Votre projet dans le Pas-de-Calais : on vous rappelle sous 24 h pour en parler.</p>
<form id="devis" data-moteur="devis" data-tel="{TEL_LIEN}" data-service="{q['nom']}" novalidate>
  <div data-etape="1" hidden>
    <div class="prog" aria-hidden="true"><i></i></div>
    <p class="pas">Étape 1 sur 2</p>
    <p class="question">{sv['question']}</p>
    <div class="choix">
{rep_sv}
    </div>
  </div>
{etape2(sv['exemple'], visible=True, choisi=q['nom'])}
{CONFIANCE}
</form>
      {tel("tel", "ou appelez le " + TEL_AFF)}
    </aside>
  </div>
</section>

<section class="s sable">
  <div class="wrap">
    <p class="kicker">Nos réalisations types</p>
    <h2 class="t">Ce qu'on réalise pour vous</h2>
    <div class="sv-var">{var}</div>
  </div>
</section>

<section class="s sombre">
  <div class="wrap sv-inclus">
    <div><p class="kicker">Ce qui est inclus</p><h2 class="t">Tout est compris, de la visite au nettoyage</h2></div>
    <ul class="garanties">{inclus}</ul>
  </div>
</section>

<section class="s">
  <div class="wrap">
    <p class="kicker">Bon à savoir</p>
    <h2 class="t">Nos conseils avant de vous lancer</h2>
    <div class="regles conseils">{conseils}</div>
  </div>
</section>

<section class="s sable" id="faq">
  <div class="wrap faq">
    <div class="gauche">
      <p class="kicker">Questions fréquentes</p>
      <h2 class="t">{q['court']} : vos questions</h2>
      <a class="btn btn-2" href="{devis_href}">Être rappelé gratuitement</a>
    </div>
    <div>
{faq}
    </div>
  </div>
</section>

<section class="s sv-zone">
  <div class="wrap">
    <p class="kicker">Zone d'intervention</p>
    <h2 class="t">{q['nom']} à Lens, Béthune, Arras et alentours</h2>
    <p class="zone-txt">On intervient dans le bassin de Lens (Liévin, Hénin-Beaumont, Avion, Carvin, Harnes), autour de Béthune (Bruay-la-Buissière, Beuvry, Nœux-les-Mines, Lillers) et dans l'Arrageois (Achicourt, Beaurains, Saint-Laurent-Blangy, Vimy). Votre commune n'est pas citée ? Demandez quand même : si vous êtes dans le secteur, on se déplace.</p>
    <div class="sv-autres"><ul>{autres}</ul></div>
  </div>
</section>

<section class="final">
  <img class="fond" src="photos/equipe.webp" alt="" width="1600" height="1000" loading="lazy">
  <div class="wrap">
    <h2>Parlons de votre projet</h2>
    <p>Devis et déplacement gratuits, sans engagement.</p>
    <div class="final-act"><a class="btn" href="{devis_href}">Recevoir mon devis gratuit</a>{tel("btn btn-blanc", TEL_IC + "Appeler le " + TEL_AFF)}</div>
  </div>
</section>
</main>
{pied_site(devis_href)}
</body>
</html>
"""

pages = {"index.html": accueil(), "devis.html": devis(),
         "mentions-legales.html": legal("mentions-legales", "Mentions légales", MENTIONS),
         "confidentialite.html": legal("confidentialite", "Politique de confidentialité", CONFID)}
for s in SERVICES:
    pages[f"devis-{s['slug']}.html"] = tunnel(s)
for q in PAGES:
    pages[f"{q['slug']}.html"] = page_service(q)
with open(os.path.join(OUT, "robots.txt"), "w") as f:
    f.write(f"User-agent: *\nDisallow: /demandes\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n")
urls = [BASE + "/"] + [f"{BASE}/{q['slug']}.html" for q in PAGES]
with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{u}</loc><lastmod>2026-11-21</lastmod></url>\n" for u in urls) + "</urlset>\n")
import re as _re
_PH = os.path.join(OUT, "photos")
def _variantes(nom):
    v = [(f"photos/w/{nom}-{w}.webp", w) for w in (200, 400, 600, 800) if os.path.exists(os.path.join(_PH, "w", f"{nom}-{w}.webp"))]
    return v
def _sizes(w):
    return {"46": "(max-width:480px) 40vw, 46px", "600": "(max-width:820px) 46vw, 290px", "800": "(max-width:820px) 92vw, 380px",
            "1200": "(max-width:820px) 92vw, 470px"}.get(w, "(max-width:820px) 92vw, 580px")
def _img(m):
    tag = m.group(0)
    if "srcset=" in tag: return tag
    src = _re.search(r'src="photos/([a-z0-9-]+)\.webp"', tag)
    if not src or src.group(1).startswith("logo"): return tag
    nom = src.group(1); v = _variantes(nom)
    if not v: return tag
    from PIL import Image as _I
    ow = _I.open(os.path.join(_PH, nom + ".webp")).width
    ss = ", ".join(f"{u} {w}w" for u, w in v) + f", photos/{nom}.webp {ow}w"
    w = _re.search(r'width="(\d+)"', tag); w = w.group(1) if w else ""
    prio = ' fetchpriority="low"' if w == "46" else ""
    return tag[:-1] + f' srcset="{ss}" sizes="{_sizes(w)}"{prio}>'
def _fond(m):
    nom = m.group(1); v = dict((w, u) for u, w in _variantes(nom))
    mob = v.get(600) or v.get(800) or f"photos/{nom}.webp"
    return f"--bgm:url('{mob}');background-image:url('photos/{nom}.webp')"
def _preload(m):
    nom = m.group(1); v = dict((w, u) for u, w in _variantes(nom))
    mob = v.get(600) or v.get(800) or f"photos/{nom}.webp"
    return (f'<link rel="preload" as="image" href="{mob}" media="(max-width:820px)" fetchpriority="high">\n'
            f'<link rel="preload" as="image" href="photos/{nom}.webp" media="(min-width:821px)" fetchpriority="high">')
FOND_MOBILE = ("<style>@media(max-width:820px){.bandeau,.sv-hero{background-image:var(--bgm)!important}"
               ".hero{background-image:url('photos/w/action-amenagement-jardin-600.webp')}"
               "}</style>")
TEL_JS = "<script>document.querySelectorAll('input[name=tel]').forEach(function(i){i.addEventListener('input',function(){if(i.selectionStart!==i.value.length)return;var v=i.value,d=v.replace(/\\D/g,''),f;if(/^\\s*\\+/.test(v)){if(d.indexOf('33')!==0)return;var r=d.slice(2).replace(/^0/,'');f='+33'+(r?' '+r.charAt(0):'')+(r.length>1?' '+r.slice(1,9).replace(/(\\d{2})(?=\\d)/g,'$1 '):'');}else if(d.charAt(0)==='0'){f=d.slice(0,10).replace(/(\\d{2})(?=\\d)/g,'$1 ');}else return;if(f!==v)i.value=f;});});</script>"
def optim(h):
    if 'name="tel"' in h:
        h = h.replace("</body>", TEL_JS + "\n</body>", 1)
    h = h.replace(">Débroussaillage, évacuation</button>", ">Débrous&shy;saillage, évacuation</button>")
    h = _re.sub(r"<img [^>]*>", _img, h)
    h = _re.sub(r"background-image:url\('photos/([a-z0-9-]+)\.webp'\)", _fond, h)
    h = _re.sub(r'<link rel="preload" as="image" href="photos/([a-z0-9-]+)\.webp" fetchpriority="high">', _preload, h)
    return h.replace("</head>", FOND_MOBILE + "\n</head>", 1)
for n, h in pages.items():
    h = optim(h)
    h = "\n".join(l for l in h.split("\n") if l.strip() != "")  # retire les lignes vides
    with open(os.path.join(OUT, n), "w", encoding="utf-8") as f:
        f.write(h + "\n")
    print(n, len(h))
