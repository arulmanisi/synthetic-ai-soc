from typing import List, Dict
from models.base import ModelListResponse, ScoreRequest, ScoreResponse
from pipelines.model import LOFModel, IsolationForestModel, OneClassSVMModel, EnsembleModel


class ScoringPipeline:
    """Pluggable anomaly scoring with IsolationForest and LOF options."""

    def __init__(self, default_model: str = "isolation-forest") -> None:
        self._default_model = default_model
        # Only initialize Isolation Forest by default for performance
        # Other models are available on-demand if explicitly requested
        self._models = {
            "isolation-forest": IsolationForestModel(random_state=42),
        }
        # Registry of available models (lazy-loaded)
        self._model_registry = {
            "isolation-forest": lambda: IsolationForestModel(random_state=42),
            "lof": lambda: LOFModel(random_state=42),
            "one-class-svm": lambda: OneClassSVMModel(random_state=42),
            "ensemble": lambda: EnsembleModel(random_state=42),
        }

    @property
    def available_models(self) -> ModelListResponse:
        return ModelListResponse(models=list(self._model_registry.keys()))

    def _get_model(self, model_name: str):
        """Get or lazily initialize a model."""
        if model_name not in self._models:
            if model_name in self._model_registry:
                self._models[model_name] = self._model_registry[model_name]()
            else:
                # Fallback to default
                return self._models[self._default_model]
        return self._models[model_name]

    def score(self, request: ScoreRequest, default_threshold: float) -> ScoreResponse:
        model_name = request.model or self._default_model
        threshold = request.threshold if request.threshold is not None else default_threshold
        scorer = self._get_model(model_name)
        score = scorer.score(request.event)
        return ScoreResponse(
            score=score,
            model=model_name,
            threshold=threshold,
            is_anomaly=score >= threshold,
        )

    def train(self, events: List[Dict], model_name: str = "isolation-forest") -> None:
        model = self._get_model(model_name)
        if hasattr(model, "fit"):
            model.fit(events)
            if hasattr(model, "save"):
                model.save(f"{model_name}.joblib")
