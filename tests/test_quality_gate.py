import subprocess
import sys

import pytest

from src.quality_gate import validate_release


@pytest.mark.parametrize("f1", [0, 0.6499, float("nan"), float("inf"), -1, 1.1])
def test_bad_f1_blocks_release(f1):
    with pytest.raises(ValueError):
        validate_release({"f1_score": f1})


@pytest.mark.parametrize("f1", [0.65, 0.8, 1.0])
def test_boundary_and_good_f1_pass(f1):
    validate_release({"f1_score": f1})


def test_regression_keeps_current_model():
    with pytest.raises(ValueError, match="existing model retained"):
        validate_release({"f1_score": 0.7, "eval_sha256": "fixed"},
                         {"f1_score": 0.8, "eval_sha256": "fixed"})


def test_equal_f1_is_deployable():
    validate_release({"f1_score": 0.8, "eval_sha256": "fixed"},
                     {"f1_score": 0.8, "eval_sha256": "fixed"})


def test_changed_holdout_blocks_comparison():
    with pytest.raises(ValueError, match="holdout changed"):
        validate_release({"f1_score": 0.9, "eval_sha256": "new"},
                         {"f1_score": 0.8, "eval_sha256": "old"})


def test_gate_cli_returns_nonzero_below_threshold():
    result = subprocess.run([sys.executable, "-m", "src.quality_gate", "--f1", "0.64"],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "Release blocked" in result.stderr
