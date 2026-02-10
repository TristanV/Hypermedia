# Architecture HM-Scene - Mise en Scène Dynamique

## Introduction

HM-Scene est la couche de présentation d'Hypermedia, responsable de la mise en scène et de la navigation dans les collections de médias. Elle permet de définir **comment** les médias sont présentés, organisés et explorés par l'utilisateur.

### Inspirations

- **CSS** : cascade, sélecteurs, propriétés, media queries
- **React** : composants, état, rendu déclaratif
- **Processing** : creative coding, visualisation dynamique
- **D3.js** : visualisation de données, transitions

### Objectifs

1. **Déclaratif** : définir l'apparence plutôt que les étapes
2. **Adaptable** : s'ajuster automatiquement au support (desktop, mobile, projection)
3. **Interactif** : réagir aux actions utilisateur (clic, hover, scroll)
4. **Performant** : rendu fluide de grandes collections (500+ médias)

---

## Concept de Scène

### Définition

Une **scène** est une vue configurée sur une collection, définissant :
- Le **layout** (disposition spatiale)
- La **navigation** (modes de déambulation)
- Les **interactions** (affordances utilisateur)
- L'**esthétique** (styles visuels)

### Types de scènes

| Type | Description | Cas d'usage |
|------|-------------|-------------|
| **Galerie** | Grille de médias avec pagination | Portfolio, catalogue |
| **Timeline** | Défilement chronologique | Journal, événements |
| **Graphe** | Visualisation des relations | Généalogie, connexions |
| **Mosaïque** | Arrangement adaptatif (masonry) | Pinterest-like |
| **Cinématique** | Diaporama automatique | Présentation, exposition |
| **Immersive** | Navigation 3D (panorama, VR) | Visites virtuelles |

### Configuration de scène

```yaml
scene:
  name: "Portfolio 2024"
  collection: "projects/2024"
  type: gallery
  layout: grid
  pagination: 24
  sort: created_at DESC
  filters:
    tags: [published]
    format: [image, video]
```

---

## Langage HM-DSS (Hypermedia Dynamic Scene Sheet)

### Philosophie

- **Déclaratif** : comme CSS, décrire le résultat souhaité
- **Cascade** : héritage de propriétés
- **Sélecteurs** : cibler des sous-ensembles de médias
- **Extensible** : custom properties et fonctions

### Syntaxe de base

```css
/* Définition de scène */
@scene portfolio {
    collection: "projects/2024";
    layout: grid;
    columns: 3;
    gap: 20px;
}

/* Sélecteurs de médias */
media {
    width: 100%;
    aspect-ratio: 1/1;
    object-fit: cover;
}

/* Sélecteur par type */
media[type="video"] {
    border: 2px solid #ff0000;
    play-on-hover: true;
}

/* Sélecteur par tag */
media[tag~="featured"] {
    grid-column: span 2;
    grid-row: span 2;
    z-index: 10;
}

/* Pseudo-classes */
media:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

media:first-child {
    border: 4px solid gold;
}
```

---

## Sélecteurs HM-DSS

### Sélecteurs de base

```css
/* Tous les médias */
media { ... }

/* Par type MIME */
media[type="image"] { ... }
media[type="video"] { ... }

/* Par format */
media[format="mp4"] { ... }
media[format="jpg"] { ... }

/* Par collection */
media[collection="landscapes"] { ... }
```

### Sélecteurs d'attributs

```css
/* Tag exact */
media[tag="nature"] { ... }

/* Contient tag */
media[tag~="nature"] { ... }

/* Condition numérique */
media[width > 1920] { ... }
media[size < 1MB] { ... }

/* Commence par */
media[created_at ^= "2024"] { ... }
```

### Sélecteurs de relations

```css
/* Ancêtres d'un média */
media:ancestor(media_id) { ... }

/* Descendants */
media:descendant(media_id) { ... }

/* Relations typées */
media:related(media_id, type="similar") { ... }
```

### Pseudo-classes

```css
/* États interactifs */
media:hover { ... }
media:active { ... }
media:focus { ... }

/* Position */
media:first-child { ... }
media:last-child { ... }
media:nth-child(2n) { ... }  /* Pairs */

/* États intrinsèques */
media:has-thumbnail { ... }
media:is-composite { ... }
media:is-local { ... }
```

---

## Propriétés HM-DSS

### Layout

```css
layout: grid | list | masonry | timeline | graph;
columns: <number> | auto;
rows: <number> | auto;
gap: <length>;
align-items: start | center | end;
justify-items: start | center | end;
```

### Dimensions

```css
width: <length> | <percentage> | auto;
height: <length> | <percentage> | auto;
aspect-ratio: <ratio>;  /* 16/9, 4/3, 1/1 */
object-fit: cover | contain | fill | none;
```

### Espacements

```css
margin: <length>;
padding: <length>;
```

### Visuels

```css
border: <width> <style> <color>;
border-radius: <length>;
box-shadow: <offset-x> <offset-y> <blur> <color>;
opacity: <number>;  /* 0.0 - 1.0 */
filter: blur(<length>) | brightness(<percentage>) | contrast(<percentage>);
```

### Transformations

```css
transform: translate(<x>, <y>) | scale(<factor>) | rotate(<angle>);
transform-origin: <position>;
```

### Transitions

```css
transition: <property> <duration> <easing>;
/* Exemple: transform 0.3s ease-in-out */
```

### Navigation

```css
cursor: pointer | grab | zoom-in;
play-on-hover: true | false;  /* Vidéos */
zoom-level: <number>;  /* Images */
```

### Pagination

```css
items-per-page: <number>;
pagination-style: numbers | dots | infinite-scroll;
```

---

## Adaptation Multi-Support

### Media Queries HM-DSS

```css
/* Desktop */
@media (min-width: 1024px) {
    @scene portfolio {
        columns: 4;
        gap: 30px;
    }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
    @scene portfolio {
        columns: 2;
        gap: 20px;
    }
}

/* Mobile */
@media (max-width: 767px) {
    @scene portfolio {
        layout: list;
        gap: 10px;
    }
}

/* Projection / Grand écran */
@media (min-width: 1920px) {
    @scene portfolio {
        columns: 6;
        gap: 40px;
    }
}

/* Orientation */
@media (orientation: portrait) {
    @scene portfolio {
        columns: 1;
    }
}
```

### Détection automatique

```python
from hypermedia.scene import DeviceDetector

detector = DeviceDetector()
device_info = detector.detect(user_agent, viewport)
# → {
#     'type': 'desktop',
#     'width': 1920,
#     'height': 1080,
#     'ratio': 16/9,
#     'touch': False,
#     'orientation': 'landscape'
# }
```

---

## Interactivité et États

### Événements supportés

```css
media:click {
    action: open-lightbox;
    preload: siblings;
}

media[type="video"]:hover {
    action: play-preview;
    muted: true;
}

media:drag {
    action: reorder;
    persist: true;
}

media:dblclick {
    action: fullscreen;
}

@scene:scroll {
    action: lazy-load;
    threshold: 200px;
}
```

### État de la scène

```python
class SceneState:
    def __init__(self):
        self.history = []  # Navigation history
        self.filters = {}  # Active filters
        self.sort = "created_at DESC"
        self.scroll_position = 0
        self.bookmarks = []
    
    def save(self):
        """Sauvegarde l'état en local storage"""
    
    def restore(self):
        """Restaure l'état au retour"""
```

---

## Templates Prédéfinis

### Template "Gallery Classic"

```css
@scene gallery-classic {
    layout: grid;
    columns: auto-fill minmax(250px, 1fr);
    gap: 15px;
}

media {
    aspect-ratio: 1/1;
    object-fit: cover;
    border-radius: 8px;
    transition: transform 0.3s;
}

media:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}
```

### Template "Timeline"

```css
@scene timeline {
    layout: timeline;
    sort: created_at ASC;
    group-by: month;
}

media {
    width: 200px;
    margin-bottom: 20px;
}

.timeline-marker {
    font-size: 18px;
    font-weight: bold;
    margin: 40px 0 20px;
}
```

### Template "Graph Viewer"

```css
@scene graph {
    layout: graph;
    physics: force-directed;
    show-relations: [parent, child, similar];
}

media {
    node-size: 80px;
    border-radius: 50%;
}

media:ancestor {
    border: 3px solid #00ff00;
}

media:descendant {
    border: 3px solid #0088ff;
}

.edge {
    stroke-width: 2px;
    stroke: #cccccc;
}

.edge[type="parent"] {
    stroke: #00ff00;
}
```

### Template "Masonry"

```css
@scene masonry {
    layout: masonry;
    columns: 4;
    gap: 10px;
}

media {
    width: 100%;
    height: auto;  /* Hauteur naturelle */
    break-inside: avoid;
}
```

---

## Moteur de Rendu

### Architecture

```python
class SceneEngine:
    def __init__(self, drive: HMDrive):
        self.drive = drive
        self.parser = DSSParser()
        self.cache = {}
    
    def load_scene(self, scene_id: str) -> Scene:
        """Charge une scène depuis la DB"""
    
    def parse_dss(self, dss_content: str) -> SceneDefinition:
        """Parse le code HM-DSS en AST"""
    
    def render(self, scene: Scene, target: str) -> RenderOutput:
        """Rend la scène pour le target spécifié"""
    
    def apply_selector(self, selector: str, media_list: List[Media]) -> List[Media]:
        """Applique un sélecteur à une liste de médias"""
    
    def compute_layout(self, scene: Scene, viewport: Viewport) -> Layout:
        """Calcule le layout pour le viewport"""
```

### Backends de rendu

**HTML/CSS/JS** (web)
```python
from hypermedia.scene.renderers import HTMLRenderer

renderer = HTMLRenderer()
output = renderer.render(scene, viewport)
# → {'html': '...', 'css': '...', 'js': '...'}
```

**Terminal** (TUI)
```python
from hypermedia.scene.renderers import TerminalRenderer

renderer = TerminalRenderer()
renderer.render(scene, terminal_size=(80, 24))
```

**Export statique**
```python
from hypermedia.scene.renderers import StaticRenderer

renderer = StaticRenderer()
renderer.export_site(scene, output_dir="site/")
```

### Pipeline de rendu

```
1. Parsing HM-DSS → AST (Abstract Syntax Tree)
2. Résolution des sélecteurs → liste de médias filtrée
3. Application des propriétés → styles calculés
4. Calcul du layout → positions absolues
5. Rendu final → HTML/TUI/autre format
```

### Optimisations

- **Cache des AST** : parse une seule fois
- **Virtualisation** : rendu uniquement des éléments visibles
- **Lazy loading** : chargement des thumbnails à la demande
- **Debouncing** : recalculs lors de resize/scroll limités

```python
from hypermedia.scene import VirtualScroller

scroller = VirtualScroller(
    total_items=1000,
    viewport_height=800,
    item_height=200,
    buffer=5  # Items préchargés hors viewport
)

visible_items = scroller.get_visible_range()
# → [12, 13, 14, 15, 16]  # Seulement 5 items rendus
```

---

## Exemple Complet

### Fichier de scène : portfolio.hmdss

```css
/* Portfolio 2024 - Galerie adaptative */

@scene portfolio {
    collection: "projects/2024";
    layout: grid;
    sort: created_at DESC;
    pagination: infinite-scroll;
}

/* Grille responsive */
@media (min-width: 1200px) {
    @scene portfolio { columns: 4; gap: 30px; }
}

@media (min-width: 768px) and (max-width: 1199px) {
    @scene portfolio { columns: 3; gap: 20px; }
}

@media (max-width: 767px) {
    @scene portfolio { columns: 1; gap: 10px; }
}

/* Styles de base */
media {
    aspect-ratio: 1/1;
    object-fit: cover;
    border-radius: 12px;
    transition: all 0.3s ease;
}

media:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}

/* Vidéos */
media[type="video"] {
    border: 3px solid #ff6b6b;
    play-on-hover: true;
}

/* Médias featured en grand */
media[tag~="featured"] {
    grid-column: span 2;
    grid-row: span 2;
    border: 4px solid gold;
}

/* Nouveaux médias (< 7 jours) */
media[created_at > "7 days ago"] {
    border: 2px solid #4ecdc4;
}

/* Actions */
media:click {
    action: open-lightbox;
    preload: 3;  /* 3 médias avant/après */
}

media:dblclick {
    action: fullscreen;
}
```

### Utilisation en Python

```python
from hypermedia import HMDrive, Scene, SceneEngine
from pathlib import Path

# Initialisation
drive = HMDrive(Path('/data/hypermedia'))
engine = SceneEngine(drive)

# Chargement du fichier HM-DSS
dss_content = Path('portfolio.hmdss').read_text()

# Création de la scène
collection = drive.get_collection('projects/2024')
scene = engine.create_scene(
    collection=collection,
    dss_content=dss_content,
    name="Portfolio 2024"
)

# Rendu pour un viewport donné
viewport = {'width': 1920, 'height': 1080}
output = engine.render(scene, target='html', viewport=viewport)

# Sauvegarde du rendu
Path('output/index.html').write_text(output['html'])
Path('output/styles.css').write_text(output['css'])
Path('output/script.js').write_text(output['js'])
```

---

## Conclusion

L'architecture HM-Scene et le langage HM-DSS fournissent un système puissant et flexible pour la mise en scène de collections de médias. L'approche déclarative inspirée de CSS permet une séparation nette entre contenu (HM-Drive) et présentation (HM-Scene), tout en offrant une grande expressivité pour créer des expériences de navigation riches et adaptées.

La combinaison de sélecteurs avancés, de media queries, et de templates prédéfinis permet de couvrir une large gamme de cas d'usage, des simples galeries aux visualisations complexes de graphes relationnels.

**Prochaine étape** : Guide de migration depuis prompt-imagine vers Hypermedia.
