# Spécifications Techniques - Hypermedia

## 1. Architecture Globale

### Principe de séparation des responsabilités

**Trois couches distinctes** :
- **Couche Stockage (HM-Drive)** : persistance, synchronisation, intégrité
- **Couche Métier (Core)** : logique applicative, validation, orchestration
- **Couche Présentation (HM-Scene)** : rendu, interaction, navigation

### Patterns architecturaux

- **Repository Pattern** : abstraction de la persistance (SQLite, PostgreSQL)
- **Factory Pattern** : création d'objets complexes (Media, Composite, Scene)
- **Observer Pattern** : notifications de changements (sync, cache invalidation)
- **Strategy Pattern** : algorithmes interchangeables (résolution conflits, layout)
- **Command Pattern** : opérations réversibles (undo/redo)

### Diagramme en couches

```
┌─────────────────────────────────────────────┐
│  Applications (Web, CLI, Desktop)           │
├─────────────────────────────────────────────┤
│  HM-Scene (Presentation Layer)              │
│  - SceneEngine, DSSParser, Renderers        │
├─────────────────────────────────────────────┤
│  Core Business Logic                        │
│  - URIResolver, GraphManager, Validators    │
├─────────────────────────────────────────────┤
│  HM-Drive (Storage Layer)                   │
│  - LocalDrive, DistributedDrive, SyncMgr    │
├─────────────────────────────────────────────┤
│  Infrastructure                             │
│  - Database, FileSystem, Network, Cache     │
└─────────────────────────────────────────────┘
```

---

## 2. Architecture des Modules Python

### Structure complète du package

```
hypermedia/
├── __init__.py                  # Point d'entrée, version
├── core/
│   ├── __init__.py
│   ├── config.py                # Configuration globale
│   ├── exceptions.py            # Exceptions custom
│   └── constants.py             # Constantes (formats, limites)
│
├── drive/
│   ├── __init__.py
│   ├── local.py                 # HM-Drive local
│   ├── distributed.py           # Gestion instances distantes
│   ├── sync.py                  # Moteur de synchronisation
│   └── instance.py              # Modèle Instance
│
├── storage/
│   ├── __init__.py
│   ├── database.py              # Abstraction SQLite/PostgreSQL
│   ├── models.py                # ORM Models (SQLAlchemy)
│   └── migrations/              # Alembic migrations
│
├── metadata/
│   ├── __init__.py
│   ├── extractor.py             # Extraction EXIF/IPTC
│   ├── descriptors.py           # Définisseurs pondérés
│   ├── tags.py                  # Gestion tags
│   └── indexer.py               # Indexation full-text
│
├── media/
│   ├── __init__.py
│   ├── processors.py            # Thumbnails, transcoding
│   ├── validators.py            # Validation formats
│   └── formats.py               # Détection type MIME
│
├── uri.py                       # Résolution URI
├── graph.py                     # Graphe relationnel
├── composite.py                 # Hypermedia composites
│
├── scene/
│   ├── __init__.py
│   ├── engine.py                # Moteur de scène
│   ├── parser.py                # Parser HM-DSS
│   ├── selectors.py             # Sélecteurs CSS-like
│   ├── layout.py                # Calcul de layout
│   ├── renderers/
│   │   ├── html.py              # Rendu HTML/CSS/JS
│   │   ├── json.py              # Export JSON
│   │   └── terminal.py          # TUI (Rich/Textual)
│   └── templates.py             # Templates prédéfinis
│
├── network/
│   ├── __init__.py
│   ├── api.py                   # REST API (FastAPI)
│   ├── client.py                # Client HTTP
│   ├── discovery.py             # mDNS/Zeroconf
│   └── protocol.py              # Protocole sync
│
├── utils/
│   ├── __init__.py
│   ├── crypto.py                # Checksums (BLAKE2b)
│   ├── cache.py                 # Cache multi-niveaux
│   ├── filesystem.py            # Opérations fichiers sécurisées
│   ├── logging.py               # Logs structurés
│   └── monitoring.py            # Métriques Prometheus
│
└── cli/
    ├── __init__.py
    ├── main.py                  # Point d'entrée CLI
    ├── commands/
    │   ├── init.py              # hm init
    │   ├── add.py               # hm add
    │   ├── list.py              # hm list
    │   ├── show.py              # hm show
    │   ├── sync.py              # hm sync
    │   ├── search.py            # hm search
    │   └── migrate.py           # hm migrate
    └── utils.py                 # Helpers CLI
```

---

## 3. Modèle de Données SQL

### Schéma complet SQLite/PostgreSQL

```sql
-- Table des instances HM-Drive
CREATE TABLE instances (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    uri TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    config_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des collections
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    parent_id TEXT,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT,
    FOREIGN KEY (instance_id) REFERENCES instances(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES collections(id) ON DELETE CASCADE,
    UNIQUE (instance_id, path)
);

CREATE INDEX idx_collections_parent ON collections(parent_id);
CREATE INDEX idx_collections_path ON collections(path);

-- Table des médias
CREATE TABLE media (
    id TEXT PRIMARY KEY,
    checksum TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT,
    size INTEGER NOT NULL,
    format TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    duration REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT,
    UNIQUE (checksum, filename)
);

CREATE UNIQUE INDEX idx_media_checksum ON media(checksum);
CREATE INDEX idx_media_format ON media(format);
CREATE INDEX idx_media_created ON media(created_at DESC);

-- FTS5 pour recherche full-text
CREATE VIRTUAL TABLE media_fts USING fts5(
    media_id UNINDEXED,
    filename,
    original_filename,
    metadata_text,
    content=media,
    content_rowid=id
);

-- Table many-to-many : médias <-> collections
CREATE TABLE media_collections (
    media_id TEXT NOT NULL,
    collection_id TEXT NOT NULL,
    position INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (media_id, collection_id),
    FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

CREATE INDEX idx_mc_collection ON media_collections(collection_id);
CREATE INDEX idx_mc_position ON media_collections(collection_id, position);

-- Table des descripteurs (définisseurs pondérés)
CREATE TABLE descriptors (
    id TEXT PRIMARY KEY,
    media_id TEXT NOT NULL,
    type TEXT NOT NULL,
    text TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    category TEXT,
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE CASCADE
);

CREATE INDEX idx_descriptors_media ON descriptors(media_id);
CREATE INDEX idx_descriptors_type ON descriptors(type);

-- Table des tags
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    color TEXT,
    category TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_category ON tags(category);

-- Table many-to-many : médias <-> tags
CREATE TABLE media_tags (
    media_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (media_id, tag_id),
    FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_mt_tag ON media_tags(tag_id);

-- Table des relations (graphe)
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    metadata_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES media(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES media(id) ON DELETE CASCADE,
    UNIQUE (source_id, target_id, type)
);

CREATE INDEX idx_rel_source ON relationships(source_id);
CREATE INDEX idx_rel_target ON relationships(target_id);
CREATE INDEX idx_rel_type ON relationships(type);

-- Table des composites
CREATE TABLE composites (
    id TEXT PRIMARY KEY,
    media_id TEXT NOT NULL UNIQUE,
    layout TEXT NOT NULL,
    definition_json TEXT NOT NULL,
    max_depth INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE CASCADE
);

-- Table des scènes
CREATE TABLE scenes (
    id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,
    dss_content TEXT NOT NULL,
    config_json TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    UNIQUE (collection_id, name)
);

CREATE INDEX idx_scenes_collection ON scenes(collection_id);

-- Table des abonnements (subscriptions)
CREATE TABLE subscriptions (
    id TEXT PRIMARY KEY,
    local_instance_id TEXT NOT NULL,
    remote_instance_id TEXT NOT NULL,
    collection_id TEXT,
    mode TEXT NOT NULL,
    schedule TEXT,
    conflict_strategy TEXT DEFAULT 'last_write_wins',
    status TEXT DEFAULT 'active',
    last_sync TIMESTAMP,
    next_sync TIMESTAMP,
    config_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (local_instance_id) REFERENCES instances(id) ON DELETE CASCADE,
    FOREIGN KEY (remote_instance_id) REFERENCES instances(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

CREATE INDEX idx_subs_local ON subscriptions(local_instance_id);
CREATE INDEX idx_subs_remote ON subscriptions(remote_instance_id);
CREATE INDEX idx_subs_next_sync ON subscriptions(next_sync);

-- Table des logs de synchronisation
CREATE TABLE sync_log (
    id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,
    direction TEXT NOT NULL,
    media_added INTEGER DEFAULT 0,
    media_updated INTEGER DEFAULT 0,
    media_deleted INTEGER DEFAULT 0,
    bytes_transferred INTEGER DEFAULT 0,
    conflicts_detected INTEGER DEFAULT 0,
    errors_json TEXT,
    stats_json TEXT,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

CREATE INDEX idx_sync_log_sub ON sync_log(subscription_id);
CREATE INDEX idx_sync_log_started ON sync_log(started_at DESC);

-- Table de la queue de synchronisation
CREATE TABLE sync_queue (
    id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    target_uri TEXT NOT NULL,
    data_json TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 5,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

CREATE INDEX idx_queue_status ON sync_queue(status, timestamp);

-- Table des liens symboliques virtuels
CREATE TABLE collection_links (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES collections(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES collections(id) ON DELETE CASCADE,
    UNIQUE (source_id, target_id, type)
);

-- Table du cache
CREATE TABLE cache_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

CREATE INDEX idx_cache_expires ON cache_metadata(expires_at);
CREATE INDEX idx_cache_accessed ON cache_metadata(accessed_at);
```

---

## 4. API Principales

### API HM-Drive

```python
from pathlib import Path
from typing import List, Optional, Dict

class HMDrive:
    def __init__(self, root_path: Path, config: Optional[Dict] = None)
    
    # Collections
    def create_collection(self, name: str, parent: Optional[str] = None) -> Collection
    def list_collections(self, parent: Optional[str] = None) -> List[Collection]
    def get_collection(self, collection_id: str) -> Collection
    def delete_collection(self, collection_id: str, delete_media: bool = False) -> bool
    
    # Médias
    def add_media(self, collection: str, file_path: Path, metadata: Optional[Dict] = None) -> Media
    def list_media(self, collection: str, filters: Optional[Dict] = None) -> List[Media]
    def get_media(self, media_id: str) -> Media
    def update_metadata(self, media_id: str, metadata: Dict) -> Media
    def delete_media(self, media_id: str, delete_file: bool = True) -> bool
    
    # Doublons
    def compute_checksum(self, file_path: Path) -> str
    def find_duplicates(self, checksum: Optional[str] = None) -> List[Media]
    def merge_duplicates(self, keep_id: str, delete_ids: List[str]) -> Media
    
    # Thumbnails
    def generate_thumbnail(self, media_id: str, size: Tuple[int, int]) -> Path
    def get_thumbnail(self, media_id: str, size: Tuple[int, int]) -> Optional[Path]
    
    # Recherche
    def search(self, query: str, collections: Optional[List[str]] = None) -> List[Media]
    
    # Maintenance
    def verify_integrity(self, collection: Optional[str] = None) -> Dict
    def repair(self, issues: Dict, auto_fix: bool = False) -> Dict
```

### API URI

```python
class URIResolver:
    def parse(self, uri: str) -> URIComponents
    def resolve(self, uri: str, use_cache: bool = True) -> Media
    def build_uri(self, instance: str, collection: str, media_id: str) -> str
    def parse_fragment(self, fragment: str) -> dict
```

**Format URI** : `hm://[instance]/[collection]/[media_id][#fragment]`

**Exemples** :
- `hm://local/portraits/abc123`
- `hm://server.com:8080/videos/demo.mp4#t=30s`
- `hm://192.168.1.100/projects/composite#component=2`

### API Synchronisation

```python
class SyncManager:
    def subscribe(self, remote_uri: str, collections: List[str], mode: SyncMode) -> str
    def unsubscribe(self, subscription_id: str)
    def sync_now(self, subscription_id: str, force: bool = False) -> SyncResult
    def resolve_conflict(self, conflict: dict, strategy: ConflictStrategy) -> Media
    def start_auto_sync(self, interval: int = 900)
    def get_sync_status(self, subscription_id: str) -> dict
```

### API Composite

```python
class Composite:
    def __init__(self, definition: dict, drive: HMDrive)
    def resolve(self, max_depth: int = 10) -> List[Media]
    def validate_dag(self) -> bool
    def to_file(self, path: Path)
    @staticmethod
    def from_file(path: Path, drive: HMDrive) -> 'Composite'
```

**Format .hm (YAML)** :
```yaml
type: composite
version: 1.0
layout: grid
components:
  - uri: hm://local/collection1/media1
    position: [0, 0]
    duration: 5s
  - uri: hm://local/collection1/media2
    position: [1, 0]
```

### API HM-Scene

```python
class Scene:
    def __init__(self, collection: Collection, dss: str)
    def render(self, target: str) -> dict
    def apply_filter(self, filter: dict)
    def paginate(self, page: int, per_page: int) -> List[Media]

class DSSParser:
    def parse(self, dss_content: str) -> SceneDefinition
    def validate(self, dss_content: str) -> List[Error]
```

---

## 5. Technologies et Dépendances

### Core
- Python 3.10+ (match statements, type hints)
- SQLite 3.35+ / PostgreSQL 13+
- SQLAlchemy 2.0+

### Médias
- Pillow 10+ (images)
- opencv-python 4+ (vidéos)
- ffmpeg-python (transcoding)

### Réseau
- FastAPI 0.100+ (API REST)
- aiohttp 3.9+ (client async)
- websockets 11+ (temps réel)

### Parsing
- lark-parser 1.1+ (HM-DSS)
- pyparsing 3.1+ (alternative)

### Graphe
- networkx 3.1+

### Monitoring
- structlog 23+ (logs structurés)
- prometheus-client 0.17+

### Tests
- pytest 7.4+
- pytest-asyncio 0.21+
- pytest-cov 4.1+

---

## 6. Sécurité

### Mesures de sécurité

- **Validation de chemins** : interdiction `../` (path traversal)
- **Transactions SQL atomiques** : rollback automatique en cas d'échec
- **TLS 1.3** : chiffrement pour synchronisation réseau
- **JWT** : authentification pour API REST
- **Rate limiting** : protection contre les abus
- **Sanitization** : nettoyage des entrées utilisateur

### Gestion des checksums

```python
def compute_checksum(file_path: Path) -> str:
    """BLAKE2b hash (128 hex chars)"""
    import hashlib
    hasher = hashlib.blake2b()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
```

---

## 7. Gestion du Cache

### Architecture

```python
class CacheManager:
    def __init__(self, cache_dir: Path, max_size: int = 10 * 1024**3)
    def get(self, key: str) -> Optional[any]
    def set(self, key: str, value: any, ttl: Optional[int] = None)
    def evict_lru(self)
```

**Niveaux de cache** :
- **L1** : Mémoire (LRU, 100MB max)
- **L2** : Disque local (thumbnails, métadonnées, 10GB max)

**Politique d'éviction** : LRU avec priorité aux médias locaux

---

## 8. Exemple d'Utilisation Complet

```python
from hypermedia import HMDrive, SyncManager, Scene, SyncMode
from pathlib import Path

# Initialisation
drive = HMDrive(Path('/data/hypermedia'))

# Création collection et import
collection = drive.create_collection('landscapes')
for img_path in Path('/photos').glob('*.jpg'):
    drive.add_media(collection.id, img_path)

# Recherche
results = drive.search('sunset mountains', collections=['landscapes'])

# Synchronisation
sync_mgr = SyncManager(drive)
sub_id = sync_mgr.subscribe(
    remote_uri='hm://backup-server.local',
    collections=['landscapes'],
    mode=SyncMode.BIDIRECTIONAL
)
sync_mgr.sync_now(sub_id)

# Création d'une scène
scene = Scene(collection, dss_content='''
    @scene gallery {
        layout: grid;
        columns: 4;
    }
    media[tag~="featured"] {
        grid-column: span 2;
    }
''')
rendered = scene.render(target='html')
```

---

## Conclusion

Cette architecture technique fournit une base solide pour le développement de la librairie Hypermedia, avec une séparation claire des responsabilités, des API bien définies et une extensibilité permettant d'évoluer vers les fonctionnalités avancées décrites dans la roadmap.
