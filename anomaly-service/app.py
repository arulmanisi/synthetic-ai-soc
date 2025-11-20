from functools import lru_cache

from fastapi import Depends, FastAPI

from config import Settings, get_settings
from models.base import ModelListResponse, ScoreRequest, ScoreResponse
from pipelines.scorer import ScoringPipeline


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

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/models", response_model=ModelListResponse)
    def list_models(pipeline: ScoringPipeline = Depends(get_pipeline)) -> ModelListResponse:
        return pipeline.available_models

    @app.post("/score", response_model=ScoreResponse)
    def score(
        request: ScoreRequest, pipeline: ScoringPipeline = Depends(get_pipeline)
    ) -> ScoreResponse:
        return pipeline.score(request)

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
