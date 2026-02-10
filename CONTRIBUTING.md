# Guide de Contribution - Hypermedia

Merci de votre intérêt pour contribuer au projet Hypermedia ! Ce guide vous aidera à bien démarrer.

## Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Configuration de l'Environnement](#configuration-de-lenvironnement)
- [Standards de Code](#standards-de-code)
- [Process de Pull Request](#process-de-pull-request)
- [Reporting de Bugs](#reporting-de-bugs)
- [Propositions de Fonctionnalités](#propositions-de-fonctionnalités)

## Code de Conduite

En participant à ce projet, vous vous engagez à respecter notre code de conduite :

- Être respectueux et inclusif
- Accepter les critiques constructives
- Se concentrer sur ce qui est le mieux pour la communauté
- Faire preuve d'empathie envers les autres membres

## Comment Contribuer

Il existe plusieurs façons de contribuer :

1. **Signaler des bugs** - Utilisez les GitHub Issues
2. **Proposer des fonctionnalités** - Ouvrez une discussion
3. **Améliorer la documentation** - Toujours apprécié !
4. **Soumettre du code** - Via des Pull Requests

## Configuration de l'Environnement

### 1. Forker et Cloner

```bash
# Forker le projet sur GitHub, puis :
git clone https://github.com/VOTRE_USERNAME/Hypermedia.git
cd Hypermedia
```

### 2. Créer un Environnement Virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les Dépendances

```bash
# Dépendances de développement
pip install -r requirements-dev.txt

# Installer le package en mode éditable
pip install -e .
```

### 4. Configurer Pre-commit

```bash
pre-commit install
```

### 5. Vérifier l'Installation

```bash
# Exécuter les tests
pytest

# Vérifier le formatage
black --check .

# Vérifier les types
mypy hypermedia/
```

## Standards de Code

### Style Python

Nous suivons les standards suivants :

- **PEP 8** pour le style général
- **Black** pour le formatage automatique (ligne 88 caractères)
- **isort** pour le tri des imports
- **Type hints** obligatoires pour les fonctions publiques
- **Docstrings** au format Google ou NumPy

### Exemple de Docstring

```python
def compute_checksum(file_path: Path) -> str:
    """Calcule le checksum BLAKE2b d'un fichier.
    
    Args:
        file_path: Chemin du fichier à hasher
    
    Returns:
        Checksum hexadécimal du fichier
    
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    
    Example:
        >>> checksum = compute_checksum(Path("image.jpg"))
    """
    pass
```

### Tests

- **Couverture minimale** : 80%
- Utilisez `pytest` pour les tests
- Nommez les fichiers de test `test_*.py`
- Incluez des tests unitaires ET d'intégration si pertinent

```bash
# Exécuter les tests
pytest

# Avec couverture
pytest --cov=hypermedia --cov-report=html
```

## Process de Pull Request

### 1. Créer une Branche

```bash
git checkout -b feature/ma-fonctionnalite
# ou
git checkout -b fix/mon-bug
```

### 2. Faire vos Modifications

- Écrivez du code clair et commenté
- Ajoutez des tests pour votre code
- Mettez à jour la documentation si nécessaire
- Suivez les standards de code

### 3. Committer

```bash
# Les pre-commit hooks vérifieront automatiquement
git add .
git commit -m "feat: ajoute la fonctionnalité X"
```

Format des messages de commit :

- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation uniquement
- `style:` Formatage, points-virgules manquants, etc.
- `refactor:` Refactoring de code
- `test:` Ajout de tests
- `chore:` Maintenance

### 4. Pousser et Ouvrir une PR

```bash
git push origin feature/ma-fonctionnalite
```

Puis ouvrez une Pull Request sur GitHub avec :

- **Titre clair** : `[Feature] Ajout du système de tags`
- **Description détaillée** :
  - Qu'est-ce qui change ?
  - Pourquoi ce changement ?
  - Comment tester ?
- **Références** aux issues reliées (`Fixes #123`)

### 5. Review et Merge

- Répondez aux commentaires de review
- Faites les ajustements demandés
- Une fois approuvée, votre PR sera mergée !

## Reporting de Bugs

Pour signaler un bug, ouvrez une issue avec :

### Template de Bug Report

```markdown
**Description du bug**
Description claire et concise du bug.

**Pour Reproduire**
Étapes pour reproduire le comportement :
1. ...
2. ...
3. ...

**Comportement Attendu**
Ce qui devrait se passer normalement.

**Comportement Réel**
Ce qui se passe actuellement.

**Captures d'écran**
Si applicable, ajoutez des captures d'écran.

**Environnement**
- OS: [ex: Ubuntu 22.04]
- Python: [ex: 3.11.5]
- Version Hypermedia: [ex: 0.1.0]

**Contexte Additionnel**
Toute autre information pertinente.
```

## Propositions de Fonctionnalités

Pour proposer une nouvelle fonctionnalité :

1. **Vérifiez** qu'elle n'existe pas déjà dans les issues
2. **Ouvrez une discussion** pour valider l'idée
3. **Décrivez** :
   - Le problème que ça résout
   - La solution proposée
   - Des alternatives considérées
   - Impact sur l'architecture existante

## Questions ?

Si vous avez des questions, n'hésitez pas à :

- Ouvrir une issue GitHub
- Consulter la [documentation](documentation/)
- Contacter les mainteneurs

---

Merci encore pour votre contribution ! 🚀
