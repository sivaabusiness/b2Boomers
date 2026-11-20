# RSA, assets et images

Règles issues des coachings de Léo (n°2 du 18/10, n°4 du 25/10, n°6 du 02/11,
décisions du 07/11 ; la session la plus récente gagne). Elles s'appliquent
DÈS LA CRÉATION de la campagne, pas seulement en correction (P3).

## RSA — une annonce par groupe

15 titres (tous remplis : plus de combinaisons à tester) + 4 descriptions
(≤ 90) + path1/path2 (≤ 15 chacun). Valider TOUTES les règles par script
avant livraison avec `scripts/verif_rsa.py <client>/rsa.json` (il applique
tout ce fichier : longueurs avec texte de secours, poubelle, villes en dur,
personnalisateur et épinglage, majuscules, « & », angle prix, mot-clé
répété, 3-4 groupes — zéro ERREUR avant de montrer les annonces) :
pas de doublon de titre, pas de « ! » dans un titre (max 1 par
description), pas de tout-majuscules, pas de numéro de téléphone dans le
texte (motif regex \d{2}[\s.]?\d{2}…) — le téléphone passe par l'asset
d'appel, sinon refus Google.

### Ce qu'on est, ce qu'on promet (décision de Léo, 07/11)

L'annonce et le site parlent comme L'ENTREPRISE qui se déplace, jamais comme
un intermédiaire : **jamais « mise en relation », « artisans partenaires »,
« un artisan de votre secteur », « réseau d'artisans »** (n°6 · P1 @12:58).
La promesse, partout où elle a sa place (titres, descriptions, callouts) :
**« On vous rappelle, devis et déplacement gratuits sous 24 h »**.

### Le titre épinglé n°1 : le mot-clé + la ville de la personne

- **Le service du groupe sort TOUJOURS en premier** : un titre épinglé en
  position 1 (`pinnedField: "HEADLINE_1"`) qui reprend le mot-clé du groupe
  et le **personnalisateur de lieu** (n°6 · P2 @37:41 ; n°4 · P1 @8:13) :
  `Élagage {LOCATION(City):Belfort}` — Google y met la ville où se trouve
  la personne ; le texte après les deux-points est la ville principale de la
  zone, affichée quand Google ne connaît pas la ville. On peut épingler 2
  variantes en position 1 (ex. `Devis Élagage {LOCATION(City):Belfort}`),
  Google les fait tourner ; AUCUN autre épinglage.
- Variante insertion de mot-clé, seulement si TOUS les mots-clés du groupe
  sont des services propres (sinon un mot-clé « tarif » ferait un titre
  « Tarif ») : `{KeyWord:Élagage} {LOCATION(City):Belfort}` (KeyWord = une
  majuscule à chaque mot ; le texte de secours est le service).
- **Plus aucune ville en dur ailleurs** : le personnalisateur couvre les 60
  communes d'un département, les villes écrites en dur « prennent de la place
  pour rien » (n°6 · P1 @25:00, P2 @51:36). Exception : le nom du département
  dans UN titre de zone (« Dans Tout Le Tarn »).
- **Le mot-clé du groupe n'est pas répété** dans d'autres titres : le titre
  épinglé l'a déjà ; 3 titres « élagage » = 3 fois le même mot à rallonge
  (n°6 · P1 @24:06). Les SOUS-services, eux, ont chacun leur titre
  (« Taille De Haie » dans un groupe Entretien de jardin : le titre capte la
  recherche, n°6 · P1 @50:31).
- Si le `--dry` refuse la syntaxe d'insertion : montrer l'erreur exacte et
  proposer la forme acceptée, sans retirer d'autres titres.

### Les règles d'or des titres (vérifiées une à une, par script)

1. **COURT : viser 18-25 caractères, 28 maxi**, insertions comptées avec
   leur texte de secours (la limite API est 30, mais un titre long fait
   sauter le 3e titre sur mobile : « les titres longs ne sortent pas »,
   n°6 · P1 @24:50, @56:30). Le script signale tout titre > 25 et REFUSE
   > 28. Couper les mots inutiles (« 1 Devis Sans Engagement » → « Devis
   Sans Engagement ») et **écrire « & » au lieu de « et »** (n°6 · P2 @52:33).
2. **UNE MAJUSCULE À CHAQUE MOT** : « Devis & Déplacement Gratuits »,
   « Obtenez Un Prix Aujourd'hui » — « ça saute plus aux yeux » (n°6 · P2
   @52:33). Pas de tout-majuscules (refus Google). Les descriptions restent
   en phrases normales.
3. **AUTONOME : chaque titre se comprend SEUL.** Google assemble 3 titres au
   hasard parmi les 15 (n°2 · P1 @32:14). Test : lu isolément, on sait de
   quel service il s'agit OU ce qu'on doit faire. La réassurance ne voyage
   jamais seule : ✖ « Gratuit Et Sans Engagement » (gratuit QUOI ?) → ✔
   « Devis Gratuit Sous 24 h ».
4. **QUI RASSURE LE « PETIT VIEUX » qui tape « devis élagage »** : il veut
   savoir si ce sera bien fait, rapide, si l'entreprise est sérieuse et
   combien ça coûte (n°6 · P1 @22:30). Chaque titre = un argument, une
   douleur, un bénéfice daté/chiffré ou un ordre clair. BANNIS (vocabulaire
   bateau) : « qualité », « sérieux », « professionnel », « savoir-faire »,
   « à votre service », « votre expert », « confiance », tout superlatif.

### La poubelle (le script REFUSE ces titres)

- **« Un Humain Vous Répond »** — banni (n°2 · P1 @31:22 ; n°6 · P1 @22:30).
- **« Votre Devis Par Téléphone »** — « non, les gens veulent quelqu'un qui
  se déplace » (n°6 · P1 @23:30).
- **« mise en relation », « partenaire(s) »** — on est l'entreprise (07/11).
- Les titres techniques ou sans apport : « Branches Broyées », « Bois Mort
  Retiré », « Bois Coupé En Bûches », « Abattage Près Des Maisons »,
  « Élagage Corde Ou Nacelle » (n°2 · P2 @14:13 ; n°6 · P1 @22:30) — et
  plus largement le jargon de chantier (corde, nacelle, étêtage, rognage).
- Deux titres quasi identiques : en garder un. Cinq titres qui ne disent que
  la ville ou le mot-clé = « un tiers de tes titres ne servent à rien »
  (n°6 · P1 @12:13, @21:10).

### Ce qui marche (titres validés par Léo)

- **Réassurance / promesse** : « Devis & Déplacement Gratuits », « Visite &
  Devis Gratuits » (« il me rassure »), « Devis Gratuit Sous 24 h », « On
  Vous Rappelle Sous 24 h », « Devis Écrit Avant Travaux », « Devis Sans
  Engagement », « Devis En 2 Minutes », « Chantier Propre »
  (n°2 · P1 @31:16, P2 @14:39 ; n°6 · P1 @22:30, @24:06, P2 @40:30).
- **Angle prix** — beaucoup de recherches contiennent « prix », « combien » :
  « Obtenez Un Prix Aujourd'hui », « Prix Honnête », « Tarif Raisonnable »
  (pas forcément « pas cher » : « c'est d'avoir un prix qui les intéresse »).
  **Obligatoire si des mots-clés du groupe contiennent « prix » ou « tarif »**
  : au moins un titre avec « Prix » ou « Tarif » (n°6 · P1 @26:35, P3 @12:00).
- **Accroches problème** (le vrai souci du client, propre au métier) :
  « Branche Qui Touche La Maison », « Arbre Fragile Face Au Vent », « Bois
  Mort, Branche Cassée », « Lierre Qui Grimpe » (n°6 · P1 @55:29).
- **Sous-services** du groupe, un titre chacun : « Abattage D'arbres Morts »
  (« la RSA le sortira à qui tape ça », n°2 · P2 @15:20).
- **Confiance, avec des chiffres RÉELS seulement** (pris sur le site de
  l'utilisateur, jamais inventés) : « 15 Ans D'expérience », « Noté 4,9/5 Sur
  Google », « 200 Clients Satisfaits », « Artisan Local Assuré » si c'est
  vrai (n°6 · P1 @25:50, @56:30).
- **CTA courts** quand il reste de la place : « Contactez-Nous », « Appelez-
  Nous Aujourd'hui » — « un tout petit truc comme ça booste ton CTR de 5 % »
  (n°6 · P1 @57:00).
- **Personnalisateur d'appareil** (n°4 · P1 @10:40) : un titre
  `{=IF(device=mobile,Appelez-Nous Maintenant):Remplissez Le Formulaire}`
  — sur mobile on pousse l'appel, sur PC le formulaire ; les deux branches
  respectent la règle de longueur. Refusé au `--dry` → deux CTA simples.
- **La saison**, au bon moment (pic de la zone) : « On Passe Avant L'hiver ».
- Une question : 1 MAXIMUM, et seulement visuelle et précise.

### Le mix des 15 titres

- **1-2 titres épinglés en position 1** : service + `{LOCATION(City):…}`.
- **3-4 réassurance / promesse** (devis & déplacement gratuits, sous 24 h,
  on vous rappelle, devis écrit avant travaux).
- **1-2 angle prix** (obligatoire si les mots-clés parlent de prix/tarif).
- **3-4 sous-services ou accroches problème** (ceux du groupe regroupé).
- **2-3 confiance chiffrée réelle** (années, note, avis, chantiers, assuré).
- **2 CTA** (dont le titre conditionnel appareil).
- **0-1 zone ou saison** (« Dans Tout Le <Département> », le pic Atlas).
- Pas de template universel : « ça dépend de ce que les concurrents font »
  (n°6 · P1 @21:40). Demander à l'utilisateur les annonces concurrentes qu'il
  voit en tapant « service + sa ville » (Google ne montre pas les annonces
  hors de sa position) et se distinguer : au moins 3-5 titres qui ne marchent
  QUE pour cet artisan, cette zone ou cette saison.
- Uniquement des faits relevés sur les pages du client. Pas de
  « certifié/assuré » ni de chiffre non vérifié.

### Les 4 descriptions

1. Services + promesse : « Élagage, abattage, taille de haie : on se
   déplace, devis gratuit sous 24 h. »
2. Le formulaire : « Remplissez le formulaire pour obtenir un prix en 2
   minutes. On vous rappelle sous 24 h. » (« le conseil de la soirée »,
   n°6 · P3 @13:35).
3. Preuve réelle + zone : note Google, années, « dans tout le <département> ».
4. Double CTA : « Appelez-nous ou laissez votre demande : devis et
   déplacement gratuits. » (description validée aussi : « On vous rappelle
   sous 24 heures », n°6 · P1 @13:30).
Mêmes interdits que les titres (jamais « mise en relation », « partenaire »,
« par téléphone »). Paths : mot-clé du groupe + département ou ville
principale (`/elagage/vendee`).

### Montrer avant d'écrire

Les titres et descriptions s'affichent à l'utilisateur dans un tableau
(titre, longueur, rôle dans le mix) AVANT tout `--apply` : « affiche-moi les
RSA avant d'appliquer » (n°6 · P2 @41:00). Lui rappeler de les RELIRE et de
regarder l'aperçu PC et mobile dans Google Ads (le crayon de l'annonce) :
« ne faites pas confiance aveuglément à Claude » (n°6 · P1 @20:15, @23:44).
Lui montrer 2 combinaisons de 3 titres tirées au hasard pour prouver que ça
tient. Note Google « moyenne » = très bien ; « médiocre » seulement est un
mauvais signe (n°6 · P1 @20:00).

### Campagnes déjà en ligne avec d'anciens titres

Si le compte contient des RSA qui violent ces règles (titres > 25, bannis,
villes en dur, pas de personnalisateur, mot-clé répété, sans majuscules) :
les lire (GAQL `ad_group_ad`), proposer la réécriture complète selon le mix
ci-dessus, tableau avant/après, `--dry` puis `--apply` par l'utilisateur,
comme toute écriture. Le nouveau CTR se juge après 3 jours et ≥ 100
impressions par annonce.

## Assets (extensions) niveau campagne

- **Appel** : le numéro du client, pays FR. Suivi d'appels par le numéro de
  transfert Google : seuls les appels de 30 s et plus comptent comme
  conversion (un vrai appel reçu = une vraie demande ; un clic sur le
  numéro n'en est pas une, n°6 · P1 @15:23).
- **Sitelinks** : 4, un par service (titre ≤ 25, 2 descriptions ≤ 35). Site du
  pack → sa page tunnel `devis-<service>.html` (titre « Devis dessouchage »…) ;
  autre site → la page du service. Quatre URL différentes.
- **Callouts** : ~8 (≤ 25, une majuscule à chaque mot) : « Devis Gratuit »,
  « Déplacement Gratuit », « On Vous Rappelle Sous 24 h », « Devis Sans
  Engagement », « Devis Écrit Avant Travaux », « Prix Clair », « Dans Tout Le
  <Département> », la note Google réelle, les spécialités. Mêmes interdits
  que les titres (jamais « mise en relation » ni « partenaire »).
- **Extrait structuré** : en-tête « Services » + les services (≤ 25 chacun,
  min 3).
- Conversion formulaire = celle de la landing page (asset formulaire Google
  optionnel).

## Images

### Specs Google (assets image, campagne Search)

- Paysage 1,91:1 : min 600×314 (reco 1200×628).
- Carré 1:1 : min 300×300 (reco 1200×1200).
- Logo : 1:1, min 128×128, fond propre. ≤ 5,2 Mo, JPG/PNG.

### Préparation depuis les photos client

Typiquement des photos 4:3 (1024×768) et des montages avant/après côte à
côte. Recettes :

- Paysage : le diptyque entier recadré verticalement (1024×536) — le format
  avant|après est très vendeur tel quel.
- Carré : UNE moitié du diptyque (512×768 → crop 512×512). Choisir la moitié
  qui raconte le service : l'« après » quand le résultat est spectaculaire
  (arbre sculpté, cercle de copeaux) ; l'« AVANT » quand le problème vend
  mieux que le résultat (arbre penché menaçant pour l'abattage — l'après
  « jardin vide » ne dit rien).
- REGARDER chaque crop généré (Read) : un crop centré peut couper le sujet
  (visages en haut → ancrer haut ; cercle de copeaux en bas → ancrer bas).
- Logo : canvas carré exact, fond blanc, RGB.
- Photo d'équipe (tenue de la marque) : excellent signal de confiance, en
  paysage + carré au niveau campagne.

### Compte trop récent

Google refuse les images sur un compte neuf (`UNSUPPORTED_FIELD_TYPE` sur
`AD_IMAGE`) : ça se débloque au bout d'une ou deux semaines. Préparer les
visuels et le script, et dire à l'utilisateur de réessayer chaque semaine
(test rapide : ajouter une image à une annonce dans l'interface ; si Google
laisse enregistrer, relancer le script sur toutes les campagnes). Les images
augmentent « carrément » le CTR (n°6 · P1 @25:12, P2 @38:30).

### Liaison

- Images service → niveau AD GROUP, field type **`AD_IMAGE`** (2 paysages +
  1 carré par groupe). `MARKETING_IMAGE`/`SQUARE_MARKETING_IMAGE` sont
  REFUSÉS sur les liens Search (`assetLinkError: UNSUPPORTED_FIELD_TYPE`) —
  c'est du Performance Max.
- Équipe → niveau campagne, `AD_IMAGE`.
- Logo → niveau campagne, `BUSINESS_LOGO` (accepté par l'API ; l'affichage
  peut exiger la vérification d'identité annonceur dans l'interface — le dire
  à l'utilisateur).
