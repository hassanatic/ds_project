import os
from fastapi import FastAPI, WebSocket, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import torch
import torch.distributed.rpc as rpc
from transformers import GPT2Tokenizer
from distributed_model import GPT2Distributed
import subprocess
from fastapi.responses import HTMLResponse, JSONResponse
from pymongo import MongoClient
from datetime import datetime
import uuid
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_html():
    return open("static/index.html", "r").read()

# Set environment variables for RPC
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "29500"

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["chat_db"]
sessions_collection = db["sessions"]
messages_collection = db["messages"]

# Automatically start Node 1 and Node 2
def start_nodes():
    subprocess.Popen(["python", "node1.py"])
    subprocess.Popen(["python", "node2.py"])

# Initialize RPC only once
def init_rpc():
    print("[Master] Initializing RPC...")
    rpc.init_rpc("master", rank=0, world_size=3)

global model, tokenizer

def initialize_model():
    print("[Master] Creating Distributed Model...")
    global model, tokenizer
    model = GPT2Distributed("node1", "node2")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

@app.get("/sessions")
def get_chat_sessions():
    sessions = list(sessions_collection.find({}, {"_id": 1, "title": 1, "created_at": 1}))
    return JSONResponse(content=sessions)

@app.post("/new_session")
def create_new_session():
    session_id = str(uuid.uuid4())[:8]
    session_data = {"_id": session_id, "created_at": datetime.utcnow().isoformat(), "title": "New Chat"}
    sessions_collection.insert_one(session_data)
    return JSONResponse(content={"session_id": session_id})

@app.delete("/delete_session")
def delete_chat_session(session_id: str = Query(...)):
    messages_collection.delete_many({"session_id": session_id})
    sessions_collection.delete_one({"_id": session_id})
    return JSONResponse(content={"message": "Chat session deleted successfully."})

@app.get("/history")
def get_chat_history(session_id: str = Query(...)):
    history = list(messages_collection.find({"session_id": session_id}, {"_id": 0}))
    return JSONResponse(content=history)

@app.get("/default_session")
def get_default_session():
    latest_session = sessions_collection.find_one(sort=[("created_at", -1)])
    if latest_session:
        return JSONResponse(content={"session_id": latest_session["_id"]})
    return JSONResponse(content={"session_id": None})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = Query(None)):
    if not session_id:
        await websocket.close()
        raise HTTPException(status_code=403, detail="Missing session ID")
    global model, tokenizer
    await websocket.accept()
    first_message = None
    while True:
        user_input = await websocket.receive_text()
        if first_message is None:
            first_message = user_input
            sessions_collection.update_one({"_id": session_id}, {"$set": {"title": first_message}})
        messages_collection.insert_one({"session_id": session_id, "text": user_input, "sender": "user", "timestamp": datetime.utcnow().isoformat()})
        input_ids = tokenizer.encode(user_input, return_tensors="pt")
        output_ids = model.generate(input_ids, max_length=50)
        decoded_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        messages_collection.insert_one({"session_id": session_id, "text": decoded_text, "sender": "ai", "timestamp": datetime.utcnow().isoformat()})
        await websocket.send_text(decoded_text)

if __name__ == "__main__":
    start_nodes()
    init_rpc()
    initialize_model()
    uvicorn.run(app, host="0.0.0.0", port=8000)
