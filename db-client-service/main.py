from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import Dict, Any, List
import pandas as pd
import io
import os


# PyDantic Object Schemas
class ItemPrice(BaseModel):
    ITEM_ID: str
    ORD_CLOSED_DT: str
    PRICE: float


class PriceHistory(BaseModel):
    documents: List[ItemPrice]


# MongoDB connection setup (NO REQUIERE AUTH)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.test_db
historic_collection = "historic_data"


# Check if a collection exists
def validate_collection(collection_name: str, empty_if_exists=False):
    if collection_name in db.list_collection_names():
        collection = db[collection_name]
        if empty_if_exists:
            collection.delete_many({})
            return {
                "message": f"Collection '{collection_name}' exists and has been emptied."
            }
        else:
            return {"message": f"Collection exists."}
    else:
        db.create_collection(collection_name)
        return {
            "message": f"Collection '{collection_name}' did not exist and has been created."
        }


# APP Y ENDPOINTS

app = FastAPI()
validate_collection(historic_collection, True)


# SUBIR CSV
@app.post("/uploadcsv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        validate_collection(historic_collection, True)
        collection = db[historic_collection]

        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        records = df.to_dict(orient="records")
        collection.insert_many(records)

        return {"message": "CSV data successfully inserted into MongoDB."}
    except Exception as e:
        return {"error": str(e)}


# OBTENER LA HSITORIA DE REGISTROS DE UN ITEM
@app.get("/item_history/{item_id}")
async def item_documents(item_id: str) -> PriceHistory:
    try:
        collection = db[historic_collection]
        query = {"ITEM_ID": item_id}
        documents = list(collection.find(query))
        return {"documents": documents}
    except Exception as e:
        return {"error": str(e)}


# LIFECHECK
@app.get("/")
def read_root():
    return {"message": "HELLO WORLD FROM DB-CLIENT"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
