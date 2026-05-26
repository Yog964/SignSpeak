"""
ISL SignSpeak — FastAPI Backend

Real-time Indian Sign Language recognition server.
The frontend extracts MediaPipe pose landmarks in the browser and streams
them over a WebSocket.  This server loads pre-trained sklearn
RandomForestClassifier models and returns predictions with confidence scores.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pydantic import BaseModel
import shutil

from landmark_processor import process_landmarks
from model_manager import ModelManager

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

MODELS_DIR = Path(__file__).parent / "models"
model_manager = ModelManager()

# ---------------------------------------------------------------------------
# Lifespan — load models on startup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all .pkl models from the models/ directory at startup."""
    print("\n[START] ISL SignSpeak Backend starting up...")
    print(f"   Models directory: {MODELS_DIR.resolve()}")
    loaded = model_manager.load_models(MODELS_DIR)
    if loaded:
        print(f"   {len(loaded)} model(s) ready: {', '.join(loaded)}\n")
    else:
        print("   [WARN] No models found - place .pkl files in the models/ directory.\n")
    yield


# ---------------------------------------------------------------------------
# App & middleware
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ISL SignSpeak",
    description="Real-time Indian Sign Language recognition API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok"}


@app.get("/api/models")
async def list_models():
    """Return every loaded model with its id and display name."""
    return {"models": model_manager.get_available_models()}

@app.post("/api/models/upload")
async def upload_model(file: UploadFile = File(...)):
    """Upload a new .pkl model and reload models."""
    if not file.filename.endswith(".pkl"):
        raise HTTPException(status_code=400, detail="Only .pkl files are allowed.")
    
    file_path = MODELS_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    model_manager.load_models(MODELS_DIR)
    return {"status": "ok", "message": f"Model {file.filename} uploaded and loaded."}

class RenameRequest(BaseModel):
    new_name: str

@app.put("/api/models/{model_id}")
async def rename_model(model_id: str, req: RenameRequest):
    """Rename a .pkl file."""
    old_path = MODELS_DIR / f"{model_id}.pkl"
    if not old_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")
        
    # ensure it ends with .pkl
    new_filename = req.new_name if req.new_name.endswith(".pkl") else f"{req.new_name}.pkl"
    new_path = MODELS_DIR / new_filename
    
    if new_path.exists():
        raise HTTPException(status_code=400, detail="A model with this name already exists")
        
    os.rename(old_path, new_path)
    model_manager.load_models(MODELS_DIR)
    return {"status": "ok", "message": "Model renamed successfully"}

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a .pkl file."""
    file_path = MODELS_DIR / f"{model_id}.pkl"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")
        
    os.remove(file_path)
    model_manager.load_models(MODELS_DIR)
    return {"status": "ok", "message": "Model deleted successfully"}


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@app.websocket("/ws/predict")
async def websocket_predict(ws: WebSocket):
    """
    Bi-directional prediction channel.

    Client sends:
        {
          "type": "predict",
          "model": "fruits",
          "landmarks": [0.43, 0.09, -0.14, 0.99, ...]   // 132 floats
        }

    Server responds:
        {
          "type": "prediction",
          "sign": "apple",
          "confidence": 85.2,
          "category": "Fruits"
        }
    """
    await ws.accept()
    print("[WS] Client connected")

    try:
        while True:
            raw = await ws.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = data.get("type")
            if msg_type != "predict":
                await ws.send_json(
                    {"type": "error", "message": f"Unknown message type: {msg_type}"}
                )
                continue

            model_id = data.get("model", "")
            landmarks = data.get("landmarks")

            # --- Validate model ------------------------------------------
            if not model_manager.has_model(model_id):
                await ws.send_json(
                    {"type": "error", "message": f"Model '{model_id}' not found"}
                )
                continue

            # --- Validate & process landmarks ----------------------------
            if not isinstance(landmarks, list):
                await ws.send_json(
                    {"type": "error", "message": "Invalid landmark data"}
                )
                continue

            try:
                features = process_landmarks(landmarks)
            except (ValueError, TypeError) as exc:
                await ws.send_json({"type": "error", "message": str(exc)})
                continue

            # --- Predict -------------------------------------------------
            try:
                result = model_manager.predict_with_confidence(model_id, features)
                await ws.send_json({"type": "prediction", **result})
            except Exception as exc:
                await ws.send_json(
                    {"type": "error", "message": f"Prediction failed: {exc}"}
                )

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as exc:
        print(f"[WS] Unexpected error: {exc}")
