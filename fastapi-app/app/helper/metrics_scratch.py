"""This module defines the REDMetrics class, middleware, and Prometheus metrics endpoint for the FastAPI application."""

import re
import time
from collections.abc import Callable

from app.config import settings
from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from prometheus_client.utils import INF
from starlette.middleware.base import BaseHTTPMiddleware


class REDMetrics:
    """Manages RED (Request, Error, Duration) metrics for HTTP requests.

    This class initializes Prometheus metrics for tracking HTTP request counts,
    durations, error counts, and in-flight requests.
    """

    def __init__(self) -> None:  # noqa: D107
        self.request_count = Counter(
            name="http_requests_total",
            documentation="Total number of HTTP requests",
            labelnames=["method", "code", "handler", "service"],
        )

        # fmt: off
        self.request_duration = Histogram(
            name="http_request_duration_seconds",
            documentation="HTTP request duration in seconds",
            labelnames=["method", "code", "handler", "service"],
            buckets=(
                0.0,    # Start
                0.01,   # Smallest bucket size
                0.025,  # Next smallest bucket size
                0.05,   # Next bucket size
                0.075,  # Next bucket size
                0.1,    # Next bucket size
                0.25,   # Larger bucket size
                0.5,    # Larger bucket size
                0.75,   # Larger bucket size
                1.0,    # Larger bucket size
                2.5,    # Transition to larger intervals
                5.0,    # Larger interval
                7.5,    # Larger interval
                10.0,   # Larger interval
                12.5,   # Larger interval
                15.0,   # Larger interval
                17.5,   # Larger interval
                20.0,   # Larger interval
                22.5,   # Interval of 2.5
                25.0,   # Interval of 2.5
                27.5,   # Interval of 2.5
                30.0,   # Interval of 2.5
                32.5,   # Interval of 2.5
                35.0,   # Interval of 2.5
                37.5,   # Interval of 2.5
                40.0,   # Interval of 2.5
                42.5,   # Interval of 2.5
                45.0,   # Interval of 2.5
                47.5,   # Interval of 2.5
                50.0,   # Interval of 2.5
                52.5,   # Interval of 2.5
                55.0,   # Interval of 2.5
                57.5,   # Interval of 2.5
                60.0,   # End
                INF,
            ),
        )
        # fmt: on

        self.error_count = Counter(
            name="http_errors_total",
            documentation="Total number of HTTP errors",
            labelnames=["method", "code", "handler", "service"],
        )

        self.requests_inflight = Gauge(
            name="http_requests_inflight",
            documentation="Number of HTTP requests currently in flight",
            labelnames=["method", "handler", "service"],
        )

    def init_app(self, app: FastAPI) -> None:
        """Initialize the FastAPI application with REDMetrics middleware.

        Parameters
        ----------
        app : FastAPI
            The FastAPI application instance.

        """
        app.add_middleware(
            REDMetricsMiddleware,
            metrics=self,
            skip_paths={
                "/metrics": True,
                "/health": True,
                "/docs": True,
                "/openapi.json": True,
                "/favicon.ico": True,
            },
        )


class REDMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting RED metrics on HTTP requests.

    This middleware intercepts HTTP requests, collects metrics, and forwards
    the request to the next handler.
    """

    def __init__(
        self,
        app: FastAPI,
        metrics: REDMetrics,
        skip_paths: dict[str, bool],
    ) -> None:
        """Initialize the REDMetricsMiddleware with the FastAPI application,
        REDMetrics instance, and paths to skip.

        Parameters
        ----------
        app : FastAPI
            The FastAPI application instance.
        metrics : REDMetrics
            The REDMetrics instance for collecting metrics.
        skip_paths : dict[str, bool]
            Dictionary of paths to skip for metrics collection.

        """
        super().__init__(app)
        self.metrics = metrics
        self.skip_paths = skip_paths

        service_name = settings.APP_NAME.lower().replace(" ", "-")
        self.service_label = f"{service_name}--{settings.APP_ENV.lower()}"

    async def dispatch(self, request: Request, call_next: Callable):  # noqa: ANN201
        """Process the request, collect metrics, and call the next handler.

        Parameters
        ----------
        request : Request
            The incoming HTTP request.
        call_next : Callable
            The next request handler in the middleware chain.

        Returns
        -------
        Response
            The HTTP response from the next handler.

        """
        endpoint = self._normalize_path(request.url.path)
        method = request.method

        if self.skip_paths.get(endpoint, False):
            return await call_next(request)

        self.metrics.requests_inflight.labels(
            method=method,
            handler=endpoint,
            service=self.service_label,
        ).inc()

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            self.metrics.requests_inflight.labels(
                method=method,
                handler=endpoint,
                service=self.service_label,
            ).dec()
            duration = time.perf_counter() - start_time
            print(duration)

        status_code = response.status_code

        self.metrics.request_count.labels(
            method=method,
            code=status_code,
            handler=endpoint,
            service=self.service_label,
        ).inc()

        self.metrics.request_duration.labels(
            method=method,
            handler=endpoint,
            code=status_code,
            service=self.service_label,
        ).observe(duration)

        if 400 <= status_code < 600:
            self.metrics.error_count.labels(
                method=method,
                handler=endpoint,
                code=status_code,
                service=self.service_label,
            ).inc()

        return response

    def _normalize_path(self, path: str) -> str:
        """Replace numeric parts of the path with ':id'.

        Parameters
        ----------
        path : str
            The original URL path.

        Returns
        -------
        str
            The normalized path with numeric parts replaced by ':id'.

        """
        return re.sub(r"/[^/]*\d[^/]*", "/:id", path)

    def skip(self, paths: list[str]) -> None:
        """Add paths to skip for metrics collection.

        Parameters
        ----------
        paths : list of str
            List of paths to skip.

        """
        for path in paths:
            self.skip_paths[path] = True


async def metrics_endpoint(request: Request) -> Response:  # noqa: ARG001
    """Endpoint for exposing collected metrics.

    Parameters
    ----------
    request : Request
        The incoming HTTP request.

    Returns
    -------
    Response
        The response containing the latest metrics.

    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


RED_METRICS = REDMetrics()
