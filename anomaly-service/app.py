from functools import lru_cache
from typing import List, Dict

from fastapi import Depends, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from config import Settings, get_settings
from models.base import ModelListResponse, ScoreRequest, ScoreResponse
from pipelines.scorer import ScoringPipeline
from pipelines.metrics import calculate_metrics


@lru_cache
def _build_pipeline(default_model: str) -> ScoringPipeline:
    return ScoringPipeline(default_model=default_model)


def get_pipeline(
    settings: Settings = Depends(get_settings),
) -> ScoringPipeline:
    return _build_pipeline(settings.default_model)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    # Instrument Prometheus metrics for request latency, count, and exception tracking.
    Instrumentator().instrument(app).expose(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/models", response_model=ModelListResponse)
    def list_models(pipeline: ScoringPipeline = Depends(get_pipeline)) -> ModelListResponse:
        return pipeline.available_models

    @app.post("/score", response_model=ScoreResponse)
    def score(
        request: ScoreRequest,
        pipeline: ScoringPipeline = Depends(get_pipeline),
        settings: Settings = Depends(get_settings),
    ) -> ScoreResponse:
        return pipeline.score(request, default_threshold=settings.default_threshold)

    @app.post("/train")
    def train(
        events: List[Dict],
        pipeline: ScoringPipeline = Depends(get_pipeline),
    ) -> dict[str, str]:
        pipeline.train(events)
        return {"status": "trained"}

    @app.post("/evaluate")
    def evaluate(
        test_data: List[Dict],
        pipeline: ScoringPipeline = Depends(get_pipeline),
        settings: Settings = Depends(get_settings),
    ) -> dict:
        """Evaluate model on labeled test data.
        
        test_data: List of dicts with 'event' and 'is_anomaly' keys
        """
        y_true = []
        y_pred = []
        y_scores = []
        
        for item in test_data:
            event = item["event"]
            true_label = item["is_anomaly"]
            
            # Score the event
            score_result = pipeline.score(
                ScoreRequest(event=event),
                default_threshold=settings.default_threshold
            )
            
            y_true.append(1 if true_label else 0)
            y_pred.append(1 if score_result.is_anomaly else 0)
            y_scores.append(score_result.score)
        
        metrics = calculate_metrics(y_true, y_pred, y_scores)
        return metrics

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
