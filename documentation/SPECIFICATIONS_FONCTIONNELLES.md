# Spécifications fonctionnelles - Hypermedia

## 1. Contexte et objectifs

### 1.1 Contexte du projet

Le projet **Hypermedia** naît de l'observation des limites des systèmes actuels de gestion de médias :

- **Centralisation** : Dépendance à des serveurs cloud propriétaires (Google Drive, Dropbox, iCloud)
- **Fragmentation** : Médias dispersés entre multiples services sans cohérence sémantique
- **Rigidité** : Structures d'organisation imposées (dossiers plats, albums chronologiques)
- **Manque de contexte** : Métadonnées limitées aux tags et descriptions textuelles
- **Linéarité** : Navigation séquentielle sans exploration des relations entre médias

Le projet **prompt-imagine** a démontré la viabilité d'un système enrichi de gestion d'images générées par IA, avec métadonnées complexes (prompts pondérés), généalogie, et navigation non linéaire. **Hypermedia** généralise ces concepts pour créer une infrastructure universelle.

### 1.2 Objectifs fonctionnels

**Objectif principal** : Fournir une librairie Python portable permettant de créer, gérer et explorer des espaces d'hypermedia distribués, résilients et richement interconnectés.

**Objectifs secondaires** :

1. **Décentralisation partielle** : Permettre la synchronisation peer-to-peer sans dépendre d'un serveur central
2. **Résilience** : Garantir l'accès aux médias même en cas de déconnexion ou de panne d'une instance
3. **Richesse sémantique** : Associer à chaque média des métadonnées structurées, pondérées et relationnelles
4. **Composition récursive** : Supporter des hypermedia composites (assemblages de médias et d'hypermedia)
5. **Mise en scène dynamique** : Offrir des modes de visualisation adaptés au contexte et aux besoins
6. **Extensibilité** : Faciliter l'ajout de nouveaux formats, protocoles et modes de présentation

### 1.3 Périmètre fonctionnel

**Dans le périmètre (version 1.0)** :

- Stockage et indexation de médias locaux et distants
- Métadonnées enrichies (définisseurs pondérés, tags, généalogie)
- Synchronisation unidirectionnelle et bidirectionnelle
- Hypermedia composites récursifs
- Langage de mise en scène HM-DSS
- CLI et API REST
- Interface web basique

**Hors périmètre (versions futures)** :

- Édition collaborative temps réel
- Auto-tagging par IA
- Architecture P2P complète (libp2p, IPFS)
- Applications mobiles natives
- Chiffrement end-to-end

---

## 2. Acteurs et rôles

### 2.1 Acteurs humains

#### Créateur de contenu
**Description** : Utilisateur générant ou important des médias dans le système.

**Besoins** :
- Importer des médias depuis disque, URL ou API
- Enrichir les médias avec métadonnées (titre, description, tags, définisseurs)
- Organiser en collections thématiques
- Créer des relations entre médias (ancêtres, descendants, variantes)

**Capacités** :
- Uploader des fichiers individuels ou en batch
- Éditer métadonnées individuellement ou en groupe
- Créer des hypermedia composites
- Définir des scènes de présentation

#### Explorateur
**Description** : Utilisateur naviguant dans les espaces d'hypermedia existants.

**Besoins** :
- Rechercher des médias par texte, tags, métadonnées
- Naviguer de manière non linéaire (liens, généalogie, similarité)
- Filtrer et trier selon divers critères
- Visualiser dans différents modes (galerie, timeline, graphe)

**Capacités** :
- Accéder aux médias locaux et distants (lecture seule)
- Suivre les liens entre médias
- Exporter des sélections
- Créer des vues personnalisées (scènes)

#### Administrateur de drive
**Description** : Utilisateur gérant une instance HM-Drive.

**Besoins** :
- Configurer les abonnements (instances distantes)
- Monitorer la synchronisation
- Gérer le cache et l'espace disque
- Sécuriser l'accès (authentification, autorisations)

**Capacités** :
- Initialiser un nouveau drive
- Ajouter/retirer des abonnements
- Configurer les politiques de cache
- Consulter les logs et statistiques

#### Développeur
**Description** : Développeur intégrant Hypermedia dans une application tierce.

**Besoins** :
- API stable et documentée
- Extensibilité (plugins, formats custom)
- Exemples et tutoriels

**Capacités** :
- Utiliser l'API Python
- Créer des formats de médias custom
- Développer des renderers HM-DSS
- Contribuer au projet open-source

### 2.2 Acteurs systèmes

#### Instance HM-Drive
**Description** : Processus Python gérant un espace de stockage local et des abonnements.

**Responsabilités** :
- Gérer le dossier principal et les collections
- Synchroniser avec les instances abonnées
- Maintenir le cache local
- Résoudre les URI
- Exposer l'API REST

#### Moteur de synchronisation
**Description** : Composant asynchrone gérant les transferts entre instances.

**Responsabilités** :
- Détecter les changements (nouveaux médias, modifications, suppressions)
- Transférer les fichiers et métadonnées
- Résoudre les conflits
- Gérer la file d'attente de synchronisation

#### Moteur de rendu HM-Scene
**Description** : Composant transformant une scène HM-DSS en représentation visuelle.

**Responsabilités** :
- Parser les feuilles HM-DSS
- Sélectionner les médias selon les règles
- Appliquer les styles et layouts
- Générer le rendu (HTML, terminal, export statique)

---

## 3. Exigences fonctionnelles

### 3.1 Gestion du HM-Drive

#### REQ-DRIVE-001 : Initialisation d'un drive
**Priorité** : Critique  
**Acteur** : Administrateur de drive

**Description** : Le système doit permettre l'initialisation d'un nouveau HM-Drive avec configuration minimale.

**Critères d'acceptation** :
- Création d'un dossier principal avec structure prédéfinie
- Génération d'un identifiant unique (UUID)
- Création de la base de métadonnées SQLite
- Fichier de configuration `.hm-config.yaml`

**Scénario nominal** :
```python
from hypermedia import HMDrive

drive = HMDrive.init("/path/to/hm-drive", name="Mon Drive")
print(drive.id)  # UUID généré
```

---

#### REQ-DRIVE-002 : Gestion des collections
**Priorité** : Critique  
**Acteur** : Créateur de contenu

**Description** : Le système doit permettre la création, édition et suppression de collections.

**Critères d'acceptation** :
- Création de collections avec nom unique
- Organisation arborescente (collections/sous-collections)
- Métadonnées de collection (description, icône, couleur)
- Suppression sécurisée (avec confirmation si non vide)

**Scénario nominal** :
```python
collection = drive.create_collection("Photos/Voyages/Japon")
collection.set_metadata(description="Photos du voyage au Japon 2024")
collection.set_icon("🗾")
```

---

#### REQ-DRIVE-003 : Ajout de médias
**Priorité** : Critique  
**Acteur** : Créateur de contenu

**Description** : Le système doit permettre l'ajout de médias depuis diverses sources.

**Critères d'acceptation** :
- Support des chemins locaux
- Support des URLs (téléchargement)
- Calcul automatique du checksum BLAKE2b
- Détection du format (MIME type)
- Génération de thumbnails pour images/vidéos
- Métadonnées physiques automatiques (taille, dimensions, durée)

**Scénario nominal** :
```python
media = collection.add_media(
    "/path/to/image.jpg",
    title="Temple Kinkaku-ji",
    tags=["temple", "kyoto", "architecture"]
)
print(media.uri)  # hm://drive-uuid/Photos/Voyages/Japon/image.jpg
```

---

#### REQ-DRIVE-004 : Système d'URI unifiés
**Priorité** : Critique  
**Acteur** : Tous

**Description** : Le système doit fournir un système d'URI permettant d'adresser tout média du HM-Drive distribué.

**Critères d'acceptation** :
- Format : `hm://[instance-id]/[collection]/[path]`
- Résolution locale et distante
- URI relatifs au sein d'une instance : `hm:///collection/path`
- Validation et normalisation des URI

**Exemples** :
- Local : `hm:///Photos/image.jpg`
- Distant : `hm://a1b2c3d4/Photos/image.jpg`
- Composite : `hm://a1b2c3d4/Hypermedia/gallery.hm`

---

### 3.2 Métadonnées et descripteurs

#### REQ-META-001 : Métadonnées physiques
**Priorité** : Critique  
**Acteur** : Système

**Description** : Le système doit calculer et stocker automatiquement les métadonnées physiques.

**Métadonnées obligatoires** :
- Checksum BLAKE2b (unicité, détection de doublons)
- Taille fichier (bytes)
- Format / MIME type
- Timestamps (création, modification, ajout au drive)

**Métadonnées conditionnelles** :
- **Images** : Dimensions (largeur, hauteur), résolution (DPI), profil couleur
- **Vidéos** : Durée, codec, résolution, framerate, bitrate
- **Audio** : Durée, codec, bitrate, sample rate, canaux
- **Texte** : Encodage, nombre de lignes/caractères

---

#### REQ-META-002 : Métadonnées sémantiques
**Priorité** : Élevée  
**Acteur** : Créateur de contenu

**Description** : Le système doit permettre l'ajout de métadonnées sémantiques riches.

**Champs standard** :
- **Titre** (chaîne, multilingue optionnel)
- **Description** (texte long, markdown)
- **Auteur** (nom ou URI)
- **Licence** (SPDX identifier)
- **Langue** (code ISO 639)
- **Date de création originale** (ISO 8601)

**Champs personnalisés** :
- Schéma extensible (JSON Schema)
- Typage des valeurs (string, number, date, URI, enum)

---

#### REQ-META-003 : Système de tags
**Priorité** : Élevée  
**Acteur** : Créateur de contenu, Explorateur

**Description** : Le système doit fournir un système de tags flexible.

**Critères d'acceptation** :
- Tags textuels (chaînes, insensibles à la casse)
- Tags multiples par média
- Autocomplétion basée sur tags existants
- Recherche par tags (union, intersection)
- Comptage des occurrences
- Tags hiérarchiques optionnels (ex: `lieu/pays/ville`)

---

#### REQ-META-004 : Définisseurs pondérés
**Priorité** : Élevée  
**Acteur** : Créateur de contenu

**Description** : Le système doit supporter des "définisseurs" (inspirés des prompts IA) : fragments textuels pondérés décrivant le média.

**Format** :
```
weight: 2.5 "temple doré, architecture japonaise"
weight: 1.0 "ciel bleu, reflets dans l'eau"
weight: -0.5 "foule, touristes"
```

**Critères d'acceptation** :
- Parsing des définisseurs avec poids
- Poids positifs (caractéristiques présentes) et négatifs (absentes)
- Indexation full-text pour recherche
- Génération de wordclouds pondérés
- Export vers formats standards (JSON, YAML)

---

#### REQ-META-005 : Relations généalogiques
**Priorité** : Moyenne  
**Acteur** : Créateur de contenu, Explorateur

**Description** : Le système doit permettre de définir des relations de filiation entre médias.

**Types de relations** :
- **Ancêtre** : Média source (ex: photo originale → photo éditée)
- **Descendant** : Média dérivé (ex: image → variations générées)
- **Variante** : Média alternatif (ex: crop, format différent)
- **Référence** : Lien sémantique libre

**Critères d'acceptation** :
- Graphe orienté acyclique (DAG) pour ancêtres/descendants
- Visualisation de la généalogie
- Navigation interactive (remonter aux ancêtres, explorer les descendants)
- Export GraphML / DOT

---

### 3.3 Hypermedia composites

#### REQ-COMP-001 : Format hypermedia
**Priorité** : Élevée  
**Acteur** : Créateur de contenu

**Description** : Le système doit définir un format pour les hypermedia composites.

**Format `.hm` (YAML)** :
```yaml
type: hypermedia
version: 1.0
metadata:
  title: "Galerie Japon"
  description: "Collection de photos du voyage"
  tags: ["voyage", "japon", "2024"]

components:
  - uri: hm:///Photos/Voyages/Japon/temple1.jpg
    position: 0
    metadata:
      caption: "Temple Kinkaku-ji"
  
  - uri: hm://remote-drive/Shared/music.mp3
    position: 1
    autoplay: true
  
  - uri: hm:///Hypermedia/sub-gallery.hm
    position: 2
    recursive: true

layout:
  type: grid
  columns: 3
  gap: 10px
```

**Critères d'acceptation** :
- Validation du format (JSON Schema)
- Références locales et distantes
- Composition récursive (avec limite de profondeur)
- Métadonnées au niveau composite et composant

---

#### REQ-COMP-002 : Résolution de dépendances
**Priorité** : Élevée  
**Acteur** : Système

**Description** : Le système doit résoudre automatiquement les dépendances d'un hypermedia composite.

**Critères d'acceptation** :
- Téléchargement des médias distants manquants
- Mise en cache locale
- Détection de cycles (références circulaires)
- Gestion des dépendances manquantes (fallback, erreur explicite)

---

### 3.4 Synchronisation

#### REQ-SYNC-001 : Abonnements mono-directionnels
**Priorité** : Élevée  
**Acteur** : Administrateur de drive

**Description** : Le système doit permettre l'abonnement à un drive distant en lecture seule.

**Critères d'acceptation** :
- Configuration d'abonnement (URL, credentials)
- Synchronisation initiale (copie complète)
- Synchronisation incrémentale (polling ou webhooks)
- Gestion de la bande passante (throttling)

**Scénario nominal** :
```python
subscription = drive.subscribe(
    url="https://remote-drive.example.com",
    collections=["Shared/Public"],
    mode="readonly",
    sync_interval="5m"
)
```

---

#### REQ-SYNC-002 : Abonnements bidirectionnels
**Priorité** : Moyenne  
**Acteur** : Administrateur de drive

**Description** : Le système doit permettre la synchronisation bidirectionnelle entre deux drives.

**Critères d'acceptation** :
- Propagation des ajouts, modifications, suppressions
- Résolution de conflits (stratégies : dernier gagne, fusion manuelle)
- Transactions atomiques (rollback en cas d'échec)
- Logs de synchronisation (audit trail)

---

#### REQ-SYNC-003 : Cache local
**Priorité** : Élevée  
**Acteur** : Système

**Description** : Le système doit maintenir un cache local des médias distants.

**Critères d'acceptation** :
- Politique d'éviction configurable (LRU, LFU, taille max, TTL)
- Validation des checksums après téléchargement
- Préchargement intelligent (based on access patterns)
- Statistiques du cache (taux de hit, taille utilisée)

---

#### REQ-SYNC-004 : Mode hors-ligne
**Priorité** : Moyenne  
**Acteur** : Explorateur

**Description** : Le système doit fonctionner en mode hors-ligne avec le cache local.

**Critères d'acceptation** :
- Détection automatique de la déconnexion
- Fallback sur cache pour médias distants
- File d'attente des modifications locales (replay à la reconnexion)
- Indicateur visuel du mode (online/offline/syncing)

---

### 3.5 HM-Scene et navigation

#### REQ-SCENE-001 : Définition de scènes
**Priorité** : Élevée  
**Acteur** : Créateur de contenu

**Description** : Le système doit permettre la définition de scènes de présentation via HM-DSS.

**Exemple HM-DSS** :
```yaml
scene:
  name: "Galerie photos Japon"
  target: "web"
  
selectors:
  - match:
      collection: "Photos/Voyages/Japon"
      type: "image"
    style:
      layout: grid
      columns: 4
      thumbnail_size: 250px
      hover_effect: zoom
  
  - match:
      tags: ["temple"]
    style:
      border: 2px solid gold
      priority: high
```

**Critères d'acceptation** :
- Sélecteurs basés sur métadonnées (collection, type, tags, date)
- Règles de style (layout, dimensions, animations)
- Composition de règles (héritage, cascade comme CSS)
- Validation du fichier HM-DSS

---

#### REQ-SCENE-002 : Rendu adaptatif
**Priorité** : Moyenne  
**Acteur** : Explorateur

**Description** : Le système doit adapter le rendu selon le support de visualisation.

**Supports cibles** :
- **Web** : HTML/CSS responsive
- **Terminal** : TUI avec rich/textual
- **Export statique** : Galerie HTML autonome

**Critères d'acceptation** :
- Détection automatique du support
- Templates de rendu par défaut
- Surcharge possible via HM-DSS

---

#### REQ-SCENE-003 : Navigation non linéaire
**Priorité** : Élevée  
**Acteur** : Explorateur

**Description** : Le système doit permettre la navigation non linéaire entre médias.

**Modes de navigation** :
- **Liens explicites** : Suivre les relations (ancêtres, descendants, références)
- **Liens implicites** : Médias similaires (même tags, même définisseurs)
- **Filtres dynamiques** : Affiner la sélection (par tag, date, collection)
- **Recherche full-text** : Dans métadonnées et définisseurs

**Critères d'acceptation** :
- Historique de navigation (back/forward)
- Breadcrumbs (fil d'Ariane)
- Minimap de la structure (optionnel)

---

### 3.6 Recherche et filtrage

#### REQ-SEARCH-001 : Recherche full-text
**Priorité** : Élevée  
**Acteur** : Explorateur

**Description** : Le système doit fournir une recherche full-text performante.

**Champs indexés** :
- Titre, description
- Tags
- Définisseurs
- Métadonnées personnalisées

**Critères d'acceptation** :
- Recherche insensible à la casse
- Support des opérateurs booléens (AND, OR, NOT)
- Recherche par proximité (within 5 words)
- Classement par pertinence (TF-IDF ou BM25)
- Résultats < 100ms pour 10k médias

---

#### REQ-SEARCH-002 : Recherche par métadonnées
**Priorité** : Moyenne  
**Acteur** : Explorateur

**Description** : Le système doit permettre la recherche par métadonnées structurées.

**Exemples de requêtes** :
```python
# Par tags (intersection)
results = drive.search(tags=["temple", "kyoto"])

# Par date
results = drive.search(date_range=("2024-01-01", "2024-12-31"))

# Par type
results = drive.search(type="image", format="image/jpeg")

# Par collection
results = drive.search(collection="Photos/Voyages/*")

# Requête combinée
results = drive.search(
    tags=["temple"],
    date_range=("2024-03-01", "2024-03-31"),
    collection="Photos/Voyages/Japon"
)
```

---

#### REQ-SEARCH-003 : Recherche par similarité
**Priorité** : Basse  
**Acteur** : Explorateur

**Description** : Le système doit permettre la recherche de médias similaires.

**Critères de similarité** :
- Tags communs (Jaccard similarity)
- Définisseurs proches (embeddings vectoriels optionnel)
- Généalogie commune (même ancêtre)

**Critères d'acceptation** :
- Fonction `find_similar(media, limit=10)`
- Classement par score de similarité
- Seuil configurable

---

### 3.7 Interface utilisateur

#### REQ-UI-001 : Interface en ligne de commande (CLI)
**Priorité** : Élevée  
**Acteur** : Tous

**Description** : Le système doit fournir une CLI complète.

**Commandes principales** :
```bash
# Initialisation
hm init /path/to/drive --name "Mon Drive"

# Ajout de médias
hm add /path/to/image.jpg --collection Photos --tags "voyage,japon"

# Recherche
hm search "temple" --collection Photos --tags kyoto

# Synchronisation
hm sync add https://remote-drive.example.com --readonly
hm sync run

# Visualisation
hm show hm:///Photos/image.jpg
hm browse Photos/Voyages
```

**Critères d'acceptation** :
- Aide contextuelle (`--help`)
- Autocomplétion (bash, zsh, fish)
- Output structuré (JSON, YAML, table)
- Mode interactif (prompt)

---

#### REQ-UI-002 : Interface web
**Priorité** : Moyenne  
**Acteur** : Créateur de contenu, Explorateur

**Description** : Le système doit fournir une interface web responsive.

**Pages principales** :
- **Accueil** : Vue d'ensemble des collections
- **Galerie** : Affichage des médias (grille, liste, timeline)
- **Détail** : Vue détaillée d'un média (métadonnées, généalogie)
- **Recherche** : Formulaire de recherche avancée
- **Upload** : Formulaire d'ajout de médias
- **Paramètres** : Configuration du drive, abonnements

**Critères d'acceptation** :
- Design responsive (mobile-first)
- Lightbox pour images/vidéos
- Lecteur audio/vidéo intégré
- Édition inline des métadonnées
- Glisser-déposer pour upload

---

#### REQ-UI-003 : API REST
**Priorité** : Élevée  
**Acteur** : Développeur

**Description** : Le système doit exposer une API REST complète.

**Endpoints principaux** :
```
GET    /api/collections
GET    /api/collections/{id}
POST   /api/collections
DELETE /api/collections/{id}

GET    /api/media
GET    /api/media/{id}
POST   /api/media
PUT    /api/media/{id}
DELETE /api/media/{id}

GET    /api/media/{id}/thumbnail
GET    /api/media/{id}/download

GET    /api/search?q={query}&tags={tags}

GET    /api/sync/subscriptions
POST   /api/sync/subscriptions
POST   /api/sync/run
```

**Critères d'acceptation** :
- Documentation OpenAPI/Swagger
- Authentification (JWT, API keys)
- Pagination (liens HATEOAS)
- Gestion des erreurs (codes HTTP standards)
- CORS configurable

---

## 4. Exigences non fonctionnelles

### 4.1 Performance

- **REQ-PERF-001** : Recherche full-text < 100ms pour 10k médias
- **REQ-PERF-002** : Synchronisation < 1s pour 100 médias (hors transfert réseau)
- **REQ-PERF-003** : Génération de thumbnail < 500ms par image
- **REQ-PERF-004** : Chargement interface web < 2s (first paint)

### 4.2 Scalabilité

- **REQ-SCAL-001** : Support de 100k+ médias par instance
- **REQ-SCAL-002** : Support de 10+ abonnements simultanés
- **REQ-SCAL-003** : Cache configurable jusqu'à 1TB

### 4.3 Fiabilité

- **REQ-FIAB-001** : Transactions atomiques pour toutes les opérations d'écriture
- **REQ-FIAB-002** : Rollback automatique en cas d'échec de synchronisation
- **REQ-FIAB-003** : Validation des checksums après chaque transfert
- **REQ-FIAB-004** : Logs détaillés de toutes les opérations critiques

### 4.4 Sécurité

- **REQ-SECU-001** : HTTPS obligatoire pour synchronisation distante
- **REQ-SECU-002** : Authentification robuste (JWT, expiration tokens)
- **REQ-SECU-003** : Validation des chemins (pas d'accès hors du drive)
- **REQ-SECU-004** : Protection CSRF pour interface web
- **REQ-SECU-005** : Rate limiting sur API REST

### 4.5 Portabilité

- **REQ-PORT-001** : Python 3.10+ uniquement
- **REQ-PORT-002** : Dépendances stdlib privilégiées
- **REQ-PORT-003** : Compatibilité Linux, macOS, Windows
- **REQ-PORT-004** : Installation via pip (PyPI)
- **REQ-PORT-005** : Docker images officielles

### 4.6 Maintenabilité

- **REQ-MAIN-001** : Couverture de tests > 85%
- **REQ-MAIN-002** : Documentation API complète (docstrings)
- **REQ-MAIN-003** : Architecture modulaire (découplage composants)
- **REQ-MAIN-004** : Versionnement sémantique (semver)
- **REQ-MAIN-005** : Changelog à jour

### 4.7 Utilisabilité

- **REQ-UTIL-001** : Temps de prise en main < 1h pour utilisateur avancé
- **REQ-UTIL-002** : Messages d'erreur explicites (pas de stacktraces brutes)
- **REQ-UTIL-003** : Confirmations pour actions destructives
- **REQ-UTIL-004** : Aide contextuelle (`--help`, tooltips)

---

## 5. Scénarios d'usage

### 5.1 Scénario : Créer et peupler un drive

**Acteur** : Créateur de contenu  
**Prérequis** : Python 3.10+ installé, hypermedia installé

**Étapes** :

1. Initialiser un drive
```bash
hm init ~/my-hypermedia-drive --name "Mes Créations"
```

2. Créer une collection
```bash
hm collection create "Photos/Voyages/Japon"
```

3. Ajouter des médias
```bash
hm add ~/Downloads/temple.jpg \
  --collection "Photos/Voyages/Japon" \
  --title "Temple Kinkaku-ji" \
  --tags "temple,kyoto,architecture" \
  --definers 'weight: 2.5 "temple doré, reflets dans l'eau"'
```

4. Vérifier l'ajout
```bash
hm search "temple" --collection "Photos/Voyages/Japon"
```

**Résultat attendu** : Le média est ajouté, indexé et recherchable.

---

### 5.2 Scénario : Synchroniser avec un drive distant

**Acteur** : Administrateur de drive  
**Prérequis** : Drive local initialisé, drive distant accessible

**Étapes** :

1. Ajouter un abonnement
```bash
hm sync add https://remote-drive.example.com \
  --collections "Shared/Public" \
  --mode readonly \
  --interval 5m
```

2. Lancer la synchronisation initiale
```bash
hm sync run --subscription remote-drive.example.com
```

3. Monitorer la synchronisation
```bash
hm sync status
```

4. Accéder aux médias distants
```bash
hm browse "Shared/Public"
```

**Résultat attendu** : Les médias distants sont copiés dans le cache local et accessibles.

---

### 5.3 Scénario : Créer un hypermedia composite

**Acteur** : Créateur de contenu  
**Prérequis** : Médias déjà présents dans le drive

**Étapes** :

1. Créer un fichier `.hm`
```bash
hm composite create "Galerie Japon" \
  --output "Hypermedia/galerie-japon.hm" \
  --collection "Photos/Voyages/Japon" \
  --layout grid \
  --columns 4
```

2. Ajouter un média audio
```bash
hm composite add "Hypermedia/galerie-japon.hm" \
  --uri "hm:///Music/ambient-japon.mp3" \
  --autoplay
```

3. Prévisualiser
```bash
hm show "Hypermedia/galerie-japon.hm"
```

**Résultat attendu** : Un hypermedia composite est créé, affichant les photos avec musique d'ambiance.

---

### 5.4 Scénario : Définir et appliquer une scène HM-DSS

**Acteur** : Créateur de contenu  
**Prérequis** : Collection de médias existante

**Étapes** :

1. Créer une feuille HM-DSS
```yaml
# scenes/galerie-japon.hm-dss
scene:
  name: "Galerie Japon"
  target: web

selectors:
  - match:
      collection: "Photos/Voyages/Japon"
      type: image
    style:
      layout: masonry
      thumbnail_size: auto
      hover_effect: zoom
      border_radius: 8px
```

2. Appliquer la scène
```bash
hm scene apply scenes/galerie-japon.hm-dss \
  --output gallery.html
```

3. Ouvrir le rendu
```bash
open gallery.html
```

**Résultat attendu** : Une galerie HTML responsive est générée avec le style défini.

---

### 5.5 Scénario : Explorer la généalogie d'un média

**Acteur** : Explorateur  
**Prérequis** : Médias avec relations généalogiques

**Étapes** :

1. Afficher les détails d'un média
```bash
hm show "hm:///Photos/edited-image.jpg"
```

2. Remonter aux ancêtres
```bash
hm genealogy ancestors "hm:///Photos/edited-image.jpg"
```

3. Explorer les descendants
```bash
hm genealogy descendants "hm:///Photos/original.jpg"
```

4. Visualiser le graphe complet
```bash
hm genealogy graph "hm:///Photos/original.jpg" --output graph.png
```

**Résultat attendu** : L'utilisateur peut explorer l'arbre généalogique complet.

---

## 6. Critères de succès

### 6.1 Critères fonctionnels

- ✅ Toutes les exigences critiques et élevées implémentées
- ✅ Scénarios d'usage validés par tests end-to-end
- ✅ Interface CLI complète et documentée
- ✅ API REST fonctionnelle avec documentation OpenAPI
- ✅ Interface web basique opérationnelle

### 6.2 Critères techniques

- ✅ Couverture de tests > 85%
- ✅ Performance conforme aux exigences (< 100ms recherche, < 1s sync)
- ✅ Zéro vulnérabilité critique (scan de sécurité)
- ✅ Documentation technique complète

### 6.3 Critères utilisateur

- ✅ Temps de prise en main < 1h (mesure via user testing)
- ✅ Retours utilisateurs positifs (> 80% satisfaction)
- ✅ Migration réussie depuis prompt-imagine (validation sur cas réel)

---

## 7. Limites et contraintes

### 7.1 Limites techniques

- **Taille maximale d'un hypermedia composite** : 1000 composants (limite de profondeur récursive : 10 niveaux)
- **Taille maximale d'un média** : 10 GB (configurable)
- **Nombre maximal d'abonnements** : 50 par instance
- **Taille maximale du cache** : Limitée par l'espace disque disponible

### 7.2 Contraintes opérationnelles

- **Synchronisation** : Requiert une connectivité réseau stable
- **Performance** : Dégradation possible avec > 100k médias (requiert optimisation BDD)
- **Compatibilité** : Python 3.10+ uniquement (pas de support Python 2.x ou 3.9-)

### 7.3 Évolutions futures

- Chiffrement end-to-end (version 1.1)
- Auto-tagging par IA (version 1.2)
- Architecture P2P complète (version 2.0)
- Applications mobiles (version 2.1)

---

## 8. Glossaire

- **HM-Drive** : Instance du système de stockage Hypermedia
- **Collection** : Dossier logique organisant les médias (équivalent d'un répertoire)
- **Média** : Fichier simple (image, vidéo, audio, texte)
- **Hypermedia** : Fichier composite référençant d'autres médias ou hypermedia
- **Définisseur** : Fragment textuel pondéré décrivant un média (inspiré des prompts IA)
- **HM-DSS** : Hypermedia Dynamic Scene Sheet, langage de mise en scène
- **URI HM** : Identifiant universel de ressource au format `hm://[instance]/[collection]/[path]`
- **Abonnement** : Configuration de synchronisation vers un drive distant
- **Cache local** : Stockage temporaire des médias distants
- **Checksum** : Empreinte cryptographique BLAKE2b pour identification unique
- **Généalogie** : Graphe de relations (ancêtres/descendants) entre médias
