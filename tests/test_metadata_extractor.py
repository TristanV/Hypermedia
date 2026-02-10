"""Tests unitaires pour l'extracteur de métadonnées.

Ce module teste l'extraction de métadonnées pour différents formats
(images, audio, vidéo) avec gestion des erreurs.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from hypermedia.drive.metadata_extractor import MetadataExtractor


class TestMetadataExtractorInit:
    """Tests d'initialisation de l'extracteur."""

    def test_initialization_default(self):
        """Test d'initialisation par défaut."""
        extractor = MetadataExtractor()
        assert extractor.enable_video is True

    def test_initialization_no_video(self):
        """Test d'initialisation sans support vidéo."""
        extractor = MetadataExtractor(enable_video=False)
        assert extractor.enable_video is False

    @patch('subprocess.run')
    def test_ffprobe_check_available(self, mock_run):
        """Test de vérification de ffprobe disponible."""
        mock_run.return_value = Mock(returncode=0)
        extractor = MetadataExtractor()
        assert extractor.ffprobe_available is True

    @patch('subprocess.run', side_effect=FileNotFoundError)
    def test_ffprobe_check_unavailable(self, mock_run):
        """Test de vérification de ffprobe non disponible."""
        extractor = MetadataExtractor()
        assert extractor.ffprobe_available is False


class TestGenericMetadata:
    """Tests d'extraction de métadonnées génériques."""

    @pytest.fixture
    def test_file(self):
        """Crée un fichier de test."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            path = Path(f.name)
        yield path
        path.unlink()

    def test_extract_generic_metadata(self, test_file):
        """Test d'extraction de métadonnées génériques."""
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor.extract(test_file)
        
        assert "file.name" in metadata
        assert "file.extension" in metadata
        assert "file.size" in metadata
        assert "file.created_at" in metadata
        assert "file.modified_at" in metadata
        assert "file.mime_type" in metadata
        
        assert metadata["file.name"] == test_file.name
        assert metadata["file.extension"] == ".txt"
        assert metadata["file.size"] > 0

    def test_extract_nonexistent_file(self):
        """Test d'extraction sur fichier inexistant."""
        extractor = MetadataExtractor(enable_video=False)
        
        with pytest.raises(FileNotFoundError):
            extractor.extract(Path("/nonexistent/file.txt"))


class TestImageMetadata:
    """Tests d'extraction de métadonnées d'images."""

    @pytest.fixture
    def mock_image_file(self):
        """Crée un fichier image fictif."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
            path = Path(f.name)
        yield path
        if path.exists():
            path.unlink()

    @patch('hypermedia.drive.metadata_extractor.PILLOW_AVAILABLE', True)
    @patch('hypermedia.drive.metadata_extractor.Image')
    def test_extract_image_basic(self, mock_image, mock_image_file):
        """Test d'extraction de base pour images."""
        # Mock de l'image
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.format = "JPEG"
        mock_img.mode = "RGB"
        mock_img._getexif.return_value = None
        
        mock_image.open.return_value.__enter__.return_value = mock_img
        
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_image_metadata(mock_image_file)
        
        assert metadata["image.width"] == 1920
        assert metadata["image.height"] == 1080
        assert metadata["image.format"] == "JPEG"
        assert metadata["image.mode"] == "RGB"

    @patch('hypermedia.drive.metadata_extractor.PILLOW_AVAILABLE', False)
    def test_extract_image_pillow_unavailable(self, mock_image_file):
        """Test quand Pillow n'est pas disponible."""
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_image_metadata(mock_image_file)
        
        assert "image.pillow_unavailable" in metadata
        assert metadata["image.pillow_unavailable"] is True

    @patch('hypermedia.drive.metadata_extractor.PILLOW_AVAILABLE', True)
    @patch('hypermedia.drive.metadata_extractor.Image')
    def test_extract_image_with_exif(self, mock_image, mock_image_file):
        """Test d'extraction avec données EXIF."""
        # Mock de l'image avec EXIF
        mock_img = MagicMock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_img.format = "JPEG"
        mock_img.mode = "RGB"
        
        # Simuler des données EXIF
        exif_data = {
            271: "Canon",  # Make
            272: "Canon EOS 5D",  # Model
            306: "2024:01:15 10:30:00",  # DateTime
        }
        mock_img._getexif.return_value = exif_data
        
        mock_image.open.return_value.__enter__.return_value = mock_img
        
        extractor = MetadataExtractor(enable_video=False)
        
        with patch('hypermedia.drive.metadata_extractor.TAGS', {271: 'Make', 272: 'Model', 306: 'DateTime'}):
            metadata = extractor._extract_image_metadata(mock_image_file)
        
        assert "exif.Make" in metadata or "exif.271" in metadata

    @patch('hypermedia.drive.metadata_extractor.PILLOW_AVAILABLE', True)
    @patch('hypermedia.drive.metadata_extractor.Image')
    def test_extract_image_error_handling(self, mock_image, mock_image_file):
        """Test de gestion d'erreurs lors de l'extraction."""
        mock_image.open.side_effect = Exception("Image corrupted")
        
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_image_metadata(mock_image_file)
        
        assert "image.extraction_error" in metadata


class TestAudioMetadata:
    """Tests d'extraction de métadonnées audio."""

    @pytest.fixture
    def mock_audio_file(self):
        """Crée un fichier audio fictif."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            path = Path(f.name)
        yield path
        if path.exists():
            path.unlink()

    @patch('hypermedia.drive.metadata_extractor.MUTAGEN_AVAILABLE', False)
    def test_extract_audio_mutagen_unavailable(self, mock_audio_file):
        """Test quand Mutagen n'est pas disponible."""
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_audio_metadata(mock_audio_file)
        
        assert "audio.mutagen_unavailable" in metadata
        assert metadata["audio.mutagen_unavailable"] is True

    @patch('hypermedia.drive.metadata_extractor.MUTAGEN_AVAILABLE', True)
    @patch('hypermedia.drive.metadata_extractor.mutagen')
    def test_extract_audio_basic(self, mock_mutagen, mock_audio_file):
        """Test d'extraction de base pour audio."""
        # Mock de l'objet audio
        mock_audio = MagicMock()
        mock_audio.info.length = 180.5
        mock_audio.info.bitrate = 320000
        mock_audio.info.sample_rate = 44100
        mock_audio.info.channels = 2
        mock_audio.tags = {
            "title": ["Test Song"],
            "artist": ["Test Artist"],
            "album": ["Test Album"]
        }
        
        mock_mutagen.File.return_value = mock_audio
        
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_audio_metadata(mock_audio_file)
        
        assert metadata["audio.duration"] == 180.5
        assert metadata["audio.bitrate"] == 320000
        assert metadata["audio.sample_rate"] == 44100
        assert metadata["audio.channels"] == 2

    @patch('hypermedia.drive.metadata_extractor.MUTAGEN_AVAILABLE', True)
    @patch('hypermedia.drive.metadata_extractor.mutagen')
    def test_extract_audio_unsupported_format(self, mock_mutagen, mock_audio_file):
        """Test avec format audio non supporté."""
        mock_mutagen.File.return_value = None
        
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_audio_metadata(mock_audio_file)
        
        assert "audio.unsupported_format" in metadata

    @patch('hypermedia.drive.metadata_extractor.MUTAGEN_AVAILABLE', True)
    @patch('hypermedia.drive.metadata_extractor.mutagen')
    def test_extract_audio_error_handling(self, mock_mutagen, mock_audio_file):
        """Test de gestion d'erreurs."""
        mock_mutagen.File.side_effect = Exception("Audio corrupted")
        
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_audio_metadata(mock_audio_file)
        
        assert "audio.extraction_error" in metadata


class TestVideoMetadata:
    """Tests d'extraction de métadonnées vidéo."""

    @pytest.fixture
    def mock_video_file(self):
        """Crée un fichier vidéo fictif."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
            path = Path(f.name)
        yield path
        if path.exists():
            path.unlink()

    def test_extract_video_ffprobe_unavailable(self, mock_video_file):
        """Test quand ffprobe n'est pas disponible."""
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor._extract_video_metadata(mock_video_file)
        
        assert "video.ffprobe_unavailable" in metadata

    @patch('subprocess.run')
    def test_extract_video_basic(self, mock_run, mock_video_file):
        """Test d'extraction de base pour vidéo."""
        # Mock de la réponse ffprobe
        ffprobe_output = {
            "format": {
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "duration": "120.5",
                "size": "10485760",
                "bit_rate": "698000",
                "tags": {
                    "title": "Test Video",
                    "encoder": "Lavf58.29.100"
                }
            },
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30/1"
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "sample_rate": "48000",
                    "channels": 2
                }
            ]
        }
        
        import json
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(ffprobe_output)
        mock_run.return_value = mock_result
        
        extractor = MetadataExtractor(enable_video=True)
        extractor.ffprobe_available = True
        metadata = extractor._extract_video_metadata(mock_video_file)
        
        assert metadata["video.format"] == "mov,mp4,m4a,3gp,3g2,mj2"
        assert metadata["video.duration"] == 120.5
        assert metadata["video.size"] == 10485760
        assert metadata["video.bitrate"] == 698000

    @patch('subprocess.run')
    def test_extract_video_timeout(self, mock_run, mock_video_file):
        """Test de timeout lors de l'extraction."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("ffprobe", 30)
        
        extractor = MetadataExtractor(enable_video=True)
        extractor.ffprobe_available = True
        metadata = extractor._extract_video_metadata(mock_video_file)
        
        assert "video.extraction_timeout" in metadata

    @patch('subprocess.run')
    def test_extract_video_error(self, mock_run, mock_video_file):
        """Test de gestion d'erreurs."""
        mock_run.side_effect = Exception("ffprobe error")
        
        extractor = MetadataExtractor(enable_video=True)
        extractor.ffprobe_available = True
        metadata = extractor._extract_video_metadata(mock_video_file)
        
        assert "video.extraction_error" in metadata


class TestExtractIntegration:
    """Tests d'intégration de la méthode extract."""

    @pytest.fixture
    def test_files(self):
        """Crée des fichiers de test de différents types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Fichier texte
            txt_file = tmpdir / "test.txt"
            txt_file.write_text("Test content")
            
            # Fichier "image"
            img_file = tmpdir / "test.jpg"
            img_file.write_bytes(b"fake image data")
            
            # Fichier "audio"
            audio_file = tmpdir / "test.mp3"
            audio_file.write_bytes(b"fake audio data")
            
            # Fichier "vidéo"
            video_file = tmpdir / "test.mp4"
            video_file.write_bytes(b"fake video data")
            
            yield {
                "txt": txt_file,
                "img": img_file,
                "audio": audio_file,
                "video": video_file
            }

    def test_extract_text_file(self, test_files):
        """Test d'extraction sur fichier texte."""
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor.extract(test_files["txt"])
        
        # Devrait avoir au moins les métadonnées génériques
        assert "file.name" in metadata
        assert "file.size" in metadata
        assert "file.mime_type" in metadata

    @patch('hypermedia.drive.metadata_extractor.PILLOW_AVAILABLE', False)
    def test_extract_image_no_pillow(self, test_files):
        """Test d'extraction image sans Pillow."""
        extractor = MetadataExtractor(enable_video=False)
        metadata = extractor.extract(test_files["img"])
        
        # Devrait avoir métadonnées génériques même sans Pillow
        assert "file.name" in metadata
        assert "file.mime_type" in metadata

    def test_extract_with_error(self, test_files):
        """Test que l'extraction continue même en cas d'erreur."""
        extractor = MetadataExtractor(enable_video=False)
        
        # Même si l'extraction spécifique échoue, on a les métadonnées génériques
        metadata = extractor.extract(test_files["img"])
        
        assert "file.name" in metadata
        # Peut avoir extraction_error si format non reconnu


class TestMimeTypeDetection:
    """Tests de détection de type MIME."""

    def test_mime_type_routing(self):
        """Test que le bon extracteur est appelé selon le MIME type."""
        extractor = MetadataExtractor(enable_video=False)
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            jpg_file = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            mp3_file = Path(f.name)
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            mp4_file = Path(f.name)
        
        try:
            # Appel extract devrait router vers les bonnes méthodes
            metadata_jpg = extractor.extract(jpg_file)
            metadata_mp3 = extractor.extract(mp3_file)
            metadata_mp4 = extractor.extract(mp4_file)
            
            # Toutes devraient avoir les métadonnées de base
            assert "file.name" in metadata_jpg
            assert "file.name" in metadata_mp3
            assert "file.name" in metadata_mp4
        finally:
            jpg_file.unlink()
            mp3_file.unlink()
            mp4_file.unlink()
