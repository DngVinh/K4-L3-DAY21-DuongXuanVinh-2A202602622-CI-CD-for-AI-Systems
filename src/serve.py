"""Serve the exact decision rule evaluated by the CI quality gate."""
from __future__ import annotations

from contextlib import asynccontextmanager
from io import BytesIO
import math
import os

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

FEATURE_NAMES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week",
]
MODEL_KEY = "artifacts/current/model.joblib"


def download_model():
    """Load from GCS in memory, or an explicitly supplied local path for tests."""
    local_path = os.getenv("MODEL_PATH")
    if local_path:
        return joblib.load(local_path)
    bucket_name = os.getenv("ARTIFACT_BUCKET")
    if not bucket_name:
        raise RuntimeError("Set ARTIFACT_BUCKET for GCS, or MODEL_PATH for local inference")
    from google.cloud import storage
    blob = storage.Client().bucket(bucket_name).blob(MODEL_KEY)
    loaded = joblib.load(BytesIO(blob.download_as_bytes()))
    print(f"Loaded model from gs://{bucket_name}/{MODEL_KEY}")
    return loaded


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = download_model()
    yield


app = FastAPI(title="Adult Income API", lifespan=lifespan)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz(request: Request):
    if getattr(request.app.state, "model", None) is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest, request: Request):
    if len(req.features) != 10:
        raise HTTPException(status_code=400, detail="Expected 10 features (adult income)")
    if not all(math.isfinite(value) for value in req.features):
        raise HTTPException(status_code=400, detail="Features must be finite numbers")
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    frame = pd.DataFrame([req.features], columns=FEATURE_NAMES)
    threshold = getattr(model, "decision_threshold_", 0.5)
    # Preserve sklearn's tie handling at the default threshold; custom thresholds
    # are supported for explicitly selected model artifacts as well.
    prediction = int(model.predict(frame)[0]) if threshold == 0.5 else int(
        model.predict_proba(frame)[0, 1] >= threshold)
    return {"prediction": prediction,
            "label": "thu_nhap_cao" if prediction else "thu_nhap_thap"}


@app.get("/version")
def version(request: Request):
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"run_id": getattr(model, "mlflow_run_id_", "unknown"),
            "decision_threshold": getattr(model, "decision_threshold_", 0.5)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
