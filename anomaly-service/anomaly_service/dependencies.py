from functools import lru_cache

from fastapi import Depends

from .config import Settings, get_settings
from .service import AnomalyScoringService, DummyAnomalyScoringService


@lru_cache
def _build_service(settings: Settings) -> AnomalyScoringService:
    return DummyAnomalyScoringService(model_path=settings.model_path)


def get_scoring_service(
    settings: Settings = Depends(get_settings),
) -> AnomalyScoringService:
    return _build_service(settings)
