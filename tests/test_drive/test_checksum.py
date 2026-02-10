"""Tests for checksum module."""

import pytest
from pathlib import Path
import hashlib
from hypermedia.drive.checksum import compute_blake2b, verify_integrity


class TestChecksum:
    """Test suite for checksum functions."""

    @pytest.fixture
    def test_file(self, tmp_path):
        """Create a test file with known content."""
        file_path = tmp_path / "test.txt"
        content = b"Hello, Hypermedia!"
        file_path.write_bytes(content)
        
        # Pre-compute expected checksum
        hasher = hashlib.blake2b()
        hasher.update(content)
        expected = hasher.hexdigest()
        
        return file_path, expected

    @pytest.mark.skip(reason="Not implemented yet")
    def test_compute_blake2b(self, test_file):
        """Test BLAKE2b checksum computation."""
        file_path, expected_checksum = test_file
        computed = compute_blake2b(file_path)
        assert computed == expected_checksum
        assert len(computed) == 128  # BLAKE2b produces 64-byte (128 hex chars) hash

    @pytest.mark.skip(reason="Not implemented yet")
    def test_compute_blake2b_nonexistent_file(self, tmp_path):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError):
            compute_blake2b(tmp_path / "nonexistent.txt")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_verify_integrity_valid(self, test_file):
        """Test integrity verification with valid checksum."""
        file_path, expected_checksum = test_file
        assert verify_integrity(file_path, expected_checksum) is True

    @pytest.mark.skip(reason="Not implemented yet")
    def test_verify_integrity_invalid(self, test_file):
        """Test integrity verification with invalid checksum."""
        file_path, _ = test_file
        wrong_checksum = "0" * 128
        assert verify_integrity(file_path, wrong_checksum) is False
