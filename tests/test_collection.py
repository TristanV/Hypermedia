"""Tests unitaires pour le gestionnaire de collections.

Ce module teste les fonctionnalités complètes de MediaCollection
incluant CRUD, déduplication, recherche et gestion du stockage.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from hypermedia.drive.collection import MediaCollection
from hypermedia.drive.database import DatabaseManager
from hypermedia.drive.models import Collection, MediaItem, Metadata


class TestMediaCollectionBasics:
    """Tests de base pour MediaCollection."""

    @pytest.fixture
    def setup(self):
        """Setup pour les tests avec fichiers temporaires."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            storage = tmpdir / "storage"
            db_path = tmpdir / "test.db"
            
            db = DatabaseManager(db_path)
            collection_manager = MediaCollection(storage, db)
            
            yield {
                "tmpdir": tmpdir,
                "storage": storage,
                "db": db,
                "collection": collection_manager
            }
            
            db.close()

    def test_initialization(self, setup):
        """Test de l'initialisation de MediaCollection."""
        coll = setup["collection"]
        storage = setup["storage"]
        
        assert coll.storage_path == storage
        assert storage.exists()
        assert coll.db is not None
        assert coll.dedup_manager is not None

    def test_initialization_with_auto_extract(self, setup):
        """Test avec extraction automatique de métadonnées."""
        storage = setup["storage"]
        db = setup["db"]
        
        coll = MediaCollection(storage, db, auto_extract_metadata=True)
        assert coll.auto_extract_metadata is True
        assert hasattr(coll, 'metadata_extractor')

    def test_initialization_without_auto_extract(self, setup):
        """Test sans extraction automatique."""
        storage = setup["storage"]
        db = setup["db"]
        
        coll = MediaCollection(storage, db, auto_extract_metadata=False)
        assert coll.auto_extract_metadata is False


class TestCollectionCRUD:
    """Tests des opérations CRUD sur les collections."""

    @pytest.fixture
    def setup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            db = DatabaseManager(tmpdir / "test.db")
            coll = MediaCollection(tmpdir / "storage", db, auto_extract_metadata=False)
            yield {"db": db, "collection": coll}
            db.close()

    def test_create_collection(self, setup):
        """Test de création d'une collection."""
        coll = setup["collection"]
        
        coll_id = coll.create_collection(
            name="Test Collection",
            description="A test collection"
        )
        
        assert coll_id is not None
        assert len(coll_id) == 36  # UUID format

    def test_create_collection_duplicate_name(self, setup):
        """Test de création avec nom dupliqué."""
        coll = setup["collection"]
        
        coll.create_collection(name="Unique Name")
        
        with pytest.raises(ValueError, match="already exists"):
            coll.create_collection(name="Unique Name")

    def test_get_collection(self, setup):
        """Test de récupération d'une collection."""
        coll = setup["collection"]
        
        coll_id = coll.create_collection(
            name="Get Test",
            description="Description"
        )
        
        result = coll.get_collection(coll_id)
        
        assert result is not None
        assert result["id"] == coll_id
        assert result["name"] == "Get Test"
        assert result["description"] == "Description"
        assert "created_at" in result
        assert "media_count" in result
        assert result["media_count"] == 0

    def test_get_nonexistent_collection(self, setup):
        """Test de récupération d'une collection inexistante."""
        coll = setup["collection"]
        result = coll.get_collection("nonexistent-id-123")
        assert result is None

    def test_list_collections_empty(self, setup):
        """Test de listage quand aucune collection."""
        coll = setup["collection"]
        result = coll.list_collections()
        assert result == []

    def test_list_collections(self, setup):
        """Test de listage de collections."""
        coll = setup["collection"]
        
        # Créer plusieurs collections
        coll.create_collection("Collection 1")
        coll.create_collection("Collection 2")
        coll.create_collection("Collection 3")
        
        result = coll.list_collections()
        
        assert len(result) == 3
        assert all("id" in c for c in result)
        assert all("name" in c for c in result)
        assert all("media_count" in c for c in result)


class TestMediaOperations:
    """Tests des opérations sur les médias."""

    @pytest.fixture
    def setup_with_file(self):
        """Setup avec fichier de test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Créer un fichier de test
            test_file = tmpdir / "test.txt"
            test_file.write_text("Test content for media operations")
            
            db = DatabaseManager(tmpdir / "test.db")
            coll = MediaCollection(tmpdir / "storage", db, auto_extract_metadata=False)
            
            yield {
                "tmpdir": tmpdir,
                "test_file": test_file,
                "db": db,
                "collection": coll
            }
            
            db.close()

    def test_add_media_to_collection(self, setup_with_file):
        """Test d'ajout d'un média à une collection."""
        coll = setup_with_file["collection"]
        test_file = setup_with_file["test_file"]
        
        coll_id = coll.create_collection("Media Test")
        media_id = coll.add_media_to_collection(
            coll_id,
            test_file,
            copy_file=True
        )
        
        assert media_id is not None
        assert len(media_id) == 36  # UUID
        
        # Vérifier que le fichier a été copié
        storage_path = coll.storage_path
        assert (storage_path / "media").exists()

    def test_add_media_nonexistent_file(self, setup_with_file):
        """Test d'ajout d'un fichier inexistant."""
        coll = setup_with_file["collection"]
        coll_id = coll.create_collection("Test")
        
        with pytest.raises(FileNotFoundError):
            coll.add_media_to_collection(
                coll_id,
                Path("/nonexistent/file.txt")
            )

    def test_add_media_nonexistent_collection(self, setup_with_file):
        """Test d'ajout à une collection inexistante."""
        coll = setup_with_file["collection"]
        test_file = setup_with_file["test_file"]
        
        with pytest.raises(ValueError, match="Collection not found"):
            coll.add_media_to_collection(
                "nonexistent-id",
                test_file
            )

    def test_add_duplicate_media(self, setup_with_file):
        """Test d'ajout d'un média en double."""
        coll = setup_with_file["collection"]
        test_file = setup_with_file["test_file"]
        
        coll_id = coll.create_collection("Duplicate Test")
        
        # Ajouter une première fois
        media_id1 = coll.add_media_to_collection(coll_id, test_file)
        
        # Ajouter la même chose (doublon)
        media_id2 = coll.add_media_to_collection(coll_id, test_file)
        
        # Devrait retourner le même ID (déduplication)
        assert media_id1 == media_id2

    def test_add_media_with_custom_metadata(self, setup_with_file):
        """Test d'ajout avec métadonnées personnalisées."""
        coll = setup_with_file["collection"]
        test_file = setup_with_file["test_file"]
        db = setup_with_file["db"]
        
        coll_id = coll.create_collection("Custom Meta Test")
        
        custom_meta = {
            "tags": ["important", "test"],
            "author": "Test User",
            "rating": 5
        }
        
        media_id = coll.add_media_to_collection(
            coll_id,
            test_file,
            custom_metadata=custom_meta
        )
        
        # Vérifier que les métadonnées sont sauvées
        with db.get_session() as session:
            metadata = session.query(Metadata).filter_by(media_id=media_id).all()
            meta_keys = [m.key for m in metadata]
            
            assert "custom.tags" in meta_keys
            assert "custom.author" in meta_keys
            assert "custom.rating" in meta_keys

    def test_add_media_without_copy(self, setup_with_file):
        """Test d'ajout sans copier le fichier."""
        coll = setup_with_file["collection"]
        test_file = setup_with_file["test_file"]
        
        coll_id = coll.create_collection("No Copy Test")
        media_id = coll.add_media_to_collection(
            coll_id,
            test_file,
            copy_file=False
        )
        
        assert media_id is not None
        
        # Le fichier ne devrait pas être dans le storage
        info = coll.get_media_info(media_id)
        assert str(test_file) in info["path"]


class TestMediaInfo:
    """Tests de récupération d'informations sur les médias."""

    @pytest.fixture
    def setup_with_media(self):
        """Setup avec média ajouté."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            test_file = tmpdir / "test.txt"
            test_file.write_text("Test content")
            
            db = DatabaseManager(tmpdir / "test.db")
            coll = MediaCollection(tmpdir / "storage", db, auto_extract_metadata=False)
            
            coll_id = coll.create_collection("Test Collection")
            media_id = coll.add_media_to_collection(coll_id, test_file)
            
            yield {
                "db": db,
                "collection": coll,
                "media_id": media_id,
                "collection_id": coll_id
            }
            
            db.close()

    def test_get_media_info(self, setup_with_media):
        """Test de récupération d'informations sur un média."""
        coll = setup_with_media["collection"]
        media_id = setup_with_media["media_id"]
        
        info = coll.get_media_info(media_id)
        
        assert info is not None
        assert info["id"] == media_id
        assert "checksum" in info
        assert "path" in info
        assert "size" in info
        assert "mime_type" in info
        assert "created_at" in info
        assert "collections" in info
        assert "metadata" in info

    def test_get_media_info_nonexistent(self, setup_with_media):
        """Test de récupération d'un média inexistant."""
        coll = setup_with_media["collection"]
        info = coll.get_media_info("nonexistent-id")
        assert info is None


class TestSearch:
    """Tests des fonctionnalités de recherche."""

    @pytest.fixture
    def setup_with_multiple_media(self):
        """Setup avec plusieurs médias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            db = DatabaseManager(tmpdir / "test.db")
            coll = MediaCollection(tmpdir / "storage", db, auto_extract_metadata=False)
            
            coll_id = coll.create_collection("Search Test")
            
            # Ajouter plusieurs fichiers
            media_ids = []
            for i in range(5):
                test_file = tmpdir / f"file{i}.txt"
                test_file.write_text(f"Content {i}")
                media_id = coll.add_media_to_collection(coll_id, test_file)
                media_ids.append(media_id)
            
            yield {
                "db": db,
                "collection": coll,
                "collection_id": coll_id,
                "media_ids": media_ids
            }
            
            db.close()

    def test_search_all(self, setup_with_multiple_media):
        """Test de recherche sans filtre."""
        coll = setup_with_multiple_media["collection"]
        results = coll.search()
        
        assert len(results) == 5
        assert all("id" in r for r in results)
        assert all("filename" in r for r in results)

    def test_search_by_collection(self, setup_with_multiple_media):
        """Test de recherche par collection."""
        coll = setup_with_multiple_media["collection"]
        coll_id = setup_with_multiple_media["collection_id"]
        
        results = coll.search(collection_id=coll_id)
        assert len(results) == 5

    def test_search_with_limit(self, setup_with_multiple_media):
        """Test de recherche avec limite."""
        coll = setup_with_multiple_media["collection"]
        results = coll.search(limit=2)
        assert len(results) == 2

    def test_search_with_offset(self, setup_with_multiple_media):
        """Test de recherche avec offset (pagination)."""
        coll = setup_with_multiple_media["collection"]
        
        page1 = coll.search(limit=2, offset=0)
        page2 = coll.search(limit=2, offset=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0]["id"] != page2[0]["id"]

    def test_search_by_query(self, setup_with_multiple_media):
        """Test de recherche textuelle."""
        coll = setup_with_multiple_media["collection"]
        results = coll.search(query="file0")
        
        assert len(results) >= 1
        assert any("file0" in r["filename"] for r in results)


class TestDeleteMedia:
    """Tests de suppression de médias."""

    @pytest.fixture
    def setup_with_media(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            test_file = tmpdir / "delete_test.txt"
            test_file.write_text("To be deleted")
            
            db = DatabaseManager(tmpdir / "test.db")
            coll = MediaCollection(tmpdir / "storage", db, auto_extract_metadata=False)
            
            coll_id = coll.create_collection("Delete Test")
            media_id = coll.add_media_to_collection(coll_id, test_file, copy_file=True)
            
            yield {
                "db": db,
                "collection": coll,
                "media_id": media_id,
                "storage": tmpdir / "storage"
            }
            
            db.close()

    def test_delete_media_without_file(self, setup_with_media):
        """Test de suppression sans supprimer le fichier physique."""
        coll = setup_with_media["collection"]
        media_id = setup_with_media["media_id"]
        
        result = coll.delete_media(media_id, remove_file=False)
        assert result is True
        
        # Vérifier que le média n'existe plus en DB
        info = coll.get_media_info(media_id)
        assert info is None

    def test_delete_media_with_file(self, setup_with_media):
        """Test de suppression avec fichier physique."""
        coll = setup_with_media["collection"]
        media_id = setup_with_media["media_id"]
        
        # Récupérer le chemin du fichier
        info = coll.get_media_info(media_id)
        file_path = coll.storage_path / info["path"]
        
        # Vérifier que le fichier existe
        assert file_path.exists()
        
        # Supprimer
        result = coll.delete_media(media_id, remove_file=True)
        assert result is True
        
        # Vérifier que le fichier n'existe plus
        assert not file_path.exists()

    def test_delete_nonexistent_media(self, setup_with_media):
        """Test de suppression d'un média inexistant."""
        coll = setup_with_media["collection"]
        result = coll.delete_media("nonexistent-id")
        assert result is False


class TestStorageSharding:
    """Tests du sharding du stockage."""

    @pytest.fixture
    def setup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            db = DatabaseManager(tmpdir / "test.db")
            coll = MediaCollection(tmpdir / "storage", db, auto_extract_metadata=False)
            yield {"collection": coll}
            db.close()

    def test_get_storage_path(self, setup):
        """Test de génération du chemin de stockage."""
        coll = setup["collection"]
        checksum = "abcdef1234567890"
        extension = ".jpg"
        
        path = coll._get_storage_path(checksum, extension)
        
        # Vérifier le sharding
        assert "ab" in str(path)  # Premiers 2 caractères
        assert "cd" in str(path)  # Caractères 2-4
        assert checksum in str(path)
        assert extension in str(path)

    def test_storage_path_uniqueness(self, setup):
        """Test que des checksums différents donnent des chemins différents."""
        coll = setup["collection"]
        
        path1 = coll._get_storage_path("abc123", ".jpg")
        path2 = coll._get_storage_path("xyz789", ".jpg")
        
        assert path1 != path2
