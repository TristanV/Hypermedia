# Guide d'installation - Hypermedia

Ce guide vous accompagne dans l'installation et la configuration du système Hypermedia.

---

## Prérequis

### Système
- **Python** : 3.10 ou supérieur
- **Système d'exploitation** : Linux, macOS, ou Windows
- **Espace disque** : Minimum 100 MB pour l'installation, plus espace pour vos médias

### Dépendances optionnelles

Pour bénéficier de toutes les fonctionnalités :

- **ffmpeg/ffprobe** : Extraction de métadonnées vidéo
  - Ubuntu/Debian : `sudo apt install ffmpeg`
  - macOS : `brew install ffmpeg`
  - Windows : Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html)

---

## Installation standard

### 1. Créer un environnement virtuel

```bash
# Créer l'environnement
python -m venv venv

# Activer l'environnement
# Sur Linux/macOS :
source venv/bin/activate

# Sur Windows :
venv\Scripts\activate
```

### 2. Installer depuis PyPI (bientôt disponible)

```bash
pip install hypermedia
```

### 3. Installer depuis les sources

```bash
# Cloner le dépôt
git clone https://github.com/TristanV/hypermedia.git
cd hypermedia

# Installer en mode développement
pip install -e .

# Ou installation standard
pip install .
```

---

## Installation pour le développement

Si vous souhaitez contribuer au projet :

```bash
# Cloner le dépôt
git clone https://github.com/TristanV/hypermedia.git
cd hypermedia

# Installer les dépendances de développement
pip install -r requirements-dev.txt

# Installer en mode éditable
pip install -e .

# Installer les hooks pre-commit
pre-commit install
```

### Lancer les tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=hypermedia --cov-report=html

# Tests spécifiques
pytest tests/test_models.py
```

---

## Vérification de l'installation

Vérifiez que l'installation s'est bien déroulée :

```python
import hypermedia
print(hypermedia.__version__)

from hypermedia.drive import DatabaseManager, MediaCollection
print("Installation réussie !")
```

### Vérifier les fonctionnalités optionnelles

```python
from hypermedia.drive.metadata_extractor import MetadataExtractor

extractor = MetadataExtractor()

if extractor.ffprobe_available:
    print("✓ Support vidéo activé (ffprobe détecté)")
else:
    print("⚠ Support vidéo désactivé (ffprobe non trouvé)")
```

---

## Configuration

### Structure de base

Hypermedia crée automatiquement la structure suivante :

```
votre_projet/
├── hypermedia.db          # Base de données SQLite
└── storage/                # Répertoire de stockage
    ├── media/             # Médias avec sharding
    │   ├── ab/
    │   │   └── cd/
    │   │       └── abcd1234...jpg
    │   └── ...
    └── temp/              # Fichiers temporaires
```

### Variables d'environnement (optionnel)

```bash
# Chemin de la base de données
export HYPERMEDIA_DB_PATH="/path/to/hypermedia.db"

# Chemin du stockage
export HYPERMEDIA_STORAGE_PATH="/path/to/storage"

# Niveau de logging
export HYPERMEDIA_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

---

## Désinstallation

```bash
# Désinstaller le package
pip uninstall hypermedia

# Supprimer les données (optionnel)
rm -rf hypermedia.db storage/
```

---

## Dépannage

### Problème : "ModuleNotFoundError: No module named 'hypermedia'"

**Solution** : Vérifiez que l'environnement virtuel est activé et que l'installation a réussi.

```bash
source venv/bin/activate
pip list | grep hypermedia
```

### Problème : Erreur SQLite "database is locked"

**Solution** : Assurez-vous qu'une seule instance accède à la base de données.

### Problème : "ffprobe not found"

**Solution** : Installez ffmpeg ou désactivez le support vidéo :

```python
MetadataExtractor(enable_video=False)
```

### Problème : Permissions de fichiers

**Solution** : Vérifiez les permissions du répertoire de stockage :

```bash
chmod -R 755 storage/
```

---

## Prochaines étapes

Félicitations ! Hypermedia est installé. Consultez maintenant :

- **[Quick Start](quickstart.md)** : Premiers pas en 5 minutes
- **[Référence API](api_reference.md)** : Documentation complète de l'API
- **[Exemples](../examples/)** : Exemples d'utilisation avancés

---

**Besoin d'aide ?** Ouvrez une issue sur [GitHub](https://github.com/TristanV/hypermedia/issues).
