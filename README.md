# Analyseur d'Images Pathologiques

Ce projet est un prorotype d'application d'analyse d'images pathologiques qui permet de charger une image, d'analyser les cellules présentes, de générer un rapport clinique détaillé et d'afficher une image annotée avec les anomalies détectées. 
A ce stade il s'agit plutôt de comptage et d'analyse de cellules et d'anomalies. Reste à affiner sur des exemples spécifiques et d'ajouter la couche d'expertise scientifique médicale pour pouvoir en déduire des indices d'aide au diagnostique.

## Prérequis


Installation simple avec un rappatriement du repo sur votre local : 

```bash
git clone https://github.com/friteuseb/anapath
```
Assurez-vous d'avoir installé les bibliothèques Python nécessaires en exécutant :

```bash
pip install -r requirements.txt
```
Lancement de l'interface d'analyse avec : 

```bash
python3 pathology_image_gui.py
```

## Utilisation

1. **Charger une image** : Cliquez sur le bouton "Charger une image" pour sélectionner une image de votre système de fichiers.
2. **Analyser l'image** : Cliquez sur le bouton "Analyser l'image" pour analyser les cellules de l'image chargée.
3. **Voir le rapport et l'image annotée** : Le rapport détaillé et l'image annotée seront affichés dans l'interface.


## Fonctionnement de l'analyse d'images 

1. **Chargement de l'image :**

Utilisation de OpenCV (cv2.imread) pour charger l'image.
Conversion de l'espace couleur BGR à RGB.


2. **Prétraitement de l'image :**

Conversion de l'image RGB en espace couleur LAB.
Application d'une égalisation d'histogramme adaptative limitée en contraste (CLAHE) sur le canal L pour améliorer le contraste.
Reconversion en RGB.


2. **Segmentation des cellules :**

Conversion de l'image prétraitée en niveaux de gris.
Utilisation d'un seuillage adaptatif (cv2.adaptiveThreshold) pour isoler les cellules.
Application d'opérations morphologiques (ouverture et dilatation) pour nettoyer l'image et mieux séparer les cellules.


3. **Extraction des caractéristiques :**

Utilisation de skimage.measure.label pour étiqueter les régions connectées.
Extraction des propriétés de chaque région (aire, excentricité) avec skimage.measure.regionprops_table.
Calcul manuel de l'intensité moyenne pour chaque région.


4. **Classification des cellules :**

Création d'un DataFrame pandas avec les caractéristiques extraites.
Vérification et gestion des colonnes manquantes.
Suppression des lignes avec des valeurs manquantes.
Utilisation de l'algorithme K-means (de scikit-learn) pour classifier les cellules en 3 types différents basés sur leurs caractéristiques.


5. **Génération du rapport :**

Calcul du nombre total de cellules.
Détermination de la distribution des types de cellules.
Création d'un rapport textuel avec ces informations.


## Structure du projet

- `pathology_image_analyzer.py` : Contient la logique d'analyse des images.
- `pathology_image_gui.py` : Contient l'interface utilisateur pour interagir avec l'application.
- `requirements.txt` : Liste des dépendances Python nécessaires pour exécuter le projet.

## Exemple

### Interface Utilisateur

![Interface Utilisateur](screenshot.png)

### Rapport d'Analyse

```plaintext
Rapport détaillé d'analyse des cellules:

Cellule 1:
  - Surface (aire): 351.0 unités carrées
  - Interprétation: Grande
  - Périmètre: 111.656854 unités
  - Interprétation: Élevé
  - Excentricité: 0.96 (proche de 0 pour une forme circulaire, proche de 1 pour une forme elliptique)
  - Interprétation: Anormale
  - Solidité: 0.70 (proportion de la cellule qui est solide)
  - Interprétation: Faible
  - Type de cellule: Grande
```

### Image Annotée

![Image Annotée](annotated_image.png)

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements proposés.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.