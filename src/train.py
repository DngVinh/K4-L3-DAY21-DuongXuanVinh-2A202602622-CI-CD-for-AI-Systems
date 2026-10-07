"""Reproducible Adult Income training, MLflow tracking and evaluation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

F1_THRESHOLD = 0.65
REFERENCE_POSITIVE_RATE = 0.248
DRIFT_TOLERANCE = 0.05
FEATURE_NAMES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week",
]


def read_dataset(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if list(frame.columns) != FEATURE_NAMES + ["target"]:
        raise ValueError(f"{path}: expected the 10 Adult features followed by target")
    if frame.empty or not all(pd.api.types.is_numeric_dtype(dtype) for dtype in frame.dtypes):
        raise ValueError(f"{path}: expected nonempty numeric data")
    if not np.isfinite(frame.to_numpy()).all():
        raise ValueError(f"{path}: missing or non-finite values")
    if not set(frame["target"].unique()).issubset({0, 1}):
        raise ValueError(f"{path}: target must be binary (0 or 1)")
    return frame


def select_threshold(y_true, probabilities) -> tuple[float, float, list[dict]]:
    """Scan the 17 thresholds requested by the lab; prefer 0.5 on F1 ties."""
    scores = [
        {"threshold": step / 100, "f1_score": float(f1_score(
            y_true, probabilities >= step / 100, zero_division=0))}
        for step in range(10, 91, 5)
    ]
    best = max(scores, key=lambda row: (
        row["f1_score"], -abs(row["threshold"] - 0.5), row["threshold"]))
    return best["threshold"], best["f1_score"], scores


def dataset_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def train(params: dict, data_path: str = "data/train_batch1.csv",
          eval_path: str = "data/holdout.csv", output_dir: str = "outputs",
          model_dir: str = "models", run_name: str | None = None) -> float:
    """Return positive-class F1 and save the model, threshold and diagnostics.

    The holdout is never used by fit(). The optional threshold scan follows the
    lab bonus specification as a diagnostic. The serving and release metric
    use model.predict() at its default threshold, consistently with the core lab.
    """
    df_train, df_eval = read_dataset(data_path), read_dataset(eval_path)
    if set(df_train.target.unique()) != {0, 1}:
        raise ValueError("Training data must contain both target classes")
    if Path(data_path).resolve() == Path(eval_path).resolve():
        raise ValueError("Training and holdout must be separate files")
    if "random_state" in params:
        raise ValueError("random_state is fixed at 42 for reproducibility")
    x_train, y_train = df_train[FEATURE_NAMES], df_train.target
    x_eval, y_eval = df_eval[FEATURE_NAMES], df_eval.target
    positive_rate = float(y_train.mean())
    drift = abs(positive_rate - REFERENCE_POSITIVE_RATE) > DRIFT_TOLERANCE
    print(f"{'WARNING: class-distribution drift' if drift else 'Class distribution OK'}: "
          f"positive_rate={positive_rate:.2%}; reference=24.8%; tolerance=5 percentage points")

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    mlflow.set_tracking_uri(tracking_uri)
    artifact_root = str(Path(os.getenv("MLFLOW_ARTIFACT_ROOT", "mlartifacts")).resolve())
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "adult-income-lab")
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(
            experiment_name, artifact_location=Path(artifact_root).as_uri()
            if tracking_uri.startswith(("sqlite:", "file:")) else None)
    else:
        experiment_id = experiment.experiment_id

    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run:
        mlflow.log_params({**params, "random_state": 42})
        mlflow.set_tags({"git_commit": os.getenv("GITHUB_SHA", "local"),
                         "threshold_selection": "diagnostic_scan_only",
                         "deployment_decision_rule": "model.predict_default_threshold"})
        model = GradientBoostingClassifier(**params, random_state=42)
        model.fit(x_train, y_train)
        probabilities = model.predict_proba(x_eval)[:, 1]
        default_predictions = model.predict(x_eval)
        default_f1 = float(f1_score(y_eval, default_predictions, zero_division=0))
        best_threshold, best_f1, threshold_scores = select_threshold(y_eval, probabilities)
        threshold, f1 = 0.5, default_f1
        predictions = default_predictions
        accuracy = float(accuracy_score(y_eval, predictions))
        model.decision_threshold_ = threshold
        model.best_threshold_ = best_threshold
        model.mlflow_run_id_ = run.info.run_id

        metrics = {"f1_score": f1, "accuracy": accuracy,
                   "f1_at_default_threshold": default_f1,
                   "best_f1_score": best_f1, "best_threshold": best_threshold,
                   "accuracy_at_best_threshold": float(accuracy_score(
                       y_eval, probabilities >= best_threshold)),
                   "accuracy_at_default_threshold": float(accuracy_score(y_eval, default_predictions)),
                   "decision_threshold": threshold, "positive_rate": positive_rate}
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model")
        output_path, model_path = Path(output_dir), Path(model_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        model_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path / "model.joblib")
        report = {
            **metrics,
            "threshold_scan": threshold_scores, "drift_detected": drift,
            "train_rows": len(df_train), "eval_rows": len(df_eval), "params": params,
            "train_sha256": dataset_sha256(data_path), "eval_sha256": dataset_sha256(eval_path),
            "model_sha256": dataset_sha256(str(model_path / "model.joblib")),
            "run_id": run.info.run_id, "git_commit": os.getenv("GITHUB_SHA", "local"),
            "threshold_selection_data": "holdout diagnostic (lab bonus; not independent test F1)",
            "deployment_decision_rule": "model.predict_default_threshold",
        }
        (output_path / "report.json").write_text(
            json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
        detail = (
            "Confusion matrix: rows=actual, columns=predicted; labels=[0, 1]\n"
            + str(confusion_matrix(y_eval, predictions, labels=[0, 1])) + "\n\n"
            + classification_report(y_eval, predictions, labels=[0, 1],
                target_names=["thu_nhap_thap", "thu_nhap_cao"], zero_division=0)
        )
        (output_path / "detail.txt").write_text(detail, encoding="utf-8")
        mlflow.log_artifacts(str(output_path), artifact_path="evaluation")
    print(f"F1: {f1:.4f} | Accuracy: {accuracy:.4f} | threshold: {threshold:.2f} "
          f"| Best diagnostic F1: {best_f1:.4f} @ {best_threshold:.2f}")
    return float(f1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", default="params.yaml")
    parser.add_argument("--data", default="data/train_batch1.csv")
    parser.add_argument("--eval", default="data/holdout.csv")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--run-name")
    args = parser.parse_args()
    with open(args.params, encoding="utf-8") as stream:
        train(yaml.safe_load(stream), args.data, args.eval,
              args.output_dir, args.model_dir, args.run_name)
