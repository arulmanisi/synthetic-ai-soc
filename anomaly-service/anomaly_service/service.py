from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from .models import AnomalyEvent, BatchScoreResponse, ScoreResponse


class AnomalyScoringService(ABC):
    """Interface for anomaly scoring implementations."""

    @abstractmethod
    def score_event(self, event: AnomalyEvent) -> ScoreResponse:
        raise NotImplementedError

    @abstractmethod
    def score_batch(self, events: Iterable[AnomalyEvent]) -> BatchScoreResponse:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_version(self) -> str:
        raise NotImplementedError


class DummyAnomalyScoringService(AnomalyScoringService):
    """Placeholder scorer until a real model is wired in."""

    def __init__(self, model_path: str | None = None):
        self._model_path = model_path
        self._model_version = "dev-placeholder"

    @property
    def is_ready(self) -> bool:
        return True

    @property
    def model_version(self) -> str:
        return self._model_version

    def score_event(self, event: AnomalyEvent) -> ScoreResponse:
        score = self._synthetic_score(event)
        threshold = 0.8
        return ScoreResponse(
            event_id=event.event_id,
            anomaly_score=score,
            threshold=threshold,
            is_anomaly=score >= threshold,
            model_version=self.model_version,
            reason="Synthetic score placeholder; plug in trained model.",
        )

    def score_batch(self, events: Iterable[AnomalyEvent]) -> BatchScoreResponse:
        results: List[ScoreResponse] = [self.score_event(event) for event in events]
        return BatchScoreResponse(results=results)

    def _synthetic_score(self, event: AnomalyEvent) -> float:
        if not event.features:
            return 0.0
        feature_values = list(event.features.values())
        normalized = (max(feature_values) + sum(feature_values) / len(feature_values)) / (
            1 + len(feature_values)
        )
        return max(0.0, min(1.0, normalized))
