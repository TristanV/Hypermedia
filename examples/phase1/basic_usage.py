"""Exemple d'utilisation basique de Hypermedia - Phase 1.

Cet exemple montre comment créer une collection et y ajouter des médias.
"""

from pathlib import Path
from hypermedia.drive import MediaCollection


def main():
    """Exemple principal."""
    print("=" * 60)
    print("Hypermedia - Exemple d'utilisation basique (Phase 1)")
    print("=" * 60)
    print()

    # Créer une collection
    print("1. Création d'une collection...")
    collection = MediaCollection(
        name="Ma Collection de Vacances",
        description="Photos et vidéos de mes vacances 2026"
    )
    print(f"   ✓ Collection créée : {collection.name}")
    print(f"   ✓ Stockage : {collection.storage_path}")
    print()

    # TODO: Ajouter des médias (quand implémenté)
    print("2. Ajout de médias...")
    print("   [Non implémenté] Les fonctionnalités d'ajout seront disponibles prochainement.")
    print()

    # TODO: Rechercher des médias (quand implémenté)
    print("3. Recherche de médias...")
    print("   [Non implémenté] Les fonctionnalités de recherche seront disponibles prochainement.")
    print()

    print("=" * 60)
    print("✓ Exemple terminé")
    print("=" * 60)


if __name__ == "__main__":
    main()
