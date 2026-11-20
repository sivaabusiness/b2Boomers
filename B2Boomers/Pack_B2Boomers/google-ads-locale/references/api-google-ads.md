# API Google Ads (REST) — création de campagne et pièges connus

Tout passe par `scripts/google_ads_client.py` (auth refresh token, backoff
429/5xx, search GAQL, mutate). Version : voir `API_VERSION` ; les versions
sont dépréciées vite (~1 an), re-sonder en cas d'`UNSUPPORTED_VERSION`.

## Le flux d'écriture en deux temps

1. Construire TOUTES les opérations dans une seule requête
   `customers/{cid}/googleAds:mutate` avec des resource names temporaires
   négatifs (`customers/{cid}/campaigns/-2`…) — l'API valide le graphe entier.
2. `--dry` : la même requête avec `"validateOnly": true` — exécutée par toi,
   aucune écriture, les erreurs sortent avec le chemin du champ fautif.
   Corriger jusqu'à zéro erreur.
3. `--apply` : la même requête sans validateOnly — **exécutée par
   l'utilisateur** (le contrôle de permissions bloque les écritures de compte
   lancées par Claude ; donner la commande en PowerShell, séparateur `;`).
4. Relire le compte en GAQL et recompter tout (campagne, critères, groupes,
   mots-clés par correspondance, annonces, assets, négatifs).

## Réglages de campagne qui ont fait leurs preuves (artisan local)

Règles des coachings de Léo (n°2 → n°7, la plus récente gagne).

- **Une campagne = une zone** (un secteur ou un département), avec SON
  budget. Deux zones = deux campagnes, jamais deux zones fusionnées dans une
  campagne (« ça fausse toutes les stats », n°6 · P2 @10:35) ; même métier
  pour les deux au début (n°7).
- `status: PAUSED` à la création — l'utilisateur active, **le jour même**
  dès que le test des conversions est passé : « plus vite c'est activé, mieux
  c'est » (n°4 · P1 @52:26).
- `manualCpc: {}` (l'eCPC n'existe plus). Jamais d'enchères automatiques ni
  « maximiser les clics » : vérifier dans les paramètres que la campagne est
  bien en CPC manuel et ignorer l'avertissement de Google (n°4 · P1 @55:10).
- **Enchère PAR MOT-CLÉ, pas uniforme** (« les CPC ne sont pas les mêmes sur
  chaque mot-clé », n°6 · P1 @3:20, @13:45) : `cpcBidMicros` sur chaque
  `adGroupCriterion` = le milieu de sa fourchette du kit
  ((`cpc_bas` + `cpc_haut`) / 2, arrondi à 0,05 €) — de quoi dépenser dès
  les premières heures (n°7 · P2 ~@29:10) sans surpayer ; un seul des deux
  publié → celui-là ; n/d → la médiane du groupe. Le `cpcBidMicros` du
  groupe = la médiane de ses mots-clés (filet de sécurité). Étiqueter ces
  enchères « départ, à ajuster » dans le récapitulatif.
- **Budget quotidien : 10 à 15 €/jour par campagne au départ**, et **au moins
  10 clics par jour** : clics/jour ≈ budget ÷ CPC bas médian des mots-clés
  retenus ; sous 10, le dire (« à 2 € le clic pour 10 €/jour, ça va
  ramer », n°7 · P1 @56:49) et proposer 15 €/jour ou de garder les groupes
  les moins chers. Jamais de « budget du mois ÷ 30 » : le budget ne se
  divise pas entre les zones, on coupe vite celle qui ne marche pas
  (pilotage-campagne.md, « Couper »).
- `networkSettings` : Google Search seul (tout le reste false).
- **Ciblage = la zone du kit** (depuis le 03/11, les zones sont des secteurs de
  communes qui ne se chevauchent pas) : un critère `location` POSITIF par commune
  de `communes` (geoTargetConstant trouvé par `suggest_geos`, type City ; le code
  INSEE et le département départagent les homonymes ; une commune que Google ne
  connaît pas comme City → son code postal). Si `tout_dept` est vrai : le seul
  geoTargetConstant du département. Ni `proximity` ni rayon (il déborde sur les
  secteurs voisins, vendus à d'autres), pas de négatifs géographiques à ajouter.
- **Ajustements par commune de la fiche Atlas, dès le lancement** (« étape
  zappée par tous », n°4 · P1 @14:08, @15:00) : si l'utilisateur a téléchargé
  la fiche de sa zone dans l'Atlas, appliquer « Où enchérir plus » en
  `bidModifier` = 1 + N/100 sur les critères `location` DÉJÀ dans le secteur
  (plafond +25 %, jamais plus que la fiche) et les lignes « à exclure ou
  −30 % » en `bidModifier` 0.70 (exclusion seulement s'il le demande —
  « les exclusions sont très importantes », ne pas les oublier). Jamais de
  commune hors du secteur. Pas de fiche → le proposer pour plus tard.
- `geoTargetTypeSetting` : PRESENCE / PRESENCE (gens physiquement là).
- Langue : critère `language` avec wrapper `{"languageConstant":
  "languageConstants/1002"}`.
- `containsEuPoliticalAdvertising: "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"`
  (obligatoire UE).
- Négatifs : `sharedSet` NEGATIVE_KEYWORDS + `sharedCriterion` × N +
  `campaignSharedSet`. Large→BROAD, Expression→PHRASE.
- Groupes : **3-4 maximum** (n°6 · P1 @46:50), `SEARCH_STANDARD`, ENABLED
  (la pause campagne suffit), `cpcBidMicros` en chaîne. Un groupe en trop
  se met en PAUSE, il ne se supprime jamais.
- Mots-clés : `adGroupCriterion` keyword EXACT/PHRASE avec son
  `cpcBidMicros` (voir plus haut), pas d'URL au niveau mot-clé.
- RSA : `adGroupAd` avec `responsiveSearchAd` (headlines avec `pinnedField:
  "HEADLINE_1"` pour le titre « service + `{LOCATION(City):<ville>}` »
  seulement), `path1/path2`, `finalUrls`. Les insertions s'écrivent telles
  quelles dans le texte du titre (`{LOCATION(City):Belfort}`,
  `{KeyWord:Élagage}`, `{=IF(device=mobile,Appelez-Nous Maintenant):Remplissez
  Le Formulaire}`) ; la longueur se compte sur le texte de secours.
- Assets : `callAsset` (numéro national + countryCode FR, et
  `callConversionReportingState: "USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION"` —
  voir Conversions), `sitelinkAsset`
  (finalUrls au niveau Asset), `calloutAsset`, `structuredSnippetAsset`
  (header localisé « Services ») ; liaison `campaignAsset` avec fieldType
  CALL / SITELINK / CALLOUT / STRUCTURED_SNIPPET.
- Images : `imageAsset: {"data": "<base64>"}` ; liaison en **AD_IMAGE**
  (groupe ou campagne), logo en BUSINESS_LOGO campagne. Voir
  rsa-et-assets.md.

## Conversions — obligatoires, une fois par compte (avant la 1re campagne)

Sans conversions, le compte optimise à l'aveugle (« 20 000 € dépensés sans
tracking », n°3). Mais une conversion doit être une VRAIE demande : un
formulaire rempli ou un appel réellement reçu. **Un clic sur le numéro n'est
pas une demande** (bots, clics depuis un PC sans appel, doublons avec le
formulaire) : « si vous ne voulez pas optimiser sur de la merde comme ça,
enlevez la conversion appel », on ne compte que les vrais trucs (n°6 · P1
@15:23, P2 @7:10). Le site trace toujours les clics sur le numéro de son côté
(notif Telegram du criquet, liste dans `/demandes` — moteur du site,
`api/suivi.js` + `api/appel.js`) : c'est une info, pas une conversion.

1. Vérifier en GAQL qu'elles n'existent pas déjà (par nom), puis les créer en
   une requête mutate (`conversionActionOperation.create`), en `--dry` puis
   `--apply` comme le reste :

| name | type | category | en plus |
|---|---|---|---|
| Formulaire (site) | `WEBPAGE` | `SUBMIT_LEAD_FORM` | `countingType: ONE_PER_CLICK` |
| Appels depuis le site | `WEBSITE_CALL` | `PHONE_CALL_LEAD` | `phoneCallDurationSeconds: 30` |
| Appels depuis les annonces | `AD_CALL` | `PHONE_CALL_LEAD` | `phoneCallDurationSeconds: 30` |

   Pour toutes : `status: ENABLED`, `primaryForGoal: true`,
   `countingType: ONE_PER_CLICK` (une personne = une demande, même si elle
   rappelle), `clickThroughLookbackWindowDays: 30`, `valueSettings:
   {"defaultValue": 1, "alwaysUseDefaultValue": true}`.
   **Pas de conversion « Clic sur le numéro »** (`CLICK_TO_CALL`). Si le
   compte en a une (anciens packs) : `conversionActionOperation.update` avec
   `primaryForGoal: false` (elle passe en « secondaire » : visible, mais elle
   ne compte plus dans la colonne Conversions), `--dry` puis `--apply`. Le
   rapport quotidien le signale (alerte `conversion_clic_tel`).
2. Appels depuis l'annonce : `customerOperation.update` sur
   `customers/{cid}` avec `callReportingSetting: {callReportingEnabled: true,
   callConversionReportingEnabled: true, callConversionAction:
   "customers/{cid}/conversionActions/{id de « Appels depuis les annonces »}"}`
   (`updateMask` : les trois chemins), et le `callAsset` de la campagne en
   `USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION`.
3. Relire : `SELECT conversion_action.id, conversion_action.name,
   conversion_action.type, conversion_action.tag_snippets FROM
   conversion_action WHERE conversion_action.status = 'ENABLED'`. Dans chaque
   `event_snippet`, la ligne `'send_to': 'AW-123456789/AbC-dEf'` donne
   l'identifiant (avant la barre, le même partout) et le libellé (après).
4. Donner à l'utilisateur les **variables Vercel de son site** (Settings →
   Environment Variables, puis redéployer) — il ne colle AUCUN code :
   `GADS_ID` (AW-…), `GADS_FORMULAIRE`, `GADS_APPEL_SITE` (libellés des deux
   actions du site) et `GADS_NUMERO` = son numéro écrit EXACTEMENT comme sur
   le site (Google le remplace par un numéro de transfert pour les visiteurs
   venus de la pub). `GADS_CLIC_TEL` reste VIDE (supprimer la variable si
   elle existe, puis redéployer) : le clic sur le numéro n'est plus une
   conversion.
5. **Lui faire faire le test des 3 appuis** (guide du site, étape 9 C) :
   site ouvert avec `?gclid=test`, « Accepter » sur le bandeau, 3 appuis sur le
   numéro à 30 s d'écart → 3 notifs Telegram + 3 lignes dans `/demandes` (le
   suivi du site, pas une conversion Google) ; 1 formulaire test → l'événement
   « conversion » du formulaire visible dans Tag Assistant.
   Ne pas annoncer le suivi comme en place avant ce test. Le site doit avoir
   son numéro en lien `tel:` partout et la ligne `/api/suivi` (ou
   `/api/clarity`) dans chaque page — sinon, le dire et donner la consigne du
   guide (« site déjà en ligne »).

## Pièges rencontrés (tous vérifiés)

| Symptôme | Cause / correction |
|---|---|
| `PAGE_SIZE_NOT_SUPPORTED` sur search | Ne pas envoyer `pageSize` (fixe à 10 000). |
| `EXPECTED_REFERENCED_FIELD_IN_SELECT_CLAUSE` | Tout champ utilisé en WHERE doit être dans le SELECT. |
| `Invalid value … LanguageInfo` | Le critère langue attend l'objet wrapper, pas la string. |
| `keywordPlanIdeaError: INVALID_VALUE` sur geo_target_constants | Deux causes vues : un geo de type Postal Code (retirer — la campagne, elle, le supporte), OU plus de 10 geos dans la requête (le Keyword Planner plafonne à 10 : échantillonner les communes les plus peuplées). |
| `assetLinkError: UNSUPPORTED_FIELD_TYPE` (MARKETING_IMAGE) | Sur Search, lier les images en `AD_IMAGE`. |
| `assetLinkError: UNSUPPORTED_FIELD_TYPE` (AD_IMAGE) sur un compte NEUF | Les assets image exigent l'éligibilité du compte (ancienneté/activité/conformité). Un compte créé le jour même les refuse, campagne comme groupe ; un compte ancien les accepte. Préparer les visuels + le script, ré-exécuter quand le compte a tourné. |
| `assetLinkError: CUSTOMER_NOT_VERIFIED` (BUSINESS_LOGO) | Le logo d'entreprise exige la vérification d'identité annonceur (à faire dans l'interface). Réessayer après validation. |
| `USER_PERMISSION_DENIED` KeywordPlanIdeaService sur un compte client | Essayer les autres comptes, puis le manager en customer_id. |
| Écriture bloquée par le classifier de permissions | Normal : donner la commande `--apply` à l'utilisateur (PowerShell : `;`, jamais `&&`). |
| Volumes tous à 0/10 sur petite zone | Tranches Google, pas un bug. Écrire « n/d » quand la métrique est absente. |

## Vérifications GAQL utiles (relecture post-création)

- Campagne : `SELECT campaign.id, campaign.name, campaign.status,
  campaign.bidding_strategy_type, campaign_budget.amount_micros FROM campaign`
- Critères : type + negative + proximity.radius + location.geo_target_constant
  depuis `campaign_criterion`.
- Comptes mots-clés : `ad_group_criterion` type KEYWORD, grouper par
  ad_group.name et match_type.
- Annonces : `ad_group_ad.policy_summary.approval_status` (UNKNOWN = examen en
  attente, normal en pause).
- Assets liés : `campaign_asset.field_type` / `ad_group_asset.field_type`.
- Négatifs : `shared_criterion` filtré sur le nom de la liste.
- Conversions : `conversion_action.name/type/status/primary_for_goal` +
  `customer.call_reporting_setting` (les 3 actions ENABLED et principales,
  aucune « clic sur le numéro » principale, l'appel depuis l'annonce relié).
- Enchères : `ad_group_criterion.cpc_bid_micros` par mot-clé (pas toutes
  identiques) ; ajustements Atlas : `campaign_criterion.bid_modifier`.
