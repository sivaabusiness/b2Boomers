---
name: google-ads-locale
description: >
  Lancer de A à Z une campagne Google Ads Search locale de génération de leads
  pour un client artisan (élagueur, couvreur, plombier, paysagiste…) : recherche
  de mots-clés avec les vrais volumes/CPC de l'API, fichier Excel livrable,
  annonces RSA, création de la campagne via l'API (en pause, CPC manuel par
  mot-clé, 3-4 groupes, ville de l'internaute dans les titres), images et
  assets. Utiliser ce skill dès que l'utilisateur parle de lancer,
  préparer ou monter une campagne Google Ads pour un client, d'une recherche de
  mots-clés locale, d'un « kit campagne », d'un nouveau client artisan à mettre
  en ligne, de RSA, de mots-clés négatifs ou d'estimer un budget Ads — même si
  le mot « campagne » n'est pas prononcé. Couvre aussi les reprises partielles
  (ajouter des mots-clés, refaire les RSA, ajouter les images à une campagne
  existante), et le PILOTAGE d'une campagne qui tourne déjà : diagnostic
  (« où j'en suis », P1), kickstart d'une campagne qui ne dépense pas (P2),
  titres et CTR (P3), mots-clés négatifs et termes de recherche (P4),
  optimisation des enchères (P5), conversions et URL finales (P6), site (P7).
---

# Campagne Google Ads Search locale — process complet

Process éprouvé en production (client artisan élagueur, 2026) pour transformer
un brief client en campagne Search prête à activer. Chaque phase produit un
livrable vérifiable ; ne jamais sauter la vérification de fin de phase.
Le skill applique DÈS LA CRÉATION ce que Léo a enseigné en coaching (n°2 →
n°7, la session la plus récente gagne) : l'utilisateur n'a pas à relancer
les prompts de coaching (L1-L4, P3) pour avoir une campagne « aux règles ».

## Campagne déjà en ligne : le pilotage (P1 à P7)

Dès que la campagne tourne, tout passe par
[references/pilotage-campagne.md](references/pilotage-campagne.md) : les
stades (bloquée / ne dépense pas / trop tôt / on lit / on optimise /
accélérer / couper), les règles (un changement puis 72 h, +20-30 % maxi sur
les enchères jamais ×2, accélérer = +5 € de budget pas les enchères, 100
clics avant toute décision sur les enchères, 10-15 demandes avant
d'optimiser, les seuils pour couper une zone, jamais une recommandation
Google) et les 7 procédures numérotées. L'utilisateur peut dire « fais le
P1 » ou décrire son problème : commencer par le diagnostic P1 si le stade
n'est pas évident.

## Règles non négociables

- **Lecture seule par défaut.** Toute écriture sur un compte Google Ads passe
  par un script à deux modes : `--dry` (validateOnly, que TU exécutes) et
  `--apply` (que l'UTILISATEUR exécute — le contrôle de permissions bloque les
  écritures de compte lancées par Claude, c'est voulu). Donne la commande
  `--apply` en syntaxe PowerShell (`;` et non `&&`).
- **Aucun chiffre inventé.** Volume, CPC, concurrence viennent de l'API ou
  valent « n/d ». Les preuves des annonces (avis, délais, garanties) viennent
  des pages du client, jamais de ton imagination.
- **Tout ce qui est créé naît en PAUSE.** L'utilisateur active lui-même, et
  vite : le jour même, dès que le test des conversions est passé.
- **Après chaque écriture, relire le compte** (GAQL) et recompter. Après chaque
  fichier produit, le relire depuis le disque, pas depuis le script.
- **Une campagne = une zone** (jamais deux zones fusionnées), **3-4 groupes
  d'annonces maximum** (les sous-services se regroupent et vont dans les
  titres). Chaque groupe a une destination qui en parle vraiment : site du
  pack B2Boomers → l'accueil avec `?travaux=<service>` ; autre site → la page
  du service. Jamais une destination inventée.
- **On est l'entreprise, jamais un intermédiaire** : aucune annonce, aucun
  texte de site ne dit « mise en relation », « artisans partenaires », « un
  artisan de votre secteur ». La promesse : « On vous rappelle, devis et
  déplacement gratuits sous 24 h ».
- **Montrer avant d'écrire** : les annonces (titres, descriptions) et la
  liste des mots-clés s'affichent à l'utilisateur, qui les relit, AVANT le
  `--apply` (« ne faites pas confiance aveuglément à Claude »).

## Environnement

- Credentials dans `env.local.txt` à la racine du projet (client OAuth,
  refresh token, numéro de compte — créé en suivant le Guide Clé API du pack ;
  pas de token développeur ni de compte manager depuis sept. 2026).
  Vérifier la connexion avec `scripts/test_connexion.py` avant toute phase.
  Les mots-clés et chiffres de la zone : `scripts/kit.py` (Phase 2).
  Client REST prêt à l'emploi :
  [scripts/google_ads_client.py](scripts/google_ads_client.py) — auth, backoff,
  search GAQL, mutate avec validateOnly, keyword ideas, historical metrics,
  suggestion de géos. Version d'API : voir `API_VERSION` dans le script ;
  re-sonder si dépréciée (les versions durent ~1 an).
- Travailler dans un sous-dossier par client (`<client>/`), brut API dans
  `<client>/raw/`.

## Phase 0 — Cadrage (avec l'utilisateur)

Obtenir : activité et services, site + URL de chaque page de destination (site
du pack : l'accueil et ses pages tunnel `devis-<service>.html`), zone
= celle du kit (le secteur réservé et sa liste de communes, ou tout le département ;
jamais un rayon : il déborderait sur les secteurs voisins, vendus à d'autres), capacité de leads/mois de l'artisan, objectifs
de conversion (formulaire, appel réel). Hypothèse de taux de conversion : 2 %
par défaut (3 % au mieux sans preuve). La capacité limitée d'un artisan
signifie précision > volume : 100-150 mots-clés justes, pas 600 gonflés.
**Le budget** (coachings n°7, décisions du 07/11) : demander ce que
l'utilisateur peut perdre le premier mois. **Au moins 400 € → 2 zones (deux
campagnes, même métier) ; sinon 1 seule.** Chaque campagne démarre à **10-15
€/jour** et doit pouvoir acheter **au moins 10 clics par jour** (sinon 15 €/j
ou des groupes moins chers). Pas de « budget ÷ 30 jours ÷ 2 zones » : on
coupe vite la zone qui ne marche pas (seuils dans pilotage-campagne.md).

## Phase 1 — Compte et pages

1. Vérifier le compte (`scripts/test_connexion.py` : nom, devise, statut,
   campagnes existantes). Le compte cible est `GOOGLE_ADS_CUSTOMER_ID` dans
   `env.local.txt` — un seul compte, pas de manager.
2. **Vérifier chaque page de destination AVANT de structurer les groupes**
   (WebFetch : H1, vocabulaire exact, 404 ?). Le brief peut mentionner une page
   qui n'existe pas, ou le site peut distinguer deux services que le brief
   fusionne — la structure des groupes suit les pages réelles, pas le brief.
   **Site du pack B2Boomers** (un accueil + des pages tunnel
   `devis-<service>.html`, gros boutons `data-travaux` sur l'accueil) : l'URL
   finale de chaque groupe est `https://<domaine>/?travaux=<service>` — le
   moteur du site y met le service dans le H1, sa photo en haut et son bouton
   en premier. Vérifier pour chaque service le bouton `data-travaux="<service>"`
   sur l'accueil et la page `devis-<service>.html` (WebFetch voit le H1 par
   défaut : l'adaptation se fait dans le navigateur, c'est normal). Les pages
   tunnel (courtes, noindex) ne servent qu'aux sitelinks, jamais d'URL finale
   d'annonce.
   Relever au passage les preuves réutilisables en annonce (note Google, nombre
   d'avis, « devis gratuit », délais, rayon d'intervention).
3. Noter les conversions déjà présentes sur le compte (`conversion_action`).

## Phase 2 — Mots-clés et chiffres

**Les volumes et CPC viennent du kit de la zone, préparé par l'espace membre
B2Boomers** (atlas pré-calculé niche × ville), PAS de l'API : le niveau
d'accès Explorateur du compte bloque le Keyword Planner
(`generateKeywordIdeas` / `generateKeywordHistoricalMetrics` renverront
PERMISSION_DENIED — ne pas réessayer, ne pas inventer de chiffres à la place).

1. **Récupérer le kit** (lecture seule, TU l'exécutes) :
   `python google-ads-locale/scripts/kit.py` (`--zone <id>` si le script liste
   plusieurs zones). Il écrit `kit/kit_<niche>_<ville>.json` : `kit.mots_cles`
   = les mots-clés de service déjà classés par sous-service, variantes
   fusionnées, avec le volume mensuel et les CPC bas/haut mesurés pour la ville
   de la zone (`kit.reference` ; un CPC `null` = non publié par Google, écrire
   « n/d ») et une correspondance suggérée ; `kit.negatifs` = toutes les
   requêtes exclues trouvées dans la zone, avec leur catégorie. Le JSON donne
   aussi la zone à cibler : `secteur` {id, nom, dept, n}, `tout_dept` et
   `communes` [{insee, nom}] = la liste EXACTE des communes du secteur (vide si
   `tout_dept` : on cible le département). Plus trois CSV pour l'utilisateur
   (mots, négatifs, communes). Ne jamais lui demander de copier-coller des chiffres.
2. Le script répond « aucune zone validée » → l'utilisateur réserve sa zone
   dans l'onglet Zones et attend la validation de Léo. « Pas encore de kit » →
   il prévient Léo. Dans les deux cas, pas de chiffres inventés en attendant.
3. **Le kit est la matière première, la méthode s'applique dessus**
   ([references/recherche-mots-cles.md](references/recherche-mots-cles.md),
   sections 3 à 9 — les sections 1-2, géos et collecte API, sont remplacées
   par le kit) : groupes calés sur les services RÉELS du site (site du pack :
   un bouton `data-travaux` + une page tunnel par service ; autre site : une
   page par service — un sous-service sans destination = groupe annexe hors
   campagne), **3-4 groupes maximum** (regrouper les sous-services ; garder
   ceux à plus grosse valeur de chantier et pas trop chers), rétention
   (**intention d'achat** obligatoire : devis, prix, tarif, entreprise,
   artisan, service + ville ; pas les curieux), correspondances (les
   suggestions du kit sont un point de départ ; jamais de requête large),
   priorités, négatifs (condenser `kit.negatifs` en ~100-120 entrées, chaque
   négatif accentué EN DOUBLE ; « prix » et « gratuit » ne sont PAS des
   négatifs), enchère de départ par mot-clé, budget. Livrable :
   `mots_cles_google_ads.xlsx` (structure et checklist dans la même référence
   — la passe de vérification est obligatoire avant de livrer).

## Phase 3 — RSA et assets

Suivre [references/rsa-et-assets.md](references/rsa-et-assets.md) : 15 titres
remplis / 4 descriptions par groupe, copy fondée sur les preuves des pages,
interdits de policy (téléphone dans le texte, « ! » dans les titres). **Non
négociable (coachings n°2, n°4, n°6) :**
- **Titre épinglé n°1 = le service + la ville de la personne** :
  `Élagage {LOCATION(City):<ville principale>}` ; seul épinglage ; **plus
  aucune ville en dur** ailleurs ; le mot-clé du groupe n'est pas répété
  dans les autres titres (les sous-services, oui, un titre chacun).
- **COURT** (18-25 caractères, 28 maxi, insertions comptées avec leur texte
  de secours), **une majuscule à chaque mot**, « & » au lieu de « et ».
- **AUTONOME et qui rassure** : chaque titre a du sens seul ; réassurance
  « Devis & Déplacement Gratuits », « On Vous Rappelle Sous 24 h », « Devis
  Écrit Avant Travaux » ; confiance chiffrée RÉELLE ; accroches problème ;
  CTA courts (« Contactez-Nous ») ; un titre conditionnel appareil (mobile →
  appeler, PC → formulaire).
- **Angle prix** : si des mots-clés contiennent « prix » ou « tarif », au
  moins un titre « Obtenez Un Prix Aujourd'hui » / « Prix Honnête ».
- **La poubelle, refusée par le script** : « Un Humain Vous Répond »,
  « Votre Devis Par Téléphone », « mise en relation », « partenaire »,
  titres techniques (corde, nacelle, branches broyées), vocabulaire bateau
  (qualité, sérieux, professionnel…), doublons.
Valider longueurs ET règles PAR SCRIPT : écrire `<client>/rsa.json` (format
en tête du script) et lancer `python google-ads-locale/scripts/verif_rsa.py
<client>/rsa.json` jusqu'à zéro ERREUR ; puis **afficher les RSA à
l'utilisateur** (tableau titre / longueur / rôle) avant de livrer. Ajouter
les onglets RSA, Assets et Import RSA au fichier Excel.

## Phase 4 — Création de la campagne via l'API

Suivre [references/api-google-ads.md](references/api-google-ads.md) : une seule
transaction `googleAds:mutate` avec ids temporaires (budget → campagne →
ciblage → négatifs → groupes → mots-clés → RSA → assets), les réglages par
défaut qui ont fait leurs preuves (pause, CPC manuel, **une enchère par
mot-clé** = le milieu de sa fourchette du kit, pas une enchère uniforme ;
budget 10-15 €/jour ; la zone du kit — les communes de `communes`, ou le
département si `tout_dept`, pas de rayon — ; présence, Search seul) et les
pièges connus de l'API. **Si l'utilisateur a la fiche de sa zone (Atlas),
appliquer ses ajustements par commune dès la création** (`bidModifier`,
+25 % maxi, « à exclure » → −30 %), jamais de commune hors du secteur.
Toujours : `--dry` propre, puis commande `--apply` à l'utilisateur, puis
relecture complète.

**Les conversions sont obligatoires** (section « Conversions » de la même
référence) et ne comptent que les VRAIES demandes : formulaire, appels depuis
le site et appels depuis les annonces (30 s et plus). **Pas de conversion
« clic sur le numéro »** (coaching n°6 : un clic n'est pas une demande ; si
elle existe, la passer en secondaire). Donner à l'utilisateur les 4 variables
Vercel de son site (`GADS_ID`, `GADS_FORMULAIRE`, `GADS_APPEL_SITE`,
`GADS_NUMERO` ; `GADS_CLIC_TEL` reste vide) et lui faire faire le **test**
(guide du site, étape 9) AVANT d'activer la campagne. Puis : **activer le
jour même** (« plus vite c'est activé, mieux c'est »). Une campagne dépense
dans les heures qui suivent ; si le lendemain elle n'a presque rien dépensé,
c'est l'enchère → P2.

## Phase 5 — Images

Demander photos chantier (avant/après = or massif), photo d'équipe, logo.
Specs, recadrages et choix éditoriaux dans
[references/rsa-et-assets.md](references/rsa-et-assets.md) (section Images).
REGARDER les images (Read) avant et après recadrage — un crop centré peut
rater le sujet. Lier les images service au niveau du groupe, équipe et logo au
niveau campagne. Field type `AD_IMAGE` (pas MARKETING_IMAGE).

## Phase 6 — Clôture

Relire le compte de bout en bout et présenter le récapitulatif : ce qui est en
place, ce qui manque, ce que l'utilisateur doit faire (activer, vérifier la
facturation, vérification d'identité annonceur pour le logo, poser les
variables de conversion sur son site et faire le test des 3 appuis s'il ne
l'a pas encore fait). Lui rappeler les 3 règles de la suite : un seul
changement puis 72 h, mots-clés négatifs 2 fois par semaine (P4), et les
seuils pour couper une zone (60 € sans demande, 1 demande puis 100-150 € sans
la 2e, plus de 50 € la demande). Annoncer explicitement ce qui n'a PAS pu
être récupéré et pourquoi. Mettre à jour la mémoire projet (compte, ids,
décisions, préférences de ciblage de l'utilisateur).

**Toujours terminer la session par la remontée de données** (CGU du pack) :
exécuter `python google-ads-locale/scripts/rapport.py` et confirmer l'envoi.
C'est non négociable et non optionnel — si l'envoi échoue (hors ligne),
le dire et demander à l'utilisateur de relancer la commande plus tard.
Vérifier aussi que l'envoi quotidien est en place (Windows : `schtasks /Query
/TN "B2Boomers Rapport"` ; Mac : présence de
`~/Library/LaunchAgents/com.b2boomers.rapport.plist`) ; sinon, proposer
`scripts/rapport_auto.py` (l'utilisateur l'exécute).
Le pack se met à jour TOUT SEUL : chaque envoi de rapport compare sa version
à celle de l'espace et remplace `google-ads-locale` si besoin. Si rapport.py
affiche « Pack mis a jour en vX », le signaler à l'utilisateur — la nouvelle
version est active à la prochaine session.
