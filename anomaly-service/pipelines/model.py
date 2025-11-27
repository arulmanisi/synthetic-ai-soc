from typing import Dict, List, Protocol, Sequence

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


class AnomalyModel(Protocol):
    name: str

    def score(self, features: Dict) -> float:
        ...


class BaseVectorizer:
    """Utility to vectorize arbitrary features deterministically."""

    def __init__(self, feature_order: List[str] | None = None) -> None:
        self._feature_order = feature_order

    @property
    def feature_order(self) -> List[str] | None:
        return self._feature_order

    def vectorize(self, features: Dict) -> np.ndarray:
        if self._feature_order is None:
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
        try:
            import hashlib

            hashed = int(hashlib.sha1(str(value).encode("utf-8")).hexdigest(), 16)
            return (hashed % 10**6) / 10**6
        except Exception:
            return 0.0


class IsolationForestModel(AnomalyModel):
    """Lazy-fitted IsolationForest wrapper with deterministic baseline."""

    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        random_state: int | None = 42,
    ) -> None:
        self.name = "isolation-forest"
        self._contamination = contamination
        self._n_estimators = n_estimators
        self._random_state = random_state
        self._model: IsolationForest | None = None
        self._vectorizer = BaseVectorizer()

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def _fit_baseline(self, feature_dim: int) -> None:
        rng = np.random.default_rng(self._random_state)
        baseline = rng.normal(loc=0.0, scale=1.0, size=(256, feature_dim))
        self._model = IsolationForest(
            contamination=self._contamination,
            n_estimators=self._n_estimators,
            random_state=self._random_state,
        )
        self._model.fit(baseline)

    def score(self, features: Dict) -> float:
        vector = self._vectorizer.vectorize(features)
        if not self.is_trained:
            self._fit_baseline(feature_dim=vector.shape[0])
        assert self._model is not None
        raw = self._model.decision_function(vector.reshape(1, -1))[0]
        return float(1 / (1 + np.exp(-raw)))


class LOFModel(AnomalyModel):
    """Local Outlier Factor scorer using a baseline fit."""

    def __init__(self, contamination: float = 0.1, random_state: int | None = 42) -> None:
        self.name = "lof"
        self._contamination = contamination
        self._random_state = random_state
        self._model: LocalOutlierFactor | None = None
        self._vectorizer = BaseVectorizer()

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def _fit_baseline(self, feature_dim: int) -> None:
        rng = np.random.default_rng(self._random_state)
        baseline = rng.normal(loc=0.0, scale=1.0, size=(256, feature_dim))
        # LOF requires n_neighbors < n_samples; using defaults.
        self._model = LocalOutlierFactor(
            contamination=self._contamination,
            novelty=True,
        )
        self._model.fit(baseline)

    def score(self, features: Dict) -> float:
        vector = self._vectorizer.vectorize(features)
        if not self.is_trained:
            self._fit_baseline(feature_dim=vector.shape[0])
        assert self._model is not None
        raw = self._model.decision_function(vector.reshape(1, -1))[0]
        return float(1 / (1 + np.exp(-raw)))
