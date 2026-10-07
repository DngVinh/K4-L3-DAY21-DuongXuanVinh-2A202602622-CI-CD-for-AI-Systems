import numpy as np
import pytest
from fastapi.testclient import TestClient

from src import serve


class ThresholdModel:
    decision_threshold_ = 0.3
    mlflow_run_id_ = "test-run"

    def predict_proba(self, features):
        assert list(features.columns) == serve.FEATURE_NAMES
        return np.array([[0.6, 0.4]])


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(serve, "download_model", lambda: ThresholdModel())
    with TestClient(serve.app) as client:
        yield client


def test_health_ready(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_scoring_uses_evaluated_threshold(client):
    response = client.post("/score", json={"features": [28, 2, 14, 2, 11, 0, 1, 0, 0, 45]})
    assert response.status_code == 200
    assert response.json() == {"prediction": 1, "label": "thu_nhap_cao"}
    assert client.get("/version").json()["run_id"] == "test-run"


@pytest.mark.parametrize("features", [[], [1] * 9, [1] * 11])
def test_invalid_feature_count(client, features):
    assert client.post("/score", json={"features": features}).status_code == 400


def test_invalid_json_types(client):
    assert client.post("/score", json={"features": ["invalid"] * 10}).status_code == 422


def test_default_threshold_preserves_classifier_ties(monkeypatch):
    model = ThresholdModel()
    model.decision_threshold_ = 0.5
    monkeypatch.setattr(model, "predict", lambda features: np.array([0]), raising=False)
    monkeypatch.setattr(serve, "download_model", lambda: model)
    with TestClient(serve.app) as client:
        assert client.post("/score", json={"features": [1] * 10}).json()["prediction"] == 0


def test_missing_model_not_ready():
    saved = getattr(serve.app.state, "model", None)
    serve.app.state.model = None
    try:
        client = TestClient(serve.app)
        assert client.get("/healthz").status_code == 503
        assert client.post("/score", json={"features": [1] * 10}).status_code == 503
    finally:
        serve.app.state.model = saved
