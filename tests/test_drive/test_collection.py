"""Tests for MediaCollection class."""

import pytest
from pathlib import Path
from hypermedia.drive import MediaCollection


class TestMediaCollection:
    """Test suite for MediaCollection."""

    @pytest.fixture
    def temp_storage(self, tmp_path):
        """Create temporary storage directory."""
        return tmp_path / "test_collections"

    @pytest.fixture
    def collection(self, temp_storage):
        """Create a test collection."""
        return MediaCollection(
            name="Test Collection",
            storage_path=temp_storage,
            description="Test collection for unit tests"
        )

    def test_collection_creation(self, collection, temp_storage):
        """Test that collection is created with correct attributes."""
        assert collection.name == "Test Collection"
        assert collection.description == "Test collection for unit tests"
        assert collection.storage_path == temp_storage
        assert collection.storage_path.exists()

    def test_storage_directory_created(self, collection):
        """Test that storage directory is created."""
        assert collection.storage_path.is_dir()

    @pytest.mark.skip(reason="Not implemented yet")
    def test_add_media(self, collection, tmp_path):
        """Test adding a media file."""
        # TODO: Implement when add_media is ready
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_get_media_info(self, collection):
        """Test retrieving media info."""
        # TODO: Implement when get_media_info is ready
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_search(self, collection):
        """Test searching media by metadata."""
        # TODO: Implement when search is ready
        pass
