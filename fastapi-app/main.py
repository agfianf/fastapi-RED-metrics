from contextlib import asynccontextmanager

from app.controllers.example import router as route_example
from app.helper.metrics_scratch import RED_METRICS, metrics_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, D103
    yield


app = FastAPI(
    title="FastAPI RED Metrics",
    description="Example RED Metrics implementations",
    version="v0.0.1-local",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# Add routes
app.include_router(route_example)

# Add metrics endpoint
RED_METRICS.init_app(app)
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    print("running app")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
