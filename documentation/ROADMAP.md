# Roadmap du Projet Hypermedia

## Vision et Objectifs Stratégiques

### Vision
Construire une librairie Python portable **Hypermedia (HM)** permettant la gestion décentralisée de médias avec navigation non linéaire et mise en scène dynamique. Le projet extrait et généralise les concepts essentiels de **prompt-imagine** pour créer une infrastructure universelle de gestion d'hyperdocuments.

### Objectifs stratégiques
1. **Portabilité universelle** : Déploiement sur tout système d'exploitation (Linux, macOS, Windows) et type de machine
2. **Résilience** : Fonctionnement en mode dégradé avec synchronisation différée en cas de déconnexion
3. **Décentralisation partielle** : Architecture distribuée sans point de défaillance unique
4. **Extensibilité** : Support de nouveaux formats média et types d'hypermedia composites
5. **Ergonomie** : Navigation intuitive multi-échelle et multi-modale

---

## Architecture en 3 Couches

```
┌─────────────────────────────────────────┐
│    HM-Scene (Présentation)              │
│  - Scènes dynamiques                    │
│  - Langage HM-DSS                       │
│  - Adaptation multi-support             │
├─────────────────────────────────────────┤
│    Métadonnées & Navigation             │
│  - Descripteurs pondérés                │
│  - Tags & taxonomies                    │
│  - Graphe généalogique                  │
├─────────────────────────────────────────┤
│    HM-Drive (Stockage)                  │
│  - Système de fichiers distribué        │
│  - Synchronisation & résilience         │
│  - Collections & URI unifiés            │
└─────────────────────────────────────────┘
```

---

## Phases du Projet

### Phase 0 : Préparation (Février 2026) ✅ EN COURS

**Objectif** : Analyse et spécifications

**Livrables** :
- ✅ Analyse du dépôt prompt-imagine
- ✅ Identification des éléments réutilisables
- ✅ Spécifications fonctionnelles et techniques
- ✅ Architecture conceptuelle HM-Drive et HM-Scene
- ✅ Roadmap et planning

**Durée estimée** : 1 semaine

---

### Phase 1 : Fondations HM-Drive (Mars 2026)

**Objectif** : Système de stockage local et métadonnées de base

#### Milestone 1.1 : Système de fichiers local (semaines 1-2)
- Gestion de collections arborescentes
- API de base : `create_collection()`, `add_media()`, `list_media()`
- Calcul de checksums (BLAKE2b)
- Détection de doublons
- Support formats de base : images (JPEG, PNG, WebP), vidéos (MP4, WebM)

#### Milestone 1.2 : Métadonnées enrichies (semaines 3-4)
- Modèle de données SQLite
- Métadonnées physiques (taille, format, dimensions, durée)
- Descripteurs textuels
- Système de tags avec autocomplétion
- Définisseurs pondérés (migration des "prompts" de prompt-imagine)

#### Milestone 1.3 : Génération de dérivés (semaine 5)
- Thumbnails adaptatifs (multiples résolutions)
- Extraction de métadonnées EXIF/IPTC
- Transcoding vidéo léger (preview, compression)

**Livrables Phase 1** :
- Module `hm.drive.local`
- Module `hm.metadata`
- Tests unitaires (>80% couverture)
- Documentation API

**Durée estimée** : 5 semaines

---

### Phase 2 : URI et Liens Symboliques (Avril 2026)

**Objectif** : Système d'adressage unifié et navigation intra-drive

#### Milestone 2.1 : Schéma URI (semaines 1-2)
- Définition du schéma `hm://` 
- Format : `hm://[instance]/[collection]/[media_id]`
- Résolution d'URI vers chemins physiques
- Support des fragments : `hm://...#timestamp` pour vidéos

#### Milestone 2.2 : Liens symboliques et graphe (semaines 3-4)
- Liens entre collections (équivalent symlink)
- Relations parent-enfant (généalogie)
- Relations sémantiques (similarité, opposition, dérivation)
- API de parcours de graphe : `get_ancestors()`, `get_descendants()`, `get_related()`

**Livrables Phase 2** :
- Module `hm.uri`
- Module `hm.graph`
- Spécification URI complète
- Exemples de parcours de graphe

**Durée estimée** : 4 semaines

---

### Phase 3 : Distribution et Synchronisation (Mai-Juin 2026)

**Objectif** : HM-Drive distribué avec résilience

#### Milestone 3.1 : Architecture d'instance (semaines 1-2)
- Concept d'instance HM-Drive
- Dossier principal (local)
- Configuration des instances distantes
- Protocole de découverte (mDNS/Zeroconf)

#### Milestone 3.2 : Abonnements (semaines 3-4)
- Abonnement mono-directionnel (pull)
- Abonnement bi-directionnel (sync)
- Gestion des conflits (last-write-wins, versioning)
- Politique de cache (LRU, taille max)

#### Milestone 3.3 : Synchronisation réseau (semaines 5-7)
- Protocole de transfert (REST API ou gRPC)
- Delta sync (transfert incrémental)
- Compression à la volée
- Authentification et chiffrement (TLS)

#### Milestone 3.4 : Résilience (semaine 8)
- Mode déconnecté (queue de synchronisation)
- Détection de panne réseau
- Réconciliation automatique au retour en ligne
- Logs de synchronisation

**Livrables Phase 3** :
- Module `hm.drive.distributed`
- Module `hm.sync`
- Protocole de synchronisation documenté
- Tests d'intégration multi-instances

**Durée estimée** : 8 semaines

---

### Phase 4 : Hypermedia Composites (Juillet 2026)

**Objectif** : Support des hypermedia comme composition récursive

#### Milestone 4.1 : Modèle de composition (semaines 1-2)
- Format de fichier `.hm` (JSON ou YAML)
- Références à des médias simples ou composites
- Métadonnées de composition (layout, ordre, durée)
- Validation de graphe (détection de cycles)

#### Milestone 4.2 : Résolution récursive (semaines 3-4)
- Chargement paresseux (lazy loading)
- Cache de résolution
- Gestion des médias distants non disponibles
- Fallback vers thumbnails

**Livrables Phase 4** :
- Module `hm.composite`
- Spécification format `.hm`
- Exemples de compositions
- Validateur de composition

**Durée estimée** : 4 semaines

---

### Phase 5 : HM-Scene - Couche Présentation (Août-Septembre 2026)

**Objectif** : Système de mise en scène et navigation

#### Milestone 5.1 : Modèle de scène (semaines 1-2)
- Concept de scène (vue sur une collection)
- Modes de visualisation : grille, liste, timeline, graphe
- Pagination dynamique
- Filtres et tri

#### Milestone 5.2 : Langage HM-DSS v0.1 (semaines 3-5)
- Syntaxe inspirée CSS
- Sélecteurs de médias (par type, tag, collection)
- Propriétés de mise en page (layout, spacing, size)
- Propriétés de navigation (transitions, affordances)
- Parser et interpréteur HM-DSS

#### Milestone 5.3 : Adaptation multi-support (semaines 6-7)
- Détection du support (desktop, mobile, projection)
- Media queries HM-DSS
- Templates de scènes prédéfinis

#### Milestone 5.4 : Interactivité (semaine 8)
- Événements utilisateur (clic, hover, scroll)
- Actions : navigation, filtrage, zoom, lecture
- État de la scène (historique, bookmarks)

**Livrables Phase 5** :
- Module `hm.scene`
- Spécification HM-DSS v0.1
- Parser HM-DSS
- Moteur de rendu (backend agnostique)
- Collection de templates

**Durée estimée** : 8 semaines

---

### Phase 6 : Interfaces et Applications (Octobre-Novembre 2026)

**Objectif** : Frontends utilisables et intégration

#### Milestone 6.1 : Interface Web (semaines 1-4)
- Application Flask/FastAPI
- Rendu HM-Scene en HTML/CSS/JS
- Composants interactifs (galerie, lightbox, graphe)
- Responsive design

#### Milestone 6.2 : CLI (semaines 5-6)
- Commandes de gestion : `hm init`, `hm add`, `hm sync`
- Inspection : `hm list`, `hm show`, `hm graph`
- Maintenance : `hm check`, `hm repair`

#### Milestone 6.3 : Migration prompt-imagine (semaines 7-8)
- Script de migration automatique
- Import des collections existantes
- Conversion des prompts en définisseurs
- Préservation de la généalogie

**Livrables Phase 6** :
- Application web `hm-web`
- CLI `hm`
- Outil de migration `hm-migrate`
- Documentation utilisateur

**Durée estimée** : 8 semaines

---

### Phase 7 : Optimisation et Production (Décembre 2026)

**Objectif** : Robustesse, performance et déploiement

#### Milestone 7.1 : Performance (semaines 1-2)
- Profiling et optimisation
- Indexation base de données
- Cache multi-niveaux
- Pagination efficace (cursors)

#### Milestone 7.2 : Tests et qualité (semaines 3-4)
- Tests de charge
- Tests de résilience (network failures)
- Tests de sécurité (injection, XSS)
- Couverture >90%

#### Milestone 7.3 : Packaging et distribution (semaine 5)
- Package PyPI
- Images Docker
- Documentation d'installation
- Exemples de déploiement

#### Milestone 7.4 : Documentation finale (semaine 6)
- Guide de démarrage rapide
- Tutoriels
- Référence API complète
- Cookbook (recettes courantes)

**Livrables Phase 7** :
- Package `hypermedia` sur PyPI
- Images Docker officielles
- Documentation complète
- Site web du projet

**Durée estimée** : 6 semaines

---

## Timeline Globale

```
2026
├── Février      : Phase 0 (Spécifications) ✅
├── Mars         : Phase 1 (Fondations HM-Drive)
├── Avril        : Phase 2 (URI & Liens)
├── Mai-Juin     : Phase 3 (Distribution)
├── Juillet      : Phase 4 (Composites)
├── Août-Sept    : Phase 5 (HM-Scene)
├── Oct-Nov      : Phase 6 (Interfaces)
└── Décembre     : Phase 7 (Production)

v0.1.0 : Mars 2026 (HM-Drive local)
v0.2.0 : Avril 2026 (URI)
v0.3.0 : Juin 2026 (Distribution)
v0.4.0 : Juillet 2026 (Composites)
v0.5.0 : Septembre 2026 (HM-Scene)
v1.0.0 : Décembre 2026 (Production ready)
```

**Durée totale estimée** : 11 mois (février - décembre 2026)

---

## Risques et Mitigation

### Risques techniques

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Complexité de la synchronisation distribuée | Élevé | Moyen | Prototypage précoce, utilisation de bibliothèques éprouvées (rsync, git-like) |
| Performance sur gros volumes (>100k médias) | Moyen | Élevé | Indexation agressive, pagination, benchmarking continu |
| Cycles dans les compositions récursives | Moyen | Faible | Validation de graphe acyclique dirigé (DAG), limite de profondeur |
| Parsing HM-DSS trop ambitieux | Moyen | Moyen | Commencer avec syntaxe minimale, itérer progressivement |

### Risques organisationnels

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Dérive des objectifs (scope creep) | Élevé | Moyen | Roadmap stricte, phases clairement délimitées |
| Manque de retours utilisateurs | Moyen | Élevé | Releases fréquentes, alpha/beta testing dès Phase 6 |
| Documentation insuffisante | Moyen | Moyen | Documentation incrémentale, TDD avec docstrings |

---

## Dépendances Critiques

### Bibliothèques Python essentielles
- **Stockage** : SQLite (embedded), SQLAlchemy (ORM)
- **Réseau** : aiohttp, FastAPI, websockets
- **Médias** : Pillow, opencv-python, ffmpeg-python
- **Sync** : watchdog (file monitoring), paramiko (SFTP)
- **DSL** : pyparsing ou lark (parsing HM-DSS)
- **Graphe** : networkx (analyse de graphe)

### Contraintes de portabilité
- Python ≥3.10 (match statements, type hints)
- Éviter dépendances système complexes (compiler ffmpeg si nécessaire)
- Tests sur Linux, macOS, Windows

---

## Critères de Succès

### Phase 1 (v0.1.0)
- [ ] Import d'une collection de 1000 images en <30s
- [ ] Détection de 100% des doublons
- [ ] Génération de thumbnails en parallèle (4+ workers)

### Phase 3 (v0.3.0)
- [ ] Synchronisation de 10GB entre instances en <5min (LAN)
- [ ] Résilience à 5 déconnexions/reconnexions consécutives
- [ ] Résolution de conflits sans perte de données

### Phase 5 (v0.5.0)
- [ ] Rendu d'une scène de 100 médias en <1s
- [ ] Support de 10+ templates HM-DSS
- [ ] Navigation fluide (60fps) sur grilles de 500+ éléments

### Phase 7 (v1.0.0)
- [ ] Package installable via `pip install hypermedia`
- [ ] Documentation complète (>100 pages)
- [ ] 10+ utilisateurs alpha/beta testeurs
- [ ] Couverture de tests >90%

---

## Évolutions Futures (Post-v1.0)

### v1.1 : Intelligence artificielle
- Extraction automatique de tags (vision AI)
- Génération de descriptions textuelles
- Clustering sémantique des collections
- Recommandations de médias similaires

### v1.2 : Collaboration
- Annotations collaboratives
- Commentaires et discussions
- Workflows de validation (modération)
- Droits d'accès granulaires

### v1.3 : Intégrations
- Connecteurs vers clouds (S3, GCS, Azure)
- Import depuis réseaux sociaux (Instagram, Flickr)
- Export vers plateformes de publication
- API REST publique

### v2.0 : Blockchain & NFT
- Horodatage cryptographique des créations
- Preuve d'authenticité et provenance
- Tokenisation optionnelle des hypermedia

---

## Contributions et Gouvernance

### Modèle de développement
- **Licence** : MIT (open source permissive)
- **Contributions** : Pull requests avec review obligatoire
- **Issues** : GitHub Issues avec labels (bug, feature, doc)
- **Releases** : Semantic versioning (semver.org)

### Communication
- **Discussions** : GitHub Discussions
- **Documentation** : ReadTheDocs ou GitHub Pages
- **Demos** : YouTube ou site web dédié

---

## Conclusion

Cette roadmap définit un chemin pragmatique vers une librairie Hypermedia robuste et extensible. L'approche incrémentale par phases permet de valider chaque composant avant d'ajouter de la complexité. La priorité est donnée à la **portabilité**, la **résilience** et l'**ergonomie**, héritées des leçons de prompt-imagine.

**Prochain jalon immédiat** : Démarrage de la Phase 1 (HM-Drive local) en mars 2026.
