from models.base import ModelListResponse, ScoreRequest, ScoreResponse


class ScoringPipeline:
    """Simple deterministic scoring stub with thresholding."""

    def __init__(self, default_model: str = "placeholder-v0") -> None:
        self._default_model = default_model

    @property
    def available_models(self) -> ModelListResponse:
        return ModelListResponse(models=[self._default_model])

    def score(self, request: ScoreRequest, default_threshold: float) -> ScoreResponse:
        model = request.model or self._default_model
        threshold = request.threshold if request.threshold is not None else default_threshold
        score = self._pseudo_score(request.event)
        return ScoreResponse(
            score=score,
            model=model,
            threshold=threshold,
            is_anomaly=score >= threshold,
        )

    def _pseudo_score(self, payload: dict) -> float:
        """Deterministic pseudo-score in [0,1] based on event content."""
        if not payload:
            return 0.0
        accum = 0
        for key, value in sorted(payload.items()):
            accum += hash(f"{key}:{value}") & 0xFFFFFFFF
        # Normalize using a simple modulus; ensures repeatability for same payload.
        max_uint32 = 2**32 - 1
        return (accum % max_uint32) / max_uint32
