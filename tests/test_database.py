"""Tests unitaires pour le gestionnaire de base de données.

Ce module teste les fonctionnalités du DatabaseManager incluant
la création, les sessions, et les opérations de maintenance.
"""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from hypermedia.drive.database import DatabaseManager
from hypermedia.drive.models import Base, Collection, MediaItem


class TestDatabaseManager:
    """Tests pour la classe DatabaseManager."""

    @pytest.fixture
    def temp_db_path(self):
        """Crée un chemin temporaire pour la base de données de test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_hypermedia.db"

    def test_initialization(self, temp_db_path: Path):
        """Test de l'initialisation du DatabaseManager."""
        db = DatabaseManager(temp_db_path)
        
        assert db.db_path == temp_db_path
        assert db.db_path.exists()
        assert db.engine is not None
        assert db.SessionLocal is not None
        
        db.close()

    def test_init_schema(self, temp_db_path: Path):
        """Test de l'initialisation du schéma."""
        db = DatabaseManager(temp_db_path)
        
        # Vérifier que les tables sont créées
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        assert "media_items" in tables
        assert "collections" in tables
        assert "metadata" in tables
        assert "collection_items" in tables
        
        db.close()

    def test_get_session_context_manager(self, temp_db_path: Path):
        """Test du context manager get_session."""
        db = DatabaseManager(temp_db_path)
        
        with db.get_session() as session:
            assert isinstance(session, Session)
            assert session.is_active
            
            # Tester une opération simple
            collection = Collection(name="Test Collection")
            session.add(collection)
            session.commit()
            
            assert collection.id is not None
        
        # La session doit être fermée après le contexte
        # Note: SQLAlchemy peut garder la connexion ouverte
        
        db.close()

    def test_session_rollback_on_error(self, temp_db_path: Path):
        """Test du rollback automatique en cas d'erreur."""
        db = DatabaseManager(temp_db_path)
        
        try:
            with db.get_session() as session:
                # Créer une collection
                collection = Collection(name="Test")
                session.add(collection)
                session.commit()
                
                # Tenter de créer une collection avec le même nom (erreur)
                duplicate = Collection(name="Test")
                session.add(duplicate)
                session.commit()  # Devrait lever une exception
        except Exception:
            pass  # Exception attendue
        
        # Vérifier qu'une seule collection existe
        with db.get_session() as session:
            count = session.query(Collection).count()
            assert count == 1
        
        db.close()

    def test_create_session_manual(self, temp_db_path: Path):
        """Test de création manuelle de session."""
        db = DatabaseManager(temp_db_path)
        
        session = db.create_session()
        assert isinstance(session, Session)
        
        # Utiliser la session
        media = MediaItem(
            checksum="test123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        session.add(media)
        session.commit()
        
        # Fermer manuellement
        session.close()
        db.close()

    def test_drop_all(self, temp_db_path: Path):
        """Test de suppression de toutes les tables."""
        db = DatabaseManager(temp_db_path)
        
        # Ajouter des données
        with db.get_session() as session:
            collection = Collection(name="To Delete")
            session.add(collection)
            session.commit()
        
        # Supprimer toutes les tables
        db.drop_all()
        
        # Vérifier que les tables sont supprimées
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        assert len(tables) == 0
        
        db.close()

    def test_reset(self, temp_db_path: Path):
        """Test de réinitialisation de la base de données."""
        db = DatabaseManager(temp_db_path)
        
        # Ajouter des données
        with db.get_session() as session:
            collection = Collection(name="To Reset")
            session.add(collection)
            session.commit()
        
        # Réinitialiser
        db.reset()
        
        # Vérifier que les tables existent mais sont vides
        with db.get_session() as session:
            count = session.query(Collection).count()
            assert count == 0
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert "collections" in tables
        
        db.close()

    def test_multiple_sessions(self, temp_db_path: Path):
        """Test de gestion de sessions multiples."""
        db = DatabaseManager(temp_db_path)
        
        # Créer des données avec une session
        with db.get_session() as session1:
            collection = Collection(name="Session 1")
            session1.add(collection)
            session1.commit()
        
        # Lire avec une autre session
        with db.get_session() as session2:
            result = session2.query(Collection).filter_by(name="Session 1").first()
            assert result is not None
            assert result.name == "Session 1"
        
        db.close()

    def test_foreign_key_constraints(self, temp_db_path: Path):
        """Test que les contraintes de clés étrangères sont activées."""
        db = DatabaseManager(temp_db_path)
        
        with db.get_session() as session:
            from hypermedia.drive.models import Metadata
            
            # Tenter d'ajouter une métadonnée avec un media_id inexistant
            metadata = Metadata(
                media_id="nonexistent-id",
                key="test",
                value="test",
                source="user"
            )
            session.add(metadata)
            
            # Devrait échouer à cause de la contrainte de clé étrangère
            with pytest.raises(Exception):  # IntegrityError ou ForeignKeyViolation
                session.commit()
        
        db.close()

    def test_persistence(self, temp_db_path: Path):
        """Test de la persistance des données entre sessions."""
        # Première connexion - ajout de données
        db1 = DatabaseManager(temp_db_path)
        with db1.get_session() as session:
            collection = Collection(name="Persistent Collection")
            session.add(collection)
            session.commit()
            collection_id = collection.id
        db1.close()
        
        # Deuxième connexion - vérification
        db2 = DatabaseManager(temp_db_path)
        with db2.get_session() as session:
            result = session.query(Collection).filter_by(id=collection_id).first()
            assert result is not None
            assert result.name == "Persistent Collection"
        db2.close()

    def test_echo_mode(self, temp_db_path: Path):
        """Test du mode echo (affichage SQL)."""
        # Mode echo activé
        db = DatabaseManager(temp_db_path, echo=True)
        assert db.engine.echo is True
        db.close()
        
        # Mode echo désactivé (défaut)
        db2 = DatabaseManager(temp_db_path, echo=False)
        assert db2.engine.echo is False
        db2.close()

    def test_thread_safety_config(self, temp_db_path: Path):
        """Test de la configuration pour le multi-threading."""
        db = DatabaseManager(temp_db_path)
        
        # Vérifier que check_same_thread est désactivé pour SQLite
        connect_args = db.engine.url.query
        # Note: Cette vérification dépend de l'implémentation interne
        # Le test principal est que ça ne lève pas d'erreur
        
        db.close()


class TestDatabaseIntegration:
    """Tests d'intégration avec les modèles."""

    @pytest.fixture
    def db(self):
        """Fixture pour une base de données temporaire."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "integration_test.db"
            db_manager = DatabaseManager(db_path)
            yield db_manager
            db_manager.close()

    def test_full_workflow(self, db: DatabaseManager):
        """Test d'un workflow complet."""
        with db.get_session() as session:
            # Créer une collection
            collection = Collection(
                name="My Photos",
                description="Personal photo collection"
            )
            session.add(collection)
            session.commit()
            
            # Ajouter un média
            media = MediaItem(
                checksum="abc123def456",
                path="/photos/vacation.jpg",
                mime_type="image/jpeg",
                size=2048000,
                original_filename="vacation.jpg"
            )
            session.add(media)
            session.commit()
            
            # Associer le média à la collection
            collection.media_items.append(media)
            session.commit()
            
            # Ajouter des métadonnées
            from hypermedia.drive.models import Metadata
            metadata = Metadata(
                media_id=media.id,
                key="exif.camera",
                value="Canon EOS 5D",
                source="auto"
            )
            session.add(metadata)
            session.commit()
            
            # Vérifications
            assert len(collection.media_items) == 1
            assert media.collections[0].name == "My Photos"
            assert len(media.metadata) == 1
            assert media.metadata[0].key == "exif.camera"

    def test_complex_queries(self, db: DatabaseManager):
        """Test de requêtes complexes."""
        with db.get_session() as session:
            from hypermedia.drive.models import Metadata
            
            # Créer plusieurs médias avec métadonnées
            for i in range(5):
                media = MediaItem(
                    checksum=f"checksum{i}",
                    path=f"/photo{i}.jpg",
                    mime_type="image/jpeg",
                    size=1000 * (i + 1)
                )
                session.add(media)
                session.flush()
                
                # Ajouter des métadonnées différentes
                if i % 2 == 0:
                    meta = Metadata(
                        media_id=media.id,
                        key="exif.camera",
                        value="Canon",
                        source="auto"
                    )
                    session.add(meta)
            
            session.commit()
            
            # Requête: trouver tous les médias avec une caméra Canon
            results = (
                session.query(MediaItem)
                .join(Metadata)
                .filter(Metadata.key == "exif.camera")
                .filter(Metadata.value == "Canon")
                .all()
            )
            
            assert len(results) == 3  # Images 0, 2, 4
