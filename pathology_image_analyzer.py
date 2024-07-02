import cv2
import numpy as np
from skimage import measure, morphology
import pandas as pd

class PathologyImageAnalyzer:
    def __init__(self):
        self.image = None
        self.processed_image = None
        self.cell_data = None
        self.sample_type = None

        # Define default thresholds for cell classification
        self.thresholds = {
            'sang': {
                'area': 3000,  # Adjusted based on average cell size
                'perimeter': 150,  # Adjusted to a more realistic value
                'eccentricity': 0.7,  # Increased to differentiate elongated shapes
                'solidity': 0.85  # Lowered to capture slightly irregular cells
            },
            'urine': {
                'area': 150,
                'perimeter': 70,
                'eccentricity': 0.6,
                'solidity': 0.75
            }
        }

    def set_sample_type(self, sample_type):
        if sample_type not in self.thresholds:
            raise ValueError("Type d'échantillon non supporté. Utilisez 'sang' ou 'urine'.")
        self.sample_type = sample_type

    def load_image(self, image_path):
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

    def preprocess_image(self):
        lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        self.processed_image = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

    def analyze(self, image_path):
        self.load_image(image_path)
        self.preprocess_image()
        binary = self.segment_cells()
        features = self.extract_features(binary)
        self.cell_data = self.classify_cells(features)
        return self.cell_data

    def segment_cells(self):
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        cleared = morphology.remove_small_objects(thresh.astype(bool), min_size=150)
        return cleared.astype(np.uint8)

    def extract_features(self, binary):
        labels = measure.label(binary)
        properties = measure.regionprops_table(labels, properties=('area', 'perimeter', 'eccentricity', 'solidity', 'bbox'))
        df = pd.DataFrame(properties)
        return df

    def classify_cells(self, features):
        thresholds = self.thresholds[self.sample_type]
        if self.sample_type == 'sang':
            features['type'] = np.where(
                (features['area'] < thresholds['area']) & 
                (features['perimeter'] < thresholds['perimeter']) & 
                (features['eccentricity'] < thresholds['eccentricity']) & 
                (features['solidity'] > thresholds['solidity']), 
                'globules rouges', 
                'globules blancs'
            )
        else:
            features['type'] = np.where(features['area'] > thresholds['area'], 'grande', 'normale')
        return features

    def generate_report(self):
        if self.cell_data is None:
            return "Aucune donnée disponible. Veuillez analyser une image d'abord."

        global_stats = self.generate_global_stats()
        detailed_report = self.generate_detailed_report()
        clinical_summary = self.generate_clinical_summary()

        return detailed_report, global_stats + "\n" + clinical_summary

    def identify_cell_type(self, row):
        if self.sample_type == 'sang':
            if row['type'] == 'globules rouges':
                return 'globules rouges'
            elif row['type'] == 'globules blancs':
                return 'globules blancs'
            else:
                return 'autres'
        elif self.sample_type == 'urine':
            if row['area'] < 100:
                return 'cellules épithéliales'
            else:
                return 'autres'

    def clinical_observations(self, row):
        observations = []
        thresholds = self.thresholds[self.sample_type]
        if row['area'] >= thresholds['area']:
            observations.append("Surface élevée, pouvant indiquer une inflammation ou une hypertrophie.")
        if row['perimeter'] >= thresholds['perimeter']:
            observations.append("Périmètre élevé, pouvant indiquer une irrégularité de la forme.")
        if row['eccentricity'] >= thresholds['eccentricity']:
            observations.append("Excentricité élevée, suggérant une forme allongée ou irrégulière.")
        if row['solidity'] <= thresholds['solidity']:
            observations.append("Faible solidité, pouvant indiquer une structure cellulaire compromise.")
        
        return " ".join(observations)

    def generate_global_stats(self):
        stats_report = "Statistiques globales:\n\n"
        stats_report += f"Nombre total de cellules analysées: {len(self.cell_data)}\n"
        stats_report += f"Aire moyenne des cellules: {self.cell_data['area'].mean():.2f} unités carrées\n"
        stats_report += f"Périmètre moyen des cellules: {self.cell_data['perimeter'].mean():.2f} unités\n"
        stats_report += f"Excentricité moyenne des cellules: {self.cell_data['eccentricity'].mean():.2f}\n"
        stats_report += f"Solidité moyenne des cellules: {self.cell_data['solidity'].mean():.2f}\n"
        stats_report += "\n"
        stats_report += f"Aire médiane des cellules: {self.cell_data['area'].median():.2f} unités carrées\n"
        stats_report += f"Périmètre médian des cellules: {self.cell_data['perimeter'].median():.2f} unités\n"
        stats_report += f"Excentricité médiane des cellules: {self.cell_data['eccentricity'].median():.2f}\n"
        stats_report += f"Solidité médiane des cellules: {self.cell_data['solidity'].median():.2f}\n"
        stats_report += "\n"
        stats_report += f"Écart-type de l'aire des cellules: {self.cell_data['area'].std():.2f} unités carrées\n"
        stats_report += f"Écart-type du périmètre des cellules: {self.cell_data['perimeter'].std():.2f} unités\n"
        stats_report += f"Écart-type de l'excentricité des cellules: {self.cell_data['eccentricity'].std():.2f}\n"
        stats_report += f"Écart-type de la solidité des cellules: {self.cell_data['solidity'].std():.2f}\n"
        return stats_report

    def generate_clinical_summary(self):
        clinical_summary = "Résumé clinique des observations:\n\n"
        anomaly_count = 0
        cell_counts = {'globules rouges': 0, 'globules blancs': 0, 'autres': 0}

        for index, row in self.cell_data.iterrows():
            cell_type = self.identify_cell_type(row)
            cell_counts[cell_type] += 1

            if row['type'] == 'grande':
                anomaly_count += 1
                clinical_summary += f"Cellule {index + 1} ({cell_type}): {self.clinical_observations(row)}\n"

        clinical_summary = f"Nombre total de cellules: {len(self.cell_data)}\n" + \
                           f"Nombre total d'anomalies: {anomaly_count}\n\n" + \
                           "Quantification des cellules:\n" + \
                           f"  - Globules rouges: {cell_counts['globules rouges']}\n" + \
                           f"  - Globules blancs: {cell_counts['globules blancs']}\n" + \
                           f"  - Autres: {cell_counts['autres']}\n\n" + \
                           clinical_summary

        return clinical_summary

    def generate_detailed_report(self):
        detailed_report = "Rapport détaillé d'analyse des cellules:\n\n"

        for index, row in self.cell_data.iterrows():
            cell_type = self.identify_cell_type(row)
            detailed_report += f"Cellule {index + 1} ({cell_type}):\n"
            detailed_report += f"  - Surface: {row['area']} unités carrées\n"
            detailed_report += f"  - Périmètre: {row['perimeter']} unités\n"
            detailed_report += f"  - Excentricité: {row['eccentricity']:.2f}\n"
            detailed_report += f"  - Solidité: {row['solidity']:.2f}\n"
            detailed_report += f"  - Type: {row['type']}\n"
            detailed_report += "\n"

        return detailed_report

    def generate_recommendations(self):
        recommendations = "Recommandations cliniques:\n\n"
        thresholds = self.thresholds[self.sample_type]
        if self.cell_data['area'].mean() > thresholds['area']:
            recommendations += "- La moyenne de l'aire des cellules est élevée. Cela pourrait indiquer une inflammation ou une hypertrophie généralisée.\n"
        if self.cell_data['perimeter'].mean() > thresholds['perimeter']:
            recommendations += "- La moyenne du périmètre des cellules est élevée. Cela pourrait indiquer une irrégularité générale dans la forme des cellules.\n"
        if self.cell_data['eccentricity'].mean() > thresholds['eccentricity']:
            recommendations += "- La moyenne de l'excentricité des cellules est élevée. Cela pourrait suggérer que les cellules ont une forme plus allongée ou irrégulière.\n"
        if self.cell_data['solidity'].mean() < thresholds['solidity']:
            recommendations += "- La moyenne de la solidité des cellules est faible. Cela pourrait indiquer une structure cellulaire compromise.\n"
        recommendations += "\n"
        recommendations += "Il est recommandé de consulter un spécialiste pour une évaluation plus approfondie et pour discuter des résultats en détail."
        return recommendations

    def highlight_anomalies(self, output_image_path):
        image_copy = self.image.copy()
        for _, row in self.cell_data.iterrows():
            minr, minc, maxr, maxc = int(row['bbox-0']), int(row['bbox-1']), int(row['bbox-2']), int(row['bbox-3'])
            if row['type'] == 'globules rouges':
                cv2.rectangle(image_copy, (minc, minr), (maxc, maxr), (0, 255, 0), 2)  # Green for red blood cells
            elif row['type'] == 'globules blancs':
                cv2.rectangle(image_copy, (minc, minr), (maxc, maxr), (0, 0, 255), 2)  # Red for white blood cells
            else:
                cv2.rectangle(image_copy, (minc, minr), (maxc, maxr), (255, 0, 0), 2)  # Blue for others

        cv2.imwrite(output_image_path, cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR))

