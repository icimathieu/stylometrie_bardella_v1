# Étape 8 — Interprétation des résultats stylométriques

## Fichiers de référence (versionnés GitHub)

- Pipeline méthodologique : [`pipeline.txt`](../../pipeline.txt)
- Script d'extraction des features (étape 5) : [`scripts_notebooks/stylométrie/extract_features_stylo.py`](../../scripts_notebooks/stylométrie/extract_features_stylo.py)
- Script de comparaison (étapes 6-7) : [`scripts_notebooks/stylométrie/compare_stylo.py`](../../scripts_notebooks/stylométrie/compare_stylo.py)
- Rapport char n-grams : [`data/output/stylometry_comparisons_char_ngrams.json`](./stylometry_comparisons_char_ngrams.json)
- Rapport function words : [`data/output/stylometry_comparisons_function_words.json`](./stylometry_comparisons_function_words.json)
- Rapport discourse markers : [`data/output/stylometry_comparisons_discourse_markers.json`](./stylometry_comparisons_discourse_markers.json)
- Rapport combiné handcrafted : [`data/output/stylometry_comparisons_handcrafted_combined.json`](./stylometry_comparisons_handcrafted_combined.json)

## Corpus utilisé (aligné avec README)

- Sous-corpus oral (Bardella)
  - Source de collecte : [`data/urls_bardella.json`](../urls_bardella.json)
  - Fichier de blocs versionné : `data/blocks2/blocks_oral_bardella.json`

- Sous-corpus livres (Bardella)
  - *Ce que je cherche* (Fayard, 2024)
  - *Ce que veulent les Français* (Fayard, 2025)

- Sous-corpus livres (Sarkozy)
  - *Le Temps des Tempêtes* (Éditions de l'Observatoire, 2020)
  - *Le Temps des combats* (Fayard, 2023)
  - *Le journal d'un prisonnier* (Fayard, 2025)

## Note de versionnement

- Les blocs livres dans `data/blocks2/` ne sont pas versionnés (droits d'auteur).
- Le bloc oral `data/blocks2/blocks_oral_bardella.json` est versionné.
- Les artefacts de features (`data/features/`) et les rapports (`data/output/`) sont versionnés.

## 1) Rappel du travail effectué (étapes 5 à 7)

- Extraction des traits stylométriques sur les 3 corpus (`E`, `O`, `C`) :
  - n-grammes de caractères (3-4) ;
  - mots-outils (`function words`) ;
  - marqueurs discursifs ;
  - statistiques de phrases.
- Comparaisons de distances avec deux métriques :
  - distance cosinus ;
  - Burrows' Delta.
- Comparaisons calculées :
  - `E ↔ E`, `O ↔ O`, `E ↔ O`, `E ↔ C`, `O ↔ C`.
- Analyse renforcée avec bootstrap équilibré (`n=123` par corpus, 1000 runs).

## 2) Contrôles internes (étape 6)

Les contrôles internes apparaissent globalement satisfaisants et interprétables :

- `E ↔ E` est nettement plus faible que `E ↔ O`.
- `O ↔ O` est nettement plus faible que `E ↔ O`.

Ce résultat est cohérent avec un effet de registre oral/écrit : le corpus oral est plus éloigné de l'écrit que l'écrit de lui-même, mais les corpus restent structurés et non aléatoires.

## 3) Lecture des indicateurs principaux

## 3.1 n-grammes de caractères (indicateur principal, le plus robuste)

- **Cosinus** :
  - `E ↔ O` > `E ↔ E` et `O ↔ O` (écart oral/écrit net),
  - mais `E ↔ O` < `E ↔ C` (E plus proche de O que de C).
  - Lecture : signal plutôt compatible avec une auctorialité plausible sous effet de registre.

- **Burrows' Delta** :
  - `E ↔ O` > `E ↔ E` et `O ↔ O`,
  - et `E ↔ C` < `E ↔ O`.
  - Lecture : signal inverse, allant vers une incompatibilité relative (au sens de la règle de renforcement définie dans la pipeline).

=> **Contradiction réelle entre cosinus et Delta** sur le couple `E ↔ O` vs `E ↔ C`.

## 3.2 Mots-outils (function words)

- Les mots-outils confirment un écart `E ↔ O` par rapport aux distances internes.
- Sur `E ↔ O` vs `E ↔ C`, le signal reste plus ambigu et moins tranché que les char n-grammes.
- Delta sur mots-outils donne des valeurs très proches entre `E ↔ O` et `E ↔ C`.

## 3.3 Marqueurs discursifs (bonus)

- Les résultats sont instables selon la métrique.
- Le poids de ces traits dans la conclusion finale reste limité (peu de variables, forte sensibilité au protocole de transcription et à la situation orale).

## 4) Conclusion méthodologique (étape 8)

- Les deux distances donnent effectivement des conclusions en partie contradictoires.
- Formulation fidèle aux résultats :
  - **Cosinus** tend à soutenir que `E` est plus proche de `O` que de `C` (compatibilité relative `E/O`).
  - **Delta** tend à montrer que `E` est plus proche de `C` que de `O` (signal inverse).


> Les résultats sont **mixtes** : ils confirment un écart oral/écrit important (`E↔O` > distances internes), mais l'attribution finale dépend de la métrique choisie (cosinus vs Delta). En conséquence, l'analyse ne permet pas de conclure de manière univoque à l'incompatibilité ni à une compatibilité forte sans analyses complémentaires.
