import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score

from src.train import FEATURE_NAMES, read_dataset, select_threshold, train

PARAMS = {"n_estimators": 10, "learning_rate": 0.1, "max_depth": 2}


@pytest.fixture(autouse=True)
def isolated_tracking(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}")
    monkeypatch.setenv("MLFLOW_ARTIFACT_ROOT", str(tmp_path / "mlartifacts"))
    monkeypatch.setenv("MLFLOW_EXPERIMENT_NAME", "unit-tests")


def _make_temp_data(tmp_path):
    rng = np.random.default_rng(0)
    frame = pd.DataFrame(rng.random((200, len(FEATURE_NAMES))), columns=FEATURE_NAMES)
    frame["target"] = rng.integers(0, 2, size=200)
    train_path, eval_path = tmp_path / "train.csv", tmp_path / "holdout.csv"
    frame.iloc[:160].to_csv(train_path, index=False)
    frame.iloc[160:].to_csv(eval_path, index=False)
    return str(train_path), str(eval_path)


@pytest.fixture
def trained(tmp_path):
    paths = _make_temp_data(tmp_path)
    result = train(PARAMS, data_path=paths[0], eval_path=paths[1])
    return paths, result


def test_train_returns_float(trained):
    assert isinstance(trained[1], float)
    assert 0 <= trained[1] <= 1


def test_report_file_created(trained):
    report = json.loads(Path("outputs/report.json").read_text(encoding="utf-8"))
    assert {"f1_score", "accuracy", "positive_rate", "decision_threshold"} <= report.keys()
    assert report["f1_score"] == trained[1]
    assert len(report["threshold_scan"]) == 17
    assert report["f1_score"] == report["f1_at_default_threshold"]
    assert report["best_f1_score"] >= report["f1_score"]
    assert report["decision_threshold"] == 0.5
    assert report["drift_detected"] is True
    assert report["train_rows"] == 160 and report["eval_rows"] == 40
    assert "precision" in Path("outputs/detail.txt").read_text()


def test_model_file_created(trained):
    model = joblib.load("models/model.joblib")
    report = json.loads(Path("outputs/report.json").read_text())
    holdout = pd.read_csv(trained[0][1])
    predictions = model.predict(holdout[FEATURE_NAMES])
    assert model.decision_threshold_ == report["decision_threshold"]
    assert f1_score(holdout.target, predictions) == report["f1_score"]


def test_threshold_ties_prefer_default():
    threshold, f1, _ = select_threshold([0, 1], np.array([0.01, 0.99]))
    assert threshold == 0.5 and f1 == 1


@pytest.mark.parametrize("kind", ["missing", "nonfinite", "label", "empty"])
def test_invalid_dataset_rejected(tmp_path, kind):
    path, _ = _make_temp_data(tmp_path)
    frame = pd.read_csv(path)
    if kind == "missing":
        frame = frame.drop(columns="age")
    elif kind == "nonfinite":
        frame.loc[0, "age"] = float("inf")
    elif kind == "label":
        frame.loc[0, "target"] = 2
    else:
        frame = frame.iloc[:0]
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError):
        read_dataset(path)
