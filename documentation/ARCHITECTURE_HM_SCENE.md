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
- La **navigation** (modes de déambulat