# bardella — Pipeline stylométrie oral/écrit

Ce dépôt implémente une pipeline de vérification stylométrique entre corpus écrits et un corpus oral transcrit.

La méthodologie, les indices de mesure, la pipeline sont librement inspirés de cours reçus à l'École nationale des Chartes (qui n'a aucunement pris part à ce projet, ainsi libérée de toute responsabilité!)

## Objectif

Comparer des segments de textes écrits (`E`) et de productions orales transcrites (`O`), avec un corpus de contrôle (`C`), en utilisant des traits stylométriques et des mesures de distance.

## Auteur

- Nom: Mathieu Rivière
- Statut: étudiant en M1 Humanités Numériques à l'École nationale des Chartes 
- GitHub: [@icimathieu](https://github.com/icimathieu)
- Site: à venir

## Arborescence du projet

- `pipeline.txt` : spécification de la pipeline (étapes 1 à 10).
- `requirements_min.txt` : dépendances minimales pour exécuter les scripts stylométriques.
- `requirements.txt` : snapshot complet du `.venv` (`pip freeze`).
- `data/`
- `data/blocks2/` : blocs de corpus JSON.
  - `blocks_oral_bardella.json` : **versionné** 
  - `blocks_livres_bardella.json` : **non versionné** (ignoré, droits d'auteur).
  - `blocks_livres_sarkozy.json` : **non versionné** (ignoré, droits d'auteur).
- `data/features/` : artefacts de features (CSV/JSON) **versionnés**.
  - `features_char_ngrams.csv`
  - `features_handcrafted.csv`
  - `char_ngram_vocabulary.json`
  - `manifest_features.json`
- `data/output/` : rapports stylométriques JSON et interprétation.
  - `stylometry_comparisons_char_ngrams.json`
  - `stylometry_comparisons_function_words.json`
  - `stylometry_comparisons_discourse_markers.json`
  - `stylometry_comparisons_handcrafted_combined.json`
  - `interpretation_etape8.md`
- `data/trash/`
  - `whisper_transcriptions_merged.json` : **versionné**.
- `data/urls_bardella.json` : index des sources utilisées pour le sous-corpus oral.
- `scripts_notebooks/`
- `scripts_notebooks/stylométrie/`
  - `preprocessing_stylo.py` : normalisation et nettoyage contrôlé.
  - `extract_features_stylo.py` : extraction des traits stylométriques (étape 5).
  - `compare_stylo.py` : étapes 6-7 (cosinus, Burrows' Delta, bootstrap équilibré).
  - `osef.ipynb` : notebook d'exploration.
- `scripts_notebooks/scraping_formatage_data/` : scraping/formatage EPUB/PDF/JSON.
- `scripts_notebooks/audio_2_text_colab/` : 3 notebooks Google Colab audio -> texte.
  - `audio_to_text_bardella.ipynb`
  - `scraping_audio_bardella.ipynb`
  - `jsons_to_json_bardella.ipynb`
  - Note : ces notebooks Colab n'ont pas été adaptés pour une exécution directe sous VSCode avec le `.venv` local ; leurs dépendances Colab spécifiques ne sont pas incluses dans `requirements_min.txt`.

## Corpus et sous-corpus

- Sous-corpus oral (Bardella) noté `O` :
  - Source de collecte et index d'URLs : `data/urls_bardella.json`.
  - Fichier de blocs versionné : `data/blocks2/blocks_oral_bardella.json`.

- Sous-corpus livres de Sarkozy, noté `C`, construit à partir de 3 livres :
  - *Le Temps des Tempêtes* — Nicolas Sarkozy, Éditions de l'Observatoire, parution 24/07/2020, 528 pages, ISBN/EAN `9791032917169` ([source éditeur](https://www.editions-observatoire.com/livres/le-temps-des-tempetes/)).
  - *Le Temps des combats* — Nicolas Sarkozy, Fayard, parution 19/08/2023, ISBN `9782213726489` ([source éditeur](https://www.fayard.fr/livre/le-temps-des-combats-9782213726489/)).
  - *Le journal d'un prisonnier* — Nicolas Sarkozy, Fayard, parution 10/12/2025, ISBN `9782213734699` ([source éditeur](https://www.fayard.fr/livre/le-journal-dun-prisonnier-9782213734699/)).

- Sous-corpus livres de Bardella, noté `E`, construit à partir de 2 livres :
  - *Ce que je cherche* — Jordan Bardella, Fayard, parution 09/11/2024, ISBN `9782213731384` ([source éditeur](https://www.fayard.fr/livre/ce-que-je-cherche-9782213731384/)).
  - *Ce que veulent les Français* — Jordan Bardella, Fayard, parution 29/10/2025, ISBN `9782213733630` ([source éditeur](https://www.fayard.fr/livre/ce-que-veulent-les-francais-9782213733630)).

## Notes Git

- Les fichiers de livres dans `data/blocks2/` sont exclus du dépôt.
- Les transcriptions orales (`data/blocks2/blocks_oral_bardella.json`) sont versionnées.
- Le fichier `data/trash/whisper_transcriptions_merged.json` est versionné.
- Les artefacts de features (`data/features/`) et les distances (`data/output/`) sont versionnés.

## Confidentialité

- Ce projet a été réalisé avec l'aide de Codex/ChatGPT.
- Le mode `opt-out` a été activé dès le début du projet ; les échanges et données de travail n'ont donc pas été utilisés pour l'entraînement des modèles.
- Les blocs de textes issus des livres ne sont pas publiés, car ils pourraient permettre de reconstruire des contenus sous droits d'auteur.
- Les transcriptions orales sont publiées car proviennent d'oraux publics disponibles sur YouTube.

## Licence et réutilisation

- Le dépôt est diffusé sous licence `Apache-2.0` (fichier `LICENSE` à la racine du dépôt GitHub).
- Les réutilisations sont autorisées, y compris: usage privé/public, modification, redistribution et usage commercial.
- Toute redistribution doit conserver les mentions de licence et de copyright prévues par Apache-2.0.
- Un fichier `NOTICE` est fourni à la racine pour rappeler l'attribution du projet et l'absence d'endossement des versions dérivées.
- Si vous réutilisez ce travail dans un contexte académique/public, merci de citer le dépôt.

## Citation

Citation recommandée (texte):

`Mathieu Rivière (2026). bardella - Pipeline stylométrie oral/écrit. GitHub. https://github.com/icimathieu/stylometrie_bardella_v1`

BibTeX:

```bibtex
@misc{riviere2026_bardella,
  author       = {Mathieu Riviere},
  title        = {bardella - Pipeline stylometrie oral/ecrit},
  year         = {2026},
  howpublished = {\url{https://github.com/icimathieu/stylometrie_bardella_v1}},
  note         = {Version consultee le 2026-02-25}
}
```

## Conclusion 

Les mesures de distance étant contradictoires selon l'indicateur, je pense développer une autre méthode en comparant les mesures entre le sous-corpus oral et écrit de Jordan Bardella à d'autres corpus oral-écrit pour lesquels l'auctorialité de l'écrit est certaine. À poursuivre.
