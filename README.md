# Hypermedia

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Phase](https://img.shields.io/badge/Phase_1-75%25-orange.svg)](TODO.md)
[![Tests](https://img.shields.io/badge/Coverage-65%25-yellow.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Librairie Python pour la gestion décentralisée d'hypermedia avec système de fichiers distribué **HM-Drive** et scènes dynamiques **HM-Scene**.

## 🎯 Vision

Hypermedia propose une architecture innovante à deux couches pour gérer, organiser et naviguer dans des collections de médias numériques de manière non linéaire et contextuelle :

- **HM-Drive** : Couche de stockage décentralisé avec déduplication, métadonnées enrichies et synchronisation pair-à-pair
- **HM-Scene** : Couche de scènes dynamiques permettant une navigation hypermedia multi-échelle et multi-modale

## 📚 Documentation

### Guides utilisateur
- **[Installation](docs/installation.md)** - Guide d'installation complet
- **[Quick Start](docs/quickstart.md)** - Premiers pas en 5 minutes
- **[Référence API](docs/api_reference.md)** - Documentation API complète
- **[Exemples](examples/)** - Exemples d'utilisation

### Documentation technique
- **[ROADMAP.md](documentation/ROADMAP.md)** - Vision stratégique et planning détaillé
- **[TODO.md](TODO.md)** - Liste des tâches et progression Phase 1 (75%)
- **[PROGRESS_REPORT.md](PROGRESS_REPORT.md)** - Rapport de progression détaillé
- **[SPECIFICATIONS_FONCTIONNELLES.md](documentation/SPECIFICATIONS_FONCTIONNELLES.md)** - Spécifications fonctionnelles
- **[SPECIFICATIONS_TECHNIQUES.md](documentation/SPECIFICATIONS_TECHNIQUES.md)** - Spécifications techniques
- **[ARCHITECTURE_HM_DRIVE.md](documentation/ARCHITECTURE_HM_DRIVE.md)** - Architecture HM-Drive
- **[ARCHITECTURE_HM_SCENE.md](documentation/ARCHITECTURE_HM_SCENE.md)** - Architecture HM-Scene

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/TristanV/hypermedia.git
cd hypermedia

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Installer en mode développement
pip install -e .
```

Consultez le [guide d'installation complet](docs/installation.md) pour plus de détails.

### Premier exemple

```python
from pathlib import Path
from hypermedia.drive import DatabaseManager, MediaCollection

# Initialisation
db = DatabaseManager(Path("./hypermedia.db"))
collection = MediaCollection(Path("./storage"), db)

# Créer une collection
coll_id = collection.create_collection(
    "Mes Photos",
    "Collection de photos personnelles"
)

# Ajouter un média avec détection automatique des doublons
media_id = collection.add_media_to_collection(
    coll_id,
    Path("/chemin/vers/photo.jpg"),
    custom_metadata={
        "tags": ["vacances", "montagne"],
        "location": "Alpes",
        "rating": 5
    }
)

# Rechercher par métadonnées
results = collection.search(
    collection_id=coll_id,
    metadata_filters={"custom.rating": "5"}
)

for media in results:
    print(f"- {media['filename']} ({media['mime_type']})")

# Fermeture
db.close()
```

Consultez le [Quick Start](docs/quickstart.md) pour plus d'exemples.

## ✨ Fonctionnalités Phase 1 (75% complété)

### ✅ Implémenté

- **Gestion de collections** : Création, organisation, recherche
- **Checksums BLAKE2b** : Calcul rapide et vérification d'intégrité
- **Déduplication automatique** : Détection de doublons avec 3 politiques (reference/ignore/alert)
- **Extraction de métadonnées** :
  - Images : EXIF complet (caméra, GPS, dimensions)
  - Audio : ID3/Vorbis (titre, artiste, durée)
  - Vidéo : ffprobe (codec, résolution, bitrate)
- **Base de données SQLite** : Modèles complets avec relations many-to-many
- **Sharding intelligent** : Organisation hiérarchique du stockage
- **Recherche avancée** : Par collection, métadonnées, texte, avec pagination
- **Métadonnées personnalisées** : Tags, annotations, notes utilisateur
- **Tests unitaires** : 140+ tests (couverture ~65%)

### 🚧 En cours

- Complétion des tests (objectif : 80%+ couverture)
- Documentation API (Sphinx)
- CLI basique
- Optimisations performance

## 🏗️ Structure du Projet

```
Hypermedia/
├── docs/                      # Documentation utilisateur
│   ├── installation.md
│   ├── quickstart.md
│   └── api_reference.md
├── documentation/           # Documentation technique complète
│   ├── ROADMAP.md
│   ├── SPECIFICATIONS_*.md
│   └── ARCHITECTURE_*.md
├── hypermedia/             # Package principal
│   ├── __init__.py
│   ├── drive/             # Couche HM-Drive (Phase 1)
│   │   ├── __init__.py
│   │   ├── collection.py       # ✅ Gestion collections
│   │   ├── checksum.py          # ✅ Checksums BLAKE2b
│   │   ├── deduplication.py     # ✅ Déduplication
│   │   ├── database.py          # ✅ Gestionnaire DB
│   │   ├── models.py            # ✅ Modèles SQLAlchemy
│   │   └── metadata_extractor.py # ✅ Extraction métadonnées
│   ├── scene/             # Couche HM-Scene (Phase 3)
│   │   └── __init__.py
│   └── common/            # Utilitaires partagés
│       └── __init__.py
├── tests/                  # Tests unitaires (140+ tests)
│   ├── test_models.py          # ✅ Tests modèles
│   ├── test_database.py        # ✅ Tests DB
│   ├── test_checksum_dedup.py  # ✅ Tests checksums
│   ├── test_collection.py      # ✅ Tests collections
│   └── test_metadata_extractor.py # ✅ Tests extraction
├── examples/               # Exemples d'utilisation
│   └── phase1_basic_usage.py
├── TODO.md                # Liste des tâches détaillée
├── PROGRESS_REPORT.md     # Rapport de progression
├── requirements.txt       # Dépendances runtime
├── requirements-dev.txt   # Dépendances développement
├── setup.py               # Configuration du package
├── pyproject.toml         # Configuration outils
└── README.md              # Ce fichier
```

## 📈 Métriques de Qualité

| Métrique | Valeur | Objectif |
|----------|--------|----------|
| **Phase 1** | 75% ⬛⬛⬛⬜⬜ | 100% |
| **Tests unitaires** | 140+ tests | 180+ tests |
| **Couverture** | ~65% | >80% |
| **Docstrings** | 90% | 100% |
| **Type hints** | 95% | 100% |
| **PEP8** | 100% (black) | 100% |

## 📅 Roadmap

### ✅ Phase 0 - Conception (Terminée)
- Vision stratégique et architecture globale
- Spécifications fonctionnelles et techniques
- Documentation exhaustive

### 🔵 Phase 1 - Fondations HM-Drive (75% - En cours)
- ✅ Structure du package Python
- ✅ Système de collections local
- ✅ Checksums BLAKE2b et déduplication
- ✅ Modèle de données SQLite
- ✅ Métadonnées enrichies
- ✅ Suite de tests unitaires (140+ tests)
- 🔵 Documentation complète

**Release v0.1.0-alpha** : Prévue 12-13 février 2026

### ⏳ Phase 2 - API et Synchronisation (Q2 2026)
- API RESTful avec FastAPI
- Synchronisation pair-à-pair
- Détection et résolution de conflits
- Authentification JWT
- WebSockets temps réel

### ⏳ Phase 3 - HM-Scene (Q3 2026)
- Modèle de scènes multi-échelles
- Navigation hypermedia non linéaire
- Système de transitions et contextes
- Graphe de relations sémantiques

### ⏳ Phase 4 - Fonctionnalités Avancées (Q4 2026)
- Embeddings multimodaux (CLIP, etc.)
- Recherche sémantique par similarité
- Clustering et recommandations IA
- Export et interopérabilité

Consultez [ROADMAP.md](documentation/ROADMAP.md) et [TODO.md](TODO.md) pour plus de détails.

## 🛠️ Technologies

### Phase 1 (Implémenté)
- **Python 3.10+** - Langage principal
- **SQLAlchemy 2.0** - ORM pour SQLite
- **BLAKE2b** - Fonction de hachage cryptographique
- **Pillow** - Traitement d'images et extraction EXIF
- **Mutagen** - Métadonnées audio (MP3, FLAC, OGG)
- **ffmpeg/ffprobe** - Métadonnées vidéo (optionnel)
- **pytest** - Framework de tests (140+ tests)
- **black** - Formatage de code
- **mypy** - Typage statique
- **pre-commit** - Hooks Git

### Phases Futures
- **FastAPI** - API REST (Phase 2)
- **libp2p** / **IPFS** - Réseau pair-à-pair (Phase 2)
- **Transformers** / **CLIP** - Embeddings IA (Phase 4)
- **NetworkX** - Graphes de navigation (Phase 3)
- **Qdrant** / **FAISS** - Recherche vectorielle (Phase 4)

## 🧪 Tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=hypermedia --cov-report=html

# Tests spécifiques
pytest tests/test_models.py
pytest tests/test_collection.py -v

# Tests rapides (sans vidéo)
pytest -m "not slow"
```

Couverture actuelle : **~65%** (objectif : >80%)

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

### Workflow de contribution

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Standards de code

- **Formatage** : black (ligne 88 caractères)
- **Linting** : flake8, mypy
- **Docstrings** : Style Google/NumPy
- **Tests** : pytest avec couverture >80%
- **Commits** : Messages descriptifs en anglais

## 📝 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**Tristan Vanrullen**
- GitHub: [@TristanV](https://github.com/TristanV)
- LinkedIn: [Tristan Vanrullen](https://www.linkedin.com/in/tristan-vanrullen/)

## 🙏 Remerciements

- Projet inspiré par [prompt-imagine](https://github.com/TristanV/prompt-imagine)
- Références académiques en hypermédia et systèmes distribués
- Communauté open-source Python

---

**Statut actuel** : Phase 1 - Fondations HM-Drive (75%)  
**Prochaine release** : v0.1.0-alpha (12-13 février 2026)  
**Dernière mise à jour** : 2026-02-10 03:05 CET
