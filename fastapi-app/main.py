from contextlib import asynccontextmanager

from app.controllers.ai import router as route_ai
from app.controllers.example import router as route_example
from app.helper.metrics import METRICS_COLLECTOR, expose_metrics_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, D103
    yield


app = FastAPI(
    title="FastAPI RED Metrics",
    description="""FastAPI RED Metrics Example 🚀

Monitor your API's **R**ate, **E**rrors, and **D**uration with this FastAPI 
example. 

#### Visualize API Traffic 📊
Explore the metrics in Grafana and Prometheus:

- [Grafana](http://localhost:3000) (admin:admin) 
- [Prometheus](http://localhost:9090) 
    """,
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


# add redirect to docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():  # noqa: ANN201, D103
    return RedirectResponse(url="/docs")


# Add routes sample
app.include_router(route_example)
app.include_router(route_ai)

# Add metrics endpoint
METRICS_COLLECTOR.init_app(app)
app.add_api_route(
    "/metrics",
    expose_metrics_endpoint,
    methods=["GET"],
    include_in_schema=False,
)


if __name__ == "__main__":
    import uvicorn

    print("running app")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # set to False for production
    )
