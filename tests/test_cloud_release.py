from unittest.mock import Mock
from pathlib import Path

import pytest
from google.api_core.exceptions import NotFound

from src import cloud_release


def test_release_never_uploads_a_regression(monkeypatch):
    bucket = Mock()
    model, report = Mock(), Mock()
    model.generation, report.generation = 12, 13
    report.download_as_text.return_value = '{"f1_score":0.8,"eval_sha256":"same"}'
    bucket.blob.side_effect = [model, report]
    monkeypatch.setattr(cloud_release, "read_candidate",
                        lambda: {"f1_score": 0.7, "eval_sha256": "same"})
    with pytest.raises(ValueError, match="existing model retained"):
        cloud_release.publish_approved(bucket, "new-run")
    model.upload_from_filename.assert_not_called()
    report.upload_from_filename.assert_not_called()
    bucket.copy_blob.assert_not_called()


def test_first_release_still_requires_quality_gate(monkeypatch):
    bucket = Mock()
    model, report = Mock(), Mock()
    model.reload.side_effect = NotFound("model missing")
    report.reload.side_effect = NotFound("report missing")
    bucket.blob.side_effect = [model, report]
    monkeypatch.setattr(cloud_release, "read_candidate", lambda: {"f1_score": 0.64})
    with pytest.raises(ValueError, match="Release blocked"):
        cloud_release.publish_approved(bucket, "new-run")
    model.upload_from_filename.assert_not_called()
    report.upload_from_filename.assert_not_called()


def test_approved_release_preserves_history_before_upload(monkeypatch):
    bucket = Mock()
    model, report = Mock(), Mock()
    model.generation, report.generation = 12, 13
    model.name, report.name = "artifacts/current/model.joblib", "artifacts/current/report.json"
    model.metadata = {"run_id": "old"}
    report.download_as_text.return_value = '{"f1_score":0.8,"eval_sha256":"same","run_id":"old"}'
    bucket.blob.side_effect = [model, report]
    monkeypatch.setattr(cloud_release, "read_candidate",
                        lambda: {"f1_score": 0.85, "eval_sha256": "same", "run_id": "new"})
    cloud_release.publish_approved(bucket, "new-run")
    assert bucket.copy_blob.call_count == 2
    model.upload_from_filename.assert_called_once_with(str(Path("models/model.joblib")), if_generation_match=12)
    report.upload_from_filename.assert_called_once_with(str(Path("outputs/report.json")), if_generation_match=13)
