#!/usr/bin/env python3
"""Exemple d'utilisation de base de la couche HM-Drive (Phase 1).

Cet exemple montre comment:
1. Initialiser la base de données
2. Créer des collections
3. Ajouter des médias avec checksums BLAKE2b
4. Détecter les doublons
5. Extraire et ajouter des métadonnées
6. Rechercher et organiser les médias
"""

import json
import logging
from pathlib import Path

from hypermedia.drive.checksum import compute_blake2b, verify_integrity
from hypermedia.drive.collection import MediaCollection
from hypermedia.drive.database import DatabaseManager
from hypermedia.drive.deduplication import DeduplicationManager
from hypermedia.drive.metadata_extractor import MetadataExtractor
from hypermedia.drive.models import Collection, MediaItem, Metadata

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_setup():
    """Exemple 1: Configuration de base et initialisation."""
    logger.info("=" * 60)
    logger.info("Exemple 1: Configuration de base")
    logger.info("=" * 60)

    # Création de la base de données
    db_path = Path("./data/hypermedia_example.db")
    db = DatabaseManager(db_path, echo=True)

    logger.info(f"Base de données créée: {db_path}")

    # Création d'une collection
    with db.get_session() as session:
        collection = Collection(
            name="Photos Vacances 2026",
            description="Collection de photos de vacances"
        )
        session.add(collection)
        session.commit()
        logger.info(f"Collection créée: {collection}")

    return db


def example_add_media(db: DatabaseManager, file_path: Path):
    """Exemple 2: Ajout d'un média avec checksum.
    
    Args:
        db: Gestionnaire de base de données
        file_path: Chemin du fichier à ajouter
    """
    logger.info("=" * 60)
    logger.info("Exemple 2: Ajout d'un média")
    logger.info("=" * 60)

    # Calcul du checksum BLAKE2b
    checksum = compute_blake2b(file_path)
    logger.info(f"Checksum BLAKE2b: {checksum}")

    # Vérification de l'intégrité
    is_valid = verify_integrity(file_path, checksum)
    logger.info(f"Intégrité vérifiée: {is_valid}")

    # Ajout à la base de données
    with db.get_session() as session:
        media = MediaItem(
            checksum=checksum,
            path=str(file_path),
            mime_type="image/jpeg",
            size=file_path.stat().st_size,
            original_filename=file_path.name
        )
        session.add(media)
        session.commit()
        logger.info(f"Média ajouté: {media}")
        return media.id


def example_deduplication(db: DatabaseManager, file_path: Path):
    """Exemple 3: Détection de doublons.
    
    Args:
        db: Gestionnaire de base de données
        file_path: Chemin du fichier à vérifier
    """
    logger.info("=" * 60)
    logger.info("Exemple 3: Détection de doublons")
    logger.info("=" * 60)

    dedup_manager = DeduplicationManager(db)

    # Vérification si le fichier existe déjà
    checksum = compute_blake2b(file_path)
    existing = dedup_manager.find_duplicate(checksum)

    if existing:
        logger.info(f"Doublon détecté: {existing}")
    else:
        logger.info("Aucun doublon trouvé")

    return existing


def example_metadata_extraction(db: DatabaseManager, media_id: str, file_path: Path):
    """Exemple 4: Extraction et ajout de métadonnées.
    
    Args:
        db: Gestionnaire de base de données
        media_id: ID du média
        file_path: Chemin du fichier
    """
    logger.info("=" * 60)
    logger.info("Exemple 4: Extraction de métadonnées")
    logger.info("=" * 60)

    # Extraction des métadonnées
    extractor = MetadataExtractor()
    metadata_dict = extractor.extract(file_path)
    logger.info(f"Métadonnées extraites: {json.dumps(metadata_dict, indent=2)}")

    # Ajout dans la base de données
    with db.get_session() as session:
        for key, value in metadata_dict.items():
            metadata = Metadata(
                media_id=media_id,
                key=key,
                value=json.dumps(value) if isinstance(value, (dict, list)) else str(value),
                source="auto"
            )
            session.add(metadata)
        session.commit()
        logger.info(f"{len(metadata_dict)} métadonnées ajoutées")


def example_search_and_organize(db: DatabaseManager):
    """Exemple 5: Recherche et organisation des médias.
    
    Args:
        db: Gestionnaire de base de données
    """
    logger.info("=" * 60)
    logger.info("Exemple 5: Recherche et organisation")
    logger.info("=" * 60)

    with db.get_session() as session:
        # Liste tous les médias
        all_media = session.query(MediaItem).all()
        logger.info(f"Total de médias: {len(all_media)}")

        # Recherche par collection
        collections = session.query(Collection).all()
        for collection in collections:
            logger.info(f"Collection: {collection.name}")
            logger.info(f"  - Nombre de médias: {len(collection.media_items)}")

        # Recherche par métadonnée
        media_with_location = (
            session.query(MediaItem)
            .join(Metadata)
            .filter(Metadata.key.like('exif.gps%'))
            .all()
        )
        logger.info(f"Médias avec localisation GPS: {len(media_with_location)}")


def example_collection_operations(db: DatabaseManager):
    """Exemple 6: Opérations sur les collections.
    
    Args:
        db: Gestionnaire de base de données
    """
    logger.info("=" * 60)
    logger.info("Exemple 6: Opérations sur collections")
    logger.info("=" * 60)

    storage_path = Path("./data/storage")
    collection_manager = MediaCollection(storage_path, db)

    # Création d'une collection
    collection_id = collection_manager.create_collection(
        name="Projets 2026",
        description="Documents et médias pour projets professionnels"
    )
    logger.info(f"Collection créée: {collection_id}")

    # Liste des collections
    collections = collection_manager.list_collections()
    for coll in collections:
        logger.info(f"- {coll['name']}: {coll['description']}")


def main():
    """Fonction principale exécutant tous les exemples."""
    logger.info("Démarrage des exemples Phase 1 - HM-Drive")

    try:
        # Exemple 1: Configuration de base
        db = example_basic_setup()

        # Exemple 6: Opérations sur collections
        example_collection_operations(db)

        # Pour les exemples 2-5, il faudrait un fichier réel
        # Exemple avec un fichier de test (si disponible)
        test_file = Path("./data/test_image.jpg")
        if test_file.exists():
            # Exemple 2: Ajout de média
            media_id = example_add_media(db, test_file)

            # Exemple 3: Détection de doublons
            example_deduplication(db, test_file)

            # Exemple 4: Métadonnées
            example_metadata_extraction(db, media_id, test_file)

        # Exemple 5: Recherche
        example_search_and_organize(db)

        logger.info("\n" + "=" * 60)
        logger.info("Tous les exemples ont été exécutés avec succès!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des exemples: {e}", exc_info=True)
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()
