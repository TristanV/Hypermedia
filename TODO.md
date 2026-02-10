# TODO List - Projet Hypermedia

## Phase 1 - Fondations HM-Drive (En cours)

### Infrastructure de base
- [x] Créer la structure du package Python `hypermedia/`
  - [x] `hypermedia/__init__.py`
  - [x] `hypermedia/drive/` (couche stockage)
  - [x] `hypermedia/scene/` (couche scènes)
  - [x] `hypermedia/common/` (utilitaires partagés)
- [x] Configurer les outils de développement
  - [x] Configuration pytest (`tests/`, `pytest.ini`)
  - [x] Configuration black (`.black.toml` ou `pyproject.toml`)
  - [x] Configuration mypy (`mypy.ini`)
  - [x] Pre-commit hooks (`.pre-commit-config.yaml`)
- [x] Créer environnement virtuel et dépendances
  - [x] `requirements.txt` (dépendances runtime)
  - [x] `requirements-dev.txt` (dépendances dev/test)
  - [x] `setup.py` ou `pyproject.toml` pour installation package

### Système de collections local (HM-Drive)
- [ ] Améliorer `hypermedia/drive/collection.py`
  - [x] Classe `MediaCollection` avec gestion locale (squelette existant)
  - [ ] Compléter méthodes CRUD de base (add, get, delete, list)
  - [ ] Intégration avec le système de base de données
  - [ ] Gestion avancée du répertoire de stockage local
- [x] Développer le système de checksums BLAKE2b
  - [x] `hypermedia/drive/checksum.py` (implémenté)
  - [x] Fonction `compute_blake2b(file_path)` 
  - [x] Fonction `verify_integrity(file_path, checksum)`
- [x] Implémenter la détection de doublons
  - [x] `hypermedia/drive/deduplication.py` (implémenté)
  - [x] Index des checksums par collection
  - [x] Détection avant ajout de nouveau média
  - [x] Options de politique (ignorer/référencer/alerter)

### Modèle de données SQLite
- [x] Créer le schéma de base de données
  - [x] `hypermedia/drive/models.py` avec définitions SQLAlchemy
  - [x] Table `media_items` (id, checksum, path, mime_type, size, created_at)
  - [x] Table `collections` (id, name, description, created_at)
  - [x] Table `collection_items` (relation many-to-many)
  - [x] Table `metadata` (key-value enrichi par item)
- [x] Implémenter le gestionnaire de base de données
  - [x] `hypermedia/drive/database.py`
  - [x] Connexion et initialisation du schéma
  - [ ] Migrations (Alembic) - À faire
  - [x] Session management

### Gestion des métadonnées enrichies
- [ ] Améliorer l'extracteur de métadonnées
  - [x] `hypermedia/drive/metadata_extractor.py` (squelette existant)
  - [ ] Extraction EXIF (images) - Implémentation à compléter
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
- [ ] Docstrings complètes (style Google/NumPy) - En cours
- [x] Exemples d'usage dans `examples/phase1/`
- [x] Guide de contribution (`CONTRIBUTING.md`)

---

## Tâches prioritaires immédiates

### À faire maintenant (Sprint actuel)
1. **Compléter l'extracteur de métadonnées** (`metadata_extractor.py`)
   - Implémenter extraction EXIF pour images
   - Ajouter support audio (ID3, Vorbis)
   - Ajouter support vidéo (ffmpeg)
   - Gérer les erreurs et cas limites

2. **Améliorer MediaCollection** (`collection.py`)
   - Intégrer avec DatabaseManager
   - Implémenter ajout de média avec détection de doublons
   - Ajouter gestion des métadonnées lors de l'ajout
   - Implémenter recherche et filtrage

3. **Créer tests unitaires de base**
   - Tests pour models.py (création, relations, contraintes)
   - Tests pour database.py (connexion, sessions, transactions)
   - Tests pour checksum.py (calcul, vérification)
   - Tests pour deduplication.py (détection, politiques)

4. **Documentation et exemples**
   - Compléter docstrings pour tous les modules
   - Créer guide d'utilisation rapide
   - Ajouter exemples d'intégration

### À planifier (Prochains sprints)
5. **Migrations de base de données**
   - Configurer Alembic
   - Créer migration initiale
   - Documentation de gestion des migrations

6. **Optimisations et performance**
   - Indexation optimale des colonnes
   - Caching des checksums
   - Batch operations pour imports massifs

7. **CLI (Interface en ligne de commande)**
   - Créer commandes de base (init, add, list, search)
   - Intégration avec rich pour UI avancée
   - Commandes d'export/import

---

## Phase 2 - API et Synchronisation (Planifié)

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

## Phase 3 - HM-Scene (Système de scènes) (Planifié)

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

## Phase 4 - Fonctionnalités Avancées (Planifié)

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

## Changelog

### 2026-02-10 - Implémentations majeures Phase 1
- ✅ Implémentation complète des modèles SQLAlchemy (models.py)
- ✅ Implémentation complète du DatabaseManager (database.py)
- ✅ Création d'exemples d'utilisation Phase 1
- ✅ Mise à jour de la TODO list

**Dernière mise à jour** : 2026-02-10 02:40 CET  
**Phase active** : Phase 1 - Fondations HM-Drive  
**Statut** : En développement actif - Modèles et DB implémentés
**Progression Phase 1** : ~45% (fondations solides posées)
