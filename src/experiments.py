"""Run five lab experiments and an optional local batch-2 comparison."""
import argparse
import json
from pathlib import Path

import pandas as pd

from src.train import train

EXPERIMENTS = [
    {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
    {"n_estimators": 50, "learning_rate": 0.05, "max_depth": 2},
    {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 5},
    {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 3},
    {"n_estimators": 200, "learning_rate": 0.05, "max_depth": 3},
]


def run_experiments(compare=False):
    reports = []
    for index, params in enumerate(EXPERIMENTS, start=1):
        directory = f"outputs/experiments/run-{index}"
        train(params, output_dir=directory, model_dir=f"{directory}/models",
              run_name=f"experiment-{index}")
        reports.append(json.loads(Path(directory, "report.json").read_text()))
    best = max(reports, key=lambda report: report["f1_score"])
    summary = {"experiments": reports, "best_params": best["params"],
               "selected_by": "positive-class F1 of model.predict() (fixed default threshold)"}
    # Fit the selected configuration into the standard serving/artifact paths.
    train(best["params"], run_name="selected-batch1")
    summary["batch1"] = json.loads(Path("outputs/report.json").read_text())
    if compare:
        combined_path = Path("data/local_combined.csv")
        batch1 = pd.read_csv("data/train_batch1.csv")
        batch2 = pd.read_csv("data/train_batch2.csv")
        combined = pd.concat([batch1, batch2], ignore_index=True)
        if combined_path.exists():
            if not pd.read_csv(combined_path).equals(combined):
                raise ValueError("Existing combined dataset differs; retained without replacement")
        else:
            combined.to_csv(combined_path, index=False)
        train(best["params"], data_path=str(combined_path),
              output_dir="outputs/batch2", model_dir="outputs/batch2/models",
              run_name="local-batch1-plus-batch2")
        summary["batch1_plus_batch2_local"] = json.loads(
            Path("outputs/batch2/report.json").read_text())
    Path("outputs/experiments.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Best parameters:", best["params"])
    print("Summary: outputs/experiments.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare", action="store_true")
    run_experiments(parser.parse_args().compare)
