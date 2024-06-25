from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import joblib
import pandas as pd
from datetime import datetime
import requests
import numpy as np
import os
from prometheus_client import start_http_server, Summary, Counter, Gauge
from prometheus_client import generate_latest

# Inicializar la aplicación FastAPI
app = FastAPI()


# Métricas Prometheus
REQUEST_TIME = Summary("request_processing_seconds", "Tiempo procesando la solicitud")
PREDICTION_COUNT = Counter("prediction_count", "# Total de predicciones")
ANOMALY_COUNT = Counter("anomaly_count", "# Total de anomalias detectadas")
LAST_PREDICTION_RESULT = Gauge(
    "last_prediction_result", "Resultado de la última predicción (1 anomalo, 0 normal)"
)

# Iniciar el servidor de métricas Prometheus en un puerto diferente
start_http_server(8001)

client_url = os.getenv("CLIENT_URI")
# Cargar el modelo y el escalador guardados
model = joblib.load(f"model.pkl")


# Definir el esquema de los datos de entrada
class PredictionRequest(BaseModel):
    PRICE: float
    ITEM_ID: str


class PredictionOutput(BaseModel):
    ITEM_ID: str
    PRICE: float
    ANOMALY: int


@app.post("/anomaly", response_model=PredictionOutput)
@REQUEST_TIME.time()
def predict_anomaly(input: PredictionRequest):
    PREDICTION_COUNT.inc()
    try:
        response = requests.get(f"http://{client_url}/item_history/{input.ITEM_ID}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=500, detail="Error al obtener los registros del item_id"
            )

        res = response.json()
        if len(res["documents"]) == 0:
            price_deviation = 0.0
        else:
            # Convertir los registros a un DataFrame
            item_data = pd.DataFrame(res["documents"])
            # Calcular las características adicionales
            item_mean_price = item_data["PRICE"].mean()
            price_deviation = input.PRICE - item_mean_price

        # Crear un DataFrame con las características del nuevo registro
        new_data = pd.DataFrame(
            [{"PRICE": input.PRICE, "price_deviation": price_deviation}]
        )

        # Hacer la predicción
        prediction = model.predict(new_data)
        anomaly = prediction[0] == -1  # 1 indica anomalía, 0 indica normal
        int_anomaly = int(anomaly)

        # Actualizar métricas Prometheus
        LAST_PREDICTION_RESULT.set(int_anomaly)
        if anomaly == 1:
            ANOMALY_COUNT.inc()

        return PredictionOutput(
            ITEM_ID=input.ITEM_ID, PRICE=input.PRICE, ANOMALY=int_anomaly
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para métricas Prometheus
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
