# Time Series Analysis and Volatility Forecasting for Major Stock Indices

## Présentation

Projet de stage de six semaines portant sur les indices S&P 500, CAC 40 et FTSE 100. L’étude couvre la préparation des cours de clôture Yahoo Finance, les rendements et la volatilité, deux méthodes de prévision et leur évaluation, puis les drawdowns historiques.

L’historique enregistré va du 6 septembre 2016 au 4 septembre 2026. Les méthodes de prévision sont une fenêtre mobile de 21 séances et une EWMA de facteur 0,94. L’évaluation utilise des rendements au carré comme approximation bruitée de la variance quotidienne.

## Parcours de lecture

Les notebooks contiennent leurs sorties enregistrées et peuvent être consultés sans relancer les calculs dans un éditeur compatible.

| Phase | Notebook | Script |
|---|---|---|
| 1 — Collecte et nettoyage | `notebooks/01_data_collection_and_cleaning.ipynb` | `src/phase1.py` |
| 2 — Rendements et volatilité | `notebooks/02_returns_and_volatility.ipynb` | `src/phase2.py` |
| 3 — Analyse exploratoire | `notebooks/03_exploratory_analysis.ipynb` | `src/phase3.py` |
| 4 — Prévision | `notebooks/04_volatility_forecasting.ipynb` | `src/phase4.py` |
| 5 — Évaluation | `notebooks/05_forecast_evaluation.ipynb` | `src/phase5.py` |
| 6 — Risque historique | `notebooks/06_risk_analysis.ipynb` | `src/phase6.py` |

La phase 7 concerne la documentation, les vérifications et la restitution. Les rapports Word sont transmis séparément.

## Contenu

- `src/` : scripts de traitement, contrôles numériques et commandes de reproduction.
- `notebooks/` : six notebooks avec leurs sorties enregistrées.
- `data/raw/` : réponses Yahoo et métadonnées conservées.
- `data/processed/` : prix préparés, rendements et indicateurs.
- `data/forecasts/`, `data/evaluation/`, `data/risk/` : prévisions, évaluation et drawdowns.
- `reports/` : tableaux de résultats, configuration et figures.
- `requirements*.txt` : versions des dépendances enregistrées dans le projet.
- `MANIFEST_SHA256.json` : empreintes des fichiers de cette archive.

## Installation et exécution

Extraire entièrement l’archive, puis ouvrir un terminal dans le dossier `PROJET_VOLATILITE_PYTHON`. Les commandes suivantes sont prévues pour Linux ou macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-review.txt
python src/run_all.py
```

Sous Windows, créer l’environnement avec `py -m venv .venv`, puis utiliser `.venv\Scripts\activate` dans l’invite de commandes à la place de la commande `source`.

L’environnement d’origine consigné utilise Python 3.14.6. Les versions précises des bibliothèques figurent dans les fichiers de dépendances ; leur disponibilité dépend de la version de Python et de la plateforme. L’installation nécessite un accès Internet. La chaîne de calcul réutilise les données brutes incluses. Si ces fichiers sont supprimés, la phase 1 peut tenter une nouvelle collecte.

`run_all.py` exécute les six phases et les contrôles disponibles. Pour une phase particulière, utiliser par exemple :

```bash
python src/phase5.py
python src/check_phase5.py
```

Les scripts régénèrent les tableaux et les figures dans le dossier extrait. Conserver les données brutes intactes et travailler dans une copie si l’on souhaite comparer les résultats avant et après exécution.

## Exécuter les notebooks

Enregistrer d’abord le noyau de l’environnement :

```bash
python -m ipykernel install --user --name internship --display-name 'Internship'
python src/run_notebooks.py
```

Le second script exécute les notebooks dans l’ordre et enregistre leurs nouvelles sorties. Un autre noyau déjà installé peut être sélectionné avec `--kernel NOM`.

Pour une consultation interactive, ouvrir les notebooks dans un éditeur compatible, comme VS Code avec son support Jupyter, et sélectionner l’environnement installé. Les dépendances du projet ne comprennent pas une interface Web Jupyter complète.

## Points méthodologiques

Une clôture FTSE manque le 22 décembre 2020 ; elle reste manquante. La chronologie des prévisions distingue dates d’origine et dates cibles. Les deux méthodes sont évaluées sur les mêmes dates au sein de chaque marché. Les données finales ont déjà été visualisées dans les premières phases, ce qui limite le caractère inédit de la période de test.

## Vérification de cette copie

Les scripts et les données sont identiques à ceux du workspace. Les titres et commentaires Markdown des notebooks ont été reformulés en français pour la présentation du projet. Les cellules de code, leurs compteurs d’exécution et leurs sorties enregistrées restent identiques. La syntaxe des scripts et l’absence de sorties d’erreur ont été vérifiées. L’intégrité du ZIP est contrôlée lors de sa création.

La chaîne complète n’a pas été réexécutée à l’occasion de cet empaquetage. Les sorties incluses sont celles enregistrées dans le projet. L’archive contient uniquement les fichiers utiles à l’analyse et à sa consultation ; les environnements virtuels, caches et anciens rapports sont exclus.

