"""Système de déduplication basé sur les checksums.

Ce module gère la détection des fichiers en double dans les collections
en utilisant les checksums BLAKE2b.
"""

from typing import Optional, Dict, Set
from enum import Enum


class DuplicationPolicy(Enum):
    """Politique de gestion des doublons.
    
    IGNORE: Ignorer les doublons (ne pas ajouter)
    REFERENCE: Créer une référence vers le fichier existant
    ALERT: Alerter l'utilisateur et demander confirmation
    ALLOW: Autoriser les doublons (créer une copie)
    """
    IGNORE = "ignore"
    REFERENCE = "reference"
    ALERT = "alert"
    ALLOW = "allow"


class DeduplicationIndex:
    """Index des checksums pour détection rapide des doublons.
    
    Attributes:
        checksums: Mapping checksum -> media_id
        policy: Politique de gestion des doublons
    
    Example:
        >>> index = DeduplicationIndex(policy=DuplicationPolicy.IGNORE)
        >>> duplicate = index.check_duplicate(checksum)
    """
    
    def __init__(self, policy: DuplicationPolicy = DuplicationPolicy.REFERENCE):
        """Initialise l'index de déduplication.
        
        Args:
            policy: Politique de gestion des doublons
        """
        self.checksums: Dict[str, str] = {}
        self.policy = policy
    
    def check_duplicate(self, checksum: str) -> Optional[str]:
        """Vérifie si un checksum existe déjà.
        
        Args:
            checksum: Checksum BLAKE2b à vérifier
        
        Returns:
            media_id du doublon si existe, None sinon
        """
        # TODO: Chercher dans l'index
        raise NotImplementedError("Méthode à implémenter")
    
    def register(self, checksum: str, media_id: str) -> None:
        """Enregistre un nouveau checksum dans l'index.
        
        Args:
            checksum: Checksum du fichier
            media_id: Identifiant du média
        """
        # TODO: Ajouter à l'index
        raise NotImplementedError("Méthode à implémenter")
    
    def remove(self, checksum: str) -> None:
        """Retire un checksum de l'index.
        
        Args:
            checksum: Checksum à retirer
        """
        # TODO: Retirer de l'index
        raise NotImplementedError("Méthode à implémenter")
