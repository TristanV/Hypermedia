# Hypermedia

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Phase_1-orange.svg)](documentation/ROADMAP.md)

Librairie Python pour la gestion décentralisée d'hypermedia avec système de fichiers distribué **HM-Drive** et scènes dynamiques **HM-Scene**.

## 🎯 Vision

Hypermedia propose une architecture innovante à deux couches pour gérer, organiser et naviguer dans des collections de médias numériques de manière non linéaire et contextuelle :

- **HM-Drive** : Couche de stockage décentralisé avec déduplication, métadonnées enrichies et synchronisation pair-à-pair
- **HM-Scene** : Couche de scènes dynamiques permettant une navigation hypermedia multi-échelle et multi-modale

## 📚 Documentation Complète

La documentation exhaustive du projet est disponible dans le répertoire [`documentation/`](documentation/) :

### Documentation Stratégique
- [**ROADMAP.md**](documentation/ROADMAP.md) - Vision stratégique et planning détaillé par phase

### Spécifications
- [**SPECIFICATIONS_FONCTIONNELLES.md**](documentation/SPECIFICATIONS_FONCTIONNELLES.md) - Spécifications fonctionnelles exhaustives
- [**SPECIFICATIONS_TECHNIQUES.md**](documentation/SPECIFICATIONS_TECHNIQUES.md) - Spécifications techniques détaillées

### Architecture
- [**ARCHITECTURE_HM_DRIVE.md**](documentation/ARCHITECTURE_HM_DRIVE.md) - Architecture de la couche stockage
- [**ARCHITECTURE_HM_SCENE.md**](documentation/ARCHITECTURE_HM_SCENE.md) - Architecture de la couche scènes

### Guide Pratique
- [**MIGRATION_GUIDE.md**](documentation/MIGRATION_GUIDE.md) - Guide de migration depuis prompt-imagine

## 🚀 Démarrage Rapide

### Installation (à venir)

```bash
# Cloner le dépôt
git clone https://github.com/TristanV/Hypermedia.git
cd Hypermedia

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

### Utilisation Basique (Phase 1)

```python
from hypermedia.drive import MediaCollection

# Créer une collection locale
collection = MediaCollection("Ma Collection")

# Ajouter un média avec détection automatique des doublons
media_id = collection.add_media(
    "/chemin/vers/image.jpg",
    metadata={"tags": ["vacances", "montagne"], "date": "2026-02-10"}
)

# Rechercher par métadonnées
results = collection.search(tags=["montagne"])

# Obtenir les informations d'un média
info = collection.get_media_info(media_id)
print(f"Checksum: {info.checksum}")
print(f"Taille: {info.size} bytes")
```

## 🏗️ Structure du Projet

```
Hypermedia/
├── documentation/           # Documentation complète
│   ├── ROADMAP.md
│   ├── SPECIFICATIONS_FONCTIONNELLES.md
│   ├── SPECIFICATIONS_TECHNIQUES.md
│   ├── ARCHITECTURE_HM_DRIVE.md
│   ├── ARCHITECTURE_HM_SCENE.md
│   └── MIGRATION_GUIDE.md
├── hypermedia/             # Package principal (à créer)
│   ├── __init__.py
│   ├── drive/             # Couche HM-Drive
│   │   ├── __init__.py
│   │   ├── collection.py
│   │   ├── checksum.py
│   │   ├── deduplication.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── metadata_extractor.py
│   ├── scene/             # Couche HM-Scene (Phase 3)
│   │   └── __init__.py
│   └── common/            # Utilitaires partagés
│       └── __init__.py
├── tests/                 # Tests unitaires et d'intégration
│   ├── test_drive/
│   └── test_scene/
├── examples/              # Exemples d'utilisation
├── TODO.md               # Liste des tâches détaillée
├── requirements.txt      # Dépendances runtime
├── requirements-dev.txt  # Dépendances développement
├── setup.py             # Configuration du package
└── README.md            # Ce fichier
```

## 📋 Phases de Développement

### ✅ Phase 0 - Conception (Terminée)
- [x] Vision stratégique et architecture globale
- [x] Spécifications fonctionnelles et techniques
- [x] Documentation exhaustive

### 🔄 Phase 1 - Fondations HM-Drive (En cours)
- [ ] Structure du package Python
- [ ] Système de collections local
- [ ] Checksums BLAKE2b et déduplication
- [ ] Modèle de données SQLite
- [ ] Métadonnées enrichies

### 🔜 Phase 2 - API et Synchronisation
- API RESTful avec FastAPI
- Synchronisation pair-à-pair
- Détection et résolution de conflits

### 🔜 Phase 3 - HM-Scene
- Modèle de scènes multi-échelles
- Navigation hypermedia non linéaire
- Système de transitions et contextes

### 🔜 Phase 4 - Fonctionnalités Avancées
- Embeddings multimodaux et recherche sémantique
- Clustering et recommandations IA
- Export et interopérabilité

Consultez [ROADMAP.md](documentation/ROADMAP.md) et [TODO.md](TODO.md) pour plus de détails.

## 🛠️ Technologies

### Phase 1 (Fondations)
- **Python 3.11+** - Langage principal
- **SQLAlchemy** - ORM pour SQLite
- **BLAKE2b** - Fonction de hachage cryptographique
- **Pillow** - Traitement d'images et extraction EXIF
- **mutagen** - Métadonnées audio
- **pytest** - Framework de tests
- **black** - Formatage de code
- **mypy** - Typage statique

### Phases Futures
- **FastAPI** - API REST (Phase 2)
- **libp2p** / **IPFS** - Réseau pair-à-pair (Phase 2)
- **Transformers** / **sentence-transformers** - Embeddings IA (Phase 4)
- **NetworkX** - Graphes de navigation (Phase 3)

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

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

**Statut actuel** : Phase 1 - Fondations HM-Drive  
**Dernière mise à jour** : 2026-02-10
