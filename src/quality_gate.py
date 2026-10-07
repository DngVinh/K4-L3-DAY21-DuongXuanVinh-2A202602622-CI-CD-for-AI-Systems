"""Quality and regression gates shared by CI and tests (no cloud dependencies)."""
import argparse
import json
import math
from pathlib import Path

F1_THRESHOLD = 0.65


def validate_release(candidate: dict, current: dict | None = None) -> None:
    f1 = float(candidate["f1_score"])
    if not math.isfinite(f1) or not 0 <= f1 <= 1:
        raise ValueError("FAILED: f1_score must be finite and in [0, 1]")
    if f1 < F1_THRESHOLD:
        raise ValueError(f"FAILED: f1_score {f1:.4f} < {F1_THRESHOLD}; Release blocked")
    if current is not None:
        previous = float(current["f1_score"])
        if not math.isfinite(previous) or not 0 <= previous <= 1:
            raise ValueError("FAILED: current report has invalid F1; cannot safely compare")
        if candidate.get("eval_sha256") != current.get("eval_sha256"):
            raise ValueError("FAILED: holdout changed; F1 scores are not comparable")
        print(f"Regression check: candidate F1={f1:.6f}; current F1={previous:.6f}")
        if f1 < previous:
            raise ValueError("FAILED: candidate F1 is lower; existing model retained")
    print(f"PASSED: positive-class F1={f1:.6f} >= {F1_THRESHOLD}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--f1", type=float)
    group.add_argument("--report", type=Path)
    parser.add_argument("--current", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text()) if args.report else {"f1_score": args.f1}
    current = json.loads(args.current.read_text()) if args.current else None
    try:
        validate_release(report, current)
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error))
