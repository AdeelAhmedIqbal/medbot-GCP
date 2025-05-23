import os
import sys
import logging
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient, errors
from pymongo.uri_parser import parse_uri
from fastapi.encoders import jsonable_encoder

# ——— App setup —————————————————————————————————————————————
app = FastAPI(title="Medical Misinformation Gateway")
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ——— MongoDB connection ——————————————————————————————————————
# 1) Grab the full URI from the Secret
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logging.error("MONGO_URI is not set; exiting.")
    sys.exit(1)

# 2) Parse the database name from the URI (e.g. ".../chatlogs")
db_name = parse_uri(MONGO_URI).get("database") or "chatlogs"

# 3) Create client with a short server-selection timeout
mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = mongo_client[db_name]
chats = db.get_collection("chats")

# 4) On startup, verify connectivity
@app.on_event("startup")
def verify_mongo_connection():
    try:
        # This actually sends a ping to the server
        mongo_client.admin.command("ping")
        logging.info(f"✅ Successfully connected to MongoDB database '{db_name}'")
    except errors.ServerSelectionTimeoutError as e:
        logging.exception("❌ Could not connect to MongoDB; terminating.")
        sys.exit(1)


# ——— Data models —————————————————————————————————————————————
class Query(BaseModel):
    question: str


# ——— Health check ————————————————————————————————————————————
@app.get("/health")
async def health_check():
    try:
        mongo_client.admin.command("ping")
        return {"status": "ok", "db": "reachable"}
    except Exception:
        raise HTTPException(503, detail="Database unreachable")


# ——— Endpoints ———————————————————————————————————————————————
INFERENCE_URL = os.getenv("INFERENCE_API_URL")
if not INFERENCE_URL:
    logging.warning("INFERENCE_API_URL is not set; /classify may fail.")

@app.post("/classify")
def classify(query: Query):
    # 1) Proxy to inference service
    try:
        resp = requests.post(
            f"{INFERENCE_URL}/predict",
            json={"question": query.question},
            timeout=5
        ).json()
    except Exception as e:
        raise HTTPException(502, detail=f"Inference service error: {e}")

    # 2) Save result to MongoDB
    try:
        entry = {
            "prompt":  query.question,
            "label":   resp.get("label", "error"),
            "created": datetime.utcnow()
        }
        chats.insert_one(entry)
    except Exception as e:
        logging.exception("Failed to write to MongoDB")
        # you can still return the inference even if logging fails
    return resp


@app.get("/history")
def history():
    docs = chats.find().sort("created", -1).limit(50)
    return [
        {
            "prompt":  d["prompt"],
            "label":   d["label"],
            "created": d["created"].isoformat()
        }
        for d in docs
    ]
