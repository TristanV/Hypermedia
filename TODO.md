# TODO List - Projet Hypermedia

## Phase 1 - Fondations HM-Drive (⚡ En cours - 75% complété)

### Infrastructure de base ✅ COMPLÉTÉE
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
  - [x] `setup.py` et `pyproject.toml` pour installation package

### Système de collections local (HM-Drive) ✅ COMPLÉTÉ
- [x] Implémenter `hypermedia/drive/collection.py`
  - [x] Classe `MediaCollection` avec gestion locale complète
  - [x] Méthodes CRUD de base (add, get, delete, list, search)
  - [x] Intégration avec le système de base de données
  - [x] Gestion avancée du répertoire de stockage local (sharding)
- [x] Développer le système de checksums BLAKE2b
  - [x] `hypermedia/drive/checksum.py` (implémenté)
  - [x] Fonction `compute_blake2b(file_path)` 
  - [x] Fonction `verify_integrity(file_path, checksum)`
- [x] Implémenter la détection de doublons
  - [x] `hypermedia/drive/deduplication.py` (implémenté)
  - [x] Index des checksums par collection
  - [x] Détection avant ajout de nouveau média
  - [x] Options de politique (ignorer/référencer/alerter)

### Modèle de données SQLite ✅ COMPLÉTÉ
- [x] Créer le schéma de base de données
  - [x] `hypermedia/drive/models.py` avec définitions SQLAlchemy complètes
  - [x] Table `media_items` (id, checksum, path, mime_type, size, created_at)
  - [x] Table `collections` (id, name, description, created_at)
  - [x] Table `collection_items` (relation many-to-many)
  - [x] Table `metadata` (key-value enrichi par item)
- [x] Implémenter le gestionnaire de base de données
  - [x] `hypermedia/drive/database.py` complet
  - [x] Connexion et initialisation du schéma
  - [x] Session management avec context managers
  - [ ] Migrations (Alembic) - À faire si nécessaire

### Gestion des métadonnées enrichies ✅ COMPLÉTÉE
- [x] Implémenter l'extracteur de métadonnées complet
  - [x] `hypermedia/drive/metadata_extractor.py`
  - [x] Extraction EXIF (images via Pillow)
  - [x] Extraction ID3/Vorbis (audio via Mutagen)
  - [x] Extraction métadonnées vidéo (ffprobe)
  - [x] Extraction métadonnées génériques (fichiers)
  - [x] Gestion des erreurs et cas limites
- [x] Implémenter le système de métadonnées personnalisées
  - [x] Interface pour ajout/modification métadonnées utilisateur
  - [x] Stockage flexible (clé-valeur avec source)
  - [x] Intégration dans MediaCollection

### Tests unitaires Phase 1 ⚡ EN COURS (60%)
- [x] Tests pour `models.py` (relations, contraintes, CRUD)
- [x] Tests pour `database.py` (connexion, sessions, transactions)
- [x] Tests pour `checksum.py` (calcul, vérification, edge cases)
- [x] Tests pour `deduplication.py` (détection, politiques)
- [ ] Tests pour `collection.py` (opérations complètes)
- [ ] Tests pour `metadata_extractor.py` (extraction multi-formats)
- [ ] Tests d'intégration end-to-end
- [ ] Couverture de code > 80%

### Documentation Phase 1 ⚡ EN COURS (70%)
- [x] README.md principal avec liens documentation
- [x] Docstrings complètes (style Google/NumPy) pour modules core
- [x] Exemples d'usage dans `examples/phase1_basic_usage.py`
- [x] Guide de contribution (`CONTRIBUTING.md`)
- [ ] Guide d'installation détaillé
- [ ] Guide de déploiement
- [ ] Documentation API complète (Sphinx)

---

## Tâches prioritaires immédiates (Sprint actuel)

### 🔥 Finalisation Phase 1 (Objectif: 100% sous 48h)

1. **Compléter les tests unitaires** (Priorité HAUTE)
   - ✅ Tests models et database
   - ✅ Tests checksum et deduplication
   - ⏳ Tests collection.py (toutes méthodes)
   - ⏳ Tests metadata_extractor.py
   - ⏳ Tests d'intégration complets
   - ⏳ Atteindre 80%+ de couverture

2. **Documentation et guides** (Priorité MOYENNE)
   - ⏳ Guide d'installation pas-à-pas
   - ⏳ Guide "Quick Start" de 5 minutes
   - ⏳ Documentation des patterns d'utilisation
   - ⏳ Générer documentation Sphinx

3. **Optimisations et robustesse** (Priorité MOYENNE)
   - ⏳ Gestion d'erreurs robuste partout
   - ⏳ Logging structuré et niveaux appropriés
   - ⏳ Validation des inputs utilisateur
   - ⏳ Performance : indexation optimale, caching

4. **CLI basique** (Priorité BASSE - BONUS)
   - ⏳ Créer commandes de base (init, add, list, search)
   - ⏳ Intégration avec rich pour UI avancée
   - ⏳ Commandes d'export/import

---

## Phase 2 - API et Synchronisation (Planifié - Q2 2026)

### API RESTful
- [ ] Développer endpoints FastAPI
  - [ ] CRUD collections
  - [ ] Upload/download médias
  - [ ] Recherche avancée
  - [ ] Gestion métadonnées
- [ ] Authentification et autorisation
  - [ ] JWT tokens
  - [ ] Permissions par collection
  - [ ] Multi-utilisateurs
- [ ] Documentation OpenAPI/Swagger automatique
- [ ] Rate limiting et caching (Redis)
- [ ] WebSockets pour notifications temps réel

### Synchronisation pair-à-pair
- [ ] Protocole de synchronisation
  - [ ] Découverte de pairs (mDNS/Bonjour)
  - [ ] Échange de checksums
  - [ ] Transfert incrémental
- [ ] Détection des conflits
  - [ ] Vector clocks ou CRDT
  - [ ] Stratégies de résolution
- [ ] Résolution automatique/manuelle
- [ ] Interface de gestion des conflits

---

## Phase 3 - HM-Scene (Système de scènes) (Planifié - Q3 2026)

### Architecture HM-Scene
- [ ] Modèle de scènes multi-échelles
  - [ ] Graphe de scènes hiérarchique
  - [ ] Contextes et états de navigation
  - [ ] Transitions et animations
- [ ] Graphe de navigation hypermedia
  - [ ] Liens typés entre scènes
  - [ ] Navigation non linéaire
  - [ ] Historique et breadcrumbs
- [ ] Moteur de transitions
  - [ ] Transitions fluides
  - [ ] Préchargement intelligent
  - [ ] Cache adapté
- [ ] Système de contextes locaux
  - [ ] État par scène
  - [ ] Persistance contexte
  - [ ] Restauration état

### Interactions et IHM
- [ ] Interface de navigation non linéaire
  - [ ] Vue graphe interactif
  - [ ] Timeline et chronologie
  - [ ] Cartographie spatiale
- [ ] Filtres et vues multiples
  - [ ] Filtres dynamiques
  - [ ] Vues prédéfinies
  - [ ] Sauvegarde de vues
- [ ] Manipulation directe des médias
  - [ ] Drag & drop
  - [ ] Multi-sélection
  - [ ] Batch operations
- [ ] Preview et streaming adaptatif
  - [ ] Génération de thumbnails
  - [ ] Streaming vidéo adaptatif
  - [ ] Transcoding à la volée

---

## Phase 4 - Fonctionnalités Avancées (Planifié - Q4 2026)

### IA et Embeddings
- [ ] Génération d'embeddings multimodaux
  - [ ] CLIP pour images
  - [ ] Whisper pour audio
  - [ ] Modèles multimodaux unifiés
- [ ] Recherche sémantique
  - [ ] Recherche par similarité
  - [ ] Recherche cross-modale
  - [ ] Indexation vectorielle (FAISS/Qdrant)
- [ ] Clustering automatique
  - [ ] Regroupement par similarité
  - [ ] Détection de thèmes
  - [ ] Organisation automatique
- [ ] Recommandations contextuelles
  - [ ] Suggestions basées contenu
  - [ ] Découverte de relations
  - [ ] Navigation guidée

### Export et Interopérabilité
- [ ] Export formats standards
  - [ ] JSON-LD avec vocabulaires standard
  - [ ] RDF/Turtle
  - [ ] Schema.org markup
- [ ] Import depuis autres systèmes
  - [ ] Google Photos
  - [ ] Dropbox
  - [ ] Formats archives (ZIP, TAR)
- [ ] Plugins d'intégration
  - [ ] Architecture plugin extensible
  - [ ] SDK pour développeurs tiers
  - [ ] Marketplace de plugins

---

## Notes de migration depuis prompt-imagine

### Éléments à récupérer
- [ ] Logique de checksum de `app/initial_ingestion.py`
- [ ] Gestion des doublons de `app/orphan_manager.py`
- [ ] Configuration base de `app/config.py`
- [ ] Utilitaires de `app/utils.py`
- [ ] Patterns d'organisation de `app/routes/`

### Éléments à adapter
- [x] Structure Flask → Librairie Python modulaire
- [ ] Routes web → API publique du package
- [ ] Templates → Pas nécessaire (backend)

---

## Changelog

### 2026-02-10 - Sprint Phase 1 Core (🚀 MAJEUR)
- ✅ Implémentation complète des modèles SQLAlchemy (models.py)
- ✅ Implémentation complète du DatabaseManager (database.py)
- ✅ Extracteur de métadonnées multiformat complet (images/audio/vidéo)
- ✅ MediaCollection avec intégration DB et déduplication complète
- ✅ Suite de tests unitaires (models, database, checksum, dedup)
- ✅ Exemples d'utilisation Phase 1
- ✅ Mise à jour documentation et roadmap

**Dernière mise à jour** : 2026-02-10 02:47 CET  
**Phase active** : Phase 1 - Fondations HM-Drive  
**Statut** : Développement actif - Core implémenté, finalisation en cours
**Progression Phase 1** : ~75% (core fonctionnel, tests et doc à finaliser)
**Prochaine étape** : Finalisation tests + documentation → Release v0.1.0-alpha
