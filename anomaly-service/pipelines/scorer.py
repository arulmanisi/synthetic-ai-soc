from models.base import ModelListResponse, ScoreRequest, ScoreResponse


class ScoringPipeline:
    """Simple placeholder scoring pipeline."""

    def __init__(self, default_model: str = "placeholder-v0") -> None:
        self._default_model = default_model

    @property
    def available_models(self) -> ModelListResponse:
        return ModelListResponse(models=[self._default_model])

    def score(self, request: ScoreRequest) -> ScoreResponse:
        _ = request.event  # reserved for future feature extraction
        return ScoreResponse(score=0.5, model=self._default_model)
