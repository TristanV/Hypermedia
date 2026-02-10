"""Module HM-Drive - Couche de stockage décentralisé.

Ce module gère :
- Collections de médias locales et distribuées
- Checksums BLAKE2b pour intégrité et déduplication
- Base de données SQLite pour métadonnées
- Extraction et indexation de métadonnées enrichies
"""

from hypermedia.drive.collection import MediaCollection  # noqa: F401

__all__ = ["MediaCollection"]
