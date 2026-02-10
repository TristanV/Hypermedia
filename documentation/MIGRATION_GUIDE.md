# Guide de Migration : prompt-imagine → Hypermedia

## Introduction

Ce guide détaille la migration d'une installation **prompt-imagine** existante vers **Hypermedia**. La migration préserve l'intégralité de vos données tout en les enrichissant avec les nouvelles capacités d'Hypermedia.

### Garanties de migration

✅ **Intégrité** : Aucune perte de données (médias, métadonnées, relations)  
✅ **Réversibilité** : Possibilité de revenir à prompt-imagine si besoin  
✅ **Incrémentalité** : Migration progressive, collection par collection  
✅ **Validation** : Vérifications automatiques de cohérence  

---

## Mapping Conceptuel

### Correspondances directes

| prompt-imagine | Hypermedia | Notes |
|----------------|------------|-------|
| **Project** | **Collection** | Hiérarchie arborescente supportée |
| **Image** | **Media** | Support multi-formats (image, video, audio) |
| **Checksum (BLAKE2b)** | **Checksum (BLAKE2b)** | Identique, aucune reconversion |
| **Prompt** | **Descriptor** | Pondération ajoutée (weight: 0.0-10.0) |
| **Tags** | **Tags** | Catégorisation ajoutée |
| **Parent-Child relations** | **Relationship (parent/child)** | Graphe étendu avec types multiples |
| **Thumbnails** | **Thumbnails** | Multi-résolutions (128, 256, 512px) |

### Concepts nouveaux dans Hypermedia

✨ **Instances** : support multi-instances distantes  
✨ **URI** : adressage global `hm://instance/collection/media_id`  
✨ **Subscriptions** : synchronisation inter-instances  
✨ **Composites** : hypermedia récursifs  
✨ **Scenes** : mise en scène via HM-DSS  
✨ **Relations typées** : similar, derived, reference, etc.  

---

## Schéma de Migration

### Vue d'ensemble

```
prompt-imagine/           Hypermedia/
├── projects/          →  ├── collections/
│   ├── project1/      │   ├── project1/
│   └── project2/      │   └── project2/
├── database.db       →  ├── database.db (nouveau schéma)
├── thumbnails/       →  ├── cache/thumbnails/
└── config.yaml       →  └── config.yaml (nouveau format)
```

### Mapping des tables SQL

#### Table `projects` → `collections`

```sql
-- prompt-imagine
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL
);

-- Hypermedia
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    parent_id TEXT,              -- Nouveau: hiérarchie
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    description TEXT,            -- Nouveau
    icon TEXT,                   -- Nouveau
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    metadata_json TEXT,          -- Nouveau
    FOREIGN KEY (instance_id) REFERENCES instances(id),
    FOREIGN KEY (parent_id) REFERENCES collections(id)
);
```

**Conversion** :
```python
for project in prompt_imagine_db.get_all_projects():
    collection = hypermedia_db.create_collection(
        id=project.id,                    # Conserver ID
        instance_id='local',              # Instance locale
        parent_id=None,                   # Racine
        name=project.name,
        path=project.path,
        description='',
        icon='📸'
    )
```

#### Table `images` → `media`

```sql
-- prompt-imagine
CREATE TABLE images (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    checksum TEXT NOT NULL,
    filename TEXT NOT NULL,
    size INTEGER,
    width INTEGER,
    height INTEGER
);

-- Hypermedia
CREATE TABLE media (
    id TEXT PRIMARY KEY,
    checksum TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT,      -- Nouveau
    size INTEGER NOT NULL,
    format TEXT NOT NULL,        -- Nouveau
    mime_type TEXT NOT NULL,     -- Nouveau
    width INTEGER,
    height INTEGER,
    duration REAL,               -- Nouveau (vidéos)
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    imported_at TIMESTAMP,
    metadata_json TEXT           -- Nouveau
);
```

**Conversion** :
```python
import mimetypes
from pathlib import Path

for image in prompt_imagine_db.get_all_images():
    path = Path(image.filename)
    mime_type, _ = mimetypes.guess_type(str(path))
    
    media = hypermedia_db.create_media(
        id=image.id,                      # Conserver ID
        checksum=image.checksum,          # Checksum identique
        filename=image.filename,
        original_filename=image.filename,
        size=image.size,
        format=path.suffix.lower()[1:],   # "jpg", "png"
        mime_type=mime_type or 'image/jpeg',
        width=image.width,
        height=image.height,
        duration=None
    )
    
    # Association collection
    hypermedia_db.add_media_to_collection(media.id, image.project_id)
```

#### Table `prompts` → `descriptors`

```sql
-- prompt-imagine
CREATE TABLE prompts (
    id TEXT PRIMARY KEY,
    image_id TEXT,
    text TEXT NOT NULL
);

-- Hypermedia
CREATE TABLE descriptors (
    id TEXT PRIMARY KEY,
    media_id TEXT NOT NULL,
    type TEXT NOT NULL,          -- Nouveau: 'prompt', 'style', 'quality'
    text TEXT NOT NULL,
    weight REAL DEFAULT 1.0,     -- Nouveau: pondération
    category TEXT,               -- Nouveau
    language TEXT DEFAULT 'en',  -- Nouveau
    created_at TIMESTAMP,
    FOREIGN KEY (media_id) REFERENCES media(id)
);
```

**Conversion** :
```python
for prompt in prompt_imagine_db.get_all_prompts():
    descriptor = hypermedia_db.create_descriptor(
        id=prompt.id,
        media_id=prompt.image_id,
        type='prompt',               # Par défaut
        text=prompt.text,
        weight=1.0,                  # Poids par défaut
        category='generation',
        language='en'
    )
```

#### Table `parent_child` → `relationships`

```sql
-- prompt-imagine
CREATE TABLE parent_child (
    parent_id TEXT,
    child_id TEXT,
    PRIMARY KEY (parent_id, child_id)
);

-- Hypermedia
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,          -- Nouveau: 'parent', 'child', 'similar'
    strength REAL DEFAULT 1.0,   -- Nouveau: force relation
    metadata_json TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES media(id),
    FOREIGN KEY (target_id) REFERENCES media(id)
);
```

**Conversion** :
```python
import uuid

for relation in prompt_imagine_db.get_all_parent_child():
    # Créer relation parent → child
    hypermedia_db.create_relationship(
        id=str(uuid.uuid4()),
        source_id=relation.parent_id,
        target_id=relation.child_id,
        type='parent',
        strength=1.0
    )
    
    # Créer relation inverse child → parent
    hypermedia_db.create_relationship(
        id=str(uuid.uuid4()),
        source_id=relation.child_id,
        target_id=relation.parent_id,
        type='child',
        strength=1.0
    )
```

---

## Script de Migration Automatisé

### Installation

```bash
# Installation d'Hypermedia
pip install hypermedia

# Ou depuis les sources
git clone https://github.com/TristanV/Hypermedia.git
cd Hypermedia
pip install -e .
```

### Commande de migration

```bash
# Migration complète
hm migrate \
  --from /path/to/prompt-imagine \
  --to /path/to/hypermedia \
  --verify \
  --backup

# Migration sélective (1 projet)
hm migrate \
  --from /path/to/prompt-imagine \
  --to /path/to/hypermedia \
  --project "landscapes" \
  --verify

# Dry-run (simulation)
hm migrate \
  --from /path/to/prompt-imagine \
  --to /path/to/hypermedia \
  --dry-run
```

### Script Python

```python
from hypermedia.migration import PromptImagineMigrator
from pathlib import Path

# Initialisation
migrator = PromptImagineMigrator(
    source_path=Path('/data/prompt-imagine'),
    target_path=Path('/data/hypermedia')
)

# Analyse de la source
stats = migrator.analyze_source()
print(f"Projets: {stats['projects_count']}")
print(f"Images: {stats['images_count']}")
print(f"Taille totale: {stats['total_size_gb']:.2f} GB")

# Backup (recommandé)
backup_path = migrator.create_backup()
print(f"Backup créé: {backup_path}")

# Migration
result = migrator.migrate(
    verify=True,               # Vérification post-migration
    preserve_timestamps=True,  # Conserver dates originales
    progress_callback=print    # Callback pour progression
)

print(f"Migration terminée:")
print(f"- Collections: {result['collections_migrated']}")
print(f"- Médias: {result['media_migrated']}")
print(f"- Descripteurs: {result['descriptors_migrated']}")
print(f"- Relations: {result['relationships_migrated']}")
print(f"- Erreurs: {len(result['errors'])}")

# Vérification d'intégrité
if result['errors']:
    print("\nErreurs détectées:")
    for error in result['errors']:
        print(f"  - {error}")
else:
    print("\n✅ Migration réussie sans erreurs")
```

---

## Vérifications Post-Migration

### Vérification automatique

```python
from hypermedia.migration import MigrationValidator

validator = MigrationValidator(
    source_path=Path('/data/prompt-imagine'),
    target_path=Path('/data/hypermedia')
)

report = validator.validate_all()

print(f"Checksums valides: {report['checksums_valid']}/{report['checksums_total']}")
print(f"Fichiers présents: {report['files_present']}/{report['files_total']}")
print(f"Métadonnées préservées: {report['metadata_preserved']}")
print(f"Relations intactes: {report['relationships_intact']}")

if report['is_valid']:
    print("\n✅ Toutes les vérifications passées")
else:
    print(f"\n⚠️ {len(report['issues'])} problèmes détectés")
    for issue in report['issues']:
        print(f"  - {issue}")
```

### Vérifications manuelles

**1. Comptage des éléments**
```bash
# prompt-imagine
sqlite3 /data/prompt-imagine/database.db "SELECT COUNT(*) FROM projects;"
sqlite3 /data/prompt-imagine/database.db "SELECT COUNT(*) FROM images;"

# Hypermedia
hm stats
# → Collections: 42
# → Médias: 1337
```

**2. Vérification des checksums**
```bash
# Générer liste des checksums
hm verify --checksums > checksums_hypermedia.txt

# Comparer avec prompt-imagine
diff checksums_prompt_imagine.txt checksums_hypermedia.txt
```

**3. Test de navigation**
```bash
# Lister une collection
hm list landscapes

# Afficher un média avec ses métadonnées
hm show hm://local/landscapes/abc123

# Rechercher
hm search "sunset mountain"
```

---

## Rollback (Retour Arrière)

### Si migration échouée

```bash
# Restauration depuis backup
hm restore --from /path/to/backup --to /data/hypermedia

# Ou simplement supprimer et recommencer
rm -rf /data/hypermedia
mkdir /data/hypermedia
hm migrate --from /data/prompt-imagine --to /data/hypermedia
```

### Retour à prompt-imagine

Si nécessaire, prompt-imagine reste fonctionnel avec ses données originales :

```bash
# Relancer prompt-imagine
cd /data/prompt-imagine
python -m prompt_imagine
```

**Note** : Les modifications faites dans Hypermedia après migration ne seront pas reflétées dans prompt-imagine.

---

## Co-existence Temporaire

### Configuration hybride

Pendant la phase de transition, il est possible de faire coexister les deux systèmes :

```yaml
# config.yaml
mode: hybrid

sources:
  - type: prompt-imagine
    path: /data/prompt-imagine
    mode: read-only
  
  - type: hypermedia
    path: /data/hypermedia
    mode: read-write

sync:
  direction: prompt-imagine → hypermedia
  interval: 3600  # 1 heure
  auto: true
```

Cette configuration permet :
- Continuer à utiliser prompt-imagine (lecture seule)
- Ajouter de nouveaux médias dans Hypermedia
- Synchronisation unidirectionnelle automatique

---

## Cas Particuliers

### Médias orphelins

```python
# Détection
orphans = migrator.find_orphans()
print(f"Médias orphelins: {len(orphans)}")

# Création collection de quarantaine
quarantine = hypermedia.create_collection('_orphans')

for orphan in orphans:
    hypermedia.add_media_to_collection(orphan.id, quarantine.id)
```

### Doublons

```python
# Détection
duplicates = migrator.find_duplicates()
print(f"Groupes de doublons: {len(duplicates)}")

for group in duplicates:
    print(f"Checksum {group['checksum']}: {len(group['media'])} instances")
    
    # Stratégie: conserver le plus récent, lier les autres
    primary = max(group['media'], key=lambda m: m.created_at)
    
    for duplicate in group['media']:
        if duplicate.id != primary.id:
            hypermedia.create_relationship(
                source_id=duplicate.id,
                target_id=primary.id,
                type='duplicate_of'
            )
```

### Checksums manquants

```python
# Recalcul des checksums manquants
media_without_checksum = hypermedia.query(
    "SELECT * FROM media WHERE checksum IS NULL"
)

for media in media_without_checksum:
    file_path = hypermedia.get_media_path(media.id)
    checksum = compute_checksum(file_path)
    
    hypermedia.update_media(media.id, checksum=checksum)
```

---

## Optimisations Post-Migration

### Indexation full-text

```bash
# Reconstruction des index FTS5
hm reindex --verbose
```

### Génération des thumbnails manquants

```bash
# Génération parallèle (8 workers)
hm thumbnails --regenerate --workers 8
```

### Optimisation base de données

```bash
hm optimize --vacuum --analyze
```

---

## FAQ Migration

### Q: La migration modifie-t-elle prompt-imagine ?
**R:** Non, la migration est non destructive. prompt-imagine reste intact.

### Q: Combien de temps prend la migration ?
**R:** Environ 1-2 minutes pour 1000 images (selon la machine). La génération des thumbnails peut prendre plus de temps.

### Q: Puis-je migrer partiellement ?
**R:** Oui, utilisez l'option `--project` pour migrer collection par collection.

### Q: Les dates de création sont-elles préservées ?
**R:** Oui, avec l'option `--preserve-timestamps` (activée par défaut).

### Q: Que faire si la migration échoue ?
**R:** Utilisez le backup automatique pour restaurer, corrigez le problème, et relancez.

### Q: Les thumbnails sont-ils réutilisés ?
**R:** Oui, si les résolutions correspondent (128, 256, 512px). Sinon, ils sont regénérés.

---

## Timeline de Migration Recommandée

**Jour 1-2 : Préparation**
- Installation Hypermedia
- Analyse de l'instance prompt-imagine
- Backup complet
- Dry-run de migration

**Jour 3 : Migration**
- Migration effective
- Vérifications automatiques
- Tests manuels

**Jour 4-7 : Validation**
- Utilisation en parallèle (co-existence)
- Vérification exhaustive des données
- Détection d'éventuels problèmes

**Jour 8+ : Transition complète**
- Basculement définitif vers Hypermedia
- Archive de prompt-imagine (conservation en backup)

---

## Support

En cas de difficulté lors de la migration :

- **Documentation** : https://hypermedia.readthedocs.io
- **Issues GitHub** : https://github.com/TristanV/Hypermedia/issues
- **Discussions** : https://github.com/TristanV/Hypermedia/discussions

---

## Conclusion

La migration de prompt-imagine vers Hypermedia est conçue pour être **sécurisée**, **incrémentale** et **réversible**. Les outils automatisés garantissent la préservation de l'intégralité de vos données tout en ouvrant l'accès aux nouvelles fonctionnalités (distribution, scènes dynamiques, URI globaux).

La coexistence temporaire permet une transition en douceur, et les mécanismes de rollback offrent une sécurité supplémentaire.

**Bonne migration !** 🚀
