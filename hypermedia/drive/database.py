"""Gestion de la base de données SQLite.

Ce module gère la connexion et les opérations sur la base de données
SQLite utilisée pour stocker les métadonnées des médias.
"""

from pathlib import Path
from typing import Optional
# TODO: Ajouter imports SQLAlchemy
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session


class DatabaseManager:
    """Gestionnaire de connexion à la base de données.
    
    Attributes:
        db_path: Chemin du fichier SQLite
        engine: Moteur SQLAlchemy
        SessionLocal: Factory de sessions
    
    Example:
        >>> db = DatabaseManager("/path/to/hypermedia.db")
        >>> with db.get_session() as session:
        ...     # Utiliser la session
        ...     pass
    """
    
    def __init__(self, db_path: Path):
        """Initialise le gestionnaire de base de données.
        
        Args:
            db_path: Chemin du fichier SQLite
        """
        self.db_path = db_path
        # TODO: Créer engine SQLAlchemy
        # TODO: Créer sessionmaker
        # TODO: Initialiser le schéma si nécessaire
    
    def init_schema(self) -> None:
        """Initialise le schéma de base de données.
        
        Crée toutes les tables nécessaires si elles n'existent pas.
        """
        # TODO: Utiliser Base.metadata.create_all()
        raise NotImplementedError("Méthode à implémenter")
    
    def get_session(self):  # -> Session
        """Crée une nouvelle session de base de données.
        
        Returns:
            Session SQLAlchemy (context manager)
        """
        # TODO: Retourner session
        raise NotImplementedError("Méthode à implémenter")
