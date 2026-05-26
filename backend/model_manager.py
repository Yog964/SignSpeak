"""
Model Manager for ISL SignSpeak

Loads sklearn RandomForestClassifier .pkl models from a directory at startup,
provides thread-safe prediction with confidence scoring, and auto-generates
display names from filenames (e.g. ``fruits.pkl`` → ``Fruits``).
"""

import os
import threading
from pathlib import Path
from typing import Any

import joblib
import numpy as np


class ModelManager:
    """Manages loading and inference for multiple sklearn classifier models."""

    DEFAULT_CONFIDENCE_THRESHOLD = 30.0  # percent

    def __init__(self, confidence_threshold: float | None = None):
        self._models: dict[str, Any] = {}
        self._model_names: dict[str, str] = {}
        self._lock = threading.Lock()
        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else self.DEFAULT_CONFIDENCE_THRESHOLD
        )

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_models(self, models_dir: str | Path) -> list[str]:
        """
        Scan *models_dir* for ``.pkl`` files and load each with joblib.

        Returns a list of model IDs that were successfully loaded.
        """
        models_dir = Path(models_dir)
        if not models_dir.is_dir():
            print(f"[ModelManager] Models directory not found: {models_dir}")
            return []

        loaded: list[str] = []
        with self._lock:
            self._models.clear()
            self._model_names.clear()

        for pkl_path in sorted(models_dir.glob("*.pkl")):
            model_id = pkl_path.stem.lower()
            display_name = model_id.replace("_", " ").replace("-", " ").title()
            try:
                model = joblib.load(pkl_path)
                with self._lock:
                    self._models[model_id] = model
                    self._model_names[model_id] = display_name
                loaded.append(model_id)
                print(f"  [OK] Loaded model: {display_name} ({pkl_path.name})")
            except Exception as exc:
                print(f"  [ERR] Failed to load {pkl_path.name}: {exc}")

        return loaded

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def get_available_models(self) -> list[dict[str, str]]:
        """Return a list of ``{"id": ..., "name": ...}`` dicts."""
        with self._lock:
            return [
                {"id": mid, "name": self._model_names[mid]}
                for mid in sorted(self._models)
            ]

    def has_model(self, model_id: str) -> bool:
        with self._lock:
            return model_id in self._models

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_with_confidence(
        self, model_id: str, features: np.ndarray
    ) -> dict[str, Any]:
        """
        Run prediction on *features* using the model identified by *model_id*.

        Parameters
        ----------
        model_id : str
            Key that was derived from the ``.pkl`` filename (e.g. ``"fruits"``).
        features : np.ndarray
            Feature array of shape ``(1, N)`` ready for ``model.predict_proba``.

        Returns
        -------
        dict
            ``{"sign": str, "confidence": float, "category": str}``
            If the highest probability is below the confidence threshold the
            result will be ``{"sign": "", "confidence": 0, "category": ""}``.
        """
        with self._lock:
            model = self._models.get(model_id)
            display_name = self._model_names.get(model_id, "")

        if model is None:
            raise KeyError(f"Model '{model_id}' not found")

        # Thread-safe prediction (RandomForest is not inherently thread-safe)
        with self._lock:
            probabilities = model.predict_proba(features)[0]

        max_idx = int(np.argmax(probabilities))
        max_confidence = float(probabilities[max_idx] * 100)

        if max_confidence < self.confidence_threshold:
            return {"sign": "", "confidence": 0, "category": ""}

        predicted_class = model.classes_[max_idx]
        return {
            "sign": str(predicted_class),
            "confidence": round(max_confidence, 1),
            "category": display_name,
        }
