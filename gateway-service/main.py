from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os, requests
from pymongo import MongoClient
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId

app = FastAPI(title="Medical Misinformation Gateway")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://medbot.local"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inference API & MongoDB
INFERENCE_URL = os.getenv("INFERENCE_API_URL")
MONGO_URI      = os.getenv("MONGO_URI", "mongodb://localhost:27017/chatlogs")
mongo_client   = MongoClient(MONGO_URI)
db             = mongo_client.get_database()          # chatlogs
chats          = db.get_collection("chats")

class Query(BaseModel):
    question: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/classify")
def classify(query: Query):
    # 1) Proxy to inference
    try:
        resp = requests.post(
            f"{INFERENCE_URL}/predict",
            json={"question": query.question}
        ).json()
    except Exception as e:
        return {"error": str(e)}

    # 2) Save to MongoDB
    entry = {
        "prompt":   query.question,
        "label":    resp.get("label", "error"),
        "created":  datetime.utcnow()
    }
    chats.insert_one(entry)

    return resp

@app.get("/history")
def history():
    # fetch last 50, newest first
    docs = chats.find().sort("created", -1).limit(50)
    out = []
    for d in docs:
        out.append({
            "prompt":   d["prompt"],
            "label":    d["label"],
            "created":  d["created"].isoformat()
        })
    return out
