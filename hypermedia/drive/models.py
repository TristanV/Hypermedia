"""Modèles SQLAlchemy pour la base de données.

Ce module définit les modèles de données pour le stockage
des médias et métadonnées dans SQLite.
"""

from datetime import datetime
from typing import Optional, List
# TODO: Ajouter imports SQLAlchemy
# from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table
# from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


# TODO: Définir Base = DeclarativeBase()


class MediaItem:
    """Modèle pour un item média.
    
    Attributes:
        id: Identifiant unique (UUID)
        checksum: Checksum BLAKE2b du fichier
        path: Chemin relatif dans le stockage
        mime_type: Type MIME du fichier
        size: Taille en bytes
        created_at: Date d'ajout
        updated_at: Date de dernière modification
        collections: Collections contenant ce média
        metadata: Métadonnées associées
    """
    # TODO: Implémenter avec SQLAlchemy
    pass


class Collection:
    """Modèle pour une collection de médias.
    
    Attributes:
        id: Identifiant unique (UUID)
        name: Nom de la collection
        description: Description
        created_at: Date de création
        updated_at: Date de modification
        media_items: Médias dans cette collection
    """
    # TODO: Implémenter avec SQLAlchemy
    pass


class Metadata:
    """Modèle pour les métadonnées d'un média.
    
    Attributes:
        id: Identifiant unique
        media_id: Référence au média
        key: Clé de la métadonnée
        value: Valeur (JSON serializé)
        source: Source de la métadonnée (auto/user/import)
        created_at: Date de création
    """
    # TODO: Implémenter avec SQLAlchemy
    pass


# TODO: Table d'association many-to-many pour Collection <-> MediaItem
# collection_items = Table(...)
