"""Exemple de calcul de checksums BLAKE2b.

Cet exemple montre comment calculer et vérifier des checksums.
"""

from pathlib import Path
import tempfile
# from hypermedia.drive.checksum import compute_blake2b, verify_integrity


def main():
    """Exemple de checksums."""
    print("=" * 60)
    print("Hypermedia - Démonstration des checksums BLAKE2b")
    print("=" * 60)
    print()

    # Créer un fichier de test temporaire
    print("1. Création d'un fichier de test...")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = Path(f.name)
        f.write("Contenu de test pour Hypermedia")
    print(f"   ✓ Fichier créé : {test_file}")
    print()

    # TODO: Calculer checksum (quand implémenté)
    print("2. Calcul du checksum BLAKE2b...")
    print("   [Non implémenté] La fonction compute_blake2b() sera disponible prochainement.")
    print()

    # TODO: Vérifier intégrité (quand implémenté)
    print("3. Vérification d'intégrité...")
    print("   [Non implémenté] La fonction verify_integrity() sera disponible prochainement.")
    print()

    # Nettoyage
    test_file.unlink()
    print("=" * 60)
    print("✓ Exemple terminé")
    print("=" * 60)


if __name__ == "__main__":
    main()
