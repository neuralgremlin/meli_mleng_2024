from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    silhouette_score,
)
import uuid
import joblib
import os

from price_anomaly import load_config


class ModelBuilder:
    def __init__(self):
        self.config = load_config()

    def run(self, data_path: Path, output_dir: Path):
        run_id = str(uuid.uuid4())
        print(f"Ejecutando entrenamiento de modelo con UUID: {run_id}")
        df = self.read_data(data_path)

        # scaler = RobustScaler()
        # X = scaler.fit_transform(df[self.config.features.numerical])
        X = df[self.config.features.numerical]
        y = df["manual_label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.data.test_size, stratify=df["DOMINANTES"]
        )

        # Entrenar el modelo
        model = IsolationForest(contamination=self.config.model.contamination)
        model.fit(X_train)

        # Predicción en el conjunto de prueba
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        # Convertir predicciones a etiquetas de anomalías
        y_pred_train = [1 if x == -1 else 0 for x in y_pred_train]  # 1 indica anomalía
        y_pred_test = [1 if x == -1 else 0 for x in y_pred_test]

        self.evaluate(y_train, y_pred_train)
        self.evaluate(y_test, y_pred_test)
        self.export_model(output_dir / run_id, model)

    @staticmethod
    def read_data(data_path: Path) -> pd.DataFrame:
        return pd.read_csv(data_path)

    def evaluate(self, real: pd.Series, predicted: pd.Series) -> pd.DataFrame:
        # Silhouette Test
        # silhouette_avg_test = silhouette_score(X_test_scaled, predictions)
        # print(f"Silhouette Score para prueba con modelo cargado: {silhouette_avg_test}")
        # Confusion Matrix
        conf_matrix = confusion_matrix(real, predicted)
        print("Confusion Matrix:")
        print(conf_matrix)
        # Precision, Recall, F1 Score
        precision = precision_score(real, predicted)
        recall = recall_score(real, predicted)
        f1 = f1_score(real, predicted)
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"F1 Score: {f1}")

    def export_model(self, outpur_dir: Path, model, scaler=None):

        # Crear una carpeta con UUID de la corrida para guardar los modelos si no existe
        os.makedirs(
            outpur_dir,
            exist_ok=True,
        )

        # Guardar el modelo y el escalador
        model_filename = f"{outpur_dir}/model.pkl"
        joblib.dump(model, model_filename)

        if scaler:
            scaler_filename = f"{outpur_dir}/scaler.pkl"
            joblib.dump(scaler, scaler_filename)
            print("Modelo y escalador guardados exitosamente")
        else:
            print("Modelo guardado exitosamente")
