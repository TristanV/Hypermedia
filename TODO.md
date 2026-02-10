# TODO List - Projet Hypermedia

## Phase 1 - Fondations HM-Drive (En cours)

### Infrastructure de base
- [ ] Créer la structure du package Python `hypermedia/`
  - [ ] `hypermedia/__init__.py`
  - [ ] `hypermedia/drive/` (couche stockage)
  - [ ] `hypermedia/scene/` (couche scènes)
  - [ ] `hypermedia/common/` (utilitaires partagés)
- [ ] Configurer les outils de développement
  - [ ] Configuration pytest (`tests/`, `pytest.ini`)
  - [ ] Configuration black (`.black.toml` ou `pyproject.toml`)
  - [ ] Configuration mypy (`mypy.ini`)
  - [ ] Pre-commit hooks (`.pre-commit-config.yaml`)
- [ ] Créer environnement virtuel et dépendances
  - [ ] `requirements.txt` (dépendances runtime)
  - [ ] `requirements-dev.txt` (dépendances dev/test)
  - [ ] `setup.py` ou `pyproject.toml` pour installation package

### Système de collections local (HM-Drive)
- [ ] Implémenter `hypermedia/drive/collection.py`
  - [ ] Classe `MediaCollection` avec gestion locale
  - [ ] Méthodes CRUD de base (add, get, delete, list)
  - [ ] Gestion du répertoire de stockage local
- [ ] Développer le système de checksums BLAKE2b
  - [ ] `hypermedia/drive/checksum.py`
  - [ ] Fonction `compute_blake2b(file_path)` 
  - [ ] Fonction `verify_integrity(file_path, checksum)`
- [ ] Implémenter la détection de doublons
  - [ ] `hypermedia/drive/deduplication.py`
  - [ ] Index des checksums par collection
  - [ ] Détection avant ajout de nouveau média
  - [ ] Options de politique (ignorer/référencer/alerter)

### Modèle de données SQLite
- [ ] Créer le schéma de base de données
  - [ ] `hypermedia/drive/models.py` avec définitions SQLAlchemy
  - [ ] Table `media_items` (id, checksum, path, mime_type, size, created_at)
  - [ ] Table `collections` (id, name, description, created_at)
  - [ ] Table `collection_items` (relation many-to-many)
  - [ ] Table `metadata` (key-value enrichi par item)
- [ ] Implémenter le gestionnaire de base de données
  - [ ] `hypermedia/drive/database.py`
  - [ ] Connexion et initialisation du schéma
  - [ ] Migrations (Alembic)
  - [ ] Session management

### Gestion des métadonnées enrichies
- [ ] Développer l'extracteur de métadonnées
  - [ ] `hypermedia/drive/metadata_extractor.py`
  - [ ] Extraction EXIF (images)
  - [ ] Extraction ID3/Vorbis (audio)
  - [ ] Extraction métadonnées vidéo (ffmpeg)
  - [ ] Extraction métadonnées documents (PDF, etc.)
- [ ] Implémenter le système de métadonnées personnalisées
  - [ ] Interface pour ajout/modification métadonnées utilisateur
  - [ ] Validation des schémas de métadonnées
  - [ ] Indexation pour recherche rapide

### Tests unitaires Phase 1
- [ ] Tests pour `collection.py`
- [ ] Tests pour `checksum.py` et `deduplication.py`
- [ ] Tests pour modèles SQLite
- [ ] Tests pour `metadata_extractor.py`
- [ ] Couverture de code > 80%

### Documentation Phase 1
- [x] README.md principal avec liens documentation
- [ ] Docstrings complètes (style Google/NumPy)
- [ ] Exemples d'usage dans `examples/phase1/`
- [ ] Guide de contribution (`CONTRIBUTING.md`)

---

## Phase 2 - API et Synchronisation (À venir)

### API RESTful
- [ ] Développer endpoints FastAPI
- [ ] Authentification et autorisation
- [ ] Documentation OpenAPI/Swagger
- [ ] Rate limiting et caching

### Synchronisation pair-à-pair
- [ ] Protocole de synchronisation
- [ ] Détection des conflits
- [ ] Résolution automatique/manuelle
- [ ] Synchronisation incrémentale

---

## Phase 3 - HM-Scene (Système de scènes) (À venir)

### Architecture HM-Scene
- [ ] Modèle de scènes multi-échelles
- [ ] Graphe de navigation hypermedia
- [ ] Moteur de transitions
- [ ] Système de contextes locaux

### Interactions et IHM
- [ ] Interface de navigation non linéaire
- [ ] Filtres et vues multiples
- [ ] Manipulation directe des médias
- [ ] Preview et streaming adaptatif

---

## Phase 4 - Fonctionnalités Avancées (À venir)

### IA et Embeddings
- [ ] Génération d'embeddings multimodaux
- [ ] Recherche sémantique
- [ ] Clustering automatique
- [ ] Recommandations contextuelles

### Export et Interopérabilité
- [ ] Export formats standards (JSON-LD, RDF)
- [ ] Import depuis autres systèmes
- [ ] Plugins d'intégration

---

## Notes de migration depuis prompt-imagine

### Éléments à récupérer
- [ ] Logique de checksum de `app/initial_ingestion.py`
- [ ] Gestion des doublons de `app/orphan_manager.py`
- [ ] Configuration base de `app/config.py`
- [ ] Utilitaires de `app/utils.py`

### Éléments à adapter
- [ ] Structure Flask → Structure librairie Python
- [ ] Routes web → API publique du package
- [ ] Templates → Pas nécessaire (librairie backend)

---

**Dernière mise à jour** : 2026-02-10  
**Phase active** : Phase 1 - Fondations HM-Drive  
**Statut** : Initialisation
