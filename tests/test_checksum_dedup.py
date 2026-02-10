"""Tests pour les systèmes de checksum et déduplication."""

import tempfile
from pathlib import Path

import pytest

from hypermedia.drive.checksum import compute_blake2b, verify_integrity
from hypermedia.drive.database import DatabaseManager
from hypermedia.drive.deduplication import DeduplicationManager, DuplicatePolicy
from hypermedia.drive.models import MediaItem


class TestChecksum:
    """Tests pour le module checksum."""

    @pytest.fixture
    def test_file(self):
        """Crée un fichier temporaire pour les tests."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as f:
            f.write("Test content for checksum calculation")
            test_path = Path(f.name)
        
        yield test_path
        
        # Cleanup
        if test_path.exists():
            test_path.unlink()

    def test_compute_blake2b(self, test_file):
        """Test le calcul de checksum BLAKE2b."""
        checksum = compute_blake2b(test_file)
        
        # Vérifier le format
        assert isinstance(checksum, str)
        assert len(checksum) == 128  # BLAKE2b-512 hex = 128 chars
        assert all(c in '0123456789abcdef' for c in checksum)

    def test_compute_blake2b_deterministic(self, test_file):
        """Test que le checksum est déterministe."""
        checksum1 = compute_blake2b(test_file)
        checksum2 = compute_blake2b(test_file)
        
        assert checksum1 == checksum2

    def test_compute_blake2b_different_files(self):
        """Test que des fichiers différents ont des checksums différents."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write("Content 1")
            file1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write("Content 2")
            file2 = Path(f2.name)
        
        try:
            checksum1 = compute_blake2b(file1)
            checksum2 = compute_blake2b(file2)
            
            assert checksum1 != checksum2
        finally:
            file1.unlink()
            file2.unlink()

    def test_verify_integrity_valid(self, test_file):
        """Test la vérification d'intégrité avec un checksum valide."""
        checksum = compute_blake2b(test_file)
        is_valid = verify_integrity(test_file, checksum)
        
        assert is_valid is True

    def test_verify_integrity_invalid(self, test_file):
        """Test la vérification d'intégrité avec un checksum invalide."""
        wrong_checksum = "0" * 128
        is_valid = verify_integrity(test_file, wrong_checksum)
        
        assert is_valid is False

    def test_compute_blake2b_large_file(self):
        """Test avec un fichier plus volumineux."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Créer un fichier de 10 MB
            f.write(b"x" * (10 * 1024 * 1024))
            large_file = Path(f.name)
        
        try:
            checksum = compute_blake2b(large_file)
            assert len(checksum) == 128
        finally:
            large_file.unlink()

    def test_compute_blake2b_nonexistent_file(self):
        """Test avec un fichier inexistant."""
        with pytest.raises(FileNotFoundError):
            compute_blake2b(Path("/nonexistent/file.txt"))


class TestDeduplication:
    """Tests pour le gestionnaire de déduplication."""

    @pytest.fixture
    def db(self):
        """Base de données temporaire."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DatabaseManager(db_path, echo=False)
            yield db
            db.close()

    @pytest.fixture
    def dedup_manager(self, db):
        """Gestionnaire de déduplication."""
        return DeduplicationManager(db)

    def test_find_duplicate_not_exists(self, dedup_manager):
        """Test la recherche d'un doublon inexistant."""
        result = dedup_manager.find_duplicate("nonexistent_checksum")
        assert result is None

    def test_find_duplicate_exists(self, db, dedup_manager):
        """Test la recherche d'un doublon existant."""
        # Ajouter un média
        with db.get_session() as session:
            media = MediaItem(
                checksum="duplicate_test_123",
                path="/test/path",
                size=1000
            )
            session.add(media)
            session.commit()
            media_id = media.id

        # Rechercher le doublon
        result = dedup_manager.find_duplicate("duplicate_test_123")
        assert result is not None
        assert result.id == media_id
        assert result.checksum == "duplicate_test_123"

    def test_is_duplicate_false(self, dedup_manager):
        """Test is_duplicate avec un checksum unique."""
        is_dup = dedup_manager.is_duplicate("unique_checksum_456")
        assert is_dup is False

    def test_is_duplicate_true(self, db, dedup_manager):
        """Test is_duplicate avec un doublon."""
        # Ajouter un média
        with db.get_session() as session:
            media = MediaItem(
                checksum="dup_checksum_789",
                path="/test/path",
                size=1000
            )
            session.add(media)
            session.commit()

        # Vérifier
        is_dup = dedup_manager.is_duplicate("dup_checksum_789")
        assert is_dup is True

    def test_handle_duplicate_skip_policy(self, db, dedup_manager):
        """Test la politique SKIP."""
        # Ajouter un média original
        with db.get_session() as session:
            original = MediaItem(
                checksum="skip_test",
                path="/original",
                size=100
            )
            session.add(original)
            session.commit()

        # Tenter d'ajouter un doublon avec politique SKIP
        result = dedup_manager.handle_duplicate(
            "skip_test",
            Path("/duplicate"),
            DuplicatePolicy.SKIP
        )
        
        assert result["action"] == "skipped"
        assert result["existing_media"] is not None

    def test_handle_duplicate_reference_policy(self, db, dedup_manager):
        """Test la politique REFERENCE."""
        with db.get_session() as session:
            original = MediaItem(
                checksum="ref_test",
                path="/original",
                size=100
            )
            session.add(original)
            session.commit()

        result = dedup_manager.handle_duplicate(
            "ref_test",
            Path("/duplicate"),
            DuplicatePolicy.REFERENCE
        )
        
        assert result["action"] == "referenced"
        assert result["existing_media"] is not None

    def test_list_duplicates_empty(self, dedup_manager):
        """Test list_duplicates avec une base vide."""
        duplicates = dedup_manager.list_duplicates()
        assert len(duplicates) == 0

    def test_multiple_media_same_checksum_detection(self, db):
        """Test que le système prévient les vrais doublons en base."""
        from sqlalchemy.exc import IntegrityError
        
        with db.get_session() as session:
            media1 = MediaItem(
                checksum="same_checksum",
                path="/path1",
                size=100
            )
            session.add(media1)
            session.commit()

        # La contrainte d'unicité doit empêcher l'ajout
        with pytest.raises(IntegrityError):
            with db.get_session() as session:
                media2 = MediaItem(
                    checksum="same_checksum",
                    path="/path2",
                    size=200
                )
                session.add(media2)
                session.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
