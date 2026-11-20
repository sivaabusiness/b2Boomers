# Les 16 photos du site Allô Paysagiste Artois

Où : **aistudio.google.com** (gratuit avec un compte Google) → modèle **gemini-2.5-flash-image** (« Nano Banana ») → format **4:3**.

Pour chaque photo :
1. Colle le prompt (en anglais, c'est normal) → génère → télécharge l'image.
2. Compresse-la sur **squoosh.app** : glisse la photo → à droite, format **WebP**, qualité **70-75**, « Resize » largeur **1600 px** au plus → télécharge.
   Chaque photo doit peser **moins de 200 Ko**. La photo du haut de page (`action-amenagement-jardin.webp`), **moins de 150 Ko** : baisse la qualité ou la largeur à 1200 px si besoin.
3. Renomme-la **exactement** avec le nom indiqué (minuscules, tirets, `.webp`) et garde-la dans un dossier sur ton ordinateur. Je te dirai comment me les envoyer.

Règles du guide :
- Photos « amateur », comme prises au smartphone. Varie la lumière d'une photo à l'autre (ciel gris, fin de journée, après la pluie). Pas de grain ajouté.
- La moitié des photos montrent des gens : c'est ce qui rend le site crédible.
- Avant/après : on **AJOUTE** toujours des éléments en éditant (ajouter préserve le décor ; retirer le fait bouger). Donc :
  - quand l'APRÈS a **plus** de choses que l'AVANT (jardin créé, terrasse posée, clôture neuve) → génère d'abord l'**AVANT**, puis édite-le pour faire l'APRÈS ;
  - quand l'AVANT a **plus** de choses que l'APRÈS (haie qui déborde, herbe haute) → génère d'abord l'**APRÈS**, puis édite-le pour faire l'AVANT.
- Vérifie chaque paire côte à côte : chaque objet (maison, poubelle, muret…) doit être **au même endroit** sur les deux photos. Sinon, recommence.
- Si le changement ne saute pas aux yeux en 1 seconde sur un téléphone, régénère avec un prompt plus radical.

---

## A. Les 4 paires avant / après (8 photos)

### 1. Aménagement de jardin — `avant-amenagement-jardin.webp` puis `apres-amenagement-jardin.webp`
**On commence par l'AVANT (texte → image) :**
```
Casual amateur photo taken with a mid-range smartphone by a French homeowner in their garden, to ask a local company for a quote on WhatsApp: the bare back garden of a recent red-brick house in northern France, just bare muddy brown soil with tyre ruts, a few weeds, a pile of leftover bricks in a corner, an old wire fence at the back, no plants at all, a plastic garden chair near the patio door. Lighting: overcast white-grey sky, flat dull daylight, no shadows. Perfectly ordinary, boring snapshot look: framing slightly tilted and a bit too wide, subject off-center. Cheap smartphone camera rendering: slightly soft, mildly over-sharpened edges, dull slightly washed-out colors, everything roughly in focus. NO bokeh, NO added grain or noise texture, NO vignette, NO HDR drama, NO golden-hour glow, nothing cinematic. Absolutely not professional and not AI-looking. No people, no text, no watermark.
```
**Puis l'APRÈS (joins la photo AVANT) :**
```
Edit this exact photo: show the SAME place from the SAME viewpoint AFTER the professional work is done. THE DIFFERENCE MUST BE DRAMATIC AND OBVIOUS: the whole muddy plot is now a NEW GARDEN — fresh bright green lawn covering the ground, a curved planted border with young shrubs and dark bark mulch along the side, a young hornbeam hedge planted along the old wire fence, the brick pile is GONE. CRITICAL: this is the SAME spot photographed again — keep the camera in the SAME position with the SAME framing (at most a tiny hand-held shift), and keep EVERY background element (house, walls, bins, fences, sheds, cracks) in EXACTLY the same place and shape. Change ONLY the work described, plus a slightly different time of day for the light. Same dull amateur smartphone look — no added grain, nothing cinematic. No people, no text, no watermark.
```

### 2. Terrasse et allées — `avant-terrasse-allee.webp` puis `apres-terrasse-allee.webp`
**AVANT d'abord :**
```
Casual amateur photo taken with a mid-range smartphone by a French homeowner in their garden, to ask a local company for a quote on WhatsApp: the area right behind a red-brick northern French house, patchy worn grass and bare earth along the back wall, a few cracked old concrete slabs in front of the patio door, a wheelie bin against the wall, a drainpipe. Lighting: dull cloudy day just after rain, damp ground. Perfectly ordinary, boring snapshot look: framing slightly tilted and a bit too wide, subject off-center. Cheap smartphone camera rendering: slightly soft, mildly over-sharpened edges, dull slightly washed-out colors, everything roughly in focus. NO bokeh, NO added grain or noise texture, NO vignette, NO HDR drama, NO golden-hour glow, nothing cinematic. Absolutely not professional and not AI-looking. No people, no text, no watermark.
```
**Puis l'APRÈS (joins l'AVANT) :**
```
Edit this exact photo: show the SAME place from the SAME viewpoint AFTER the professional work is done. THE DIFFERENCE MUST BE DRAMATIC AND OBVIOUS: a brand-new large terrace of light grey stone-look paving slabs, perfectly level, covering the whole area in front of the house, with a neat grey border edging and a clean strip of new lawn beyond it; the cracked slabs and bare earth are GONE. CRITICAL: this is the SAME spot photographed again — keep the camera in the SAME position with the SAME framing (at most a tiny hand-held shift), and keep EVERY background element (house, walls, bins, fences, sheds, cracks) in EXACTLY the same place and shape. Change ONLY the work described, plus a slightly different time of day for the light. Same dull amateur smartphone look — no added grain, nothing cinematic. No people, no text, no watermark.
```

### 3. Entretien de jardin — `apres-entretien-jardin.webp` D'ABORD, puis `avant-entretien-jardin.webp`
**APRÈS d'abord (texte → image) :**
```
Casual amateur photo taken with a mid-range smartphone by a French homeowner in their garden: a freshly trimmed tall thuja hedge with a perfectly flat top and straight sides along the side of a small lawn, the lawn freshly mowed with visible mowing stripes, a low brick wall at the end, a green wheelie bin, a red-brick house corner on the right. Lighting: weak late-afternoon light, long soft shadows. Perfectly ordinary, boring snapshot look: framing slightly tilted and a bit too wide, subject off-center. Cheap smartphone camera rendering: slightly soft, mildly over-sharpened edges, dull slightly washed-out colors, everything roughly in focus. NO bokeh, NO added grain or noise texture, NO vignette, NO HDR drama, NO golden-hour glow, nothing cinematic. Absolutely not professional and not AI-looking. No people, no text, no watermark.
```
**Puis l'AVANT (joins l'APRÈS) :**
```
Edit this exact photo: show the SAME place from the SAME viewpoint BEFORE the gardening work, by ADDING overgrowth only. THE DIFFERENCE MUST BE DRAMATIC AND OBVIOUS: the hedge has grown wild — shaggy, much wider and taller, long uneven shoots sticking out in every direction and bulging over the lawn; the lawn grass is long, uneven and full of dandelions and weeds, dead leaves scattered. CRITICAL: keep the camera in the SAME position with the SAME framing, and keep EVERY background element (house, low wall, wheelie bin) in EXACTLY the same place and shape. Change ONLY the overgrowth described, plus a slightly different light (overcast grey sky). Same dull amateur smartphone look — no added grain, nothing cinematic. No people, no text, no watermark.
```

### 4. Clôture et portail — `avant-cloture-portail.webp` puis `apres-cloture-portail.webp`
**AVANT d'abord :**
```
Casual amateur photo taken with a mid-range smartphone by a French homeowner in their garden, to ask a local company for a quote on WhatsApp: the side boundary of a suburban garden in northern France, an old sagging rusty wire fence on leaning concrete posts, partly torn, a few weeds at its foot, the neighbour's red-brick house visible behind it, a lawn in the foreground. Lighting: overcast white-grey sky, flat dull daylight, no shadows. Perfectly ordinary, boring snapshot look: framing slightly tilted and a bit too wide, subject off-center. Cheap smartphone camera rendering: slightly soft, mildly over-sharpened edges, dull slightly washed-out colors, everything roughly in focus. NO bokeh, NO added grain or noise texture, NO vignette, NO HDR drama, NO golden-hour glow, nothing cinematic. Absolutely not professional and not AI-looking. No people, no text, no watermark.
```
**Puis l'APRÈS (joins l'AVANT) :**
```
Edit this exact photo: show the SAME place from the SAME viewpoint AFTER the professional work is done. THE DIFFERENCE MUST BE DRAMATIC AND OBVIOUS: the old wire fence is replaced by a brand-new, perfectly straight anthracite grey rigid panel fence about 1.8 m high with matching grey posts and grey privacy slats woven in, clean concrete footings, the weeds at its foot cleared, a little fresh soil along the base. CRITICAL: this is the SAME spot photographed again — keep the camera in the SAME position with the SAME framing (at most a tiny hand-held shift), and keep EVERY background element (houses, lawn, sheds) in EXACTLY the same place and shape. Change ONLY the work described, plus a slightly different time of day for the light. Same dull amateur smartphone look — no added grain, nothing cinematic. No people, no text, no watermark.
```

---

## B. Les 4 photos « en action », une par service (4 photos)
Ce sont aussi les petites images des gros boutons « Quels travaux ? ». La première est aussi la grande photo du haut de l'accueil.

### 5. `action-amenagement-jardin.webp` (photo du haut de page : < 150 Ko)
```
Casual amateur photo taken with a mid-range smartphone from a few meters away by a coworker: a landscaper in worn work clothes and gloves planting young shrubs in a freshly prepared border with dark mulch, a wheelbarrow full of soil and potted plants next to him, a newly laid lawn around, in a TYPICAL northern French suburban setting (red-brick houses, low brick walls, hedges). Lighting: overcast soft grey daylight. Slightly tilted framing, face barely visible (distance, cap). Clean smooth smartphone image quality: NO added grain, NO film texture, NO gritty look, no bokeh, nothing cinematic — and not AI-perfect either. No text, no watermark.
```

### 6. `action-terrasse-allee.webp`
```
Casual amateur photo taken with a mid-range smartphone from a few meters away by a coworker: one worker kneeling with knee pads, setting a large grey paving slab on a sand bed with a rubber mallet, a spirit level and a stack of slabs next to him, a half-finished terrace behind a red-brick house, in a TYPICAL northern French suburban setting. Lighting: weak late-afternoon light, long soft shadows. Slightly tilted framing, face barely visible (distance, looking down). Clean smooth smartphone image quality: NO added grain, NO film texture, NO gritty look, no bokeh, nothing cinematic — and not AI-perfect either. No text, no watermark.
```

### 7. `action-entretien-jardin.webp`
```
Casual amateur photo taken with a mid-range smartphone from a few meters away by a coworker: a gardener in a worn hi-vis vest and ear defenders trimming the top of a tall hedge with a long-reach hedge trimmer from a small step ladder, green clippings falling on a tarp on the ground, in a TYPICAL northern French suburban garden (red-brick houses, lawn). Lighting: dull cloudy day just after rain, damp ground. Slightly tilted framing, face barely visible (distance, ear defenders). Clean smooth smartphone image quality: NO added grain, NO film texture, NO gritty look, no bokeh, nothing cinematic — and not AI-perfect either. No text, no watermark.
```

### 8. `action-cloture-portail.webp`
```
Casual amateur photo taken with a mid-range smartphone from a few meters away by a coworker: two workers in worn work clothes installing an anthracite grey rigid fence panel, one holding the panel straight while the other tightens a clip on the post, a bucket of concrete and a spirit level on the grass, in a TYPICAL northern French suburban setting (red-brick houses, small front gardens). Lighting: overcast white-grey sky. Slightly tilted framing, faces barely visible (distance, caps). Clean smooth smartphone image quality: NO added grain, NO film texture, NO gritty look, no bokeh, nothing cinematic — and not AI-perfect either. No text, no watermark.
```

---

## C. Les 4 photos de confiance (4 photos)

### 9. `equipe.webp` — l'équipe (utilisée en grand sur l'accueil, en haut de devis.html et en fond du bas de page)
```
Casual amateur photo taken with a mid-range smartphone: a small crew of 3 landscaper workers with ordinary average builds standing a bit awkwardly, mid-laugh, in front of their dirty white flatbed truck loaded with garden waste, a mower and bags of soil, parked along the curb of an ordinary northern French residential street of red-brick terraced houses at the end of a work day. Worn stained work clothes, muddy boots, gloves in hand, natural imperfect faces and skin. Composition slightly off-center like a photo taken quickly by one of them. Weak late-afternoon light, slightly dim. NOT a professional team photo: no studio lighting, no AI-perfect faces, no added grain, nothing cinematic. No text, no watermark.
```

### 10. `conseil-client.webp` — le conseil (photo verticale de préférence : choisis le format 3:4 ou 4:5)
```
Casual amateur photo taken with a mid-range smartphone: a landscaper artisan in worn work clothes standing in a garden with a homeowner in his sixties wearing a fleece jacket, both looking at the bare corner of the lawn where a new terrace will go, the artisan pointing with one hand and holding a paper notepad in the other, mid-conversation, seen from a few meters away, in a typical northern French suburban garden with a red-brick house. Lighting: overcast soft grey daylight. Natural imperfect faces, ordinary builds, nothing posed. Clean smooth smartphone quality: no grain, no bokeh, nothing cinematic, not AI-perfect. No text, no watermark.
```

### 11. `materiel.webp` — le matériel (grande bande photo au milieu de l'accueil)
```
Casual amateur photo taken with a mid-range smartphone from a few meters away by a coworker: a small yellow mini-excavator digging out soil for a garden terrace, a worker in a hi-vis vest guiding it, a pile of earth and a plate compactor nearby, behind a red-brick house in a TYPICAL northern French suburban setting. Lighting: dull cloudy day just after rain, damp ground. Slightly tilted framing, faces barely visible (distance). Clean smooth smartphone image quality: NO added grain, NO film texture, NO gritty look, no bokeh, nothing cinematic — and not AI-perfect either. No text, no watermark.
```

### 12. `chantier-propre.webp` — le chantier nettoyé
```
Casual amateur photo taken with a mid-range smartphone from a few meters away by a coworker: a worker in worn work clothes sweeping a freshly finished garden path with a stiff broom, full green waste bags and a wheelbarrow being loaded onto a small trailer, tools neatly stored, in a TYPICAL northern French suburban garden (red-brick house, new lawn). Lighting: weak late-afternoon light, long soft shadows. Slightly tilted framing, face barely visible (distance, cap). Clean smooth smartphone image quality: NO added grain, NO film texture, NO gritty look, no bokeh, nothing cinematic — and not AI-perfect either. No text, no watermark.
```

---

## Récapitulatif des 16 noms de fichiers
```
avant-amenagement-jardin.webp    apres-amenagement-jardin.webp
avant-terrasse-allee.webp        apres-terrasse-allee.webp
avant-entretien-jardin.webp      apres-entretien-jardin.webp
avant-cloture-portail.webp       apres-cloture-portail.webp
action-amenagement-jardin.webp   action-terrasse-allee.webp
action-entretien-jardin.webp     action-cloture-portail.webp
equipe.webp                      conseil-client.webp
materiel.webp                    chantier-propre.webp
```

⚠️ Rappel du guide : ce sont des photos d'illustration (le pied de page le dit). Jamais de légende « chantier réalisé à [commune] » sur une photo générée. Dès que ton artisan dit oui, on les remplace par SES vraies photos, avec son accord écrit.
