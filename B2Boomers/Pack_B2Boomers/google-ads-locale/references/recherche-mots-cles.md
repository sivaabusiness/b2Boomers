# Recherche de mots-clés locale — méthode détaillée

## 1. Résolution des géos

`GeoTargetConstantService.SuggestGeoTargetConstants` (locale fr, countryCode
FR) sur chaque commune du brief. Garder les constants de type City.

**Piège vérifié** : certaines petites communes n'ont pas de constant City,
seulement un code postal — et le Keyword Planner REJETTE les codes postaux
(`keywordPlanIdeaError: INVALID_VALUE`). Les exclure des mesures, le signaler
dans les limites du livrable ; la campagne, elle, peut cibler le code postal.

## 2. Collecte

Par thème/groupe : `GenerateKeywordIdeas` avec `keywordAndUrlSeed` (10-12
seeds : tête de série, synonymes, prix/devis/tarif, service+ville + l'URL de
la page), langue 1002, géos = communes, réseau GOOGLE_SEARCH, pagination.
Puis `GenerateKeywordHistoricalMetrics` sur les combos manuels
« service + ville » pour CHAQUE commune de la zone, plus les têtes de série et
variantes d'intention. Pause 2-3 s entre les appels. Tout sauver en JSON brut.

Sur une petite zone (< 500 k habitants), attendre des volumes par tranches
(10, 20, 30…), beaucoup de zéros sur les communes secondaires et des CPC
absents sur ~95 % des requêtes (Google ne publie pas sous un seuil de
volume) : c'est normal, écrire « n/d », ne rien estimer.

## 3. Filtrage — catégories d'exclusion

Regex sur texte normalisé (minuscules, sans accents, apostrophes → espaces) :

- **emploi / formation** : emploi, recrutement, salaire, formation, cap, bts,
  apprentissage, stage, métier, devenir, reconversion, cv, fiche…
- **matériel / location** : location, louer, tronçonneuse, rogneuse, broyeur,
  nacelle, échelle, corde, matériel, achat, vente, occasion, marques (stihl,
  husqvarna), enseignes (kiloutou, loxam, castorama, leroy merlin)…
- **sens détourné** : selon le métier — abattage → abattoir/animaux/halal ;
  souche → virus/bactérie/levure ; adapter au vocabulaire du client.
- **informationnel** : comment, quand, pourquoi, tuto, technique, période,
  saison, lune, calendrier, définition, vidéo, soi-même, quel(le), taux
  horaire…
- **juridique** : loi, voisin, réglementation, distance, droit, obligation,
  mairie, autorisation, amende, code civil, limite, propriété, assurance…
- **hors zone** : les villes exclues du brief + toute ville hors zone vue dans
  les résultats.
- **bois de chauffage / gratuit** (métiers de l'arbre) : bois, stère,
  chauffage, « contre bois » — chasseurs de bois gratuit = faux leads.

GARDER prix, tarif, devis, coût : forte intention d'achat. Ne PAS négativer
« gratuit » (tuerait « devis gratuit »).

## 4. Affectation aux groupes — 3 ou 4 groupes, pas plus

**3-4 groupes d'annonces maximum par campagne** (coaching n°6 · P1 @43:00,
@46:50) : un groupe par sous-service dilue le budget (15 groupes à 5-20 €
chacun = impossible à analyser à 10-15 €/jour). On REGROUPE : tonte,
entretien, taille de haie → un seul groupe « Entretien de jardin » ; les
sous-services vont dans les titres (« les mots-clés c'est ce sur quoi tu veux
tomber, les titres c'est ce qui est écrit dans tes annonces »). Garder les
groupes « là où il y a la plus grosse valeur de chantier pour l'artisan et là
où ça ne coûte pas trop cher » (CPC du kit) ; à 10-15 €/jour, rester sur les
3-4 services coeur du métier (élagage : élagage, abattage, dessouchage, taille
de haie). Les sous-services écartés vont dans un onglet « annexes » (hors
campagne), on les ajoute seulement si le budget ne se dépense pas malgré des
enchères hautes (zone trop petite, n°4 · P1 @30:00). Chaque groupe a sa
destination : site du pack → l'accueil avec `?travaux=<service principal du
groupe>`.

Liste ordonnée de motifs, premier match gagne — l'ordre résout les mots-clés
multi-services (« abattage et élagage ») de façon déterministe. Mettre les
vocabulaires les plus spécifiques d'abord (ex. souche avant abattage avant
élagage). Zéro doublon inter-groupes par construction ; le vérifier quand même.
Un mot-clé qui ne matche aucun groupe = « générique / hors service », écarté
(PAS négativé : une expression comme « prix élagage » peut encore matcher la
requête, c'est un bon clic).

## 5. Fusion des variantes et rétention

**Signature** : mots significatifs triés, singulier forcé, stopwords et bruit
retirés (le/la/de/pour…, m2, ml, mètre, heure, horaire, moyen, gros, grand,
faire, rapide, professionnel, particulier, nombres/hauteurs). Même signature
+ même groupe → une seule ligne (garder : tête de série > volume > graphie
accentuée > plus court). Divise la liste par ~3 sans perdre de couverture
(les correspondances exact/expression absorbent les variantes proches).

**Rétention — l'intention d'achat d'abord** (n°6 · P2 @21:40, @22:20) :
garder tête de série, combo ville (même à volume nul — couverture exacte
gratuite), requête courte (≤ 4 mots significatifs) AVEC une intention
d'achat : le service + « devis », « prix », « tarif », « entreprise »,
« artisan », « société », « réparation », « traitement », ou le service +
une ville (« entreprise qui coupe les arbres » : « ça, c'est un mot-clé avec
une intention derrière »). Un volume ≥ 20 ne suffit plus : « terrasse
extérieure », « muret en pierre » = des curieux qui « cliquent et
t'envoient de la merde ». Écarter : espèce d'arbre/plante sans intention
(DIY), > 4 mots significatifs, volume nul sans intention ni ville. Un
générique à gros volume (« entretien de jardin », 1 500/mois) vaut mieux que
dix mots précis à 10 recherches : « autant tout envoyer là-dedans et que ce
soit ton site qui fasse le tri » (n°6 · P1 @51:00). Ordre de grandeur : 100-150
mots-clés pour la campagne, 200 c'est trop (n°6 · P2 @57:20). Montrer la
liste à l'utilisateur : il doit « jauger » chaque mot-clé lui-même (n°6 · P2
@23:00).
Pour un groupe naissant sans volume mesuré (vocabulaire rare type
« rabotage »), garder aussi ses requêtes d'intention à volume nul.

## 6. Correspondances et priorités

- **Exact** : têtes de série + combos service+ville. **Expression** : le
  reste. **JAMAIS de requête large.**
- Priorité **A** : ville avec volume, tête de série ≥ 10/mois, intention
  courte ≥ 10/mois (les espèces plafonnent à B). **B** : autre volume ≥ 10.
  **C** : volume nul/n-d gardé pour couverture.

## 7. Négatifs

Liste partagée niveau campagne, ~100-120 entrées issues des catégories
d'exclusion : mots seuls en Large, locutions en Expression, villes hors zone.
Vérifier par simulation qu'AUCUN mot-clé retenu ne matche un négatif (Large =
tous les mots présents ; Expression = séquence contenue).

**PIÈGE VÉRIFIÉ EN PRODUCTION : les négatifs ne matchent PAS les variantes
désaccentuées.** Un négatif accentué « élagage écologique » ne bloque pas la requête
sans accent « elagage ecologique ». Toujours créer CHAQUE négatif accentué en double : version
accentuée + version sans accent (même correspondance). Autres trous vus en
vrai dans les rapports de termes : « produit(s) », « que faire », « détruire »,
« tuer », « dévitaliser », « recette », « sel », « vinaigre » (DIY souche) —
à inclure d'office pour les métiers de l'arbre. Relire le rapport des termes
de recherche 48-72 h après tout lancement : c'est là que les fuites
apparaissent.

## 8. Budget

Uniquement des chiffres du kit + hypothèses étiquetées.

- **Combien de zones** : ce que l'utilisateur peut perdre le premier mois.
  **Au moins 400 € → 2 zones (2 campagnes, même métier) ; sinon 1 seule**
  (coaching n°7, décision du 07/11). On coupe vite celle qui ne marche pas
  (pilotage-campagne.md). Pas de « budget du mois ÷ 30 jours ÷ 2 zones ».
- **Budget de départ : 10 à 15 €/jour par campagne.** Contrôle : clics/jour ≈
  budget ÷ CPC bas médian des mots-clés retenus ; il en faut **au moins 10
  par jour**, « sinon c'est la chance qui rentre en jeu » (n°7 · P1 @56:49).
  Sous 10 : le dire, proposer 15 €/jour ou de garder les groupes les moins
  chers.
- **Rythme attendu** (à dire à l'utilisateur, pour qu'il ne panique pas) :
  taux de conversion par défaut **2 %** (3 % au mieux sans preuve, jamais
  plus à l'estime) ; demandes/mois ≈ budget × 30 ÷ CPC × 2 %. Repère de
  Léo : à 15 €/jour et ~45 € la demande, une demande tous les 3 jours
  (n°7 · P1 @43:23).
- Contrôle de réalisme : part de clics requise = clics ÷ volume total mesuré ;
  au-delà de 15-20 %, dire clairement que l'objectif dépasse la zone.
- Les mots à 10 recherches/mois sont un plancher Google, pas de la demande :
  ne pas les additionner pour estimer la taille du marché (n°5).

## 9. Livrable Excel

Charger le skill xlsx avant de construire. Onglets :

1. Un par groupe : Mot-clé | Correspondance | Volume mensuel | Concurrence |
   CPC bas (€) | CPC haut (€) | Priorité | Source (idée API / ajout manuel) +
   ligne TOTAL en formules.
2. Groupes annexes éventuels (service sans destination sur le site) : même format, note rouge
   « hors campagne », exclus de l'import et du budget.
3. Négatifs : Mot-clé | Correspondance | Catégorie.
4. Budget : hypothèses en cellules bleues/jaunes étiquetées, calculs en
   formules (MEDIAN/COUNT/SUM sur les onglets groupes), contrôle de réalisme.
5. Import Editor : Campaign | Ad Group | Keyword | Criterion Type (Exact/
   Phrase) | Final URL | Max CPC (l'enchère de départ du mot-clé : milieu de
   sa fourchette bas-haut du kit, médiane du groupe si n/d — voir
   api-google-ads.md). Final URL :
   site du pack → `https://<domaine>/?travaux=<service>` (le même slug que
   sa page tunnel `devis-<service>.html`) ; autre site → la page du service.

Piège openpyxl : ne pas fixer freeze_panes via `ws.cell(...)` (crée une
cellule fantôme qui décale les données) — passer la chaîne `"A2"`.

**Vérification obligatoire, sur le fichier relu depuis le disque** : zéro
doublon inter-groupes, zéro conflit négatif/retenu, recomptes par onglet
(mots-clés, volumes) vs analyse, cohérence URL/groupe de l'import, simulation
Python des formules (pas de moteur de recalcul sur la machine : ni
LibreOffice ni Excel).
