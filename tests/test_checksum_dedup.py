"""Tests unitaires pour les systèmes de checksum et déduplication.

Ce module teste le calcul de checksums BLAKE2b, la vérification d'intégrité
et la détection de doublons.
"""

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
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("This is a test file for checksum validation.\n")
            f.write("It contains multiple lines.\n")
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Nettoyage
        temp_path.unlink()

    def test_compute_blake2b_basic(self, test_file: Path):
        """Test du calcul de checksum BLAKE2b."""
        checksum = compute_blake2b(test_file)
        
        assert checksum is not None
        assert isinstance(checksum, str)
        assert len(checksum) == 128  # BLAKE2b produit un hash de 64 bytes (128 hex)
        # Vérifier que c'est bien de l'hexadécimal
        assert all(c in '0123456789abcdef' for c in checksum)

    def test_compute_blake2b_deterministic(self, test_file: Path):
        """Test que le checksum est déterministe."""
        checksum1 = compute_blake2b(test_file)
        checksum2 = compute_blake2b(test_file)
        
        assert checksum1 == checksum2

    def test_compute_blake2b_different_files(self):
        """Test que des fichiers différents produisent des checksums différents."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write("Content A")
            path1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write("Content B")
            path2 = Path(f2.name)
        
        try:
            checksum1 = compute_blake2b(path1)
            checksum2 = compute_blake2b(path2)
            
            assert checksum1 != checksum2
        finally:
            path1.unlink()
            path2.unlink()

    def test_compute_blake2b_empty_file(self):
        """Test du checksum d'un fichier vide."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = Path(f.name)
        
        try:
            checksum = compute_blake2b(path)
            assert checksum is not None
            assert len(checksum) == 128
        finally:
            path.unlink()

    def test_compute_blake2b_large_file(self):
        """Test du checksum d'un fichier de grande taille."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Créer un fichier de 10 MB
            chunk = b'A' * (1024 * 1024)  # 1 MB
            for _ in range(10):
                f.write(chunk)
            path = Path(f.name)
        
        try:
            checksum = compute_blake2b(path)
            assert checksum is not None
            assert len(checksum) == 128
        finally:
            path.unlink()

    def test_compute_blake2b_nonexistent_file(self):
        """Test avec un fichier inexistant."""
        with pytest.raises(FileNotFoundError):
            compute_blake2b(Path("/nonexistent/file.txt"))

    def test_verify_integrity_valid(self, test_file: Path):
        """Test de vérification d'intégrité avec checksum valide."""
        checksum = compute_blake2b(test_file)
        is_valid = verify_integrity(test_file, checksum)
        
        assert is_valid is True

    def test_verify_integrity_invalid(self, test_file: Path):
        """Test de vérification d'intégrité avec checksum invalide."""
        fake_checksum = "0" * 128
        is_valid = verify_integrity(test_file, fake_checksum)
        
        assert is_valid is False

    def test_verify_integrity_after_modification(self, test_file: Path):
        """Test de vérification après modification du fichier."""
        original_checksum = compute_blake2b(test_file)
        
        # Modifier le fichier
        with open(test_file, 'a') as f:
            f.write("\nAdditional content")
        
        # Le checksum original ne devrait plus correspondre
        is_valid = verify_integrity(test_file, original_checksum)
        assert is_valid is False
        
        # Nouveau checksum devrait être différent
        new_checksum = compute_blake2b(test_file)
        assert new_checksum != original_checksum


class TestDeduplication:
    """Tests pour le gestionnaire de déduplication."""

    @pytest.fixture
    def db(self):
        """Fixture pour une base de données temporaire."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "dedup_test.db"
            db_manager = DatabaseManager(db_path)
            yield db_manager
            db_manager.close()

    @pytest.fixture
    def dedup_manager(self, db: DatabaseManager):
        """Fixture pour un gestionnaire de déduplication."""
        return DeduplicationManager(db)

    def test_initialization(self, dedup_manager: DeduplicationManager):
        """Test de l'initialisation du DeduplicationManager."""
        assert dedup_manager.db is not None
        assert dedup_manager.policy == DuplicatePolicy.REFERENCE

    def test_find_duplicate_none(self, dedup_manager: DeduplicationManager):
        """Test de recherche de doublon quand il n'y en a pas."""
        result = dedup_manager.find_duplicate("nonexistent_checksum_123")
        assert result is None

    def test_find_duplicate_existing(self, db: DatabaseManager, dedup_manager: DeduplicationManager):
        """Test de détection de doublon existant."""
        checksum = "abc123def456"
        
        # Ajouter un média
        with db.get_session() as session:
            media = MediaItem(
                checksum=checksum,
                path="/test.jpg",
                mime_type="image/jpeg",
                size=1000
            )
            session.add(media)
            session.commit()
            media_id = media.id
        
        # Rechercher le doublon
        duplicate = dedup_manager.find_duplicate(checksum)
        assert duplicate is not None
        assert duplicate.id == media_id
        assert duplicate.checksum == checksum

    def test_is_duplicate_false(self, dedup_manager: DeduplicationManager):
        """Test is_duplicate avec un nouveau checksum."""
        assert dedup_manager.is_duplicate("new_checksum_xyz") is False

    def test_is_duplicate_true(self, db: DatabaseManager, dedup_manager: DeduplicationManager):
        """Test is_duplicate avec un checksum existant."""
        checksum = "duplicate_test_123"
        
        # Ajouter un média
        with db.get_session() as session:
            media = MediaItem(
                checksum=checksum,
                path="/test.jpg",
                mime_type="image/jpeg",
                size=1000
            )
            session.add(media)
            session.commit()
        
        # Vérifier le doublon
        assert dedup_manager.is_duplicate(checksum) is True

    def test_get_duplicates_count(self, db: DatabaseManager, dedup_manager: DeduplicationManager):
        """Test du comptage des doublons."""
        checksum = "multi_test_456"
        
        # Pas de doublons initialement
        assert dedup_manager.get_duplicates_count(checksum) == 0
        
        # Ajouter un média
        with db.get_session() as session:
            media = MediaItem(
                checksum=checksum,
                path="/test.jpg",
                mime_type="image/jpeg",
                size=1000
            )
            session.add(media)
            session.commit()
        
        # Devrait compter 1
        assert dedup_manager.get_duplicates_count(checksum) == 1

    def test_list_all_duplicates_empty(self, dedup_manager: DeduplicationManager):
        """Test de liste des doublons quand il n'y en a pas."""
        duplicates = dedup_manager.list_all_duplicates()
        assert len(duplicates) == 0

    def test_list_all_duplicates(self, db: DatabaseManager, dedup_manager: DeduplicationManager):
        """Test de liste de tous les doublons."""
        # Note: list_all_duplicates devrait retourner les checksums avec plusieurs entrées
        # Pour ce test, on vérifie juste que la fonction fonctionne
        
        # Ajouter plusieurs médias
        checksums = ["check1", "check2", "check3"]
        with db.get_session() as session:
            for i, checksum in enumerate(checksums):
                media = MediaItem(
                    checksum=checksum,
                    path=f"/test{i}.jpg",
                    mime_type="image/jpeg",
                    size=1000 * (i + 1)
                )
                session.add(media)
            session.commit()
        
        # Liste des doublons (devrait être vide car tous les checksums sont uniques)
        duplicates = dedup_manager.list_all_duplicates()
        assert isinstance(duplicates, list)

    def test_policy_reference(self, db: DatabaseManager):
        """Test de la politique REFERENCE."""
        dedup = DeduplicationManager(db, policy=DuplicatePolicy.REFERENCE)
        assert dedup.policy == DuplicatePolicy.REFERENCE

    def test_policy_ignore(self, db: DatabaseManager):
        """Test de la politique IGNORE."""
        dedup = DeduplicationManager(db, policy=DuplicatePolicy.IGNORE)
        assert dedup.policy == DuplicatePolicy.IGNORE

    def test_policy_alert(self, db: DatabaseManager):
        """Test de la politique ALERT."""
        dedup = DeduplicationManager(db, policy=DuplicatePolicy.ALERT)
        assert dedup.policy == DuplicatePolicy.ALERT

    def test_multiple_checksums(self, db: DatabaseManager, dedup_manager: DeduplicationManager):
        """Test avec plusieurs checksums différents."""
        checksums = {f"check_{i}": f"/test{i}.jpg" for i in range(10)}
        
        # Ajouter tous les médias
        with db.get_session() as session:
            for checksum, path in checksums.items():
                media = MediaItem(
                    checksum=checksum,
                    path=path,
                    mime_type="image/jpeg",
                    size=1000
                )
                session.add(media)
            session.commit()
        
        # Vérifier que tous sont détectables
        for checksum in checksums.keys():
            assert dedup_manager.is_duplicate(checksum) is True
            duplicate = dedup_manager.find_duplicate(checksum)
            assert duplicate is not None
            assert duplicate.checksum == checksum


class TestChecksumDeduplicationIntegration:
    """Tests d'intégration entre checksum et déduplication."""

    @pytest.fixture
    def setup(self):
        """Setup pour les tests d'intégration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Créer des fichiers de test
            file1 = tmpdir / "file1.txt"
            file1.write_text("Content A")
            
            file2 = tmpdir / "file2.txt"
            file2.write_text("Content A")  # Même contenu que file1
            
            file3 = tmpdir / "file3.txt"
            file3.write_text("Content B")  # Contenu différent
            
            # Base de données
            db = DatabaseManager(tmpdir / "test.db")
            dedup = DeduplicationManager(db)
            
            yield {
                "tmpdir": tmpdir,
                "file1": file1,
                "file2": file2,
                "file3": file3,
                "db": db,
                "dedup": dedup
            }
            
            db.close()

    def test_identical_files_same_checksum(self, setup):
        """Test que des fichiers identiques produisent le même checksum."""
        checksum1 = compute_blake2b(setup["file1"])
        checksum2 = compute_blake2b(setup["file2"])
        
        assert checksum1 == checksum2

    def test_workflow_add_and_detect(self, setup):
        """Test du workflow complet: ajout et détection."""
        file1 = setup["file1"]
        file2 = setup["file2"]
        db = setup["db"]
        dedup = setup["dedup"]
        
        # Calculer checksums
        checksum1 = compute_blake2b(file1)
        checksum2 = compute_blake2b(file2)
        
        # Ajouter le premier fichier
        with db.get_session() as session:
            media1 = MediaItem(
                checksum=checksum1,
                path=str(file1),
                mime_type="text/plain",
                size=file1.stat().st_size
            )
            session.add(media1)
            session.commit()
        
        # Vérifier que le deuxième fichier est détecté comme doublon
        assert dedup.is_duplicate(checksum2) is True
        duplicate = dedup.find_duplicate(checksum2)
        assert duplicate is not None
        assert duplicate.checksum == checksum1

    def test_workflow_different_files_no_duplicate(self, setup):
        """Test que des fichiers différents ne sont pas détectés comme doublons."""
        file1 = setup["file1"]
        file3 = setup["file3"]
        db = setup["db"]
        dedup = setup["dedup"]
        
        checksum1 = compute_blake2b(file1)
        checksum3 = compute_blake2b(file3)
        
        # Les checksums devraient être différents
        assert checksum1 != checksum3
        
        # Ajouter le premier fichier
        with db.get_session() as session:
            media1 = MediaItem(
                checksum=checksum1,
                path=str(file1),
                mime_type="text/plain",
                size=file1.stat().st_size
            )
            session.add(media1)
            session.commit()
        
        # Le troisième fichier ne devrait pas être détecté comme doublon
        assert dedup.is_duplicate(checksum3) is False
