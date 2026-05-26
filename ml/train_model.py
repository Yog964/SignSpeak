"""
ISL SignSpeak — Model Training Script

Trains a RandomForestClassifier on CSV landmark data and saves
the model as a .pkl file for use by the FastAPI backend.

Usage examples:
    python train_model.py --data-dir ./data/fruits --output ./models/fruits.pkl --category Fruits
    python train_model.py --data-dir ./data/vegetables --output ./models/vegetables.pkl --category Vegetables
"""

import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def find_csv_files(data_dir: Path) -> list[Path]:
    """Recursively find all CSV files in *data_dir*."""
    csvs = sorted(data_dir.rglob("*.csv"))
    if not csvs:
        print(f"[ERR] No CSV files found in {data_dir}")
        sys.exit(1)
    return csvs


def load_data(csv_files: list[Path]) -> pd.DataFrame:
    """Load and concatenate all CSV files, dropping rows with NaN."""
    frames: list[pd.DataFrame] = []
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        frames.append(df)
        print(f"  [FILE] {csv_path.name}: {len(df)} rows, {len(df.columns)} cols")

    combined = pd.concat(frames, ignore_index=True)
    before = len(combined)
    combined.dropna(inplace=True)
    after = len(combined)
    if before != after:
        print(f"  [WARN] Dropped {before - after} rows with NaN values")

    return combined


def train(
    data_dir: str,
    output_path: str,
    category: str,
    n_estimators: int = 200,
    random_state: int = 42,
    test_size: float = 0.2,
) -> None:
    """End-to-end training pipeline."""
    data_dir = Path(data_dir)
    output_path = Path(output_path)

    print(f"\n[START] Training model for category: {category}")
    print(f"   Data directory : {data_dir.resolve()}")
    print(f"   Output path    : {output_path.resolve()}\n")

    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    csv_files = find_csv_files(data_dir)
    print(f"Found {len(csv_files)} CSV file(s):")
    df = load_data(csv_files)

    # ------------------------------------------------------------------
    # 2. Split features / labels
    # ------------------------------------------------------------------
    if "action" not in df.columns:
        print("[ERR] CSV files must contain an 'action' column for labels.")
        sys.exit(1)

    y = df["action"]
    X = df.drop(columns=["action"])

    classes = sorted(y.unique())
    print(f"\n[INFO] Dataset summary")
    print(f"   Total samples : {len(df)}")
    print(f"   Features      : {X.shape[1]}")
    print(f"   Classes ({len(classes)}): {', '.join(str(c) for c in classes)}")

    # ------------------------------------------------------------------
    # 3. Train / test split
    # ------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"   Train samples : {len(X_train)}")
    print(f"   Test samples  : {len(X_test)}")

    # ------------------------------------------------------------------
    # 4. Train model
    # ------------------------------------------------------------------
    print(f"\n[RUN] Training RandomForestClassifier (n_estimators={n_estimators})...")
    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    # ------------------------------------------------------------------
    # 5. Evaluate
    # ------------------------------------------------------------------
    train_acc = accuracy_score(y_train, clf.predict(X_train))
    test_acc = accuracy_score(y_test, clf.predict(X_test))

    print(f"\n[RESULT] Results")
    print(f"   Train accuracy : {train_acc:.4f}")
    print(f"   Test accuracy  : {test_acc:.4f}")
    print(f"\n   Per-class report:\n")
    print(classification_report(y_test, clf.predict(X_test)))

    # ------------------------------------------------------------------
    # 6. Save model
    # ------------------------------------------------------------------
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, output_path)
    print(f"[OK] Model saved to {output_path.resolve()}")


# ======================================================================
# CLI
# ======================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a RandomForestClassifier for ISL SignSpeak",
    )
    parser.add_argument(
        "--data-dir",
        required=True,
        help="Directory containing CSV files with landmark data",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the trained .pkl model file",
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Human-readable category name (e.g. Fruits, Vegetables)",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=200,
        help="Number of trees in the random forest (default: 200)",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of data used for testing (default: 0.2)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(
        data_dir=args.data_dir,
        output_path=args.output,
        category=args.category,
        n_estimators=args.n_estimators,
        test_size=args.test_size,
    )
