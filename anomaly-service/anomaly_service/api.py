from typing import Dict

from fastapi import Depends, FastAPI

from .config import Settings, get_settings
from .dependencies import get_scoring_service
from .models import AnomalyEvent, BatchScoreRequest, BatchScoreResponse, ScoreResponse
from .service import AnomalyScoringService


def create_app() -> FastAPI:
    app = FastAPI(
        title="Anomaly Scoring Service",
        version="0.1.0",
        description="UEBA/ML scoring service for the Synthetic AI SOC platform.",
    )
    register_routes(app)
    return app


def register_routes(app: FastAPI) -> None:
    @app.get("/health/live")
    def liveness_probe() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    def readiness_probe(
        scorer: AnomalyScoringService = Depends(get_scoring_service),
    ) -> Dict[str, str]:
        status = "ready" if scorer.is_ready else "initializing"
        return {"status": status, "model_version": scorer.model_version}

    @app.get("/metadata")
    def metadata(settings: Settings = Depends(get_settings)) -> Dict[str, str]:
        return {
            "service": "anomaly-service",
            "version": settings.service_version,
            "model_path": settings.model_path,
            "feature_store_url": settings.feature_store_url,
        }

    @app.post("/v1/score", response_model=ScoreResponse)
    def score_event(
        event: AnomalyEvent,
        scorer: AnomalyScoringService = Depends(get_scoring_service),
    ) -> ScoreResponse:
        return scorer.score_event(event)

    @app.post("/v1/score/batch", response_model=BatchScoreResponse)
    def score_batch(
        batch: BatchScoreRequest,
        scorer: AnomalyScoringService = Depends(get_scoring_service),
    ) -> BatchScoreResponse:
        return scorer.score_batch(batch.events)
