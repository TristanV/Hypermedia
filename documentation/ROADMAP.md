# Roadmap du projet Hypermedia

## Vision et objectifs stratégiques

**Hypermedia (HM)** est une librairie Python portable destinée à créer un écosystème distribué et résilient de gestion d'hyperdocuments multimédia. Le projet extrait et généralise les concepts clés de **prompt-imagine** pour construire une infrastructure modulaire, multi-plateforme et extensible.

### Objectifs principaux

1. **Portabilité maximale** : Code Python pur, déployable sur tout OS (Linux, macOS, Windows) et tout type de machine
2. **Décentralisation partielle** : Architecture de stockage distribuée avec synchronisation locale et résilience à la déconnexion
3. **Composition récursive** : Support d'hypermedia composites (médias simples + hypermedia imbriqués)
4. **Mise en scène dynamique** : Système de présentation adaptative via langage HM-DSS
5. **Extensibilité** : Architecture modulaire permettant l'ajout de nouveaux formats, protocoles et modes de visualisation

---

## Architecture en trois couches

```
┌─────────────────────────────────────────────────────┐
│           HM-SCENE (Couche Présentation)            │
│  • Mise en scène adaptative                         │
│  • Langage HM-DSS (Dynamic Scene Sheet)             │
│  • Navigation et déambulation                       │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│        MÉTADONNÉES & DESCRIPTEURS (Couche Sémantique)│
│  • Définisseurs pondérés (prompts)                  │
│  • Tags et taxonomies                               │
│  • Relations généalogiques                          │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│          HM-DRIVE (Couche Stockage)                 │
│  • Système de fichiers distribué                    │
│  • Synchronisation et cache local                   │
│  • Collections arborescentes                        │
│  • URI unifiés                                      │
└─────────────────────────────────────────────────────┘
```

---

## Phases de développement

### Phase 0 : Préparation et architecture (Semaines 1-2) ✅ EN COURS

**Objectif** : Poser les fondations conceptuelles et organisationnelles

- [x] Analyse approfondie de prompt-imagine
- [x] Identification des patterns réutilisables
- [x] Création du dépôt GitHub TristanV/Hypermedia
- [x] Rédaction de la documentation initiale (roadmap, spécifications)
- [ ] Définition de l'architecture modulaire
- [ ] Choix des dépendances Python (minimales)
- [ ] Setup du projet (structure de dossiers, requirements.txt, tests)

**Livrables** :
- Documentation complète (ROADMAP, SPECIFICATIONS_FONCTIONNELLES, SPECIFICATIONS_TECHNIQUES)
- Structure de projet Python avec modules vides
- Environnement de test configuré (pytest)

---

### Phase 1 : HM-Drive Core (Semaines 3-6)

**Objectif** : Implémenter le système de stockage distribué de base

#### Jalon 1.1 : Stockage local (Semaine 3)
- [ ] Classe `HMDrive` avec dossier principal
- [ ] Gestion des collections (arborescence de dossiers)
- [ ] URI unifiés pour adressage des médias (`hm://collection/path/to/media`)
- [ ] Métadonnées physiques (checksums BLAKE2b, taille, format, timestamps)
- [ ] Support multi-formats (image: jpg/png/webp, vidéo: mp4/webm, audio: mp3/wav, texte: txt/md)

#### Jalon 1.2 : Système de cache (Semaine 4)
- [ ] Cache local pour médias distants
- [ ] Politique d'éviction (LRU, taille maximale configurable)
- [ ] Indexation des médias en cache
- [ ] Mécanisme de préchargement (prefetching)

#### Jalon 1.3 : Synchronisation basique (Semaine 5)
- [ ] Abonnements mono-directionnels (lecture seule)
- [ ] Détection des changements (polling ou watchdog)
- [ ] Copie incrémentale des nouveaux médias
- [ ] Gestion des conflits (timestamps)

#### Jalon 1.4 : Résilience et robustesse (Semaine 6)
- [ ] Mode hors-ligne (fallback sur cache)
- [ ] Détection de déconnexion/reconnexion
- [ ] Transactions atomiques pour les métadonnées
- [ ] Logs et traçabilité des opérations

**Livrables** :
- Module `hm.drive` fonctionnel
- Tests unitaires (couverture > 80%)
- Documentation API
- Exemples d'utilisation

---

### Phase 2 : Métadonnées et descripteurs (Semaines 7-9)

**Objectif** : Enrichir les médias avec métadonnées sémantiques

#### Jalon 2.1 : Système de métadonnées (Semaine 7)
- [ ] Schéma de métadonnées extensible (JSON/YAML)
- [ ] Métadonnées physiques vs. sémantiques
- [ ] Système de tags avec autocomplétion
- [ ] Taxonomies et ontologies (optionnel)

#### Jalon 2.2 : Définisseurs pondérés (Semaine 8)
- [ ] Modèle de "prompts" généralisés (définisseurs textuels pondérés)
- [ ] Parsing des définisseurs (poids, catégories, négations)
- [ ] Indexation pour recherche full-text
- [ ] Génération de wordclouds à partir des définisseurs

#### Jalon 2.3 : Relations généalogiques (Semaine 9)
- [ ] Graphe de relations (ancêtres/descendants)
- [ ] Références croisées entre médias
- [ ] Visualisation de la généalogie (export GraphML/DOT)
- [ ] Héritage de métadonnées (propagation configurable)

**Livrables** :
- Module `hm.metadata` fonctionnel
- Base de données SQLite pour métadonnées
- Requêtes complexes (tags, définisseurs, généalogie)
- Documentation des schémas

---

### Phase 3 : Hypermedia composites (Semaines 10-12)

**Objectif** : Support des hypermedia récursifs

#### Jalon 3.1 : Format hypermedia (Semaine 10)
- [ ] Spécification du format `.hm` (JSON/YAML)
- [ ] Référencement de médias locaux et distants
- [ ] Composition récursive (hypermedia contenant des hypermedia)
- [ ] Validation de la structure

#### Jalon 3.2 : Résolution d'URI (Semaine 11)
- [ ] Résolution d'URI distants (`hm://instance_id/collection/media`)
- [ ] Téléchargement à la demande
- [ ] Gestion des dépendances transitives
- [ ] Détection de cycles (références circulaires)

#### Jalon 3.3 : Liens symboliques (Semaine 12)
- [ ] Liens entre collections (navigation non linéaire)
- [ ] Résolution de liens symboliques
- [ ] Liens externes (vers autres instances HM-Drive)
- [ ] Gestion des liens cassés

**Livrables** :
- Module `hm.composite` fonctionnel
- Parser et validateur de format `.hm`
- Tests d'intégration pour compositions complexes

---

### Phase 4 : Synchronisation avancée (Semaines 13-15)

**Objectif** : Implémenter la synchronisation bidirectionnelle

#### Jalon 4.1 : Protocole de synchronisation (Semaine 13)
- [ ] API REST pour communication inter-instances
- [ ] Authentification et autorisation (tokens, JWT)
- [ ] Endpoints CRUD pour médias et métadonnées
- [ ] Protocole de découverte d'instances (mDNS/Zeroconf)

#### Jalon 4.2 : Sync bidirectionnelle (Semaine 14)
- [ ] Abonnements bidirectionnels
- [ ] Résolution de conflits (merge automatique ou manuel)
- [ ] Versionnement des médias (optionnel)
- [ ] Propagation des suppressions

#### Jalon 4.3 : Performance et optimisation (Semaine 15)
- [ ] Transfert différentiel (rsync-like)
- [ ] Compression des flux (gzip, zstd)
- [ ] Parallélisation des téléchargements
- [ ] Métriques de performance (débit, latence)

**Livrables** :
- Module `hm.sync` fonctionnel
- API REST documentée (OpenAPI/Swagger)
- Tests d'intégration multi-instances
- Benchmarks de performance

---

### Phase 5 : HM-Scene et langage HM-DSS (Semaines 16-20)

**Objectif** : Système de mise en scène et navigation dynamique

#### Jalon 5.1 : Modèle de scène (Semaine 16)
- [ ] Classe `HMScene` pour représentation d'une vue
- [ ] Adaptation aux supports (desktop, mobile, CLI, web)
- [ ] Système de layouts (grille, liste, mosaïque, timeline)
- [ ] Pagination dynamique

#### Jalon 5.2 : Langage HM-DSS (Semaines 17-18)
- [ ] Spécification du langage (inspiré de CSS)
- [ ] Parser HM-DSS (YAML/DSL custom)
- [ ] Sélecteurs (par type, tag, collection, métadonnées)
- [ ] Règles de style (taille, position, ordre, visibilité)
- [ ] Propriétés dynamiques (transitions, animations)

#### Jalon 5.3 : Moteur de rendu (Semaine 19)
- [ ] Rendu HTML/CSS pour web
- [ ] Rendu terminal (rich/textual pour CLI)
- [ ] Export statique (galerie HTML)
- [ ] Prévisualisation en temps réel

#### Jalon 5.4 : Navigation et interactions (Semaine 20)
- [ ] Navigation non linéaire (liens, retour arrière)
- [ ] Filtres interactifs (par tag, date, collection)
- [ ] Recherche full-text
- [ ] Lightbox et zoom (pour images)
- [ ] Lecture vidéo/audio intégrée

**Livrables** :
- Module `hm.scene` fonctionnel
- Spécification complète HM-DSS
- Exemples de scènes (galerie, timeline, graphe)
- Documentation utilisateur

---

### Phase 6 : Migration et compatibilité (Semaines 21-22)

**Objectif** : Faciliter la migration depuis prompt-imagine

#### Jalon 6.1 : Outil de migration (Semaine 21)
- [ ] Script d'import depuis bases SQLite prompt-imagine
- [ ] Conversion des métadonnées (prompts → définisseurs)
- [ ] Préservation des relations généalogiques
- [ ] Migration des collections et tags

#### Jalon 6.2 : Rétrocompatibilité (Semaine 22)
- [ ] Lecture des formats legacy (CSV backups NightCafe)
- [ ] Export vers formats standards (JSON, CSV)
- [ ] Interopérabilité avec prompt-imagine (mode hybrid)

**Livrables** :
- Script `migrate_from_prompt_imagine.py`
- Documentation de migration
- Exemples de conversion

---

### Phase 7 : Interface utilisateur (Semaines 23-26)

**Objectif** : Créer des interfaces conviviales

#### Jalon 7.1 : CLI (Semaine 23)
- [ ] Commandes de gestion (init, add, sync, search)
- [ ] Interface interactive (questionary/prompt_toolkit)
- [ ] Rendu terminal riche (rich/textual)

#### Jalon 7.2 : API HTTP (Semaine 24)
- [ ] Serveur Flask/FastAPI
- [ ] Endpoints REST complets
- [ ] WebSockets pour sync temps réel
- [ ] Documentation interactive (Swagger UI)

#### Jalon 7.3 : Interface Web (Semaines 25-26)
- [ ] Frontend moderne (Vue.js/React ou templates Jinja2)
- [ ] Galerie responsive
- [ ] Éditeur de scènes HM-DSS (WYSIWYG)
- [ ] Gestionnaire de collections et tags

**Livrables** :
- CLI `hm` fonctionnelle
- Serveur web déployable
- Interface web responsive

---

### Phase 8 : Finalisation et release (Semaines 27-28)

**Objectif** : Préparer la première version stable

#### Jalon 8.1 : Tests et qualité (Semaine 27)
- [ ] Tests d'intégration end-to-end
- [ ] Tests de charge (performance, scalabilité)
- [ ] Analyse de sécurité (injection, XSS, CSRF)
- [ ] Couverture de code > 85%

#### Jalon 8.2 : Documentation et packaging (Semaine 28)
- [ ] Documentation utilisateur complète
- [ ] Tutoriels et guides
- [ ] Packaging PyPI (pip install hypermedia)
- [ ] Docker images
- [ ] CI/CD (GitHub Actions)

#### Jalon 8.3 : Release 1.0.0
- [ ] Tag version 1.0.0
- [ ] Annonce publique
- [ ] Collecte de retours utilisateurs

**Livrables** :
- Version 1.0.0 stable
- Package PyPI publié
- Documentation hébergée (ReadTheDocs)

---

## Jalons critiques et dépendances

### Chemin critique

```
Phase 0 → Phase 1 (HM-Drive) → Phase 2 (Métadonnées) → Phase 3 (Composites)
                                                              ↓
                                            Phase 4 (Sync avancée)
                                                              ↓
                                            Phase 5 (HM-Scene)
                                                              ↓
                              Phase 6 (Migration) + Phase 7 (UI)
                                                              ↓
                                            Phase 8 (Release)
```

### Dépendances entre phases

- **Phase 2** dépend de **Phase 1** (métadonnées stockées dans HM-Drive)
- **Phase 3** dépend de **Phase 1** (références URI)
- **Phase 4** dépend de **Phase 1** (synchronisation des drives)
- **Phase 5** dépend de **Phase 2** et **Phase 3** (affichage des métadonnées et composites)
- **Phase 6** peut démarrer en parallèle de **Phase 5**
- **Phase 7** dépend de **Phases 1-5** (toutes les fonctionnalités de base)

---

## Risques et mitigations

### Risques techniques

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Complexité de la synchronisation bidirectionnelle | Élevé | Moyen | Implémenter d'abord sync unidirectionnelle (Phase 1), puis bidirectionnelle (Phase 4) |
| Performance du cache avec gros volumes | Moyen | Élevé | Benchmarks précoces, indexation efficace, compression |
| Portabilité cross-platform | Moyen | Faible | Utiliser pathlib, éviter les dépendances OS-spécifiques |
| Sécurité des sync distantes | Élevé | Moyen | HTTPS obligatoire, authentification robuste (JWT), sandboxing |
| Complexité du langage HM-DSS | Moyen | Moyen | Commencer simple (subset CSS), itérer selon besoins |

### Risques organisationnels

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Dérive du scope (feature creep) | Élevé | Élevé | Priorisation stricte, MVP first, roadmap versionnée |
| Documentation insuffisante | Moyen | Moyen | Documenter au fil de l'eau, reviews régulières |
| Manque de tests | Élevé | Moyen | TDD, couverture minimale 80%, CI/CD |

---

## Évolutions futures (post-1.0)

### Version 1.1 : Extensibilité
- Système de plugins pour nouveaux formats
- API publique pour extensions tierces
- Marketplace de scènes HM-DSS

### Version 1.2 : Intelligence artificielle
- Auto-tagging par vision par ordinateur
- Génération automatique de définisseurs
- Recommandations de médias similaires
- Clustering automatique de collections

### Version 1.3 : Collaboration
- Édition collaborative temps réel
- Commentaires et annotations
- Historique de versions (git-like)
- Permissions granulaires

### Version 2.0 : Décentralisation complète
- Architecture P2P (libp2p, IPFS)
- Blockchain pour traçabilité (optionnel)
- Chiffrement end-to-end
- Identités décentralisées (DID)

---

## Métriques de succès

### Métriques techniques
- **Performance** : Synchronisation < 1s pour 100 médias, recherche < 100ms
- **Fiabilité** : Disponibilité > 99%, zéro perte de données
- **Scalabilité** : Support de 100k+ médias par instance
- **Qualité** : Couverture de tests > 85%, zéro vulnérabilité critique

### Métriques utilisateur
- **Adoption** : 100+ installations en 6 mois post-release
- **Documentation** : Temps de prise en main < 1h pour utilisateur avancé
- **Satisfaction** : Score NPS > 40

---

## Ressources et estimation

### Effort estimé
- **Phase 0** : 2 semaines (documentation, architecture)
- **Phases 1-4** : 13 semaines (core backend)
- **Phase 5** : 5 semaines (HM-Scene)
- **Phases 6-7** : 6 semaines (migration, UI)
- **Phase 8** : 2 semaines (finalisation)
- **Total** : **28 semaines** (~7 mois) pour 1 développeur full-time

### Stack technologique
- **Langage** : Python 3.10+
- **Dépendances core** : pathlib, hashlib (stdlib), SQLite, requests
- **Dépendances optionnelles** : Flask/FastAPI, Pillow, watchdog, rich, wordcloud
- **Tests** : pytest, pytest-cov, hypothesis
- **CI/CD** : GitHub Actions
- **Documentation** : Sphinx, ReadTheDocs

---

## Conclusion

Cette roadmap propose un développement structuré et incrémental de la librairie **Hypermedia**, avec des jalons clairs et des livrables tangibles à chaque phase. L'approche modulaire permet de tester et valider chaque composant indépendamment, tout en préservant la cohérence architecturale globale.

Le projet vise à créer une infrastructure pérenne, extensible et facile à déployer pour la gestion d'hyperdocuments multimédia distribués, en capitalisant sur les acquis de **prompt-imagine** tout en généralisant les concepts pour un usage plus large.
