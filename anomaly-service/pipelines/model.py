from typing import List, Sequence

import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestModel:
    """Lazy-fitted IsolationForest wrapper with deterministic baseline."""

    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        random_state: int | None = 42,
    ) -> None:
        self._contamination = contamination
        self._n_estimators = n_estimators
        self._random_state = random_state
        self._model: IsolationForest | None = None
        self._feature_order: List[str] | None = None

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    @property
    def feature_order(self) -> List[str] | None:
        return self._feature_order

    def _vectorize(self, features: dict) -> np.ndarray:
        if self._feature_order is None:
            # Establish feature order deterministically on first use.
            self._feature_order = sorted(features.keys())
        vector: List[float] = []
        for key in self._feature_order:
            vector.append(self._to_float(features.get(key, 0.0)))
        return np.array(vector, dtype=np.float32)

    def _to_float(self, value: object) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, bool):
            return float(int(value))
        # For categorical/string values, use a deterministic hash projection to [0,1].
        try:
            import hashlib

            hashed = int(hashlib.sha1(str(value).encode("utf-8")).hexdigest(), 16)
            return (hashed % 10**6) / 10**6
        except Exception:
            return 0.0

    def _fit_baseline(self, feature_dim: int) -> None:
        rng = np.random.default_rng(self._random_state)
        baseline = rng.normal(loc=0.0, scale=1.0, size=(256, feature_dim))
        self._model = IsolationForest(
            contamination=self._contamination,
            n_estimators=self._n_estimators,
            random_state=self._random_state,
        )
        self._model.fit(baseline)

    def score(self, features: dict) -> float:
        """Return anomaly score in [0, 1], higher means more anomalous."""
        vector = self._vectorize(features)
        if not self.is_trained:
            self._fit_baseline(feature_dim=vector.shape[0])
        assert self._model is not None
        raw = self._model.decision_function(vector.reshape(1, -1))[0]
        # Decision function typically in ~[-0.5, 0.5]; squash to (0,1).
        return float(1 / (1 + np.exp(-raw)))
