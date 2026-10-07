"""Append batch 2 once, preserving the original batch 1 for reproducibility."""
from pathlib import Path
import shutil

import pandas as pd


def append_batch():
    workspace = Path(__file__).resolve().parent
    train_path = workspace / "data/train_batch1.csv"
    new_path = workspace / "data/train_batch2.csv"
    backup_path = workspace / "data/train_batch1.before-batch2.csv"
    for path in (train_path, new_path, backup_path):
        if path.resolve() != path.absolute() or not path.resolve().is_relative_to(workspace):
            raise ValueError(f"Refusing a redirected or out-of-workspace path: {path}")
    original, new = pd.read_csv(train_path), pd.read_csv(new_path)
    if len(original) != 22361 or len(new) != 22361:
        raise ValueError("Expected two batches of 22361 rows; refusing repeated or unexpected append")
    if list(original.columns) != list(new.columns):
        raise ValueError("Batch schemas differ")
    if backup_path.exists():
        raise FileExistsError("Previous batch-1 snapshot exists; inspect it before another append")
    # Exclusive creation preserves evidence and refuses to replace an older snapshot.
    with train_path.open("rb") as source, backup_path.open("xb") as backup:
        shutil.copyfileobj(source, backup)
    updated = pd.concat([original, new], ignore_index=True)
    updated.to_csv(train_path, index=False)
    print(f"Cap nhat du lieu: {len(original)} -> {len(updated)} mau")
    print(f"Original batch preserved at: {backup_path}")


if __name__ == "__main__":
    append_batch()
