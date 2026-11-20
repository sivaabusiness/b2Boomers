# Pilotage d'une campagne en ligne — stades, règles et les 7 procédures (P1 à P7)

Issu des coachings de Léo (n°2 du 18/10, n°4 du 25/10, n°6 du 02/11, n°7 du
06/11, décisions du 07/11). Quand deux sessions se contredisent, la plus
récente gagne ; et si un prompt P/L/A donné en coaching dit autre chose que
ce fichier, c'est CE fichier qui s'applique (il est plus récent).
S'applique dès que l'utilisateur parle d'une campagne QUI TOURNE : « où j'en
suis », « ça ne dépense pas », « kickstart », « mes titres », « CTR », « mots-
clés négatifs », « termes de recherche », « optimiser », « enchères »,
« budget », « couper une zone », « Google ne compte pas mes demandes »,
« conversions », « URL finale ». L'utilisateur peut dire simplement « fais le
P1 / P4… » : chaque procédure a son numéro.

Mêmes règles que le reste du skill : lecture libre en GAQL ; toute écriture
= script `--dry` (toi) puis `--apply` (lui, PowerShell) ; aucun chiffre
inventé ; terminer par `scripts/rapport.py`. Parler simple : chaque mot
technique expliqué en 5 mots entre parenthèses, un tableau quand c'est plus
clair.

## Les règles qu'on ne casse pas

1. **Un seul changement à la fois, puis 72 h** sans rien toucher (plus encore
   à petit budget : variance). Si le dernier changement a moins de 72 h : dire
   d'attendre, quel que soit le stade (n°7 · P2 ~@20:10). Exception : les
   négatifs (P4) ne comptent pas comme un changement.
2. **Enchères : +20 à +30 % maximum, jamais ×2** une fois que la campagne a
   des impressions et des clics (« ne double pas les enchères, malheureux, ne
   détruis pas tes stats », n°6 · P1 @29:00, P2 @2:44). Les gros coups (×3)
   sont réservés au kickstart d'une campagne qui ne dépense RIEN (P2).
3. **Accélérer = le budget, pas les enchères.** Deux seuls cas pour monter le
   budget : elle tape son plafond tous les jours, ou l'utilisateur vient de
   closer un artisan. Par **+5 €/jour**, puis encore +5 € tant que ça marche ;
   jamais de 10 à 40 €/jour d'un coup, jamais « changer le prix tous les
   jours » (n°7 · P1 @26:12, P2 @35:39). Google peut dépenser jusqu'à 2 fois
   le budget certains jours, il ne dépasse jamais budget × 30 sur le mois.
4. **Une campagne qui marche, on n'y touche pas** : « elle n'a pas besoin de
   vous, elle a juste besoin de plus de data » → +5 € de budget (n°6 · P2
   @54:38 ; n°7 · P1 @25:37).
5. **Jamais de pause/relance** en attendant la réponse d'un artisan (« elles
   n'aiment pas ça », ça casse l'apprentissage) ; **jamais deux zones
   fusionnées** dans une campagne, ni un budget doublé d'un coup en cours de
   route (n°6 · P1 @28:40, P2 @10:35) ; **jamais supprimer** un groupe ou une
   campagne : on met en pause.
6. **3-4 groupes d'annonces maximum** par campagne (n°6 · P1 @46:50).
7. **Variance** : aucune décision sur les enchères avant **100 clics**
   cumulés ; aucune optimisation d'enchères (P5) avant **10-15 demandes** sur
   la campagne ; un coût par demande ne se lit qu'à partir de **4-5 demandes** ;
   on ne monte un mot-clé qu'avec **5 conversions** dessus (n°2, n°3, n°6).
   Moins de 20 impressions ou 10 clics sur une ligne → refuser d'en tirer une
   conclusion, le dire. **Exception : les titres** se jugent à l'œil dès le
   jour 1 (P3).
8. **On n'applique jamais une recommandation Google.** « Enchère insuffisante
   pour la 1re page » en rouge sur les mots-clés = BON signe (Google voudrait
   plus d'argent) ; **pas de rouge du tout = tu surpayes** (n°4 · P1 @36:52 ;
   n°6 · P1 @29:35). On ne l'écoute que si visiblement ça rame (peu
   d'impressions ET budget non dépensé). Pas de « maximiser les clics », pas
   d'enchères automatiques, pas de Display, pas de Performance Max, pas de
   requête large, pas d'élargissement de zone. CPC manuel, exact ou
   expression, toujours.
9. **Ne jamais comparer l'utilisateur aux autres membres.**
10. **Repères** : CTR **7 % = minimum**, **< 10 % = titres à retravailler**,
    15-25 % = très bon (n°2, n°6) ; un excellent CTR obtenu en étant toujours
    premier ne prouve rien (on paye trop cher). Taux de conversion 2-3 % =
    correct, 10 %+ = très bien. Coût par demande 20-40 € normal, > 50 € au
    début = on coupe. **Taux d'impressions sur le Réseau de Recherche**
    (`metrics.search_impression_share`, la part du marché captée) : bas
    (30-45 %) + budget non dépensé = enchères trop basses ; ≥ 80-85 % = le
    marché est capté, plus rien à gagner sauf le CTR ; bas + budget dépensé +
    demandes = c'est le budget qui limite (n°4, n°6). 80 % est un plafond,
    pas un objectif.
11. **Vraies demandes** = les formulaires et les appels réellement reçus
    (Telegram, /demandes), pas les clics sur le numéro, ni les conversions
    à 0,75 ou en double. Google compte avec 2-3 h à 2 jours de retard.

## Les stades (P1 les détermine)

| Stade | Symptômes | Seule action |
|---|---|---|
| 0 bloquée | campagne non diffusée, bandeau rouge, vérification entreprise, paiement, annonces en examen | régler ce que Google demande, attendre |
| 1 ne dépense pas | dès le 1er jour plein : moins de 10 impressions/jour ou moins de la moitié du budget dépensée — « trois heures après je paie déjà mes clics » (n°7) | P2 (kickstart au démarrage, +20 % ensuite) |
| 2 trop tôt | ça dépense, < 100 clics cumulés | P3 si titres douteux, P4, P6, P7 ; PAS les enchères |
| 3 on lit | ≥ 100 clics, < 10 demandes | ordre d'audit de P1 : taux d'impressions, rouge, CTR (P3 < 10 %), termes (P4), conversions (P6) |
| 4 on optimise | ≥ 10-15 demandes | P5, une dimension, par phases |
| 5 accélérer | rentable et régulier, plafond tapé, ou artisan closé | +5 €/jour de budget, puis +5 € ; une zone de plus seulement à 3 clients qui paient |
| Couper | voir « Couper une zone » | pause (jamais de suppression), l'argent va dans la zone qui marche |

## Couper une zone (n°7, budget serré — décisions du 07/11)

Au moins 400 € le premier mois → 2 zones (2 campagnes), sinon 1 ; et on
coupe VITE celle qui ne marche pas. Les seuils, sur les VRAIES demandes :
- **plus de 60 € dépensés sans aucune demande** → on coupe ;
- **1 demande, puis 100-150 € sans la 2e** → on coupe ;
- **plus de 50 € la demande au début** → on coupe ;
- **une semaine sans demande** → on coupe.
Couper = mettre en pause (on ne supprime rien). Couper ≠ remplacer : si
l'autre zone marche, son budget monte de +5 € (les euros libérés y vont) et
on attend d'avoir closé avant d'ouvrir une autre zone. Une zone relancée plus
tard l'est avec une campagne propre, jamais l'ancienne (n°6 · P2 @16:42).
Le rapport quotidien signale ces seuils sur les conversions Google
(`seuil_coupe`, `cout_demande_eleve`) : toujours recouper avec les vraies
demandes avant de couper. Ce qui tranche, c'est l'absence de demande et le
retour de l'artisan, pas une stat Google.

## P1 — Diagnostic (lecture seule, dans l'ordre de Léo)

Le rapport quotidien (`scripts/rapport.py`, via `scripts/diagnostic.py`)
calcule déjà, en lecture seule, le stade et des alertes codées par campagne
active (`ne_depense_pas` → P2 ; `ctr_faible` / `titres_longs` /
`titres_bannis` / `sans_personnalisateur` → P3 ; `termes_hors_sujet` /
`mot_cle_large` → P4 ; `conversions_absentes` / `conversion_clic_tel` /
`url_finale_tunnel` → P6 ; `groupes_dilues` / `seuil_coupe` /
`cout_demande_eleve` / `plafond_atteint` → P1) avec les mêmes seuils
qu'ici ; l'utilisateur les reçoit sur son Telegram quand une alerte est
nouvelle, plus une routine hebdo (P4 + journal). Commencer P1 par relancer
`rapport.py` et lire son diagnostic, puis approfondir dans cet ordre (l'audit
de Léo, n°6), en commençant par la campagne qui a le plus dépensé :

1. **La dépense** : coût par jour depuis le lancement ; budget atteint ou
   non (jours sous 50 % du budget) ; pic du 1er jour (un quart du budget
   parti d'un coup = surpayé au démarrage) ; pauses/relances ; changement de
   ciblage récent (`change_event`) = fusion de zones ?
2. **Les vraies conversions** : `conversion_action` par type et conversions
   30 j, comparées aux vraies demandes que l'utilisateur déclare ; Google
   sur-compte (clics sur le numéro, doublons) ou sous-compte ? Coût par VRAIE
   demande.
3. **Les groupes** : coût, impressions, clics, CTR, conversions par groupe ;
   bien réparti / un groupe mange tout (normal s'il rapporte) / dilué (plus
   de 4 groupes, 3-4 clics chacun → resserrer).
4. **Le taux d'impressions** (`metrics.search_impression_share` +
   `search_top_impression_share`) par groupe puis par mot-clé de tête :
   « marché » (≥ 85 %), « enchères » (30-45 % et budget non dépensé),
   « budget » (bas mais budget dépensé et demandes).
5. **Les mots-clés, triés par impressions** : intention d'achat ou curieux ;
   le rouge « enchère insuffisante » (`ad_group_criterion.position_estimates.
   first_page_cpc_micros` > enchère) est-il là sur ceux qui sortent le plus ?
   Pas de rouge + ça sort beaucoup = on surpaye → baisser ce mot-clé ;
   enchère max vs CPC moyen ; enchère réclamée énorme = un concurrent gagne
   sa vie dessus (ne pas le suivre pour autant).
6. **Les annonces** : titres avec longueur, personnalisateur de ville
   présent, villes en dur, mot-clé répété, bannis, majuscules, angle prix si
   les mots-clés parlent de prix, note Google (« moyenne » = très bien),
   URL finale = accueil.
7. **Les termes de recherche** (`search_term_view`, toute la période) : top
   30 par coût sans conversion, classés → candidats négatifs (P4) ; part des
   termes « prix / combien / tarif » (→ angle prix dans les titres).
8. **La décision, UNE SEULE**, avec le chiffre qui la justifie :
   LAISSER (saine : ne rien toucher) / ACCÉLÉRER (plafond tapé + demandes, ou
   artisan closé → +5 €/jour de budget) / DIFFUSER (budget non dépensé +
   taux d'impressions bas → P2, +20 %) / RESSERRER (dilué → 3-4 groupes, les
   autres en pause) / COUPER (seuils ci-dessus). Ou « n'y touche pas,
   reviens dans X jours ». Aucune écriture.

## P2 — La campagne ne dépense pas (kickstart, puis +20 %)

Avant : campagne lancée aujourd'hui → attendre demain matin (elle doit
dépenser dans les heures qui suivent) ; budget déjà dépensé à > 70 % → pas de
kickstart. Campagne/groupes/annonces bien ENABLED et approuvés, sinon c'est
ça le problème (une campagne sans annonce ne dépense pas). Relever les
enchères actuelles (mots-clés et groupes) et les NOTER : elles servent à la
redescente.

**Cas A — au démarrage, elle ne dépense (presque) rien** (n°2, n°4, n°7) :
- **DOUCE** : palier n°1 et 2 = +50 % sur toutes les enchères, à partir du
  n°3 = +30 %. Un palier par jour plein tant que rien ne part (« si demain
  les 10 € ne sont toujours pas dépensés, remonte », n°4 · P1 @49:54) ; la
  règle des 72 h reprend dès que la campagne dépense.
- **FORTE** : chaque enchère = max(3 × actuelle, 3 €), plafond de
  l'utilisateur jamais dépassé. Pour ceux qui ont fait 2 paliers doux sans
  résultat ou n'ont pas la patience (« Léo préfère griller un ou deux jours
  de budget, puis redescendre »).
- **REDESCENTE** (après FORTE, dès que ça clique, 2-3 jours) : **en une
  fois**, quasiment à l'enchère d'avant le kickstart **+20 à 30 %** —
  l'enchère de départ ne suffisait pas. **Jamais par paliers de -30 %** : une
  semaine à 3-5 € le clic vide le budget d'un membre. Enchères d'avant
  introuvables (journal, `change_event`) → milieu de la fourchette du kit
  + 20 %. Si la diffusion retombe ensuite : +30 %, et on en reste là.

**Cas B — elle a déjà tourné et cliqué, mais ne dépense pas son budget** :
vérifier d'abord le taux d'impressions. Bas (30-45 %) → enchères trop
basses : **+20 % sur tous les mots-clés** (30 % maxi, jamais ×2), puis
72 h ; si les courbes (impressions, clics, coût) ne montent pas, encore
+20 % (n°6 · P2 @33:40). Si la répartition entre mots-clés est déjà bonne, on
monte tout du même pourcentage ; sinon seulement ceux qui rapportent le plus
à l'artisan, pas ceux déjà au-dessus de 80 % de taux d'impressions. Taux
≥ 85 % et budget non dépensé → ce n'est pas l'enchère : la zone manque de
recherches (ajouter un service de l'artisan, ou une autre zone).
Cette hausse uniforme, l'utilisateur peut aussi la faire lui-même dans
l'interface en deux clics (Mots-clés → tout cocher → Modifier les enchères →
Augmenter de 20 %) : le lui dire.

Rien ne bouge même en FORTE → le problème n'est pas l'enchère (annonce
refusée, zone minuscule, mots-clés sans recherche). Budget inchangé.
Écriture : `ad_group_criterion.cpc_bid_micros` (+ groupes) en une requête
mutate, `<client>/kickstart.py --dry/--apply`, relecture GAQL.

## P3 — Titres d'annonces (CTR)

Les règles de [rsa-et-assets.md](rsa-et-assets.md) s'appliquent toutes :
titre épinglé n°1 = service + `{LOCATION(City):<ville>}` ; plus aucune ville
en dur ; mot-clé du groupe pas répété ; ≤ 25 caractères (28 absolu) ; une
majuscule à chaque mot et « & » ; chaque titre a du sens seul ; la poubelle
(« Un Humain Vous Répond », « Votre Devis Par Téléphone », « mise en
relation », « partenaire », titres techniques) ; l'angle prix si les
mots-clés le contiennent ; réassurance « Devis & Déplacement Gratuits »,
« On Vous Rappelle Sous 24 h » ; CTA courts ; personnalisateur d'appareil ;
15 titres remplis. Lire le site (WebFetch) pour les preuves ; demander les
annonces des concurrents que l'utilisateur voit en tapant « service + sa
ville ». Ne pas « trouver de bons titres » au hasard : expliquer POURQUOI
chaque ancien titre est mauvais (il ne rassure pas, ne dit pas pourquoi
choisir cette entreprise, il est redondant). Tableau titre par titre
(garder / réécrire / supprimer + raison), annonce avant/après par groupe,
2 combinaisons de 3 titres pour montrer que ça tient, longueurs et règles
vérifiées par script, puis **affiche les RSA à l'utilisateur et attends son
accord avant le `--dry`/`--apply`**. Écriture `<client>/titres.py`. Le
nouveau CTR se juge après 3 jours et ≥ 100 impressions par annonce.

## P4 — Mots-clés négatifs (2 fois par semaine, dès les premiers clics)

Lire TOUS les termes de recherche de la période (pas que 50), les négatifs
déjà en place, et signaler tout mot-clé LARGE (à passer en expression/exact
dans le même script). Juste après le lancement, ne rien trouver est normal :
il faut 2-3 jours de data. Classer les hors-sujet par catégorie avec le coût
cumulé : emploi/formation (alternance, cv, salaire, cap, bts, stage),
curieux/soi-même (comment, tuto, astuce, idée, réglementation, distance
voisin, quand tailler), matériel/produits (tronçonneuse, location, leroy
merlin, castorama, amazon, bois de chauffage), hors zone, hors métier
(variables de l'utilisateur), concurrents et noms propres, gratuit seul /
aides. Dire combien a été « dépensé dans le vent ».
Nuances : « devis gratuit » est bon ; « prix / tarif / combien » ne sont PAS
des négatifs par défaut (coaching n°6 : c'est ce qui intéresse les gens, on
les capte avec un titre « Obtenez Un Prix ») — « prix » seul sans service =
regarder ce qu'il a rapporté avant d'exclure ; ne jamais exclure un terme
service + ville de la zone ni un terme qui a converti ; les termes qui
tombent dans un groupe en pause, on s'en fiche ; en cas de doute, garder et
le dire. Ajouter 3-5 « bonnes surprises » (termes non ciblés, pile le métier,
qui cliquent) en mots-clés. Liste finale validée par l'utilisateur, puis
TOUS les termes validés AJOUTÉS (pas seulement listés) :
`<client>/negatifs.py` : `shared_criterion` dans la liste de la campagne
(créer + lier si absente), expression par défaut, accentué en double.
N'oblige pas à attendre 72 h.

## P5 — Optimisation des enchères (≥ 10-15 demandes, une dimension, par phases)

Garde-fous : < 10 demandes → refuser (« on optimiserait de la variance ») ;
Google compte beaucoup plus ou moins que l'utilisateur → P6 d'abord ;
dernier changement < 72 h → attendre ; une dimension par session :
MOTS-CLÉS (`ad_group_criterion.cpc_bid_micros`), VILLES
(`campaign_criterion` location `bid_modifier`, lecture `geographic_view`),
JOURS-HEURES (`ad_schedule` + `bid_modifier`, lecture
`segments.day_of_week` / `hour`), AUDIENCE (`age_range` / `gender` au groupe,
`device` à la campagne).
Pour chaque ligne : part des clics vs part des conversions ; l'écart entre
les deux est le signal (30 % des clics pour 14 % des demandes = trop payé ;
3 % des clics pour 23 % des demandes = sous-payé). Pousser une ligne
seulement avec **≥ 5 conversions** dessus (n°3) ; conclure qu'elle dépense
pour rien avec ≥ 30 clics sans conversion. Toujours au niveau des
MOTS-CLÉS, pas de l'enchère du groupe (« des fois c'est différent »).
**Par phases, c'est la règle** : une phase = **+20 % (jamais > +30 %)** sur
une ligne qui convertit mieux que la moyenne et sous le prix maxi de
l'utilisateur, **-30 %** sur une ligne qui dépense sans convertir (exclusion
seulement si franchement hors cible, jamais couper ce qui rapporte un peu),
**baisser** un mot-clé qui sort beaucoup SANS la mention rouge « enchère
insuffisante » (ex. 1,60 → 1,30 €), **3 lignes maxi**, budget inchangé, CPC
manuel. Pas de « ×2 le mardi » : on y arrive par phases, avec des mois de
data. Puis **7 jours** ; la phase a tenu si impressions/clics ≥ semaine
précédente, budget toujours dépensé, coût par demande pas monté, ligne
poussée convertit toujours → phase suivante, même petit pas, jusqu'à ce que
le gain s'aplatisse ; un des trois lâche → retour à la phase précédente, on
arrête sur cette dimension. Après une baisse, vérifier 2-3 jours plus tard
qu'on n'a pas trop baissé. Écriture `<client>/encheres_<dimension>.py`.

## P6 — Conversions et URL finales

Conversions : les 3 actions de la section « Conversions » de
[api-google-ads.md](api-google-ads.md) ENABLED et principales (formulaire,
appels depuis le site ≥ 30 s, appels depuis les annonces ≥ 30 s) +
`call_reporting_setting`. **Une conversion « clic sur le numéro » encore
principale → la passer en secondaire** (`primaryForGoal: false`) : un clic
n'est pas une demande (n°6 · P1 @15:23) ; et faire retirer `GADS_CLIC_TEL`
des variables Vercel du site. Conversions 30 j par action vs vraies demandes
déclarées (Google compte avec 2-3 h à 2 jours de retard : tolérer un peu
moins, pas beaucoup moins, jamais zéro avec des demandes ; deux fois plus de
conversions que de demandes = doublons) ; créer/corriger ce qui manque
(`--dry/--apply`) ; site : liens `tel:`, ligne `/api/suivi` dans chaque page,
donner les valeurs Vercel attendues depuis les `tag_snippets` ; **test**
décrit pas à pas si pas fait — tant qu'il n'est pas passé, le suivi n'est pas
en place.
URL finales : chaque RSA → accueil du site (site du pack : accueil avec
`?travaux=<service>`, « plus rassurant que le tunnel »), jamais une page
tunnel `devis-*.html` ni une 404 ; sitelinks vers des pages qui existent ;
WebFetch chaque URL. Si Google ne comptait pas (ou comptait les clics tel) :
les conversions d'avant ne valent rien, on recompte de zéro pour P5.

## P7 — Le site (dans le dossier du site, pas celui du skill)

Pas une procédure Google Ads : l'utilisateur la lance avec ses fichiers
.html. Les corrections : pop-up Clarity supprimé, aucun pop-up « laissez
votre numéro » ; premier écran mobile complet (service + département —
« dans tout le Tarn », pas trois villes —, promesse **« On vous rappelle,
devis et déplacement gratuits sous 24 h »**, zones, note Google, numéro
cliquable, bouton devis) ; **jamais « mise en relation », « artisans
partenaires », « un élagueur de votre secteur »** : on est l'entreprise,
« on se déplace » (décision du 07/11) ; près du formulaire : « Remplissez le
formulaire pour obtenir un prix en 2 minutes » (n°6) ; avis juste sous le
premier écran (jamais d'avis « exemple ») ; « Pourquoi nous » + avant/après
avant les listes de services ; pavé du haut réduit à 3 lignes ; tunnel sans
bouton retour, « Étape 1 sur 2 · 30 secondes » ; photos qui évoquent la
région ; mentions obligatoires tout en bas. Le CTR dépend des annonces, pas
du site ; le site, c'est le taux de conversion. Moteur du site
(`api/suivi.js`, formulaire, `tel:`) intact et vérifié après chaque
modification. Se mettre à la place d'une grand-mère perdue sur son téléphone.
Un seul changement de site à la fois ; pour le juger, un A/B test à nombre
de clics égal (« on fait un A/B test »), pas « un jour ou deux ».

## Le journal de campagne

À la fin de chaque procédure qui écrit, dicter la ligne : date, procédure,
changement (chiffres avant → après), chiffre à suivre, date à laquelle
regarder (72 h plus tard au plus tôt), résultat. Pas de nouvelle ligne tant
que la date de la précédente n'est pas passée. L'utilisateur connaît par
cœur, par zone : dépensé, vraies demandes, coût par demande (n°7 · P1
@27:30).
