# Triangulation de Delaunay

Application Python permettant de construire interactivement une **triangulation de Delaunay**, de générer le **diagramme de Voronoi** associé et d'effectuer quelques opérations d'analyse spatiale.

**Cours :** GMT-7035 — Structures de données géométriques et algorithmiques en SIG  
**Université Laval — Département des sciences géomatiques**  
**Réalisé par :** Corinne Dumais  
**Date :** 20 mars 2023

## Description

L'application permet à l'utilisateur d'insérer des points dans un triangle universel et de construire progressivement une triangulation de Delaunay. Chaque nouveau point est localisé dans le maillage, inséré dans le triangle correspondant, puis les triangles sont optimisés au besoin par échange de diagonales.

L'application permet également de :

- visualiser le diagramme de Voronoi;
- trouver le voisin le plus proche d'un point donné;
- trouver les voisins immédiats d'un sommet;
- réinitialiser la triangulation.

## Algorithmes implémentés

| Fonction | Description |
|---|---|
| `frame()` | Initialise le triangle universel |
| `determinant()` | Détermine la position d'un point par rapport à un segment |
| `walk()` | Recherche le triangle contenant un point |
| `insert()` | Insère un nouveau point dans le maillage |
| `optim()` | Vérifie et optimise les triangles |
| `swap()` | Effectue un échange de diagonales |
| `tracage_delaunay()` | Construit la triangulation de Delaunay |
| `tracage_voronoi()` | Génère le diagramme de Voronoi |
| `voisin_plus_proche()` | Recherche le sommet le plus proche d'un point |
| `voisins_immediats()` | Identifie les voisins immédiats d'un sommet |

La structure du maillage repose sur une représentation **TIN (Triangulated Irregular Network)** dans laquelle chaque triangle conserve ses sommets ainsi que les identifiants de ses triangles adjacents.

## Fonctionnement

La triangulation est construite de manière incrémentale :

1. Un triangle universel est créé.
2. L'utilisateur active l'insertion de points.
3. Un clic à l'intérieur du triangle ajoute un nouveau sommet.
4. `walk()` recherche le triangle contenant le nouveau point.
5. `insert()` divise ce triangle en trois nouveaux triangles.
6. `optim()` vérifie la propriété de Delaunay et effectue des échanges de diagonales au besoin.
7. Une fois l'insertion terminée, le diagramme de Voronoi ou les fonctions d'analyse spatiale peuvent être utilisés.

## Interface

L'application comporte trois menus principaux.

### Application

- **Réinitialiser** : recommence une nouvelle triangulation.
- **Exit** : ferme l'application.

### Triangulation

- **Triangulation Delaunay → Commencer** : permet d'insérer des points.
- **Arrêter** : termine l'insertion.
- **Diagramme Voronoi** : affiche le diagramme de Voronoi associé.

### Analyse spatiale

- **Voisin le plus proche** : permet de cliquer sur un point quelconque et d'identifier le sommet le plus proche.
- **Voisins immédiats** : permet de sélectionner un sommet par son numéro et d'afficher ses voisins dans le maillage.

## Installation

### Prérequis

- Python 3
- NumPy
- Tkinter

Installer NumPy au besoin :

```bash
pip install numpy
