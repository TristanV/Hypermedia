# Spécifications fonctionnelles - Hypermedia (HM)

## 1. Vue d'ensemble

### 1.1 Contexte

**Hypermedia (HM)** est né de l'analyse et de la généralisation du projet **prompt-imagine**, une application web Flask pour visualiser, gérer et rechercher des collections d'images et vidéos générées par IA. HM extrait les concepts structurants de prompt-imagine (collections, métadonnées, prompts pondérés, généalogie, checksums) pour construire une librairie Python générique, portable et résiliente.

### 1.2 Objectifs du projet

1. **Stockage distribué** : Créer un système de fichiers distribué (HM-drive) pour gérer des media sur des machines locales ou distantes, avec synchronisation et résilience.
2. **Hypermedia composites** : Permettre la création de compositions récursives de media (hypermedia) reliés par des URI.
3. **Métadonnées enrichies** : Gérer des métadonnées physiques, descripteurs sémantiques, tags et définisseurs pondérés (inspirés des prompts de prompt-imagine).
4. **Navigation hypermedia** : Offrir un système de navigation non linéaire multi-dimensionnelle (temps, espace, abstraction, relations).
5. **Mise en scène adaptative** : Créer un langage de mise en scène (HM-DSS) pour projeter les hypermedia sur différents supports (web, terminal, GUI native).
6. **Portabilité** : Fonctionner sur Linux, macOS et Windows sans modification.

### 1.3 Périmètre

#### Fonctionnalités incluses (MVP)
- Système de fichiers distribué HM-drive
- Synchronisation mono et bi-directionnelle entre instances
- Gestion de media simples (image, vidéo, audio, texte) et hypermedia composites
- Métadonnées : checksums, descripteurs, tags, définisseurs pondérés
- Relations généalogiques (parent/enfant, ancêtres/descendants)
- Recherche multi-critères (full-text, tags, date, type)
- Langage HM-DSS pour mise en scène
- Moteur de rendu multi-supports (web, terminal)
- CLI et interface web de gestion

#### Fonctionnalités exclues (post-MVP)
- Collaboration temps réel (CRDT)
- Chiffrement bout-en-bout
- Versioning avancé (branches, merges)
- Support 3D, VR, AR
- Plugins tiers
- Intégration IA (génération automatique de métadonnées)

---

## 2. Acteurs

### 2.1 Utilisateur créateur

**Description** : Personne qui crée, organise et enrichit des collections de media et hypermedia.

**Besoins** :
- Importer des media depuis des sources variées (fichiers locaux, backups NightCafe, API)
- Organiser les media en collections thématiques
- Enrichir les métadonnées (tags, descriptions, définisseurs)
- Établir des relations entre media (généalogie, similarité)
- Créer des hypermedia composites
- Visualiser les collections sous différentes facettes

**Compétences** :
- Basique : Utilisation d'interface graphique ou CLI simple
- Intermédiaire : Édition de fichiers HM-DSS, configuration d'instances

### 2.2 Utilisateur consommateur

**Description** : Personne qui navigue, explore et consomme des collections d'hypermedia.

**Besoins** :
- Accéder rapidement aux collections
- Naviguer de manière intuitive (lightbox, zoom, défilement)
- Rechercher des media par critères multiples
- Visualiser les relations entre media (graphe généalogique)
- Parcourir différentes vues d'une même collection (grille, timeline, graphe)

**Compétences** :
- Basique : Navigation web ou terminal
- Aucune compétence technique requise

### 2.3 Développeur / Intégrateur

**Description** : Développeur intégrant HM dans une application tierce ou étendant ses fonctionnalités.

**Besoins** :
- API Python claire et bien documentée
- Exemples de code et tutoriels
- Système de plugins pour étendre les fonctionnalités
- Documentation technique complète (architecture, schémas de données)

**Compétences** :
- Python intermédiaire à avancé
- Connaissance des systèmes de fichiers et bases de données

### 2.4 Administrateur système

**Description** : Personne responsable du déploiement et de la maintenance d'instances HM en production.

**Besoins** :
- Installation simple et rapide (pip, Docker)
- Configuration centralisée (fichiers .env, YAML)
- Monitoring et logs
- Outils de maintenance (réparation, nettoyage)
- Documentation de déploiement multi-OS

**Compétences** :
- Administration système Linux/macOS/Windows
- Connaissance de Docker (optionnel)

---

## 3. Exigences fonctionnelles

### 3.1 HM-drive (Stockage distribué)

#### RF-1.1 : Création d'une instance HM-drive

**Description** : L'utilisateur doit pouvoir initialiser une instance HM-drive avec un dossier principal local.

**Préconditions** :
- Python 3.8+ installé
- Droits d'écriture sur le système de fichiers

**Scénario nominal** :
1. L'utilisateur exécute `hm init /chemin/vers/dossier`
2. Le système crée la structure de dossiers (collections/, cache/, .hm/)
3. Le système crée une base SQLite locale (.hm/metadata.db)
4. Le système génère un identifiant unique pour l'instance (UUID)
5. Le système confirme la création

**Postconditions** :
- Instance HM-drive opérationnelle
- Dossier principal accessible via URI `hm://local/`

**Critères d'acceptation** :
- CR-1.1.1 : L'initialisation réussit en < 5 secondes
- CR-1.1.2 : Tous les fichiers de configuration sont créés
- CR-1.1.3 : Un message de confirmation est affiché

#### RF-1.2 : Gestion des collections

**Description** : L'utilisateur doit pouvoir créer, lister, renommer et supprimer des collections.

**Scénario nominal (création)** :
1. L'utilisateur exécute `hm collection create "Ma collection"`
2. Le système crée un dossier dans collections/
3. Le système enregistre les métadonnées de la collection en base
4. Le système confirme la création

**Critères d'acceptation** :
- CR-1.2.1 : Une collection peut contenir des sous-collections (arborescence)
- CR-1.2.2 : Le nom de collection accepte Unicode (caractères accentués, émojis)
- CR-1.2.3 : La suppression d'une collection demande confirmation
- CR-1.2.4 : La suppression d'une collection non vide peut être forcée ou refusée

#### RF-1.3 : Ajout de media

**Description** : L'utilisateur doit pouvoir ajouter des media (fichiers locaux) à une collection.

**Scénario nominal** :
1. L'utilisateur exécute `hm add /chemin/fichier.jpg "Ma collection"`
2. Le système copie le fichier dans collections/ma-collection/
3. Le système calcule le checksum BLAKE2b
4. Le système génère un thumbnail (si image/vidéo)
5. Le système extrait les métadonnées physiques (résolution, codec, durée)
6. Le système enregistre le media en base
7. Le système retourne l'URI du media (`hm://local/ma-collection/fichier.jpg`)

**Critères d'acceptation** :
- CR-1.3.1 : Support des formats : JPEG, PNG, GIF, MP4, WebM, MP3, WAV, TXT, MD
- CR-1.3.2 : Détection automatique des doublons (via checksum)
- CR-1.3.3 : Option pour ajouter un media à plusieurs collections simultanément
- CR-1.3.4 : Ajout batch de plusieurs fichiers en une commande

#### RF-1.4 : Synchronisation entre instances

**Description** : Deux instances HM-drive doivent pouvoir se synchroniser (mono ou bi-directionnel).

**Préconditions** :
- Deux instances HM-drive initialisées
- Connectivité réseau entre les deux instances (HTTP/HTTPS ou SSH)

**Scénario nominal (abonnement mono-directionnel)** :
1. L'utilisateur exécute `hm subscribe http://instance-distante:5000 "Collection distante"`
2. Le système authentifie auprès de l'instance distante (token JWT)
3. Le système récupère la liste des media de la collection distante
4. Le système compare avec le cache local (checksums)
5. Le système télécharge les media manquants ou modifiés
6. Le système met à jour le cache local
7. Le système confirme la synchronisation

**Scénario nominal (synchronisation bi-directionnelle)** :
- Idem ci-dessus, mais les deux instances s'abonnent mutuellement
- Les modifications locales sont poussées vers l'instance distante

**Critères d'acceptation** :
- CR-1.4.1 : Synchronisation incrémentale (seuls les changements sont transférés)
- CR-1.4.2 : Synchronisation automatique périodique (configurable)
- CR-1.4.3 : Gestion des conflits (stratégies : dernier gagnant, fusion, manuel)
- CR-1.4.4 : Synchronisation en arrière-plan sans bloquer l'interface

#### RF-1.5 : Résilience et mode dégradé

**Description** : Le système doit continuer à fonctionner en cas de déconnexion ou d'indisponibilité d'une instance distante.

**Scénario nominal** :
1. L'utilisateur accède à un media distant (URI `hm://instance-distante/collection/media.jpg`)
2. Le système détecte que l'instance distante est inaccessible (timeout)
3. Le système vérifie le cache local
4. Si le media est en cache, le système le retourne avec un avertissement ("Mode dégradé : cache local")
5. Si le media n'est pas en cache, le système retourne une erreur explicite

**Critères d'acceptation** :
- CR-1.5.1 : Le cache local est prioritaire en cas de déconnexion
- CR-1.5.2 : Les opérations d'écriture sont mises en file d'attente et ré-essayées à la reconnexion
- CR-1.5.3 : Un indicateur visuel montre l'état de connectivité de chaque instance abonnée
- CR-1.5.4 : Vérification périodique d'intégrité (checksums) après reconnexion

---

### 3.2 Hypermedia composites

#### RF-2.1 : Création d'un hypermedia

**Description** : L'utilisateur doit pouvoir créer un hypermedia composite (composition de media).

**Scénario nominal** :
1. L'utilisateur crée un fichier `.hm` (JSON) avec la structure suivante :
```json
{
  "type": "hypermedia",
  "title": "Mon hypermedia",
  "components": [
    {"uri": "hm://local/collection1/image1.jpg", "role": "background"},
    {"uri": "hm://local/collection1/audio1.mp3", "role": "soundtrack"},
    {"uri": "hm://instance2/collection2/video1.mp4", "role": "overlay"}
  ],
  "metadata": {
    "tags": ["composite", "multimedia"],
    "definers": {"ambiance": 2.5, "dynamique": 1.8}
  }
}
```
2. L'utilisateur exécute `hm add mon-hypermedia.hm "Ma collection"`
3. Le système valide le schéma JSON
4. Le système vérifie l'existence de tous les media référencés
5. Le système enregistre l'hypermedia en base
6. Le système retourne l'URI de l'hypermedia

**Critères d'acceptation** :
- CR-2.1.1 : Un hypermedia peut contenir d'autres hypermedia (récursivité)
- CR-2.1.2 : Les media référencés peuvent être locaux ou distants
- CR-2.1.3 : Validation stricte du schéma JSON (JSON Schema)
- CR-2.1.4 : Génération automatique d'un thumbnail composé (mosaïque)

#### RF-2.2 : Navigation dans un hypermedia

**Description** : L'utilisateur doit pouvoir naviguer dans les composants d'un hypermedia.

**Scénario nominal** :
1. L'utilisateur affiche un hypermedia (`hm view hm://local/collection/mon-hypermedia.hm`)
2. Le système charge tous les composants (avec cache si distants)
3. Le système affiche une vue composite selon la scène active (HM-DSS)
4. L'utilisateur peut cliquer sur un composant pour l'isoler ou le détailler
5. L'utilisateur peut naviguer vers les media sources via des liens

**Critères d'acceptation** :
- CR-2.2.1 : Chargement lazy des composants (uniquement si nécessaires)
- CR-2.2.2 : Prévisualisation des hypermedia imbriqués (profondeur max configurable)
- CR-2.2.3 : Historique de navigation (back/forward)

---

### 3.3 Métadonnées et recherche

#### RF-3.1 : Gestion des tags

**Description** : L'utilisateur doit pouvoir ajouter, modifier et supprimer des tags sur des media.

**Scénario nominal** :
1. L'utilisateur exécute `hm tag add "paysage" hm://local/collection/image.jpg`
2. Le système vérifie que le media existe
3. Le système ajoute le tag dans la table `media_tags` (many-to-many)
4. Le système met à jour l'index de recherche
5. Le système confirme l'ajout

**Critères d'acceptation** :
- CR-3.1.1 : Autocomplétion des tags existants dans l'interface web/CLI
- CR-3.1.2 : Tags hiérarchiques (avec séparateur `/`, ex: `nature/paysage/montagne`)
- CR-3.1.3 : Renommage de tags avec propagation automatique
- CR-3.1.4 : Suppression de tags avec confirmation si > 10 media concernés

#### RF-3.2 : Gestion des définisseurs pondérés

**Description** : L'utilisateur doit pouvoir attribuer des définisseurs pondérés (inspirés des prompts de prompt-imagine) à des media.

**Scénario nominal** :
1. L'utilisateur exécute `hm definer add "lumineux:2.5" "contrasté:1.8" hm://local/collection/image.jpg`
2. Le système parse les définisseurs (format `terme:poids`)
3. Le système enregistre les définisseurs dans la table `media_definers`
4. Le système met à jour l'index de recherche pondérée

**Critères d'acceptation** :
- CR-3.2.1 : Poids décimaux (ex: 2.5) ou entiers (ex: 3)
- CR-3.2.2 : Poids négatifs pour atténuer un terme (ex: "sombre:-1.5")
- CR-3.2.3 : Génération automatique de wordclouds pondérés par collection
- CR-3.2.4 : Recherche par définisseurs avec score de pertinence

#### RF-3.3 : Recherche multi-critères

**Description** : L'utilisateur doit pouvoir rechercher des media par titre, tags, définisseurs, date, type, collection.

**Scénario nominal** :
1. L'utilisateur exécute `hm search --tags "paysage" --type "image" --after "2025-01-01"`
2. Le système construit une requête SQLite avec clauses WHERE
3. Le système exécute la requête (avec index)
4. Le système retourne la liste des media correspondants (avec score si recherche full-text)
5. Le système affiche les résultats (thumbnails + métadonnées)

**Critères d'acceptation** :
- CR-3.3.1 : Recherche full-text sur titre, description, tags, définisseurs (FTS5)
- CR-3.3.2 : Filtres cumulatifs (AND logic)
- CR-3.3.3 : Tri par pertinence, date, titre, taille
- CR-3.3.4 : Pagination des résultats (50 par page par défaut)
- CR-3.3.5 : Recherche < 50ms pour 10k media (avec index optimisés)

---

### 3.4 HM-Scene et HM-DSS

#### RF-4.1 : Création d'une scène HM-DSS

**Description** : L'utilisateur doit pouvoir créer une scène (fichier `.hm-dss`) pour définir la mise en page d'une collection.

**Exemple de scène** :
```css
/* Scène : Galerie en grille */
@scene "Galerie" {
  layout: grid;
  columns: 4;
  gap: 16px;
  pagination: dynamic;
}

/* Sélecteur : Toutes les images */
media[type="image"] {
  aspect-ratio: 1/1;
  object-fit: cover;
  hover: zoom(1.1);
  click: lightbox;
}

/* Sélecteur : Tags "paysage" */
media[tags~="paysage"] {
  border: 2px solid green;
}

/* Navigation */
@navigation {
  mode: infinite-scroll;
  preload: 3-pages;
}
```

**Scénario nominal** :
1. L'utilisateur crée un fichier `ma-scene.hm-dss` avec la syntaxe ci-dessus
2. L'utilisateur exécute `hm scene validate ma-scene.hm-dss`
3. Le système parse le fichier et vérifie la syntaxe
4. Le système retourne les erreurs ou confirme la validité
5. L'utilisateur applique la scène : `hm scene apply ma-scene.hm-dss "Ma collection"`

**Critères d'acceptation** :
- CR-4.1.1 : Syntaxe inspirée de CSS (sélecteurs, propriétés, valeurs)
- CR-4.1.2 : Extensions spécifiques hypermedia (pagination, transitions, facettes)
- CR-4.1.3 : Validation stricte avec messages d'erreur explicites
- CR-4.1.4 : Support de variables CSS-like (`--primary-color: #3498db;`)

#### RF-4.2 : Rendu multi-supports

**Description** : Une scène HM-DSS doit pouvoir être rendue sur différents supports (web, terminal, GUI native).

**Scénario nominal (rendu web)** :
1. L'utilisateur lance l'interface web : `hm web --port 5000`
2. L'utilisateur accède à une collection dans le navigateur
3. Le système charge la scène HM-DSS associée (ou scène par défaut)
4. Le système génère le HTML/CSS correspondant
5. Le navigateur affiche la galerie selon la scène

**Critères d'acceptation** :
- CR-4.2.1 : Adaptateur web (HTML/CSS/JS) avec responsivité
- CR-4.2.2 : Adaptateur terminal (TUI avec `rich` ou `textual`)
- CR-4.2.3 : Adaptateur GUI natif (Tkinter ou Qt)
- CR-4.2.4 : Rendu différentiel (mise à jour incrémentale sans rechargement complet)

#### RF-4.3 : Navigation hypermedia

**Description** : L'utilisateur doit pouvoir naviguer de manière non linéaire dans les hypermedia via liens, filtres et facettes.

**Dimensions de navigation** :
- **Temps** : Timeline chronologique (date de création/modification)
- **Espace** : Arborescence de collections
- **Abstraction** : Du général (collection) au particulier (media)
- **Relations** : Liens généalogiques (ancêtres/descendants)
- **Sémantique** : Tags, définisseurs, similarité

**Scénario nominal** :
1. L'utilisateur affiche un media
2. Le système affiche les liens disponibles (ancêtres, descendants, tags similaires)
3. L'utilisateur clique sur un lien (ex: "Voir les ancêtres")
4. Le système charge et affiche les media liés
5. L'utilisateur peut revenir en arrière (historique)

**Critères d'acceptation** :
- CR-4.3.1 : Historique de navigation (100 dernières pages)
- CR-4.3.2 : Bookmarks pour marquer des media/collections
- CR-4.3.3 : Filtres cumulatifs (affinage progressif)
- CR-4.3.4 : Vues multiples d'une même collection (grille, timeline, graphe)

---

## 4. Exigences non fonctionnelles

### 4.1 Performance

| ID | Exigence | Critère mesurable |
|----|----------|--------------------|
| NFR-1.1 | Recherche rapide | < 50ms pour 10k media (avec index) |
| NFR-1.2 | Synchronisation rapide | < 100ms pour 1000 fichiers (incrémental) |
| NFR-1.3 | Rendu responsive | Affichage initial < 500ms (web) |
| NFR-1.4 | Génération de thumbnails | < 200ms par image (640x480) |
| NFR-1.5 | Chargement de scène | < 100ms pour un fichier HM-DSS de 1000 lignes |

### 4.2 Scalabilité

| ID | Exigence | Critère mesurable |
|----|----------|--------------------|
| NFR-2.1 | Support grandes collections | Jusqu'à 100k media par instance |
| NFR-2.2 | Pagination efficace | Pas de dégradation au-delà de 10k résultats |
| NFR-2.3 | Synchronisation multi-instances | Jusqu'à 10 instances abonnées simultanément |
| NFR-2.4 | Hypermedia imbriqus | Profondeur max 10 niveaux de récursion |

### 4.3 Fiabilité

| ID | Exigence | Critère mesurable |
|----|----------|--------------------|
| NFR-3.1 | Taux de disponibilité | 99.9% (hors maintenance) |
| NFR-3.2 | Résilience aux pannes | 100% des opérations transactionnelles avec rollback |
| NFR-3.3 | Intégrité des données | Vérification checksums après chaque synchronisation |
| NFR-3.4 | Récupération après crash | Reconstruction automatique de l'index en < 1 minute |

### 4.4 Portabilité

| ID | Exigence | Critère mesurable |
|----|----------|--------------------|
| NFR-4.1 | Multi-OS | Support Linux, macOS, Windows sans modification |
| NFR-4.2 | Multi-Python | Compatibilité Python 3.8, 3.9, 3.10, 3.11, 3.12 |
| NFR-4.3 | Dépendances minimales | < 10 dépendances directes (hors stdlib) |
| NFR-4.4 | Installation simple | Installation en 1 commande (`pip install hypermedia`) |

### 4.5 Sécurité

| ID | Exigence | Critère mesurable |
|----|----------|--------------------|
| NFR-5.1 | Validation des chemins | 100% des chemins de fichiers validés (pas d'accès hors racine) |
| NFR-5.2 | Authentification instances | Tokens JWT avec expiration (24h par défaut) |
| NFR-5.3 | Sanitisation entrées | Validation stricte de tous les inputs utilisateur |
| NFR-5.4 | Logs de sécurité | Traçage de toutes les opérations d'écriture |

### 4.6 Utilisabilité

| ID | Exigence | Critère mesurable |
|----|----------|--------------------|
| NFR-6.1 | Courbe d'apprentissage | < 30 minutes pour première utilisation (création collection + ajout media) |
| NFR-6.2 | Messages d'erreur | 100% des erreurs avec message explicite et suggestion de correction |
| NFR-6.3 | Documentation | 100% des API publiques documentées (docstrings + Sphinx) |
| NFR-6.4 | Accessibilité web | Conformité WCAG 2.1 niveau AA |

---

## 5. Critères de succès du MVP

### 5.1 Critères techniques

- ✅ Toutes les exigences fonctionnelles RF-1.x à RF-4.x implémentées
- ✅ Couverture de tests > 80% sur modules critiques (drive, media, metadata)
- ✅ Performance conforme aux exigences NFR-1.x
- ✅ Zéro régression sur les tests d'intégration

### 5.2 Critères fonctionnels

- ✅ Migration réussie d'un backup prompt-imagine vers HM sans perte d'information
- ✅ Création d'une collection, ajout de 100 media, recherche et navigation < 10 minutes
- ✅ Synchronisation entre 2 instances sur réseaux différents (LAN, Internet)
- ✅ Rendu de scène HM-DSS sur web et terminal

### 5.3 Critères d'adoption

- 🎯 3 utilisateurs testeurs externes avec feedback positif
- 🎯 1 scène HM-DSS créée par un utilisateur externe
- 🎯 Documentation complète (README, tutoriels, API)

---

## 6. Limites et exclusions

### 6.1 Fonctionnalités explicitement exclues du MVP

- Collaboration temps réel (CRDT, opérational transforms)
- Chiffrement bout-en-bout des media
- Versioning avancé (branches, merges, diff)
- Support formats 3D (OBJ, FBX, GLTF)
- Support VR/AR (WebXR, ARKit)
- Plugins tiers / Marketplace
- Intégration IA (embeddings, recherche vectorielle, génération auto de tags)
- Application mobile native (iOS, Android)

### 6.2 Limitations techniques connues

- **SQLite** : Performances dégradées au-delà de 100k media (migration vers PostgreSQL recommandée pour usage intensif)
- **Synchronisation** : Conflits complexes nécessitent résolution manuelle (pas de merge automatique intelligent)
- **HM-DSS** : Pas d'exécution de code arbitraire (sécurité), uniquement déclaratif
- **Formats media** : Support limité aux formats courants (extensible via plugins post-MVP)

---

## 7. Glossaire

| Terme | Définition |
|-------|-------------|
| **HM-drive** | Système de fichiers distribué pour stocker et synchroniser des media entre instances |
| **Instance** | Installation unique de la librairie HM avec son propre dossier principal et sa base de données |
| **Collection** | Dossier logique regroupant des media selon une thématique (ex: "Paysages 2024") |
| **Media simple** | Fichier mono-type (image, vidéo, audio, texte) |
| **Hypermedia** | Composite de plusieurs media simples ou hypermedia, décrit par un fichier `.hm` (JSON) |
| **URI HM** | Identifiant unique de ressource (ex: `hm://instance/collection/media.jpg`) |
| **Checksum** | Empreinte cryptographique BLAKE2b d'un fichier pour détecter doublons et vérifier intégrité |
| **Définisseur** | Terme pondéré décrivant un media (inspiré des prompts de prompt-imagine), ex: "lumineux:2.5" |
| **HM-DSS** | Hypermedia Dynamic Scene Sheet, langage de mise en scène inspiré de CSS |
| **Scène** | Configuration de mise en page et de navigation pour une collection (fichier `.hm-dss`) |
| **Cache local** | Copie locale des media distants pour accès hors-ligne |
| **Abonnement** | Relation de synchronisation entre deux instances (mono ou bi-directionnel) |
| **Thumbnail** | Miniature générée automatiquement pour prévisualisation rapide |
| **Facette** | Dimension de navigation (temps, espace, tags, relations) permettant de voir une collection sous un angle spécifique |

---

**Dernière mise à jour** : 10 février 2026  
**Version** : 1.0  
**Auteur** : Tristan Vanrullen
