"""Publish only approved models, retaining immutable candidates and history."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from google.api_core.exceptions import NotFound
from google.cloud import storage

from src.quality_gate import validate_release

FILES = {
    "model.joblib": Path("models/model.joblib"),
    "report.json": Path("outputs/report.json"),
    "detail.txt": Path("outputs/detail.txt"),
}


def read_candidate():
    candidate = json.loads(FILES["report.json"].read_text(encoding="utf-8"))
    digest = hashlib.sha256(FILES["model.joblib"].read_bytes()).hexdigest()
    if digest != candidate["model_sha256"]:
        raise ValueError("Model checksum does not match the evaluation report")
    return candidate


def upload_candidate(bucket, run_id):
    # Preconditions make run artifacts create-only; existing evidence is retained.
    for name, path in FILES.items():
        bucket.blob(f"artifacts/runs/{run_id}/{name}").upload_from_filename(
            str(path), if_generation_match=0)
    print(f"Saved immutable candidate: gs://{bucket.name}/artifacts/runs/{run_id}/")


def publish_approved(bucket, run_id):
    candidate = read_candidate()
    model_blob = bucket.blob("artifacts/current/model.joblib")
    report_blob = bucket.blob("artifacts/current/report.json")
    try:
        model_blob.reload()
    except NotFound:
        model_generation = 0
    else:
        model_generation = int(model_blob.generation)
    try:
        report_blob.reload()
    except NotFound:
        report_generation = 0
        previous = None
    else:
        report_generation = int(report_blob.generation)
        previous = json.loads(report_blob.download_as_text(
            if_generation_match=report_generation))
    if bool(model_generation) != bool(report_generation):
        raise ValueError("Current model/report pair is incomplete; inspect before release")
    validate_release(candidate, previous)
    if previous is not None:
        # Verify the current pair before making changes; a interrupted publication
        # is reported for inspection instead of silently replacing either object.
        if (model_blob.metadata or {}).get("run_id") != previous.get("run_id"):
            raise ValueError("Current model/report run IDs disagree; inspect before release")
        for blob in (model_blob, report_blob):
            bucket.copy_blob(
                blob, bucket, f"artifacts/history/{run_id}/{Path(blob.name).name}",
                if_generation_match=0, if_source_generation_match=int(blob.generation))
        print(f"Preserved previous model/report: artifacts/history/{run_id}/")
    model_blob.metadata = {"run_id": candidate["run_id"],
                           "f1_score": str(candidate["f1_score"])}
    model_blob.upload_from_filename(str(FILES["model.joblib"]),
                                    if_generation_match=model_generation)
    report_blob.upload_from_filename(str(FILES["report.json"]),
                                     if_generation_match=report_generation)
    print(f"Published approved run {candidate['run_id']} for release {run_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["candidate", "publish"])
    args = parser.parse_args()
    bucket = storage.Client().bucket(os.environ["ARTIFACT_BUCKET"])
    run_id = f"{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}"
    if args.operation == "candidate":
        read_candidate()
        upload_candidate(bucket, run_id)
    else:
        publish_approved(bucket, run_id)
