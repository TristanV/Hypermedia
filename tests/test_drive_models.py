"""Tests pour les modèles SQLAlchemy et le gestionnaire de base de données."""

import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError

from hypermedia.drive.database import DatabaseManager
from hypermedia.drive.models import Collection, MediaItem, Metadata


class TestDatabaseManager:
    """Tests pour DatabaseManager."""

    @pytest.fixture
    def temp_db(self):
        """Crée une base de données temporaire pour les tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DatabaseManager(db_path, echo=False)
            yield db
            db.close()

    def test_database_creation(self, temp_db):
        """Test la création de la base de données."""
        assert temp_db.db_path.exists()
        assert temp_db.engine is not None
        assert temp_db.SessionLocal is not None

    def test_session_context_manager(self, temp_db):
        """Test le context manager de session."""
        with temp_db.get_session() as session:
            assert session is not None
            # La session doit être utilisable
            result = session.execute("SELECT 1").scalar()
            assert result == 1

    def test_session_rollback_on_error(self, temp_db):
        """Test le rollback automatique en cas d'erreur."""
        try:
            with temp_db.get_session() as session:
                item = MediaItem(
                    checksum="test123",
                    path="/test/path",
                    size=100
                )
                session.add(item)
                session.commit()
                # Provoquer une erreur
                raise ValueError("Test error")
        except ValueError:
            pass

        # Vérifier que l'item a bien été commité avant l'erreur
        with temp_db.get_session() as session:
            count = session.query(MediaItem).count()
            assert count == 1

    def test_reset_database(self, temp_db):
        """Test la réinitialisation de la base."""
        # Ajouter des données
        with temp_db.get_session() as session:
            item = MediaItem(
                checksum="test456",
                path="/test/path2",
                size=200
            )
            session.add(item)
            session.commit()

        # Réinitialiser
        temp_db.reset()

        # Vérifier que les tables sont vides
        with temp_db.get_session() as session:
            count = session.query(MediaItem).count()
            assert count == 0


class TestModels:
    """Tests pour les modèles de données."""

    @pytest.fixture
    def db(self):
        """Base de données pour les tests de modèles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DatabaseManager(db_path, echo=False)
            yield db
            db.close()

    def test_media_item_creation(self, db):
        """Test la création d'un MediaItem."""
        with db.get_session() as session:
            media = MediaItem(
                checksum="blake2b_hash_here",
                path="/storage/media/ab/cd/abcd123.jpg",
                mime_type="image/jpeg",
                size=1024000,
                original_filename="photo.jpg"
            )
            session.add(media)
            session.commit()

            # Vérifier que l'ID a été généré
            assert media.id is not None
            assert len(media.id) == 36  # UUID format
            assert media.created_at is not None
            assert media.updated_at is not None

    def test_media_item_unique_checksum(self, db):
        """Test la contrainte d'unicité sur le checksum."""
        with db.get_session() as session:
            media1 = MediaItem(
                checksum="duplicate_checksum",
                path="/path1",
                size=100
            )
            session.add(media1)
            session.commit()

        # Tenter d'ajouter un doublon
        with pytest.raises(IntegrityError):
            with db.get_session() as session:
                media2 = MediaItem(
                    checksum="duplicate_checksum",  # Même checksum
                    path="/path2",
                    size=200
                )
                session.add(media2)
                session.commit()

    def test_collection_creation(self, db):
        """Test la création d'une Collection."""
        with db.get_session() as session:
            collection = Collection(
                name="Test Collection",
                description="A test collection"
            )
            session.add(collection)
            session.commit()

            assert collection.id is not None
            assert collection.name == "Test Collection"
            assert collection.description == "A test collection"
            assert collection.created_at is not None

    def test_collection_unique_name(self, db):
        """Test la contrainte d'unicité sur le nom de collection."""
        with db.get_session() as session:
            coll1 = Collection(name="Unique Name")
            session.add(coll1)
            session.commit()

        with pytest.raises(IntegrityError):
            with db.get_session() as session:
                coll2 = Collection(name="Unique Name")  # Même nom
                session.add(coll2)
                session.commit()

    def test_collection_media_relationship(self, db):
        """Test la relation many-to-many entre Collection et MediaItem."""
        with db.get_session() as session:
            # Créer une collection
            collection = Collection(name="Photos")
            session.add(collection)

            # Créer des médias
            media1 = MediaItem(checksum="hash1", path="/path1", size=100)
            media2 = MediaItem(checksum="hash2", path="/path2", size=200)
            session.add_all([media1, media2])

            # Associer les médias à la collection
            collection.media_items.append(media1)
            collection.media_items.append(media2)
            session.commit()

            # Vérifier les relations
            assert len(collection.media_items) == 2
            assert media1 in collection.media_items
            assert media2 in collection.media_items

            # Vérifier la relation inverse
            assert collection in media1.collections
            assert collection in media2.collections

    def test_metadata_creation(self, db):
        """Test la création de Metadata."""
        with db.get_session() as session:
            # Créer un média
            media = MediaItem(checksum="hash_meta", path="/path", size=100)
            session.add(media)
            session.commit()

            # Ajouter des métadonnées
            meta1 = Metadata(
                media_id=media.id,
                key="exif.camera",
                value="Canon EOS 5D",
                source="auto"
            )
            meta2 = Metadata(
                media_id=media.id,
                key="custom.tags",
                value='["nature", "landscape"]',
                source="user"
            )
            session.add_all([meta1, meta2])
            session.commit()

            # Vérifier
            assert len(media.metadata) == 2
            assert meta1 in media.metadata
            assert meta2 in media.metadata

    def test_metadata_cascade_delete(self, db):
        """Test la suppression en cascade des métadonnées."""
        with db.get_session() as session:
            # Créer média avec métadonnées
            media = MediaItem(checksum="hash_cascade", path="/path", size=100)
            session.add(media)
            session.commit()

            meta = Metadata(
                media_id=media.id,
                key="test.key",
                value="test value",
                source="auto"
            )
            session.add(meta)
            session.commit()

            media_id = media.id

        # Supprimer le média
        with db.get_session() as session:
            media = session.query(MediaItem).filter_by(id=media_id).first()
            session.delete(media)
            session.commit()

        # Vérifier que les métadonnées ont été supprimées
        with db.get_session() as session:
            count = session.query(Metadata).filter_by(media_id=media_id).count()
            assert count == 0

    def test_multiple_collections_per_media(self, db):
        """Test qu'un média peut appartenir à plusieurs collections."""
        with db.get_session() as session:
            # Créer plusieurs collections
            coll1 = Collection(name="Collection 1")
            coll2 = Collection(name="Collection 2")
            coll3 = Collection(name="Collection 3")
            session.add_all([coll1, coll2, coll3])

            # Créer un média
            media = MediaItem(checksum="shared_media", path="/path", size=100)
            session.add(media)

            # Ajouter le média à plusieurs collections
            coll1.media_items.append(media)
            coll2.media_items.append(media)
            coll3.media_items.append(media)
            session.commit()

            # Vérifier
            assert len(media.collections) == 3
            assert coll1 in media.collections
            assert coll2 in media.collections
            assert coll3 in media.collections


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
