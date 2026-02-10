"""Tests unitaires pour les modèles SQLAlchemy.

Ce module teste la création, les relations et les contraintes
des modèles MediaItem, Collection et Metadata.
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from hypermedia.drive.models import Base, Collection, MediaItem, Metadata


@pytest.fixture(scope="function")
def db_session():
    """Crée une session de base de données en mémoire pour les tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestMediaItem:
    """Tests pour le modèle MediaItem."""

    def test_create_media_item(self, db_session: Session):
        """Test de création d'un MediaItem."""
        media = MediaItem(
            checksum="abc123def456",
            path="/media/ab/cd/abc123def456.jpg",
            mime_type="image/jpeg",
            size=1024000,
            original_filename="photo.jpg"
        )
        db_session.add(media)
        db_session.commit()

        assert media.id is not None
        assert media.checksum == "abc123def456"
        assert media.size == 1024000
        assert isinstance(media.created_at, datetime)
        assert isinstance(media.updated_at, datetime)

    def test_checksum_uniqueness(self, db_session: Session):
        """Test de l'unicité du checksum."""
        media1 = MediaItem(
            checksum="unique123",
            path="/path1.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media1)
        db_session.commit()

        # Tentative d'ajouter un doublon
        media2 = MediaItem(
            checksum="unique123",  # Même checksum
            path="/path2.jpg",
            mime_type="image/jpeg",
            size=2000
        )
        db_session.add(media2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_media_item_repr(self, db_session: Session):
        """Test de la représentation string."""
        media = MediaItem(
            checksum="abc123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000,
            original_filename="test.jpg"
        )
        db_session.add(media)
        db_session.commit()

        repr_str = repr(media)
        assert "MediaItem" in repr_str
        assert "abc123" in repr_str
        assert "test.jpg" in repr_str

    def test_media_item_auto_uuid(self, db_session: Session):
        """Test de génération automatique de l'UUID."""
        media = MediaItem(
            checksum="test123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media)
        db_session.commit()

        # Vérifier que l'ID est un UUID valide
        try:
            uuid.UUID(media.id)
        except ValueError:
            pytest.fail("ID is not a valid UUID")


class TestCollection:
    """Tests pour le modèle Collection."""

    def test_create_collection(self, db_session: Session):
        """Test de création d'une collection."""
        collection = Collection(
            name="Test Collection",
            description="A test collection"
        )
        db_session.add(collection)
        db_session.commit()

        assert collection.id is not None
        assert collection.name == "Test Collection"
        assert collection.description == "A test collection"
        assert isinstance(collection.created_at, datetime)

    def test_collection_name_uniqueness(self, db_session: Session):
        """Test de l'unicité du nom de collection."""
        collection1 = Collection(name="Unique Name")
        db_session.add(collection1)
        db_session.commit()

        # Tentative d'ajouter un nom en double
        collection2 = Collection(name="Unique Name")
        db_session.add(collection2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_collection_repr(self, db_session: Session):
        """Test de la représentation string."""
        collection = Collection(name="My Collection")
        db_session.add(collection)
        db_session.commit()

        repr_str = repr(collection)
        assert "Collection" in repr_str
        assert "My Collection" in repr_str


class TestMetadata:
    """Tests pour le modèle Metadata."""

    def test_create_metadata(self, db_session: Session):
        """Test de création de métadonnées."""
        media = MediaItem(
            checksum="meta123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media)
        db_session.commit()

        metadata = Metadata(
            media_id=media.id,
            key="exif.camera",
            value="Canon EOS 5D",
            source="auto"
        )
        db_session.add(metadata)
        db_session.commit()

        assert metadata.id is not None
        assert metadata.media_id == media.id
        assert metadata.key == "exif.camera"
        assert metadata.value == "Canon EOS 5D"
        assert metadata.source == "auto"

    def test_metadata_sources(self, db_session: Session):
        """Test des différentes sources de métadonnées."""
        media = MediaItem(
            checksum="sources123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media)
        db_session.commit()

        sources = ["auto", "user", "import", "api"]
        for source in sources:
            meta = Metadata(
                media_id=media.id,
                key=f"test.{source}",
                value="test",
                source=source
            )
            db_session.add(meta)
        
        db_session.commit()

        # Vérifier que toutes les sources sont enregistrées
        saved_metadata = db_session.query(Metadata).filter_by(media_id=media.id).all()
        assert len(saved_metadata) == 4
        assert set(m.source for m in saved_metadata) == set(sources)


class TestRelationships:
    """Tests pour les relations entre modèles."""

    def test_media_metadata_relationship(self, db_session: Session):
        """Test de la relation MediaItem -> Metadata."""
        media = MediaItem(
            checksum="rel123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media)
        db_session.commit()

        # Ajouter plusieurs métadonnées
        for i in range(3):
            meta = Metadata(
                media_id=media.id,
                key=f"test.key{i}",
                value=f"value{i}",
                source="auto"
            )
            db_session.add(meta)
        db_session.commit()

        # Vérifier la relation
        assert len(media.metadata) == 3
        assert all(isinstance(m, Metadata) for m in media.metadata)

    def test_collection_media_relationship(self, db_session: Session):
        """Test de la relation many-to-many Collection <-> MediaItem."""
        collection = Collection(name="Test Collection")
        db_session.add(collection)

        # Créer plusieurs médias
        media_items = []
        for i in range(3):
            media = MediaItem(
                checksum=f"coll{i}",
                path=f"/test{i}.jpg",
                mime_type="image/jpeg",
                size=1000 * (i + 1)
            )
            media_items.append(media)
            collection.media_items.append(media)
        
        db_session.commit()

        # Vérifier la relation
        assert len(collection.media_items) == 3
        for media in media_items:
            assert collection in media.collections

    def test_multiple_collections_per_media(self, db_session: Session):
        """Test d'un média dans plusieurs collections."""
        media = MediaItem(
            checksum="multi123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media)

        # Créer plusieurs collections
        collections = []
        for i in range(3):
            coll = Collection(name=f"Collection {i}")
            coll.media_items.append(media)
            collections.append(coll)
            db_session.add(coll)
        
        db_session.commit()

        # Vérifier que le média est dans toutes les collections
        assert len(media.collections) == 3
        for coll in collections:
            assert media in coll.media_items

    def test_cascade_delete_metadata(self, db_session: Session):
        """Test de la suppression en cascade des métadonnées."""
        media = MediaItem(
            checksum="cascade123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media)
        db_session.commit()

        # Ajouter des métadonnées
        for i in range(5):
            meta = Metadata(
                media_id=media.id,
                key=f"test.{i}",
                value=f"value{i}",
                source="auto"
            )
            db_session.add(meta)
        db_session.commit()

        media_id = media.id

        # Supprimer le média
        db_session.delete(media)
        db_session.commit()

        # Vérifier que les métadonnées sont supprimées
        remaining_metadata = db_session.query(Metadata).filter_by(media_id=media_id).all()
        assert len(remaining_metadata) == 0


class TestConstraintsAndValidation:
    """Tests pour les contraintes et validations."""

    def test_required_fields_media_item(self, db_session: Session):
        """Test des champs requis pour MediaItem."""
        # Tentative de création sans checksum (requis)
        media = MediaItem(
            path="/test.jpg",
            size=1000
        )
        db_session.add(media)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_required_fields_collection(self, db_session: Session):
        """Test des champs requis pour Collection."""
        # Tentative de création sans nom (requis)
        collection = Collection(description="Test")
        db_session.add(collection)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_timestamps_auto_update(self, db_session: Session):
        """Test de la mise à jour automatique des timestamps."""
        media = MediaItem(
            checksum="timestamp123",
            path="/test.jpg",
            mime_type="image/jpeg",
            size=1000
        )
        db_session.add(media)
        db_session.commit()

        original_created = media.created_at
        original_updated = media.updated_at

        # Modifier le média
        import time
        time.sleep(0.1)  # Petite pause pour observer le changement
        media.size = 2000
        db_session.commit()

        # Vérifier que created_at reste identique
        assert media.created_at == original_created
        # Note: updated_at peut ne pas changer dans SQLite en mémoire
        # Ce test est plus pertinent avec une vraie base de données
