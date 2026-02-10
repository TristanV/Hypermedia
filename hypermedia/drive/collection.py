"""Gestion des collections de médias.

Ce module implémente la classe MediaCollection qui permet de créer
et gérer des collections de médias avec déduplication automatique.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .checksum import compute_blake2b
from .database import DatabaseManager
from .deduplication import DeduplicationManager
from .metadata_extractor import MetadataExtractor
from .models import Collection, MediaItem, Metadata

logger = logging.getLogger(__name__)


class MediaCollection:
    """Collection de médias avec gestion locale et déduplication.

    Cette classe fournit une interface de haut niveau pour gérer des collections
    de médias stockés localement, avec détection automatique des doublons via
    checksums BLAKE2b et extraction automatique de métadonnées.

    Attributes:
        storage_path: Répertoire racine de stockage
        db: Gestionnaire de base de données
        dedup_manager: Gestionnaire de déduplication
        metadata_extractor: Extracteur de métadonnées

    Example:
        >>> storage = Path("/data/hypermedia")
        >>> db = DatabaseManager(storage / "hypermedia.db")
        >>> collection = MediaCollection(storage, db)
        >>> coll_id = collection.create_collection("Vacances 2026")
        >>> media_id = collection.add_media_to_collection(coll_id, "/photos/beach.jpg")
    """

    def __init__(
        self,
        storage_path: Path,
        db: DatabaseManager,
        auto_extract_metadata: bool = True
    ):
        """Initialise le gestionnaire de collections.

        Args:
            storage_path: Chemin racine de stockage des médias
            db: Instance de DatabaseManager
            auto_extract_metadata: Active l'extraction automatique de métadonnées
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.db = db
        self.dedup_manager = DeduplicationManager(db)
        self.auto_extract_metadata = auto_extract_metadata
        
        if auto_extract_metadata:
            self.metadata_extractor = MetadataExtractor()
        
        logger.info(f"MediaCollection initialized at {storage_path}")

    def create_collection(
        self,
        name: str,
        description: str = ""
    ) -> str:
        """Crée une nouvelle collection.

        Args:
            name: Nom de la collection (doit être unique)
            description: Description optionnelle

        Returns:
            ID de la collection créée

        Raises:
            ValueError: Si une collection avec ce nom existe déjà

        Example:
            >>> coll_id = collection.create_collection(
            ...     "Photos Famille",
            ...     "Photos de famille 2020-2026"
            ... )
        """
        with self.db.get_session() as session:
            # Vérifier si le nom existe déjà
            existing = session.query(Collection).filter_by(name=name).first()
            if existing:
                raise ValueError(f"Collection '{name}' already exists")

            # Créer la collection
            collection = Collection(name=name, description=description)
            session.add(collection)
            session.commit()
            
            logger.info(f"Collection created: {name} (ID: {collection.id})")
            return collection.id

    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une collection.

        Args:
            collection_id: ID de la collection

        Returns:
            Dictionnaire avec les informations de la collection ou None
        """
        with self.db.get_session() as session:
            collection = session.query(Collection).filter_by(id=collection_id).first()
            if not collection:
                return None
            
            return {
                "id": collection.id,
                "name": collection.name,
                "description": collection.description,
                "created_at": collection.created_at.isoformat(),
                "updated_at": collection.updated_at.isoformat(),
                "media_count": len(collection.media_items)
            }

    def list_collections(self) -> List[Dict[str, Any]]:
        """Liste toutes les collections.

        Returns:
            Liste des collections avec leurs informations
        """
        with self.db.get_session() as session:
            collections = session.query(Collection).all()
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "created_at": c.created_at.isoformat(),
                    "media_count": len(c.media_items)
                }
                for c in collections
            ]

    def add_media_to_collection(
        self,
        collection_id: str,
        file_path: Path,
        custom_metadata: Optional[Dict[str, Any]] = None,
        copy_file: bool = True
    ) -> str:
        """Ajoute un média à une collection.

        Le fichier est copié dans le stockage après vérification d'intégrité
        et détection de doublons. Les métadonnées sont extraites automatiquement.

        Args:
            collection_id: ID de la collection cible
            file_path: Chemin du fichier à ajouter
            custom_metadata: Métadonnées personnalisées optionnelles
            copy_file: Si True, copie le fichier dans le stockage

        Returns:
            ID du média ajouté

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si la collection n'existe pas

        Example:
            >>> media_id = collection.add_media_to_collection(
            ...     coll_id,
            ...     Path("/photos/sunset.jpg"),
            ...     custom_metadata={"tags": ["nature", "soirée"]}
            ... )
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Calculer le checksum
        checksum = compute_blake2b(file_path)
        logger.info(f"Computed checksum for {file_path.name}: {checksum[:16]}...")

        with self.db.get_session() as session:
            # Vérifier si la collection existe
            collection = session.query(Collection).filter_by(id=collection_id).first()
            if not collection:
                raise ValueError(f"Collection not found: {collection_id}")

            # Vérifier si un doublon existe
            existing_media = self.dedup_manager.find_duplicate(checksum)
            
            if existing_media:
                logger.info(f"Duplicate detected: {existing_media.id}")
                media = existing_media
                
                # Ajouter à la collection si pas déjà présent
                if media not in collection.media_items:
                    collection.media_items.append(media)
                    session.commit()
                    logger.info(f"Existing media {media.id} added to collection {collection.name}")
            else:
                # Nouveau média - copier le fichier
                if copy_file:
                    dest_path = self._get_storage_path(checksum, file_path.suffix)
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"File copied to {dest_path}")
                else:
                    dest_path = file_path

                # Créer l'entrée MediaItem
                media = MediaItem(
                    checksum=checksum,
                    path=str(dest_path.relative_to(self.storage_path) if copy_file else dest_path),
                    mime_type=self._guess_mime_type(file_path),
                    size=file_path.stat().st_size,
                    original_filename=file_path.name
                )
                session.add(media)
                
                # Ajouter à la collection
                collection.media_items.append(media)
                session.commit()
                logger.info(f"New media {media.id} added to collection {collection.name}")

                # Extraire métadonnées automatiques
                if self.auto_extract_metadata:
                    self._extract_and_save_metadata(session, media.id, file_path)

            # Ajouter métadonnées personnalisées
            if custom_metadata:
                self._save_custom_metadata(session, media.id, custom_metadata)

            return media.id

    def get_media_info(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un média.

        Args:
            media_id: Identifiant du média

        Returns:
            Dictionnaire contenant les informations et métadonnées ou None
        """
        with self.db.get_session() as session:
            media = session.query(MediaItem).filter_by(id=media_id).first()
            if not media:
                return None

            # Compiler les métadonnées
            metadata_dict = {}
            for meta in media.metadata:
                metadata_dict[meta.key] = meta.value

            return {
                "id": media.id,
                "checksum": media.checksum,
                "path": media.path,
                "mime_type": media.mime_type,
                "size": media.size,
                "original_filename": media.original_filename,
                "created_at": media.created_at.isoformat(),
                "updated_at": media.updated_at.isoformat(),
                "collections": [c.name for c in media.collections],
                "metadata": metadata_dict
            }

    def search(
        self,
        collection_id: Optional[str] = None,
        query: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Recherche des médias par métadonnées.

        Args:
            collection_id: Filtrer par collection (optionnel)
            query: Recherche textuelle libre (optionnel)
            metadata_filters: Filtres par métadonnées
            limit: Nombre maximum de résultats
            offset: Offset pour pagination

        Returns:
            Liste des médias correspondant aux critères

        Example:
            >>> results = collection.search(
            ...     collection_id="abc123",
            ...     metadata_filters={"exif.Model": "Canon EOS"},
            ...     limit=50
            ... )
        """
        with self.db.get_session() as session:
            query_obj = session.query(MediaItem)

            # Filtrer par collection
            if collection_id:
                query_obj = query_obj.join(MediaItem.collections).filter(
                    Collection.id == collection_id
                )

            # Filtrer par métadonnées
            if metadata_filters:
                for key, value in metadata_filters.items():
                    query_obj = query_obj.join(MediaItem.metadata).filter(
                        and_(
                            Metadata.key == key,
                            Metadata.value.like(f"%{value}%")
                        )
                    )

            # Recherche textuelle (filename)
            if query:
                query_obj = query_obj.filter(
                    or_(
                        MediaItem.original_filename.like(f"%{query}%"),
                        MediaItem.path.like(f"%{query}%")
                    )
                )

            # Pagination
            results = query_obj.limit(limit).offset(offset).all()

            return [
                {
                    "id": m.id,
                    "filename": m.original_filename,
                    "path": m.path,
                    "size": m.size,
                    "mime_type": m.mime_type,
                    "created_at": m.created_at.isoformat()
                }
                for m in results
            ]

    def delete_media(
        self,
        media_id: str,
        remove_file: bool = False
    ) -> bool:
        """Supprime un média.

        Args:
            media_id: Identifiant du média
            remove_file: Si True, supprime aussi le fichier physique

        Returns:
            True si supprimé, False si non trouvé
        """
        with self.db.get_session() as session:
            media = session.query(MediaItem).filter_by(id=media_id).first()
            if not media:
                return False

            # Supprimer le fichier physique si demandé
            if remove_file:
                file_path = self.storage_path / media.path
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"File deleted: {file_path}")

            # Supprimer de la base de données
            session.delete(media)
            session.commit()
            logger.info(f"Media deleted: {media_id}")
            return True

    def _get_storage_path(self, checksum: str, extension: str) -> Path:
        """Génère le chemin de stockage basé sur le checksum.
        
        Utilise les premiers caractères du checksum pour créer une
        hiérarchie de répertoires (sharding).
        
        Args:
            checksum: Checksum BLAKE2b
            extension: Extension du fichier
            
        Returns:
            Chemin de stockage
        """
        # Sharding: premiers 2 et 4 caractères
        return self.storage_path / "media" / checksum[:2] / checksum[2:4] / f"{checksum}{extension}"

    def _guess_mime_type(self, file_path: Path) -> Optional[str]:
        """Détermine le type MIME d'un fichier."""
        import mimetypes
        return mimetypes.guess_type(str(file_path))[0]

    def _extract_and_save_metadata(
        self,
        session: Session,
        media_id: str,
        file_path: Path
    ) -> None:
        """Extrait et sauvegarde les métadonnées automatiques."""
        try:
            metadata_dict = self.metadata_extractor.extract(file_path)
            for key, value in metadata_dict.items():
                metadata = Metadata(
                    media_id=media_id,
                    key=key,
                    value=str(value),
                    source="auto"
                )
                session.add(metadata)
            session.commit()
            logger.info(f"Extracted {len(metadata_dict)} metadata entries for {media_id}")
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")

    def _save_custom_metadata(
        self,
        session: Session,
        media_id: str,
        custom_metadata: Dict[str, Any]
    ) -> None:
        """Sauvegarde les métadonnées personnalisées."""
        import json
        for key, value in custom_metadata.items():
            metadata = Metadata(
                media_id=media_id,
                key=f"custom.{key}",
                value=json.dumps(value) if isinstance(value, (dict, list)) else str(value),
                source="user"
            )
            session.add(metadata)
        session.commit()
        logger.info(f"Saved {len(custom_metadata)} custom metadata entries for {media_id}")
