from typing import List, Dict
from models.base import ModelListResponse, ScoreRequest, ScoreResponse
from pipelines.model import LOFModel, IsolationForestModel


class ScoringPipeline:
    """Pluggable anomaly scoring with IsolationForest and LOF options."""

    def __init__(self, default_model: str = "isolation-forest") -> None:
        self._default_model = default_model
        self._models = {
            "isolation-forest": IsolationForestModel(random_state=42),
            "lof": LOFModel(random_state=42),
        }

    @property
    def available_models(self) -> ModelListResponse:
        return ModelListResponse(models=list(self._models.keys()))

    def score(self, request: ScoreRequest, default_threshold: float) -> ScoreResponse:
        model = request.model or self._default_model
        threshold = request.threshold if request.threshold is not None else default_threshold
        scorer = self._models.get(model, self._models[self._default_model])
        score = scorer.score(request.event)
        return ScoreResponse(
            score=score,
            model=model,
            threshold=threshold,
            is_anomaly=score >= threshold,
        )

    def train(self, events: List[Dict], model_name: str = "isolation-forest") -> None:
        model = self._models.get(model_name)
        if hasattr(model, "fit"):
            model.fit(events)
            if hasattr(model, "save"):
                model.save(f"{model_name}.joblib")
