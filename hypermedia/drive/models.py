"""Modèles SQLAlchemy pour la base de données.

Ce module définit les modèles de données pour le stockage
des médias et métadonnées dans SQLite.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    BigInteger,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""

    pass


# Table d'association many-to-many pour Collection <-> MediaItem
collection_items = Table(
    "collection_items",
    Base.metadata,
    Column("collection_id", String(36), ForeignKey("collections.id"), primary_key=True),
    Column("media_id", String(36), ForeignKey("media_items.id"), primary_key=True),
    Column("added_at", DateTime, default=datetime.utcnow),
)


class MediaItem(Base):
    """Modèle pour un item média.

    Représente un fichier média unique dans le système, identifié
    par son checksum BLAKE2b pour garantir l'unicité.

    Attributes:
        id: Identifiant unique (UUID)
        checksum: Checksum BLAKE2b du fichier (hex digest)
        path: Chemin relatif dans le stockage
        mime_type: Type MIME du fichier
        size: Taille en bytes
        original_filename: Nom du fichier original
        created_at: Date d'ajout dans le système
        updated_at: Date de dernière modification des métadonnées
        collections: Collections contenant ce média
        metadata: Métadonnées associées
    """

    __tablename__ = "media_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    checksum: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(128))
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relations
    collections: Mapped[List["Collection"]] = relationship(
        "Collection", secondary=collection_items, back_populates="media_items"
    )
    metadata: Mapped[List["Metadata"]] = relationship(
        "Metadata", back_populates="media_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MediaItem(id={self.id[:8]}, checksum={self.checksum[:16]}, filename={self.original_filename})>"


class Collection(Base):
    """Modèle pour une collection de médias.

    Une collection est un regroupement logique de médias,
    permettant d'organiser les contenus selon différents critères.

    Attributes:
        id: Identifiant unique (UUID)
        name: Nom de la collection
        description: Description optionnelle
        created_at: Date de création
        updated_at: Date de dernière modification
        media_items: Médias dans cette collection
    """

    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relations
    media_items: Mapped[List[MediaItem]] = relationship(
        "MediaItem", secondary=collection_items, back_populates="collections"
    )

    def __repr__(self) -> str:
        return f"<Collection(id={self.id[:8]}, name={self.name})>"


class Metadata(Base):
    """Modèle pour les métadonnées d'un média.

    Stocke les métadonnées enrichies sous forme de paires clé-valeur.
    Les valeurs peuvent être de types complexes (sérialisées en JSON).

    Attributes:
        id: Identifiant unique (auto-incrémenté)
        media_id: Référence au média
        key: Clé de la métadonnée (ex: 'exif.camera_model')
        value: Valeur (stockée en JSON si complexe)
        source: Source de la métadonnée (auto/user/import/api)
        created_at: Date de création
        media_item: Relation vers le MediaItem
    """

    __tablename__ = "metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    media_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("media_items.id"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(
        String(32), nullable=False, default="user"
    )  # auto, user, import, api
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relations
    media_item: Mapped[MediaItem] = relationship("MediaItem", back_populates="metadata")

    def __repr__(self) -> str:
        return f"<Metadata(media_id={self.media_id[:8]}, key={self.key}, source={self.source})>"
