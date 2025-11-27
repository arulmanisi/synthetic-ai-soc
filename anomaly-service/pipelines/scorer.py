from models.base import ModelListResponse, ScoreRequest, ScoreResponse
from pipelines.model import IsolationForestModel


class ScoringPipeline:
    """IsolationForest-backed scoring with deterministic baseline."""

    def __init__(self, default_model: str = "isolation-forest") -> None:
        self._default_model = default_model
        self._model = IsolationForestModel(random_state=42)

    @property
    def available_models(self) -> ModelListResponse:
        return ModelListResponse(models=[self._default_model])

    def score(self, request: ScoreRequest, default_threshold: float) -> ScoreResponse:
        model = request.model or self._default_model
        threshold = request.threshold if request.threshold is not None else default_threshold
        score = self._model.score(request.event)
        return ScoreResponse(
            score=score,
            model=model,
            threshold=threshold,
            is_anomaly=score >= threshold,
        )
