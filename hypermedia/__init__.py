"""Hypermedia - Librairie Python pour gestion décentralisée d'hypermedia.

Ce package fournit une architecture à deux couches :
- HM-Drive : Système de fichiers distribué avec déduplication
- HM-Scene : Scènes dynamiques pour navigation hypermedia

Exemple d'usage :
    >>> from hypermedia.drive import MediaCollection
    >>> collection = MediaCollection("Ma Collection")
    >>> media_id = collection.add_media("/path/to/image.jpg")
"""

__version__ = "0.1.0"
__author__ = "Tristan Vanrullen"
__email__ = "tristan.vanrullen@example.com"
__license__ = "MIT"

# Imports publics de l'API
from hypermedia.drive import MediaCollection  # noqa: F401

__all__ = [
    "MediaCollection",
    "__version__",
]
