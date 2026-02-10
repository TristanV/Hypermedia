# Spécifications Fonctionnelles - Hypermedia

## 1. Introduction

### 1.1 Contexte

Le projet **Hypermedia** vise à extraire et généraliser les concepts essentiels du projet **prompt-imagine** pour construire une librairie Python portable de gestion d'hyperdocuments. Prompt-imagine a démontré l'efficacité d'une approche basée sur :
- Collections arborescentes de médias
- Métadonnées enrichies (prompts pondérés, tags, descripteurs)
- Généalogie des médias (anciens/descendants)
- Détection de doublons via checksums
- Navigation et recherche avancées

Hypermedia pousse ces concepts plus loin en ajoutant :
- Distribution et synchronisation multi-instances
- Système d'URI unifié
- Hypermedia composites récursifs
- Langage de mise en scène HM-DSS
- Résilience aux déconnexions

### 1.2 Périmètre

**Dans le périmètre** :
- Gestion de médias numériques (images, vidéos, audio, texte)
- Stockage local et distribué
- Métadonnées enrichies et navigation sémantique
- Synchronisation entre instances
- Mise en scène et présentation
- Migration depuis prompt-imagine

**Hors périmètre** (v1.0) :
- Édition de médias (pas de Photoshop-like)
- Intelligence artificielle (classification, reconnaissance) → v1.1+
- Collaboration temps réel (multi-utilisateurs simultanés) → v1.2+
- Intégration clouds tiers (S3, GCS) → v1.3+

### 1.3 Objectifs Fonctionnels

1. **Centraliser et organiser** : Collections arborescentes avec liens symboliques
2. **Enrichir et décrire** : Métadonnées multiples (descripteurs pondérés, tags, relations)
3. **Rechercher et naviguer** : Recherche full-text, filtres, parcours de graphe
4. **Distribuer et synchroniser** : Multi-instances avec résilience
5. **Composer et mettre en scène** : Hypermedia composites + langage HM-DSS
6. **Migrer facilement** : Import automatique depuis prompt-imagine

---

## 2. Acteurs du Système

### 2.1 Utilisateur Final

**Rôle** : Consulter et naviguer dans les collections

**Besoins** :
- Visualiser des galeries de médias
- Rechercher par métadonnées (tags, mots-clés, dates)
- Naviguer dans le graphe relationnel (anciens, descendants)
- Explorer différentes scènes (grille, timeline, graphe)
- Consulter en mode déconnecté

### 2.2 Créateur de Contenu

**Rôle** : Importer, organiser et enrichir les médias

**Besoins** :
- Créer des collections et sous-collections
- Importer des médias (upload, import batch)
- Ajouter des métadonnées (descripteurs, tags, relations)
- Composer des hypermedia (assemblages)
- Définir des scènes personnalisées (HM-DSS)
- Détecter et fusionner les doublons

### 2.3 Administrateur d'Instance

**Rôle** : Configurer et maintenir une instance HM-Drive

**Besoins** :
- Initialiser une instance HM-Drive
- Configurer les abonnements (instances distantes)
- Surveiller la synchronisation
- Gérer le cache local
- Effectuer la maintenance (vérification d'intégrité, réparations)
- Consulter les logs

### 2.4 Système HM-Drive

**Rôle** : Gestion automatique et résilience

**Responsabilités** :
- Calcul automatique de checksums
- Génération de thumbnails
- Détection de doublons
- Synchronisation en arrière-plan
- Gestion du cache (LRU)
- Réconciliation de conflits
- Récupération après déconnexion

---

## 3. Cas d'Usage Principaux

### UC-01 : Créer une Collection

**Acteur** : Créateur de contenu

**Description** : Créer une nouvelle collection dans l'arborescence HM-Drive

**Préconditions** :
- Instance HM-Drive initialisée
- Utilisateur authentifié (si multi-utilisateurs)

**Flux nominal** :
1. L'utilisateur spécifie le nom de la collection
2. L'utilisateur choisit la collection parente (ou racine)
3. L'utilisateur ajoute des métadonnées (description, tags)
4. Le système crée le dossier physique
5. Le système enregistre l'entrée en base de données
6. Le système retourne l'URI de la collection

**Postconditions** :
- Collection accessible via URI `hm://local/[nom_collection]`
- Dossier physique créé dans `instance_root/collections/`

**Variantes** :
- Collection imbriquée (sous-collection)
- Lien symbolique vers collection existante

---

### UC-02 : Importer des Médias

**Acteur** : Créateur de contenu

**Description** : Ajouter des fichiers média à une collection

**Préconditions** :
- Collection cible existe
- Fichiers média valides

**Flux nominal** :
1. L'utilisateur sélectionne la collection cible
2. L'utilisateur sélectionne un ou plusieurs fichiers
3. Pour chaque fichier :
   a. Le système calcule le checksum BLAKE2b
   b. Le système vérifie si un doublon existe
   c. Si doublon détecté : proposition de lier au lieu de dupliquer
   d. Le système copie le fichier dans la collection
   e. Le système extrait les métadonnées physiques (dimensions, durée, etc.)
   f. Le système génère les thumbnails (3 résolutions)
   g. Le système enregistre en base de données
4. Le système retourne la liste des médias importés

**Postconditions** :
- Médias accessibles via URI
- Thumbnails disponibles
- Checksum calculé et indexé

**Variantes** :
- Import batch (dossier complet)
- Import avec métadonnées associées (CSV)
- Import depuis URL distante

**Cas d'erreur** :
- Format non supporté : rejet avec message explicite
- Fichier corrompu : tentative de récupération, sinon rejet
- Espace disque insuffisant : arrêt et nettoyage partiel

---

### UC-03 : Enrichir les Métadonnées

**Acteur** : Créateur de contenu

**Description** : Ajouter ou modifier les métadonnées d'un média

**Flux nominal** :
1. L'utilisateur sélectionne un média
2. L'utilisateur choisit le type de métadonnées à enrichir :
   - **Descripteurs textuels** : titre, description
   - **Définisseurs pondérés** : texte + poids + catégorie
   - **Tags** : sélection multiple avec autocomplétion
   - **Relations** : parent, enfant, similaire, dérivé
3. L'utilisateur saisit les métadonnées
4. Le système valide le format
5. Le système enregistre en base de données
6. Le système met à jour les index (full-text, tags)

**Cas spécifique : Définisseurs pondérés** (hérité de prompt-imagine)

**Format** :
```
type: prompt | style | quality
text: "Description textuelle"
weight: 0.0 - 10.0
category: subject | artistic | technical | ...
```

**Exemple** :
```yaml
- type: prompt
  text: "Serene mountain landscape at sunset"
  weight: 2.5
  category: subject
  
- type: style
  text: "Impressionist painting, vibrant colors"
  weight: 1.8
  category: artistic
```

---

### UC-04 : Rechercher des Médias

**Acteur** : Utilisateur final / Créateur

**Description** : Rechercher des médias selon différents critères

**Modes de recherche** :

**1. Recherche full-text**
- Recherche dans titre, description, définisseurs
- Support opérateurs booléens (AND, OR, NOT)
- Recherche par phrase exacte (guillemets)

**2. Recherche par filtres**
- Collection(s)
- Tags (OU / ET)
- Plage de dates
- Type de média (image, vidéo, audio)
- Format (JPEG, PNG, MP4, etc.)
- Dimensions (min/max)
- Poids du fichier

**3. Recherche par checksum**
- Identification exacte d'un média
- Détection de doublons

**4. Recherche relationnelle**
- Anciens d'un média
- Descendants d'un média
- Médias similaires
- Médias dans le même graphe

**Flux nominal** :
1. L'utilisateur saisit la requête (texte ou filtres)
2. Le système exécute la recherche (index full-text + SQL)
3. Le système retourne les résultats paginés
4. L'utilisateur peut affiner (filtres additionnels)
5. L'utilisateur peut trier (pertinence, date, nom)

**Performance attendue** :
- Recherche sur 100k médias : < 100ms
- Affichage des 50 premiers résultats : < 500ms

---

### UC-05 : Naviguer dans une Collection

**Acteur** : Utilisateur final

**Description** : Parcourir les médias d'une collection selon différents modes de vue

**Modes de vue** :

**1. Grille (Grid)**
- Vignettes de taille uniforme
- Colonnes adaptatives
- Pagination ou infinite scroll

**2. Liste (List)**
- Affichage linéaire avec métadonnées visibles
- Tri multi-colonnes

**3. Timeline**
- Organisation chronologique
- Regroupement par période (jour, mois, année)

**4. Graphe**
- Visualisation des relations entre médias
- Force-directed layout
- Zoom et pan

**5. Mosaïque (Masonry)**
- Disposition adaptative (hauteurs variables)
- Optimisation espace

**Interactions** :
- Clic : ouverture lightbox plein écran
- Hover : affichage tooltip avec métadonnées
- Drag : réorganisation manuelle (si mode édition)
- Clavier : navigation (flèches, PageUp/Down)

---

### UC-06 : Créer un Hypermedia Composite

**Acteur** : Créateur de contenu

**Description** : Assembler plusieurs médias en un hypermedia composite

**Préconditions** :
- Les médias composants existent dans le HM-Drive

**Flux nominal** :
1. L'utilisateur crée un nouveau composite
2. L'utilisateur ajoute des composants (via URI) :
   - Médias simples
   - Autres composites (récursivité)
3. L'utilisateur définit le layout :
   - Grille : positions (x, y)
   - Séquentiel : ordre de lecture
   - Temporel : durées et transitions
4. L'utilisateur ajoute des métadonnées au composite
5. Le système valide le graphe (détection de cycles)
6. Le système enregistre le fichier `.hm` (YAML)
7. Le système génère un thumbnail composite

**Format `.hm`** (YAML) :
```yaml
type: composite
version: 1.0
layout: grid
metadata:
  title: "My Composite"
  tags: [composite, gallery]
components:
  - uri: hm://local/portraits/img001
    position: [0, 0]
    duration: 3s
  - uri: hm://local/landscapes/img002
    position: [1, 0]
  - uri: hm://local/composites/nested_comp
    position: [0, 1]
    scale: 0.5
```

**Validation** :
- Détection de cycles (composite référençant récursivement lui-même)
- Vérification existence des URI
- Limite de profondeur (ex: 10 niveaux max)

---

### UC-07 : Configurer une Instance HM-Drive

**Acteur** : Administrateur

**Description** : Initialiser et configurer une instance HM-Drive

**Flux nominal** :
1. L'administrateur exécute `hm init /path/to/instance`
2. Le système crée la structure de dossiers :
   ```
   /path/to/instance/
   ├── config.yaml
   ├── database.db
   ├── cache/
   ├── collections/
   └── subscriptions/
   ```
3. Le système initialise la base de données (schéma SQL)
4. Le système génère un fichier de config par défaut :
   ```yaml
   instance:
     name: "my-instance"
     uri: "hm://local"
   
   cache:
     max_size_gb: 10
     eviction_policy: lru
   
   sync:
     auto_sync: true
     interval_minutes: 15
   
   security:
     tls_enabled: true
     auth_required: false
   ```
5. L'administrateur édite la configuration
6. L'administrateur démarre l'instance : `hm start`

---

### UC-08 : S'abonner à une Instance Distante

**Acteur** : Administrateur

**Description** : Configurer un abonnement à une instance distante

**Modes d'abonnement** :
- **Pull** : récupération unidirectionnelle
- **Push** : envoi unidirectionnel
- **Sync** : synchronisation bidirectionnelle

**Flux nominal** :
1. L'administrateur exécute :
   ```bash
   hm subscribe \
     --remote hm://remote-server.example.com \
     --collections "projects/2024,assets/shared" \
     --mode sync \
     --schedule "*/15 * * * *"
   ```
2. Le système teste la connexion à l'instance distante
3. Le système vérifie l'authentification (si requise)
4. Le système enregistre l'abonnement en base
5. Le système effectue une première synchronisation initiale
6. Le système programme les synchronisations futures (cron)

**Postconditions** :
- Abonnement actif
- Collections distantes accessibles localement (cache)
- Synchronisation automatique selon le planning

---

### UC-09 : Synchroniser des Collections

**Acteur** : Système HM-Drive (automatique)

**Description** : Synchroniser les médias entre instances locale et distante

**Flux nominal** :
1. Le scheduler déclenche une synchronisation
2. Le système vérifie la connectivité réseau
3. Pour chaque abonnement actif :
   
   **Phase Discovery** :
   a. Récupération liste des médias distants (checksums + timestamps)
   b. Comparaison avec liste locale
   c. Identification des différences (ajouts, modifications, suppressions)
   
   **Phase Transfer** :
   d. Pour chaque différence :
      - Calcul du delta minimal (rsync-like)
      - Compression (zstd)
      - Transfert (HTTP/2 ou gRPC)
      - Vérification checksum
   
   **Phase Reconciliation** :
   e. Application des changements en transaction atomique
   f. Mise à jour des métadonnées locales
   g. Régénération des index
   h. Logs de synchronisation

4. Le système met à jour le statut de l'abonnement

**Gestion des conflits** :
- Détection : même média modifié des 2 côtés
- Stratégies :
  - `last_write_wins` : horodatage le plus récent
  - `manual` : notification à l'administrateur
  - `version_both` : conservation des 2 versions
  - `merge_metadata` : fusion intelligente

**Mode déconnecté** :
- Si réseau indisponible : ajout à la queue de synchronisation
- Retry automatique au retour en ligne
- Persistance de la queue (survit au redémarrage)

---

### UC-10 : Définir une Scène HM-Scene

**Acteur** : Créateur de contenu

**Description** : Créer une scène personnalisée avec le langage HM-DSS

**Flux nominal** :
1. L'utilisateur crée un fichier `.hmdss`
2. L'utilisateur écrit la définition de scène (syntaxe CSS-like) :
   ```css
   @scene portfolio {
       collection: "projects/2024";
       layout: grid;
       columns: 3;
   }
   
   media {
       width: 100%;
       aspect-ratio: 1/1;
   }
   
   media[tag~="featured"] {
       grid-column: span 2;
       border: 3px solid gold;
   }
   ```
3. L'utilisateur enregistre la scène dans HM-Drive
4. Le système parse le HM-DSS (validation syntaxique)
5. Le système compile la scène (AST)
6. L'utilisateur peut prévisualiser la scène
7. L'utilisateur publie la scène

**Postconditions** :
- Scène accessible via interface web ou CLI
- Rendu dynamique selon le support (desktop, mobile, projection)

---

### Autres Cas d'Usage (résumé)

**UC-11 : Résoudre un URI**
- Transformer `hm://instance/collection/media` en objet Media

**UC-12 : Parcourir le Graphe Relationnel**
- `get_ancestors()`, `get_descendants()`, `get_related()`

**UC-13 : Détecter et Fusionner les Doublons**
- Recherche par checksum, fusion intelligente des métadonnées

**UC-14 : Générer des Thumbnails**
- Multi-résolutions (128x128, 256x256, 512x512)

**UC-15 : Exporter une Collection**
- Formats : ZIP, tar.gz, JSON (métadonnées)

**UC-16 : Migrer depuis prompt-imagine**
- Import automatique des collections, métadonnées, généalogie

**UC-17 : Vérifier l'Intégrité**
- `hm check` : validation checksums, cohérence base/fichiers

**UC-18 : Réparer les Incohérences**
- Détection et correction fichiers orphelins, enregistrements sans fichier

**UC-19 : Consulter les Statistiques**
- Nombre de médias, taille totale, répartition par type/collection

**UC-20 : Consulter les Logs**
- Logs de synchronisation, erreurs, opérations

---

## 4. Exigences Fonctionnelles

### EF-001 : Gestion des Collections

Le système DOIT permettre la création de collections arborescentes sans limite de profondeur.

**Critères d'acceptation** :
- Création de collection racine
- Création de sous-collection (imbrication)
- Renommage de collection
- Suppression de collection (avec ou sans contenu)
- Déplacement de collection

### EF-002 : Liens Symboliques Virtuels

Le système DOIT supporter les liens symboliques entre collections (stockage en base, pas de vrais symlinks).

**Types de liens** :
- `alias` : raccourci vers collection distante
- `shortcut` : accès rapide
- `related` : relation sémantique

### EF-003 : Import Multi-Formats

Le système DOIT supporter les formats suivants :

**Images** : JPEG, PNG, WebP, GIF, TIFF, BMP
**Vidéos** : MP4, WebM, AVI, MOV, MKV
**Audio** : MP3, WAV, FLAC, OGG
**Texte** : TXT, MD, PDF
**Hypermedia** : .hm (format composite)

### EF-004 : Calcul de Checksums

Le système DOIT calculer un checksum BLAKE2b (64 bytes) pour chaque média importé.

**Objectifs** :
- Détection de doublons (100% fiabilité)
- Vérification d'intégrité
- Identification unique

### EF-005 : Métadonnées Enrichies

Le système DOIT supporter 4 types de métadonnées :

**1. Métadonnées physiques** (automatiques)
- Taille fichier
- Format (MIME type)
- Dimensions (largeur, hauteur)
- Durée (vidéo/audio)
- Bitrate, framerate, codec

**2. Descripteurs textuels** (manuels)
- Titre
- Description
- Auteur
- Licence

**3. Tags** (manuels)
- Tags multiples par média
- Autocomplétion
- Catégorisation (optionnelle)

**4. Définisseurs pondérés** (manuels, hérité de prompt-imagine)
- Texte descriptif
- Poids (0.0 - 10.0)
- Type (prompt, style, quality)
- Catégorie (subject, artistic, technical)

### EF-006 : Génération de Thumbnails

Le système DOIT générer automatiquement 3 résolutions de thumbnails :
- 128x128 (grille dense)
- 256x256 (grille standard)
- 512x512 (prévisualisation)

**Options** :
- Crop centré
- Respect aspect ratio avec padding

### EF-007 : Détection de Doublons

Le système DOIT détecter automatiquement les doublons (même checksum) lors de l'import.

**Actions possibles** :
- Refuser l'import (déduplication stricte)
- Lier au média existant (référence)
- Importer quand même (collections multiples)

### EF-008 : Fusion de Doublons

Le système DOIT permettre la fusion manuelle ou automatique de doublons.

**Fusion des métadonnées** :
- Collections : union
- Tags : union
- Descripteurs : choix utilisateur ou concaténation
- Titre : choix utilisateur

### EF-009 : Graphe Relationnel

Le système DOIT maintenir un graphe des relations entre médias.

**Types de relations** :
- `parent` / `child` : généalogie (dérivation)
- `similar` : similarité sémantique
- `derived` : transformation (crop, filter, etc.)
- `part_of` : composite (média → hypermedia)
- `related` : relation générique

### EF-010 : Parcours de Graphe

Le système DOIT fournir des API de parcours de graphe :
- `get_ancestors(media_id, depth)` : ancêtres jusqu'à profondeur N
- `get_descendants(media_id, depth)` : descendants
- `get_related(media_id, relation_type)` : relations typées
- `get_path(source_id, target_id)` : chemin le plus court

### EF-011 : Recherche Full-Text

Le système DOIT indexer et permettre la recherche full-text sur :
- Titre
- Description
- Définisseurs pondérés
- Tags

**Performance** : recherche sur 100k médias en < 100ms

### EF-012 : Filtres de Recherche

Le système DOIT supporter les filtres combinables :
- Collection(s)
- Tags (AND / OR)
- Plage de dates
- Type de média
- Format
- Dimensions (min/max)
- Taille fichier (min/max)

### EF-013 : URI Unifié

Le système DOIT implanter un schéma d'URI `hm://` :

**Format** : `hm://[instance]/[collection_path]/[media_id][#fragment]`

**Exemples** :
- `hm://local/portraits/abc123`
- `hm://remote.example.com/shared/video001#t=30s`

**Fragments** :
- `#t=30s` : timestamp vidéo
- `#xywh=100,200,300,400` : région image
- `#component=2` : composant d'un hypermedia

### EF-014 : Résolution d'URI

Le système DOIT résoudre les URI vers des objets Media concrets.

**Résolution locale** : accès direct au fichier
**Résolution distante** : téléchargement en cache local

### EF-015 : Architecture d'Instance

Le système DOIT supporter plusieurs instances HM-Drive.

**Types d'instances** :
- Principale (primary) : dossier principal local
- Secondaire (secondary) : abonnée à la principale
- Pair (peer) : égalité de statut

### EF-016 : Abonnements

Le système DOIT permettre de s'abonner à des instances distantes.

**Modes** :
- **Pull** : récupération unidirectionnelle
- **Push** : envoi unidirectionnel
- **Sync** : synchronisation bidirectionnelle

**Configuration** :
- Collections sélectionnées
- Planning (cron)
- Filtres (tags, types)

### EF-017 : Synchronisation Delta

Le système DOIT implanter une synchronisation incrémentale (delta sync).

**Algorithme** :
1. Comparaison des checksums
2. Identification des différences
3. Transfert des deltas uniquement
4. Compression (zstd)

**Performance** : sync de 10GB en < 5min sur LAN 1Gbps

### EF-018 : Mode Déconnecté

Le système DOIT fonctionner en mode déconnecté.

**Comportement** :
- Queue locale des opérations en attente
- Accès aux médias en cache
- Synchronisation automatique au retour en ligne

### EF-019 : Gestion des Conflits

Le système DOIT détecter et résoudre les conflits de synchronisation.

**Stratégies** :
- `last_write_wins`
- `manual`
- `version_both`
- `merge_metadata`

### EF-020 : Hypermedia Composites

Le système DOIT supporter les hypermedia composites récursifs.

**Format** : fichier `.hm` (YAML)

**Composants** :
- Références à des médias (URI)
- Références à des composites (récursivité)
- Propriétés de layout (positions, tailles)

### EF-021 : Validation DAG

Le système DOIT valider que les composites forment un graphe acyclique dirigé (DAG).

**Détection de cycles** : algorithme DFS avec marquage

### EF-022 : Langage HM-DSS

Le système DOIT implanter un langage de mise en scène HM-DSS (inspiré CSS).

**Éléments** :
- Sélecteurs de médias
- Propriétés de layout
- Propriétés visuelles
- Pseudo-classes (`:hover`, `:first-child`)
- Media queries (responsive)

### EF-023 : Parser HM-DSS

Le système DOIT parser et valider la syntaxe HM-DSS.

**Sortie** : AST (Abstract Syntax Tree)

### EF-024 : Moteur de Rendu

Le système DOIT rendre les scènes HM-DSS vers différents backends :
- HTML/CSS/JS (web)
- Qt (desktop)
- Terminal (TUI)

### EF-025 : Templates de Scènes

Le système DOIT fournir des templates de scènes prédéfinis :
- Gallery (grille)
- Timeline (chronologique)
- Graph (relations)
- Masonry (mosaïque)
- Slideshow (diaporama)

### EF-026 : Adaptation Multi-Support

Le système DOIT adapter les scènes selon le support :
- Desktop (large screen)
- Mobile (tactile)
- Tablet
- Projection (ultra-wide)

### EF-027 : Pagination Dynamique

Le système DOIT paginer les collections volumineuses.

**Modes** :
- Pagination classique (numéros de pages)
- Infinite scroll
- Load more (bouton)

**Performance** : affichage de 50 médias en < 500ms

### EF-028 : Cache Local

Le système DOIT maintenir un cache local des médias distants.

**Politique** :
- Taille maximale configurable (10GB par défaut)
- Éviction LRU
- Priorité aux thumbnails

### EF-029 : Migration prompt-imagine

Le système DOIT fournir un outil de migration depuis prompt-imagine.

**Import** :
- Collections
- Médias
- Métadonnées (prompts → définisseurs)
- Généalogie
- Tags
- Checksums

### EF-030 : Interface Web

Le système DOIT fournir une interface web (Flask/FastAPI).

**Pages** :
- Accueil (liste collections)
- Collection (galerie)
- Média (détail + lightbox)
- Recherche
- Admin (config, sync, logs)

### EF-031 : CLI

Le système DOIT fournir une interface en ligne de commande.

**Commandes** :
- `hm init` : initialiser instance
- `hm add` : ajouter média
- `hm list` : lister médias
- `hm search` : rechercher
- `hm sync` : synchroniser
- `hm check` : vérifier intégrité
- `hm repair` : réparer incohérences

### EF-032 : Logs Structurés

Le système DOIT produire des logs structurés (JSON).

**Niveaux** : DEBUG, INFO, WARNING, ERROR, CRITICAL

**Champs** : timestamp, level, component, message, context

### EF-033 : Monitoring

Le système DOIT exposer des métriques pour monitoring.

**Métriques** :
- Nombre de médias
- Taille totale
- Taux de cache hit
- Dureé sync
- Erreurs

### EF-034 : Transactions Atomiques

Le système DOIT utiliser des transactions atomiques pour toutes les opérations critiques.

**Garantie** : rollback automatique en cas d'échec

### EF-035 : Sécurité TLS

Le système DOIT utiliser TLS 1.3 pour les communications réseau.

### EF-036 : Authentification

Le système DOIT supporter l'authentification pour les instances distantes.

**Méthode** : JWT (JSON Web Tokens)

### EF-037 : Validation de Chemins

Le système DOIT valider tous les chemins de fichiers pour éviter les accès hors de `instance_root/`.

**Sécurité** : interdiction `../`, chemins absolus non autorisés

### EF-038 : Statistiques

Le système DOIT fournir des statistiques sur les collections.

**Statistiques** :
- Nombre de médias par type
- Taille totale par collection
- Répartition par format
- Top tags

### EF-039 : Export

Le système DOIT permettre l'export de collections.

**Formats** :
- ZIP (médias + métadonnées)
- JSON (métadonnées uniquement)
- CSV (tableau)

### EF-040 : Documentation

Le système DOIT fournir une documentation exhaustive.

**Formats** :
- API Reference (autodoc depuis docstrings)
- User Guide (tutoriels)
- Administrator Guide (déploiement)
- HM-DSS Specification (langage)

---

## 5. Exigences Non Fonctionnelles

### ENF-001 : Performance

**Import** :
- 1000 images (10MB moyenne) : < 30s

**Recherche** :
- Full-text sur 100k médias : < 100ms

**Synchronisation** :
- 10GB sur LAN 1Gbps : < 5min

**Rendu** :
- Scène 100 médias : < 1s
- Navigation 60fps sur grille 500+ éléments

### ENF-002 : Portabilité

**Plateformes** : Linux, macOS, Windows

**Python** : ≥3.10

**Dépendances** : minimales, pure Python ou wheels disponibles

### ENF-003 : Scalabilité

**Volumes supportés** :
- 100k médias par instance
- 10 To de données
- 1000 collections

### ENF-004 : Fiabilité

**Disponibilité** : 99.9% (mode local)

**Tolérance aux pannes** :
- Résilience aux déconnexions réseau
- Recovery automatique après crash

### ENF-005 : Utilisabilité

**API** : intuitive, bien documentée

**Messages d'erreur** : explicites, actionables

**Interface web** : responsive, accessible (WCAG 2.1 AA)

### ENF-006 : Maintenabilité

**Architecture** : modulaire, faible couplage

**Tests** : >90% couverture

**Documentation** : à jour, exhaustive

### ENF-007 : Sécurité

**Chiffrement** : TLS 1.3 pour réseau

**Validation** : tous les chemins, entrées utilisateur

**Transactions** : atomiques avec rollback

---

## 6. Modèle de Domaine

### Entités Principales

**Instance**
- Identifiant unique
- Nom
- URI
- Type (local, remote)
- Configuration

**Collection**
- Identifiant
- Nom
- Chemin
- Parent (collection parente)
- Métadonnées

**Media**
- Identifiant
- Checksum (BLAKE2b)
- Nom de fichier
- Format
- Taille
- Dimensions
- Durée
- Métadonnées physiques
- Collections (many-to-many)

**Descriptor** (définisseur pondéré)
- Identifiant
- Média (référence)
- Type (prompt, style, quality)
- Texte
- Poids
- Catégorie

**Tag**
- Identifiant
- Nom
- Couleur
- Catégorie

**Relationship**
- Source (média)
- Cible (média)
- Type (parent, child, similar, derived)
- Force (0.0 - 1.0)

**Composite**
- Identifiant
- Média (référence)
- Définition (YAML)
- Layout

**Scene**
- Identifiant
- Collection
- Nom
- Contenu HM-DSS
- Configuration

**Subscription** (abonnement)
- Instance locale
- Instance distante
- Collections
- Mode (pull, push, sync)
- Planning
- Dernier sync

### Relations

- Collection 1-N Media (via table intermédiaire many-to-many)
- Media 1-N Descriptor
- Media N-N Tag
- Media N-N Relationship (graphe)
- Media 1-1 Composite (optionnel)
- Collection 1-N Scene
- Instance 1-N Subscription

---

## 7. Scénarios Détaillés

### Scénario 1 : Migration d'une Collection prompt-imagine

**Contexte** : Un utilisateur possède 500 images dans prompt-imagine, collection "Landscapes"

**Étapes** :
1. L'utilisateur initialise une instance Hypermedia :
   ```bash
   hm init /home/user/hypermedia
   ```

2. L'utilisateur lance la migration :
   ```bash
   hm-migrate \
     --source /home/user/prompt-imagine \
     --target /home/user/hypermedia \
     --collection Landscapes \
     --verify-checksums
   ```

3. Le système :
   - Lit la base SQLite de prompt-imagine
   - Extrait les 500 enregistrements de "Landscapes"
   - Pour chaque média :
     - Vérifie le checksum existant
     - Copie le fichier dans HM-Drive
     - Convertit les prompts en définisseurs pondérés
     - Importe les tags
     - Reconstruit la généalogie (relations parent-enfant)
     - Génère les thumbnails

4. Résultat :
   - Collection accessible via `hm://local/Landscapes`
   - 500 médias importés
   - Métadonnées préservées
   - Généalogie conservée

### Scénario 2 : Synchronisation Multi-Instances avec Conflit

**Contexte** : Instance A (studio) et Instance B (laptop) synchronisées

**Étapes** :
1. Sur A : modification du titre de `image001.jpg` → "Sunset at Beach"
2. Sur B (déconnecté) : modification du titre de `image001.jpg` → "Golden Hour"
3. B se reconnecte au réseau
4. Synchronisation automatique se déclenche
5. Le système détecte un conflit (même média, 2 modifications)
6. Stratégie configurée : `manual`
7. Notification à l'administrateur :
   ```
   Conflit détecté sur hm://local/landscapes/image001
   
   Version A (studio) :
     Titre: "Sunset at Beach"
     Modifié: 2026-02-10 14:30:00
   
   Version B (laptop) :
     Titre: "Golden Hour"
     Modifié: 2026-02-10 14:32:00
   
   Actions possibles :
   1. Conserver A
   2. Conserver B
   3. Fusionner (concaténation)
   4. Conserver les 2 versions
   ```
8. L'administrateur choisit : Fusionner → "Sunset at Beach - Golden Hour"
9. Le système applique la résolution sur A et B

### Scénario 3 : Création d'un Hypermedia Composite Multicouche

**Contexte** : Créer un portfolio composite avec 3 niveaux

**Étapes** :
1. Création de composites de base (niveau 1) :
   ```yaml
   # portraits_2024.hm
   type: composite
   layout: grid
   components:
     - uri: hm://local/portraits/portrait001
     - uri: hm://local/portraits/portrait002
     - uri: hm://local/portraits/portrait003
   ```

2. Création de composites intermédiaires (niveau 2) :
   ```yaml
   # best_of_2024.hm
   type: composite
   layout: grid
   components:
     - uri: hm://local/composites/portraits_2024
     - uri: hm://local/composites/landscapes_2024
     - uri: hm://local/composites/architecture_2024
   ```

3. Création du composite final (niveau 3) :
   ```yaml
   # portfolio_master.hm
   type: composite
   layout: sequential
   components:
     - uri: hm://local/composites/best_of_2024
       duration: 30s
     - uri: hm://local/videos/showreel.mp4
       duration: 60s
     - uri: hm://local/composites/contact_info
       duration: 10s
   ```

4. Validation DAG :
   - Le système parcourt récursivement les composants
   - Vérifie l'absence de cycles
   - Profondeur = 3 (< limite de 10)
   - Validation OK

5. Génération du thumbnail composite :
   - Mosaïque des thumbnails des composants de niveau 1

### Scénario 4 : Navigation dans une Scène HM-DSS

**Contexte** : Utilisateur navigue dans une collection "Wildlife"

**Scène définie** :
```css
@scene wildlife {
    collection: "nature/wildlife";
    layout: masonry;
}

media[tag~="endangered"] {
    border: 3px solid red;
    z-index: 10;
}

media[type="video"] {
    play-on-hover: true;
    border-radius: 8px;
}

media:hover {
    transform: scale(1.1);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}
```

**Comportement** :
1. L'utilisateur accède à `/scene/wildlife`
2. Le moteur de rendu parse le HM-DSS
3. Le moteur résout les médias de "nature/wildlife" (150 médias)
4. Le moteur applique les sélecteurs :
   - Médias avec tag "endangered" : bordure rouge, z-index 10
   - Vidéos : play-on-hover, border-radius
5. Le moteur calcule le layout masonry (colonnes adaptatives)
6. Le moteur rend en HTML/CSS/JS
7. L'utilisateur survole une vidéo :
   - La vidéo démarre (muted)
   - Transform scale(1.1) + box-shadow
8. L'utilisateur clique :
   - Ouverture lightbox plein écran
   - Lecture avec son

### Scénario 5 : Récupération après Déconnexion

**Contexte** : Utilisateur sur laptop, déconnexion réseau pendant 2h

**Étapes** :
1. Utilisateur ajoute 10 nouvelles photos à "Travel/Japan" (mode déconnecté)
2. Le système :
   - Enregistre localement les médias
   - Calcule les checksums
   - Génère les thumbnails
   - Ajoute l'opération à la queue de sync : `ADD 10 media to Travel/Japan`
3. Utilisateur modifie les tags de 5 photos existantes
4. Le système ajoute à la queue : `UPDATE tags for 5 media`
5. Réseau revient en ligne (2h plus tard)
6. Le système détecte la reconnexion
7. Le système traite la queue :
   - Synchronisation des 10 nouveaux médias vers instance distante
   - Synchronisation des modifications de tags
   - Vérification checksums
8. Queue vidée, synchronisation complète
9. Logs : "Sync completed: 10 added, 5 updated, 0 conflicts"

---

## 8. Contraintes et Hypothèses

### Contraintes

**Techniques** :
- Python ≥3.10
- SQLite comme base de données embarquée
- Pas de droit sudo requis (installation utilisateur)

**Organisationnelles** :
- Développement open source (MIT)
- Documentation en anglais
- Releases semantic versioning

**Temporelles** :
- v1.0 en décembre 2026 (11 mois)

### Hypothèses

**Usage** :
- Utilisateurs avec connaissances informatiques de base
- Accès à Internet pour synchronisation (mais non requis localement)
- Stockage local suffisant (10-100 GB)

**Infrastructure** :
- Réseau local fiable (LAN)
- Bande passante Internet correcte pour sync (1 Mbps minimum)

---

## 9. Critères d'Acceptation

### Phase 1 (HM-Drive local)
- [ ] Import de 1000 images en < 30s
- [ ] Détection 100% des doublons (même checksum)
- [ ] Recherche full-text opérationnelle
- [ ] Tags avec autocomplétion

### Phase 3 (Distribution)
- [ ] Synchronisation 10GB en < 5min (LAN)
- [ ] Mode déconnecté : queue persistante
- [ ] Résolution conflits sans perte de données

### Phase 5 (HM-Scene)
- [ ] Rendu scène 100 médias en < 1s
- [ ] 10+ templates HM-DSS fournis
- [ ] Navigation 60fps

### Phase 7 (Production)
- [ ] Package PyPI installable
- [ ] Documentation complète (>100 pages)
- [ ] 10+ alpha testeurs
- [ ] Couverture tests >90%
- [ ] Migration prompt-imagine automatisée

---

## Conclusion

Ces spécifications fonctionnelles définissent un système complet de gestion d'hypermedia distribué, héritant des forces de prompt-imagine tout en apportant distribution, résilience et mise en scène avancée. Les 20 cas d'usage et 40 exigences fonctionnelles couvrent l'ensemble des besoins identifiés, avec des critères d'acceptation mesurables.
