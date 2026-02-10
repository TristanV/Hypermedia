"""Gestion de la base de données SQLite.

Ce module gère la connexion et les opérations sur la base de données
SQLite utilisée pour stocker les métadonnées des médias.
"""

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Active les contraintes de clés étrangères pour SQLite.
    
    Args:
        dbapi_conn: Connexion DBAPI
        connection_record: Enregistrement de connexion
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class DatabaseManager:
    """Gestionnaire de connexion à la base de données.

    Gestion centralisée de la base de données SQLite avec support
    des sessions et initialisation automatique du schéma.

    Attributes:
        db_path: Chemin du fichier SQLite
        engine: Moteur SQLAlchemy
        SessionLocal: Factory de sessions

    Example:
        >>> db = DatabaseManager("/path/to/hypermedia.db")
        >>> with db.get_session() as session:
        ...     # Utiliser la session
        ...     media = session.query(MediaItem).first()
    """

    def __init__(self, db_path: Path, echo: bool = False):
        """Initialise le gestionnaire de base de données.

        Args:
            db_path: Chemin du fichier SQLite
            echo: Si True, affiche les requêtes SQL (débogage)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Création du moteur SQLAlchemy
        db_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(
            db_url,
            echo=echo,
            connect_args={"check_same_thread": False},  # Support multi-threading
        )

        # Factory de sessions
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Initialisation du schéma si nécessaire
        self.init_schema()

        logger.info(f"Database initialized at {self.db_path}")

    def init_schema(self) -> None:
        """Initialise le schéma de base de données.

        Crée toutes les tables nécessaires si elles n'existent pas.
        Cette méthode est idempotente : elle peut être appelée
        plusieurs fois sans effet indésirable.
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Crée une nouvelle session de base de données.

        Context manager qui gère automatiquement la fermeture
        de la session et le rollback en cas d'erreur.

        Yields:
            Session SQLAlchemy

        Example:
            >>> with db.get_session() as session:
            ...     item = MediaItem(checksum="abc123", ...)
            ...     session.add(item)
            ...     session.commit()
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_session(self) -> Session:
        """Crée une nouvelle session (sans context manager).

        Attention: La session doit être fermée manuellement.
        Préférez utiliser get_session() avec un context manager.

        Returns:
            Session SQLAlchemy
        """
        return self.SessionLocal()

    def drop_all(self) -> None:
        """Supprime toutes les tables.

        ATTENTION: Cette opération est destructive et irréversible.
        À utiliser uniquement pour les tests ou les réinitialisations.
        """
        logger.warning("Dropping all database tables")
        Base.metadata.drop_all(bind=self.engine)

    def reset(self) -> None:
        """Réinitialise complètement la base de données.

        Supprime et recrée toutes les tables.
        ATTENTION: Opération destructive.
        """
        logger.warning("Resetting database")
        self.drop_all()
        self.init_schema()

    def close(self) -> None:
        """Ferme toutes les connexions et libère les ressources."""
        self.engine.dispose()
        logger.info("Database connections closed")
