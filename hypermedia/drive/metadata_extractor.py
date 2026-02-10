"""Extraction de métadonnées depuis fichiers média.

Ce module extrait automatiquement les métadonnées des fichiers
média (EXIF, ID3, métadonnées vidéo, etc.).
"""

import json
import logging
import mimetypes
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Import optionnel pour support images
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow not available - image metadata extraction disabled")

# Import optionnel pour support audio
try:
    import mutagen
    from mutagen.easyid3 import EasyID3
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logger.warning("Mutagen not available - audio metadata extraction disabled")


class MetadataExtractor:
    """Extracteur de métadonnées multiformat.

    Supporte :
    - Images : EXIF, IPTC, XMP (via Pillow)
    - Audio : ID3, Vorbis comments, APE (via Mutagen)
    - Vidéo : métadonnées conteneur (via ffprobe)
    - Documents : métadonnées de base

    Example:
        >>> extractor = MetadataExtractor()
        >>> metadata = extractor.extract("/path/to/photo.jpg")
        >>> print(metadata.get("exif.camera_model"))
    """

    def __init__(self, enable_video: bool = True):
        """Initialise l'extracteur.
        
        Args:
            enable_video: Active l'extraction vidéo (nécessite ffprobe)
        """
        self.enable_video = enable_video
        self._check_ffprobe()

    def _check_ffprobe(self) -> bool:
        """Vérifie si ffprobe est disponible.
        
        Returns:
            True si ffprobe est disponible
        """
        try:
            result = subprocess.run(
                ["ffprobe", "-version"],
                capture_output=True,
                timeout=5
            )
            self.ffprobe_available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.ffprobe_available = False
            if self.enable_video:
                logger.warning("ffprobe not available - video metadata extraction disabled")
        return self.ffprobe_available

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extrait les métadonnées d'un fichier.

        Args:
            file_path: Chemin du fichier

        Returns:
            Dictionnaire de métadonnées extraites

        Example:
            >>> metadata = extractor.extract(Path("image.jpg"))
            >>> print(metadata.keys())
            dict_keys(['file.size', 'file.modified_at', 'exif.camera', ...])
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        mime_type = mimetypes.guess_type(str(file_path))[0]
        metadata = self._extract_generic_metadata(file_path, mime_type)

        try:
            if mime_type and mime_type.startswith("image/"):
                metadata.update(self._extract_image_metadata(file_path))
            elif mime_type and mime_type.startswith("audio/"):
                metadata.update(self._extract_audio_metadata(file_path))
            elif mime_type and mime_type.startswith("video/"):
                metadata.update(self._extract_video_metadata(file_path))
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            metadata["extraction_error"] = str(e)

        return metadata

    def _extract_generic_metadata(self, file_path: Path, mime_type: Optional[str]) -> Dict[str, Any]:
        """Extrait métadonnées génériques (taille, dates, etc.).
        
        Args:
            file_path: Chemin du fichier
            mime_type: Type MIME du fichier
            
        Returns:
            Dictionnaire de métadonnées génériques
        """
        stat = file_path.stat()
        return {
            "file.name": file_path.name,
            "file.extension": file_path.suffix,
            "file.size": stat.st_size,
            "file.created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "file.modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "file.mime_type": mime_type or "application/octet-stream",
        }

    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extrait métadonnées EXIF des images.
        
        Args:
            file_path: Chemin du fichier image
            
        Returns:
            Dictionnaire de métadonnées EXIF
        """
        if not PILLOW_AVAILABLE:
            return {"image.pillow_unavailable": True}

        metadata = {}
        
        try:
            with Image.open(file_path) as img:
                # Dimensions
                metadata["image.width"] = img.width
                metadata["image.height"] = img.height
                metadata["image.format"] = img.format
                metadata["image.mode"] = img.mode

                # EXIF data
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        
                        # Conversion de valeurs spéciales
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except:
                                value = str(value)
                        
                        # GPS data spéciale
                        if tag_name == "GPSInfo" and isinstance(value, dict):
                            gps_data = {}
                            for gps_tag_id, gps_value in value.items():
                                gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                gps_data[gps_tag_name] = gps_value
                            metadata["exif.gps"] = gps_data
                        else:
                            metadata[f"exif.{tag_name}"] = value

        except Exception as e:
            logger.debug(f"Could not extract image metadata from {file_path}: {e}")
            metadata["image.extraction_error"] = str(e)

        return metadata

    def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extrait métadonnées ID3/Vorbis de l'audio.
        
        Args:
            file_path: Chemin du fichier audio
            
        Returns:
            Dictionnaire de métadonnées audio
        """
        if not MUTAGEN_AVAILABLE:
            return {"audio.mutagen_unavailable": True}

        metadata = {}
        
        try:
            audio = mutagen.File(file_path)
            
            if audio is None:
                return {"audio.unsupported_format": True}

            # Informations techniques
            if hasattr(audio.info, 'length'):
                metadata["audio.duration"] = audio.info.length
            if hasattr(audio.info, 'bitrate'):
                metadata["audio.bitrate"] = audio.info.bitrate
            if hasattr(audio.info, 'sample_rate'):
                metadata["audio.sample_rate"] = audio.info.sample_rate
            if hasattr(audio.info, 'channels'):
                metadata["audio.channels"] = audio.info.channels

            # Tags
            if audio.tags:
                for key, value in audio.tags.items():
                    # Simplifier les clés
                    clean_key = key.lower().replace(':', '.').replace(' ', '_')
                    metadata[f"audio.{clean_key}"] = str(value[0]) if isinstance(value, list) else str(value)

        except Exception as e:
            logger.debug(f"Could not extract audio metadata from {file_path}: {e}")
            metadata["audio.extraction_error"] = str(e)

        return metadata

    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extrait métadonnées vidéo via ffprobe.
        
        Args:
            file_path: Chemin du fichier vidéo
            
        Returns:
            Dictionnaire de métadonnées vidéo
        """
        if not self.enable_video or not self.ffprobe_available:
            return {"video.ffprobe_unavailable": True}

        metadata = {}
        
        try:
            # Utiliser ffprobe pour extraire les métadonnées
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    str(file_path)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Informations du conteneur
                if "format" in data:
                    fmt = data["format"]
                    metadata["video.format"] = fmt.get("format_name")
                    metadata["video.duration"] = float(fmt.get("duration", 0))
                    metadata["video.size"] = int(fmt.get("size", 0))
                    metadata["video.bitrate"] = int(fmt.get("bit_rate", 0))
                    
                    # Tags du conteneur
                    if "tags" in fmt:
                        for key, value in fmt["tags"].items():
                            metadata[f"video.tag.{key.lower()}"] = value

                # Informations des flux
                if "streams" in data:
                    for i, stream in enumerate(data["streams"]):
                        codec_type = stream.get("codec_type")
                        prefix = f"video.stream.{codec_type}.{i}"
                        
                        metadata[f"{prefix}.codec"] = stream.get("codec_name")
                        
                        if codec_type == "video":
                            metadata[f"{prefix}.width"] = stream.get("width")
                            metadata[f"{prefix}.height"] = stream.get("height")
                            metadata[f"{prefix}.fps"] = eval(stream.get("r_frame_rate", "0/1"))
                        elif codec_type == "audio":
                            metadata[f"{prefix}.sample_rate"] = stream.get("sample_rate")
                            metadata[f"{prefix}.channels"] = stream.get("channels")

        except subprocess.TimeoutExpired:
            logger.warning(f"ffprobe timeout for {file_path}")
            metadata["video.extraction_timeout"] = True
        except Exception as e:
            logger.debug(f"Could not extract video metadata from {file_path}: {e}")
            metadata["video.extraction_error"] = str(e)

        return metadata
