from typing import Dict, List, Protocol, Sequence

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM


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
        contamination: float = 0.2,
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
            # Fallback to dummy baseline if not trained
            self._fit_baseline(feature_dim=vector.shape[0])
        assert self._model is not None
        raw = self._model.decision_function(vector.reshape(1, -1))[0]
        return float(1 / (1 + np.exp(-raw)))

    def fit(self, events: List[Dict]) -> None:
        """Fit the model on real events."""
        if not events:
            return
        
        # Vectorize all events
        vectors = [self._vectorizer.vectorize(e) for e in events]
        X = np.array(vectors)
        
        self._model = IsolationForest(
            contamination=self._contamination,
            n_estimators=self._n_estimators,
            random_state=self._random_state,
        )
        self._model.fit(X)

    def save(self, path: str) -> None:
        if self._model:
            joblib.dump(self._model, path)

    def load(self, path: str) -> None:
        try:
            self._model = joblib.load(path)
        except Exception:
            self._model = None


class LOFModel(AnomalyModel):
    """Local Outlier Factor scorer using a baseline fit."""

    def __init__(self, contamination: float = 0.2, random_state: int | None = 42) -> None:
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


class OneClassSVMModel(AnomalyModel):
    """One-Class SVM for anomaly detection."""

    def __init__(
        self,
        nu: float = 0.9,  # Very aggressive - expect up to 90% anomalies
        kernel: str = "linear",  # Linear kernel often works better for high-dim data
        gamma: str = "scale",
        random_state: int | None = 42,
    ) -> None:
        self.name = "one-class-svm"
        self._nu = nu
        self._kernel = kernel
        self._gamma = gamma
        self._random_state = random_state
        self._model: OneClassSVM | None = None
        self._vectorizer = BaseVectorizer()

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def _fit_baseline(self, feature_dim: int) -> None:
        rng = np.random.default_rng(self._random_state)
        baseline = rng.normal(loc=0.0, scale=1.0, size=(256, feature_dim))
        self._model = OneClassSVM(
            nu=self._nu,
            kernel=self._kernel,
            gamma=self._gamma,
        )
        self._model.fit(baseline)

    def score(self, features: Dict) -> float:
        vector = self._vectorizer.vectorize(features)
        if not self.is_trained:
            # Fallback to dummy baseline if not trained
            self._fit_baseline(feature_dim=vector.shape[0])
        assert self._model is not None
        raw = self._model.decision_function(vector.reshape(1, -1))[0]
        return float(1 / (1 + np.exp(-raw)))

    def fit(self, events: List[Dict]) -> None:
        """Fit the model on real events."""
        if not events:
            return
        
        # Vectorize all events
        vectors = [self._vectorizer.vectorize(e) for e in events]
        X = np.array(vectors)
        
        self._model = OneClassSVM(
            nu=self._nu,
            kernel=self._kernel,
            gamma=self._gamma,
        )
        self._model.fit(X)

    def save(self, path: str) -> None:
        if self._model:
            joblib.dump(self._model, path)

    def load(self, path: str) -> None:
        try:
            self._model = joblib.load(path)
        except Exception:
            self._model = None


class EnsembleModel(AnomalyModel):
    """Ensemble model combining multiple anomaly detectors."""

    def __init__(self, random_state: int | None = 42) -> None:
        self.name = "ensemble"
        self._random_state = random_state
        self._models = [
            IsolationForestModel(random_state=random_state),
            LOFModel(random_state=random_state),
            OneClassSVMModel(random_state=random_state),
        ]
        self._vectorizer = BaseVectorizer()

    @property
    def is_trained(self) -> bool:
        return all(model.is_trained for model in self._models)

    def score(self, features: Dict) -> float:
        """Average the scores from all models."""
        scores = [model.score(features) for model in self._models]
        return float(np.mean(scores))

    def fit(self, events: List[Dict]) -> None:
        """Fit all models in the ensemble."""
        for model in self._models:
            if hasattr(model, "fit"):
                model.fit(events)

    def save(self, path: str) -> None:
        """Save all models in the ensemble."""
        for i, model in enumerate(self._models):
            if hasattr(model, "save"):
                model.save(f"{path}_model{i}.joblib")

    def load(self, path: str) -> None:
        """Load all models in the ensemble."""
        for i, model in enumerate(self._models):
            if hasattr(model, "load"):
                model.load(f"{path}_model{i}.joblib")
