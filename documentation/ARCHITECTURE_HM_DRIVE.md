# Architecture HM-Drive - Système de Stockage Distribué

## Introduction

HM-Drive est le système de fichiers distribué au cœur d'Hypermedia. Il fournit une infrastructure résiliente pour le stockage, la synchronisation et l'accès aux médias sur des instances locales et distantes.

### Inspirations architecturales

- **Git** : versioning, delta sync, intégrité par checksums
- **Syncthing** : synchronisation P2P, résilience, décentralisation
- **IPFS** : adressage par contenu (content-addressable storage)
- **Dropbox/Drive** : synchronisation sélective, cache local

### Objectifs clés

1. **Résilience** : fonctionnement en mode dégradé lors de déconnexions
2. **Performance** : cache intelligent, transferts incrémentaux
3. **Intégrité** : vérification cryptographique (BLAKE2b)
4. **Portabilité** : compatible Linux, macOS, Windows

---

## Architecture de l'Instance

### Structure d'une instance HM-Drive

```
instance_root/
├── config.yaml           # Configuration instance
├── database.db           # SQLite avec métadonnées
├── cache/                # Cache local
│   ├── thumbnails/
│   │   ├── 128x128/
│   │   ├── 256x256/
│   │   └── 512x512/
│   └── metadata/
├── collections/          # Dossier principal (médias locaux)
│   ├── collection1/
│   │   ├── media001.jpg
│   │   ├── media002.mp4
│   │   └── .index        # Index local (optionnel)
│   └── collection2/
└── subscriptions/        # Copies locales des abonnements
    ├── remote1_collection_a/
    └── remote2_collection_b/
```

### Fichier config.yaml

```yaml
instance:
  id: "local-instance-uuid"
  name: "My Workstation"
  uri: "hm://localhost:8080"
  type: "local"

storage:
  root: "/data/hypermedia"
  max_size: "500GB"
  cache_size: "10GB"

network:
  listen_address: "0.0.0.0"
  listen_port: 8080
  tls_enabled: true
  cert_path: "certs/server.crt"
  key_path: "certs/server.key"

subscriptions:
  auto_sync: true
  sync_interval: 900  # secondes (15min)
  conflict_strategy: "last_write_wins"
  bandwidth_limit: "10MB/s"

media:
  supported_formats:
    images: ["jpg", "jpeg", "png", "webp", "gif"]
    videos: ["mp4", "webm", "mov", "avi"]
    audio: ["mp3", "wav", "flac", "ogg"]
  generate_thumbnails: true
  thumbnail_sizes: [128, 256, 512]
  compute_checksums: true
```

---

## Modèle de Collections

### Structure arborescente

Les collections forment une hiérarchie arborescente illimitée :

```
root
├── projects/
│   ├── 2024/
│   │   ├── january/
│   │   ├── february/
│   │   └── march/
│   └── 2025/
├── archive/
└── shared/
    ├── public/
    └── private/
```

### Métadonnées de collection

```json
{
  "id": "uuid",
  "name": "January 2024",
  "path": "projects/2024/january",
  "parent_id": "uuid-parent",
  "description": "Photos et vidéos du mois de janvier",
  "icon": "📸",
  "tags": ["work", "2024"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-31T23:59:59Z",
  "media_count": 342,
  "total_size_bytes": 4294967296
}
```

### Liens symboliques virtuels

Stockage en base de données (pas de vrais symlinks système) :

```python
# Création d'un lien
drive.create_link(
    source="portraits/favorites",
    target="archive/2024/best-of",
    type="alias"
)

# Accès transparent
media_list = drive.list_media("portraits/favorites")
# → Liste les médias de "archive/2024/best-of"
```

**Types de liens** :
- `alias` : rédirection complète (comme un symlink)
- `shortcut` : accès rapide (conserve l'identité source)
- `related` : association sémantique (suggestion)

---

## Système d'URI Unifié

### Format canonique

```
hm://[instance]/[collection_path]/[media_id][#fragment][?params]
```

### Composants

| Composant | Description | Exemple |
|-----------|-------------|----------|
| `instance` | Nom ou adresse de l'instance | `local`, `server.com`, `192.168.1.100:8080` |
| `collection_path` | Chemin hiérarchique | `projects/2024/january` |
| `media_id` | Identifiant unique (UUID ou checksum tronqué) | `abc123def456` |
| `fragment` | Référence temporelle/spatiale | `#t=30s`, `#xywh=100,200,300,400` |
| `params` | Paramètres additionnels | `?quality=high&format=webp` |

### Exemples d'URI

```
# Média local
hm://local/landscapes/mountain001

# Média distant
hm://studio.example.com:8080/shared/video.mp4

# Avec fragment temporel (vidéo)
hm://local/tutorials/demo.mp4#t=30s,45s

# Avec fragment spatial (image)
hm://local/photos/panorama.jpg#xywh=100,200,300,400

# Composant d'un composite
hm://local/projects/composite_main#component=2

# Avec paramètres
hm://local/portraits/photo.jpg?quality=high&thumbnail=256
```

### Résolution d'URI

```python
from hypermedia import URIResolver

resolver = URIResolver(drive)

# Parsing
components = resolver.parse("hm://local/projects/abc123#t=30s")
# → URIComponents(instance='local', collection='projects', 
#                   media_id='abc123', fragment='t=30s')

# Résolution
media = resolver.resolve("hm://local/projects/abc123")
# → Objet Media avec path, métadonnées, etc.

# Construction
uri = resolver.build_uri(
    instance="server.com",
    collection="shared/videos",
    media_id="xyz789",
    fragment="t=10s"
)
# → "hm://server.com/shared/videos/xyz789#t=10s"
```

---

## Architecture Distribuée

### Types d'instances

**Instance principale (primary)**
- Référence canonique pour certaines collections
- Gère les modifications maîtresses
- Peut servir plusieurs instances secondaires

**Instance secondaire (secondary)**
- Abonnée à une ou plusieurs instances principales
- Mode lecture seule ou lecture-écriture selon config
- Synchronisation pull (réception uniquement)

**Instance pair (peer)**
- Égalité avec d'autres pairs
- Synchronisation bidirectionnelle
- Pas de hiérarchie

### Topologies supportées

**Étoile (Star)**
```
      Primary
     /   |   \
   S1   S2   S3
```
Une instance principale, N secondaires en pull.

**Maillée (Mesh)**
```
   P1 ——— P2
    |    X    |
   P3 ——— P4
```
Instances pairs avec sync bidirectionnelle.

**Hybride**
```
     Primary
     /     \
   P1  —  P2
    |       |
   S1      S2
```
Combinaison étoile + maillage.

### Découverte d'instances

**Méthode manuelle**
```yaml
subscriptions:
  - name: "Studio Server"
    uri: "hm://studio.example.com:8080"
    collections: ["projects/*", "assets"]
```

**Découverte mDNS/Zeroconf (LAN)**
```python
from hypermedia.network import InstanceDiscovery

discovery = InstanceDiscovery()
instances = discovery.scan(timeout=5)
# → [{'name': 'MacBook-Pro', 'uri': 'hm://192.168.1.50:8080'}, ...]
```

**Registry centralisé (optionnel)**
```python
registry = InstanceRegistry("https://registry.hypermedia.io")
registry.register(drive.instance)
instances = registry.search(tags=["studio", "public"])
```

---

## Abonnements (Subscriptions)

### Modes d'abonnement

**Pull (mono-directionnel Local ← Remote)**
- Instance locale récupère depuis distante
- Lecture seule sur la source
- Cas d'usage : backup, mirror, consultation

**Push (mono-directionnel Local → Remote)**
- Instance locale envoie vers distante
- Mise à jour distante automatique
- Cas d'usage : publication, deployment

**Sync (bi-directionnel Local ↔ Remote)**
- Synchronisation complète dans les 2 sens
- Gestion des conflits nécessaire
- Cas d'usage : collaboration, multi-device

### Configuration d'abonnement

```yaml
subscription:
  name: "Studio Sync"
  remote_uri: "hm://studio.example.com:8080"
  collections:
    - "projects/2024"
    - "assets/shared"
  mode: sync  # pull | push | sync
  schedule: "*/15 * * * *"  # Cron: toutes les 15min
  conflict_strategy: last_write_wins
  bandwidth_limit: "10MB/s"
  filters:
    include_tags: ["published", "approved"]
    exclude_tags: ["draft", "private"]
    min_size: "100KB"
    max_size: "100MB"
```

### Création programmatique

```python
from hypermedia import SyncManager, SyncMode, ConflictStrategy

sync_mgr = SyncManager(drive)

sub_id = sync_mgr.subscribe(
    remote_uri="hm://backup-server.local",
    collections=["projects/2024", "archive"],
    mode=SyncMode.BIDIRECTIONAL,
    schedule="0 * * * *",  # Toutes les heures
    conflict_strategy=ConflictStrategy.MERGE_METADATA,
    config={
        "bandwidth_limit": "5MB/s",
        "include_tags": ["important"],
        "retry_on_error": True,
        "max_retries": 3
    }
)

# Synchronisation immédiate
result = sync_mgr.sync_now(sub_id)
print(f"Ajoutés: {result.media_added}, Mis à jour: {result.media_updated}")
```

---

## Synchronisation et Résilience

### Algorithme de synchronisation

**Phase 1 : Discovery (Découverte)**
```python
# Récupération liste distante
remote_media = client.list_media(collection_id, with_checksums=True)

# Comparaison avec liste locale
local_media = drive.list_media(collection_id)

# Identification des différences
deltas = calculate_deltas(local_media, remote_media)
# → [{'action': 'add', 'media': ...}, {'action': 'update', ...}]
```

**Phase 2 : Delta Calculation (Calcul des différences)**
```python
def calculate_deltas(local, remote):
    local_by_checksum = {m.checksum: m for m in local}
    remote_by_checksum = {m.checksum: m for m in remote}
    
    deltas = []
    
    # Ajouts (présent remote, absent local)
    for checksum, media in remote_by_checksum.items():
        if checksum not in local_by_checksum:
            deltas.append({'action': 'add', 'media': media})
    
    # Mises à jour (checksums identiques, métadonnées différentes)
    for checksum in set(local_by_checksum) & set(remote_by_checksum):
        local_m = local_by_checksum[checksum]
        remote_m = remote_by_checksum[checksum]
        if local_m.updated_at < remote_m.updated_at:
            deltas.append({'action': 'update', 'media': remote_m})
    
    # Suppressions (présent local, absent remote)
    for checksum in set(local_by_checksum) - set(remote_by_checksum):
        deltas.append({'action': 'delete', 'checksum': checksum})
    
    return deltas
```

**Phase 3 : Transfer (Transfert)**
- Transfert des fichiers manquants (rsync-like)
- Compression à la volée (zstd)
- Vérification checksums après transfert
- Barre de progression

**Phase 4 : Reconciliation (Réconciliation)**
- Application atomique des changements
- Mise à jour base de données
- Invalidation du cache
- Logs de synchronisation

### Gestion des conflits

**Stratégies disponibles**

**1. Last Write Wins**
```python
def resolve_last_write_wins(local, remote):
    return remote if remote.updated_at > local.updated_at else local
```

**2. Merge Metadata (fusion intelligente)**
```python
def resolve_merge_metadata(local, remote):
    merged = local.copy()
    merged.tags = list(set(local.tags + remote.tags))  # Union
    merged.descriptors = local.descriptors + remote.descriptors
    merged.updated_at = max(local.updated_at, remote.updated_at)
    return merged
```

**3. Version Both (conservation des 2 versions)**
```python
def resolve_version_both(local, remote):
    # Renommer le local
    local.filename = f"{local.stem}_local{local.suffix}"
    # Garder le remote avec nom original
    return [local, remote]
```

**4. Manual (résolution manuelle)**
```python
def resolve_manual(local, remote):
    raise ManualResolutionRequired({
        'local': local,
        'remote': remote,
        'diff': compute_diff(local, remote)
    })
```

### Mode déconnecté

**Queue de synchronisation**
```python
class SyncQueue:
    def enqueue(self, subscription_id, operation, data):
        """Ajoute une opération à la queue persistante"""
        db.add_to_sync_queue(
            subscription_id=subscription_id,
            operation=operation,  # 'add', 'update', 'delete'
            target_uri=data['uri'],
            data_json=json.dumps(data),
            status='pending'
        )
    
    def process_queue(self, subscription_id):
        """Traite toutes les opérations en attente"""
        operations = db.get_sync_queue(subscription_id, status='pending')
        
        for op in operations:
            try:
                execute_operation(op)
                db.update_sync_queue_status(op.id, 'success')
            except NetworkError:
                # Retry plus tard
                op.attempts += 1
                if op.attempts >= op.max_attempts:
                    db.update_sync_queue_status(op.id, 'failed')
```

**Détection de reconnexion**
```python
from hypermedia.network import NetworkMonitor

monitor = NetworkMonitor()

@monitor.on_reconnect
def handle_reconnect():
    print("Réseau rétabli, traitement de la queue...")
    for sub in drive.get_active_subscriptions():
        sync_mgr.queue.process_queue(sub.id)
```

---

## Cache Local

### Architecture du cache

```
cache/
├── thumbnails/
│   ├── 128x128/
│   │   └── [checksum_8_premiers_chars].jpg
│   ├── 256x256/
│   └── 512x512/
├── metadata/
│   └── [checksum].json
└── previews/
    └── [checksum]_preview.mp4
```

### Politique de cache

```python
class CacheManager:
    def __init__(self, cache_dir, max_size=10*1024**3):  # 10GB
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.lru = LRUCache()
    
    def evict_if_needed(self):
        current_size = get_directory_size(self.cache_dir)
        if current_size > self.max_size:
            # Éviction LRU
            while current_size > self.max_size * 0.9:  # 90%
                oldest = self.lru.pop_oldest()
                if oldest.is_local:
                    continue  # Ne jamais évincer les médias locaux
                os.remove(oldest.path)
                current_size -= oldest.size
```

### Pré-fetching intelligent

```python
def prefetch_adjacent_media(current_media_id, collection_id, count=5):
    """
    Précharge les médias adjacents pour navigation fluide.
    """
    media_list = drive.list_media(collection_id)
    current_index = media_list.index_of(current_media_id)
    
    # Précharger count médias avant et après
    for i in range(max(0, current_index - count), 
                   min(len(media_list), current_index + count + 1)):
        media = media_list[i]
        if not cache.has(media.checksum):
            cache.prefetch(media, priority='low')
```

---

## Performance et Optimisation

### Indexation

```sql
-- Index critiques pour performance
CREATE UNIQUE INDEX idx_media_checksum ON media(checksum);
CREATE INDEX idx_media_collection ON media_collections(collection_id);
CREATE INDEX idx_media_created ON media(created_at DESC);
CREATE INDEX idx_tags_name ON tags(name);

-- Index full-text (SQLite FTS5)
CREATE VIRTUAL TABLE media_fts USING fts5(
    media_id UNINDEXED,
    filename,
    metadata_text
);
```

### Parallélisation

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def batch_import_media(file_paths, collection_id, workers=4):
    """
    Import parallèle de médias.
    """
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(drive.add_media, collection_id, path): path
            for path in file_paths
        }
        
        results = []
        for future in as_completed(futures):
            try:
                media = future.result()
                results.append(media)
            except Exception as e:
                print(f"Erreur import {futures[future]}: {e}")
        
        return results
```

### Benchmarks cibles

| Opération | Cible | Mesure |
|-----------|-------|--------|
| Import 1000 images (10MB avg) | < 30s | Avec checksums + thumbnails |
| Scan collection 10k médias | < 2s | Liste avec métadonnées de base |
| Sync 10GB (LAN 1Gbps) | < 5min | Delta sync, compression |
| Recherche full-text sur 100k | < 100ms | Avec FTS5 indexé |
| Génération thumbnail | < 500ms | Image 4K → 256x256 |

---

## Héritage de prompt-imagine

### Concepts réutilisés

✅ **Checksums BLAKE2b** : détection de doublons, intégrité  
✅ **Collections arborescentes** : organisation hiérarchique  
✅ **Thumbnails multi-résolution** : performance affichage  
✅ **Métadonnées enrichies** : prompts → définisseurs pondérés  
✅ **Orphan manager** : détection et correction incohérences  
✅ **Transactions atomiques** : robustesse des opérations  

### Améliorations apportées

✨ **Distribution et synchronisation** : multi-instances (nouveau)  
✨ **URI unifiés** : adressage global (nouveau)  
✨ **Cache multi-niveaux** : performance accès distants (nouveau)  
✨ **Mode déconnecté résilient** : queue persistante (nouveau)  
✨ **Liens symboliques virtuels** : navigation flexible (nouveau)  
✨ **API REST standardisée** : interopérabilité (nouveau)  

---

## Conclusion

L'architecture HM-Drive fournit une infrastructure solide pour le stockage et la synchronisation distribuée de médias. La combinaison de checksums cryptographiques, d'une synchronisation incrémentale intelligente et d'un cache multi-niveaux garantit à la fois **performance** et **résilience**.

Les concepts éprouvés de prompt-imagine (checksums, collections, métadonnées enrichies) sont préservés et étendus avec des capacités de distribution moderne, faisant d'HM-Drive une solution adaptée aux workflows collaboratifs et multi-devices.

**Prochaine étape** : Architecture HM-Scene pour la mise en scène et la navigation dynamique.
