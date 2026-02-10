# Quick Start - Hypermedia en 5 minutes

Ce guide vous montre comment utiliser les fonctionnalités de base d'Hypermedia.

---

## 1. Configuration initiale

```python
from pathlib import Path
from hypermedia.drive import DatabaseManager, MediaCollection

# Définir les chemins
storage_path = Path("./my_hypermedia_storage")
db_path = Path("./hypermedia.db")

# Initialiser la base de données
db = DatabaseManager(db_path)

# Créer le gestionnaire de collections
collection = MediaCollection(storage_path, db)

print("✓ Hypermedia initialisé !")
```

---

## 2. Créer votre première collection

```python
# Créer une collection
collection_id = collection.create_collection(
    name="Mes Photos de Vacances",
    description="Photos de voyage 2025-2026"
)

print(f"✓ Collection créée : {collection_id}")
```

---

## 3. Ajouter des médias

```python
# Ajouter un fichier image
photo_path = Path("/path/to/your/photo.jpg")

media_id = collection.add_media_to_collection(
    collection_id,
    photo_path,
    copy_file=True  # Copie le fichier dans le storage
)

print(f"✓ Média ajouté : {media_id}")
```

### Ajouter avec métadonnées personnalisées

```python
media_id = collection.add_media_to_collection(
    collection_id,
    photo_path,
    custom_metadata={
        "tags": ["plage", "sunset", "amis"],
        "location": "Marseille, France",
        "rating": 5,
        "favorite": True
    }
)
```

---

## 4. Rechercher des médias

### Recherche simple

```python
# Tous les médias d'une collection
results = collection.search(collection_id=collection_id)

for media in results:
    print(f"- {media['filename']} ({media['size']} bytes)")
```

### Recherche avec filtres

```python
# Rechercher par métadonnées
results = collection.search(
    collection_id=collection_id,
    metadata_filters={
        "custom.rating": "5",
        "custom.favorite": "True"
    }
)

print(f"Trouvé {len(results)} favoris avec rating 5")
```

### Recherche textuelle

```python
# Rechercher dans les noms de fichiers
results = collection.search(query="sunset")
```

### Pagination

```python
# Première page (10 résultats)
page1 = collection.search(limit=10, offset=0)

# Deuxième page
page2 = collection.search(limit=10, offset=10)
```

---

## 5. Accéder aux informations d'un média

```python
# Récupérer les informations complètes
info = collection.get_media_info(media_id)

print(f"Nom: {info['original_filename']}")
print(f"Taille: {info['size']} bytes")
print(f"Type MIME: {info['mime_type']}")
print(f"Checksum: {info['checksum']}")

# Métadonnées
for key, value in info['metadata'].items():
    print(f"  {key}: {value}")

# Collections associées
for coll in info['collections']:
    print(f"Dans la collection: {coll['name']}")
```

---

## 6. Métadonnées automatiques

Hypermedia extrait automatiquement les métadonnées des fichiers :

### Images (EXIF)

```python
info = collection.get_media_info(photo_id)

# Données EXIF extraites automatiquement
if 'exif.Make' in info['metadata']:
    print(f"Caméra: {info['metadata']['exif.Make']}")
if 'exif.DateTime' in info['metadata']:
    print(f"Date: {info['metadata']['exif.DateTime']}")
```

### Audio (ID3)

```python
# Ajouter un fichier audio
audio_id = collection.add_media_to_collection(
    collection_id,
    Path("/path/to/song.mp3")
)

info = collection.get_media_info(audio_id)

print(f"Titre: {info['metadata'].get('audio.title', 'Inconnu')}")
print(f"Artiste: {info['metadata'].get('audio.artist', 'Inconnu')}")
print(f"Durée: {info['metadata'].get('audio.duration', 0)} secondes")
```

---

## 7. Gérer les collections

### Lister toutes les collections

```python
collections = collection.list_collections()

for coll in collections:
    print(f"{coll['name']}: {coll['media_count']} médias")
```

### Récupérer une collection spécifique

```python
coll_info = collection.get_collection(collection_id)

print(f"Nom: {coll_info['name']}")
print(f"Description: {coll_info['description']}")
print(f"Créée le: {coll_info['created_at']}")
print(f"Nombre de médias: {coll_info['media_count']}")
```

---

## 8. Déduplication automatique

Hypermedia détecte automatiquement les doublons :

```python
# Ajouter le même fichier deux fois
media_id_1 = collection.add_media_to_collection(
    collection_id,
    Path("/path/to/photo.jpg")
)

media_id_2 = collection.add_media_to_collection(
    collection_id,
    Path("/path/to/photo.jpg")  # Même fichier
)

# Les deux IDs sont identiques (déduplication)
print(f"Même fichier détecté: {media_id_1 == media_id_2}")
```

---

## 9. Supprimer des médias

```python
# Supprimer de la base (garder le fichier)
collection.delete_media(media_id, remove_file=False)

# Supprimer complètement (base + fichier)
collection.delete_media(media_id, remove_file=True)
```

---

## 10. Fermer proprement

```python
# Toujours fermer la base de données
db.close()

print("✓ Session terminée")
```

---

## Exemple complet

Voici un script complet de démonstration :

```python
from pathlib import Path
from hypermedia.drive import DatabaseManager, MediaCollection

def main():
    # Configuration
    storage_path = Path("./my_media")
    db_path = Path("./hypermedia.db")
    
    # Initialisation
    db = DatabaseManager(db_path)
    coll = MediaCollection(storage_path, db)
    
    try:
        # Créer une collection
        coll_id = coll.create_collection(
            "Ma Bibliothèque Média",
            "Collection principale de mes médias"
        )
        print(f"✓ Collection créée: {coll_id}")
        
        # Ajouter des fichiers
        files = [
            Path("/path/to/photo1.jpg"),
            Path("/path/to/photo2.jpg"),
            Path("/path/to/video.mp4"),
            Path("/path/to/song.mp3")
        ]
        
        for file_path in files:
            if file_path.exists():
                media_id = coll.add_media_to_collection(
                    coll_id,
                    file_path,
                    custom_metadata={"imported": True}
                )
                print(f"✓ Ajouté: {file_path.name}")
        
        # Rechercher et afficher
        results = coll.search(collection_id=coll_id)
        print(f"\n✓ {len(results)} médias dans la collection")
        
        for media in results:
            print(f"  - {media['filename']} ({media['mime_type']})")
    
    finally:
        # Fermeture
        db.close()
        print("\n✓ Session terminée")

if __name__ == "__main__":
    main()
```

---

## Prochaines étapes

Vous maîtrisez maintenant les bases ! Explorez :

- **[Référence API complète](api_reference.md)** : Toutes les méthodes disponibles
- **[Exemples avancés](../examples/)** : Cas d'usage complexes
- **[Architecture](architecture.md)** : Comprendre le fonctionnement interne

---

**Besoin d'aide ?** Consultez la [documentation complète](README.md) ou ouvrez une [issue GitHub](https://github.com/TristanV/hypermedia/issues).
