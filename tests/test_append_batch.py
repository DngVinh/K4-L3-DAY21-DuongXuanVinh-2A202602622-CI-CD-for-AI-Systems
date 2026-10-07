import pandas as pd
import pytest

import append_batch


def test_append_preserves_original_and_refuses_repeat(tmp_path, monkeypatch):
    monkeypatch.setattr(append_batch, "__file__", str(tmp_path / "append_batch.py"))
    data = tmp_path / "data"
    data.mkdir()
    first = pd.DataFrame({"age": [28] * 22361, "target": [0] * 22361})
    second = pd.DataFrame({"age": [60] * 22361, "target": [1] * 22361})
    first.to_csv(data / "train_batch1.csv", index=False)
    second.to_csv(data / "train_batch2.csv", index=False)
    before = (data / "train_batch1.csv").read_bytes()
    append_batch.append_batch()
    assert len(pd.read_csv(data / "train_batch1.csv")) == 44722
    assert (data / "train_batch1.before-batch2.csv").read_bytes() == before
    with pytest.raises(ValueError, match="repeated"):
        append_batch.append_batch()
    assert (data / "train_batch1.before-batch2.csv").read_bytes() == before


def test_wrong_batch_size_does_not_modify_original(tmp_path, monkeypatch):
    monkeypatch.setattr(append_batch, "__file__", str(tmp_path / "append_batch.py"))
    data = tmp_path / "data"
    data.mkdir()
    frame = pd.DataFrame({"age": [28], "target": [0]})
    for name in ("train_batch1.csv", "train_batch2.csv"):
        frame.to_csv(data / name, index=False)
    before = (data / "train_batch1.csv").read_bytes()
    with pytest.raises(ValueError):
        append_batch.append_batch()
    assert (data / "train_batch1.csv").read_bytes() == before
    assert not (data / "train_batch1.before-batch2.csv").exists()
