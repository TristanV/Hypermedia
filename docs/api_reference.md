# Référence API - Hypermedia

Documentation complète de l'API publique d'Hypermedia.

---

## Table des matières

1. [DatabaseManager](#databasemanager)
2. [MediaCollection](#mediacollection)
3. [MetadataExtractor](#metadataextractor)
4. [DeduplicationManager](#deduplicationmanager)
5. [Modèles de données](#modèles-de-données)
6. [Utilitaires](#utilitaires)

---

## DatabaseManager

Gestionnaire de base de données SQLite avec SQLAlchemy.

### Constructeur

```python
DatabaseManager(
    db_path: Path,
    echo: bool = False
)
```

**Paramètres** :
- `db_path` : Chemin vers le fichier SQLite
- `echo` : Activer le logging SQL (défaut: False)

**Exemple** :
```python
from pathlib import Path
from hypermedia.drive import DatabaseManager

db = DatabaseManager(Path("./hypermedia.db"))
```

### Méthodes

#### `get_session()`

Context manager pour obtenir une session.

```python
with db.get_session() as session:
    # Opérations sur la base
    pass
```

**Retour** : Context manager de `Session` SQLAlchemy

#### `create_session()`

Crée une session manuelle (doit être fermée manuellement).

```python
session = db.create_session()
try:
    # Opérations
    session.commit()
finally:
    session.close()
```

**Retour** : `Session` SQLAlchemy

#### `close()`

Ferme toutes les connexions.

```python
db.close()
```

#### `reset()`

Réinitialise la base de données (supprime et recrée les tables).

```python
db.reset()  # Attention : supprime toutes les données !
```

#### `drop_all()`

Supprime toutes les tables.

```python
db.drop_all()
```

---

## MediaCollection

Interface principale pour gérer les collections de médias.

### Constructeur

```python
MediaCollection(
    storage_path: Path,
    db: DatabaseManager,
    auto_extract_metadata: bool = True
)
```

**Paramètres** :
- `storage_path` : Répertoire de stockage des médias
- `db` : Instance de DatabaseManager
- `auto_extract_metadata` : Extraction automatique de métadonnées (défaut: True)

**Exemple** :
```python
from hypermedia.drive import MediaCollection

collection = MediaCollection(
    storage_path=Path("./storage"),
    db=db,
    auto_extract_metadata=True
)
```

### Méthodes - Collections

#### `create_collection()`

Crée une nouvelle collection.

```python
create_collection(
    name: str,
    description: str = ""
) -> str
```

**Paramètres** :
- `name` : Nom unique de la collection
- `description` : Description (optionnel)

**Retour** : UUID de la collection créée

**Raises** :
- `ValueError` : Si le nom existe déjà

**Exemple** :
```python
coll_id = collection.create_collection(
    "Mes Photos",
    "Photos personnelles 2025-2026"
)
```

#### `get_collection()`

Récupère les informations d'une collection.

```python
get_collection(collection_id: str) -> Optional[Dict[str, Any]]
```

**Paramètres** :
- `collection_id` : UUID de la collection

**Retour** : Dictionnaire avec :
- `id` : UUID
- `name` : Nom
- `description` : Description
- `created_at` : Date de création
- `updated_at` : Dernière mise à jour
- `media_count` : Nombre de médias

Ou `None` si non trouvée.

#### `list_collections()`

Liste toutes les collections.

```python
list_collections() -> List[Dict[str, Any]]
```

**Retour** : Liste de dictionnaires (même structure que `get_collection()`)

### Méthodes - Médias

#### `add_media_to_collection()`

Ajoute un média à une collection.

```python
add_media_to_collection(
    collection_id: str,
    file_path: Path,
    copy_file: bool = True,
    custom_metadata: Optional[Dict[str, Any]] = None
) -> str
```

**Paramètres** :
- `collection_id` : UUID de la collection
- `file_path` : Chemin du fichier à ajouter
- `copy_file` : Copier dans le storage (défaut: True)
- `custom_metadata` : Métadonnées personnalisées (optionnel)

**Retour** : UUID du média

**Raises** :
- `FileNotFoundError` : Fichier inexistant
- `ValueError` : Collection inexistante

**Exemple** :
```python
media_id = collection.add_media_to_collection(
    collection_id,
    Path("/photos/sunset.jpg"),
    custom_metadata={
        "tags": ["nature", "sunset"],
        "location": "Marseille",
        "rating": 5
    }
)
```

#### `get_media_info()`

Récupère les informations d'un média.

```python
get_media_info(media_id: str) -> Optional[Dict[str, Any]]
```

**Paramètres** :
- `media_id` : UUID du média

**Retour** : Dictionnaire avec :
- `id` : UUID
- `checksum` : Checksum BLAKE2b
- `path` : Chemin relatif dans le storage
- `original_filename` : Nom d'origine
- `mime_type` : Type MIME
- `size` : Taille en bytes
- `created_at` : Date d'ajout
- `updated_at` : Dernière modification
- `metadata` : Dictionnaire de métadonnées
- `collections` : Liste des collections contenant ce média

#### `search()`

Recherche de médias.

```python
search(
    collection_id: Optional[str] = None,
    query: Optional[str] = None,
    metadata_filters: Optional[Dict[str, str]] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]
```

**Paramètres** :
- `collection_id` : Filtrer par collection (optionnel)
- `query` : Recherche textuelle dans les noms (optionnel)
- `metadata_filters` : Filtres sur métadonnées (optionnel)
- `limit` : Nombre max de résultats (défaut: 100)
- `offset` : Décalage pour pagination (défaut: 0)

**Retour** : Liste de dictionnaires de médias

**Exemple** :
```python
# Recherche simple
results = collection.search(collection_id=coll_id)

# Avec filtres
results = collection.search(
    query="vacation",
    metadata_filters={
        "custom.rating": "5",
        "exif.Make": "Canon"
    },
    limit=50
)
```

#### `delete_media()`

Supprime un média.

```python
delete_media(
    media_id: str,
    remove_file: bool = False
) -> bool
```

**Paramètres** :
- `media_id` : UUID du média
- `remove_file` : Supprimer aussi le fichier physique (défaut: False)

**Retour** : `True` si succès, `False` sinon

---

## MetadataExtractor

Extracteur de métadonnées multiformat.

### Constructeur

```python
MetadataExtractor(enable_video: bool = True)
```

**Paramètres** :
- `enable_video` : Activer extraction vidéo (nécessite ffprobe)

### Méthodes

#### `extract()`

Extrait les métadonnées d'un fichier.

```python
extract(file_path: Path) -> Dict[str, Any]
```

**Paramètres** :
- `file_path` : Chemin du fichier

**Retour** : Dictionnaire de métadonnées avec préfixes :
- `file.*` : Métadonnées génériques
- `exif.*` : Métadonnées EXIF (images)
- `audio.*` : Métadonnées audio
- `video.*` : Métadonnées vidéo

**Exemple** :
```python
from hypermedia.drive.metadata_extractor import MetadataExtractor

extractor = MetadataExtractor()
metadata = extractor.extract(Path("/photos/image.jpg"))

print(f"Caméra: {metadata.get('exif.Make', 'Inconnue')}")
print(f"Taille: {metadata['file.size']} bytes")
```

---

## DeduplicationManager

Gestionnaire de déduplication basé sur checksums.

### Constructeur

```python
DeduplicationManager(
    db: DatabaseManager,
    policy: DuplicatePolicy = DuplicatePolicy.REFERENCE
)
```

**Paramètres** :
- `db` : Instance de DatabaseManager
- `policy` : Politique de déduplication
  - `REFERENCE` : Référencer le doublon existant
  - `IGNORE` : Ignorer silencieusement
  - `ALERT` : Lever une alerte

### Méthodes

#### `is_duplicate()`

Vérifie si un checksum existe déjà.

```python
is_duplicate(checksum: str) -> bool
```

#### `find_duplicate()`

Trouve le média correspondant à un checksum.

```python
find_duplicate(checksum: str) -> Optional[MediaItem]
```

**Retour** : Objet `MediaItem` ou `None`

---

## Modèles de données

Modèles SQLAlchemy internes (rarement utilisés directement).

### MediaItem

```python
class MediaItem(Base):
    id: str  # UUID
    checksum: str  # BLAKE2b (unique)
    path: str
    mime_type: Optional[str]
    size: int
    original_filename: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Collection

```python
class Collection(Base):
    id: str  # UUID
    name: str  # Unique
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Metadata

```python
class Metadata(Base):
    id: str  # UUID
    media_id: str  # Foreign key
    key: str
    value: str
    source: str  # 'auto', 'user', 'import', 'api'
    created_at: datetime
```

---

## Utilitaires

### Checksums

```python
from hypermedia.drive.checksum import compute_blake2b, verify_integrity

# Calculer un checksum
checksum = compute_blake2b(Path("/path/to/file.jpg"))

# Vérifier l'intégrité
is_valid = verify_integrity(Path("/path/to/file.jpg"), checksum)
```

---

## Exemples avancés

### Workflow complet

```python
from pathlib import Path
from hypermedia.drive import DatabaseManager, MediaCollection

# Configuration
db = DatabaseManager(Path("./hypermedia.db"))
coll = MediaCollection(Path("./storage"), db)

try:
    # Créer collection
    coll_id = coll.create_collection("Photos 2026")
    
    # Ajouter fichiers d'un répertoire
    photo_dir = Path("/photos/2026")
    for photo in photo_dir.glob("*.jpg"):
        media_id = coll.add_media_to_collection(
            coll_id,
            photo,
            custom_metadata={"year": "2026"}
        )
        print(f"Ajouté: {photo.name}")
    
    # Rechercher et traiter
    results = coll.search(
        collection_id=coll_id,
        metadata_filters={"custom.year": "2026"}
    )
    
    for media in results:
        info = coll.get_media_info(media['id'])
        print(f"{info['original_filename']}: {info['size']} bytes")

finally:
    db.close()
```

---

**Documentation mise à jour** : 2026-02-10  
**Version** : 0.1.0-alpha
