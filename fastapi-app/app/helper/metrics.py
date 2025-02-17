"""FastAPI Prometheus metrics collection and monitoring.

This module provides a comprehensive metrics collection system for FastAPI applications
using the RED (Request rate, Error rate, and Duration) methodology. It leverages
Prometheus client library to expose metrics that can be scraped by Prometheus server.

Classes
-------
PrometheusMetricsCollector
    Main class for managing Prometheus metrics collection.
PrometheusMetricsMiddleware
    FastAPI middleware for intercepting requests and collecting metrics.

Functions
---------
expose_metrics_endpoint
    Endpoint handler for exposing Prometheus metrics.
"""  # noqa: E501

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


class PrometheusMetricsCollector:
    """Manages Prometheus metrics collection for HTTP requests using RED
    methodology.

    This class initializes and manages Prometheus metrics
    for monitoring HTTP requests, including request counts,
    durations, error counts, and in-flight requests.

    Attributes
    ----------
    request_counter : Counter
        Tracks total number of HTTP requests
    request_latency : Histogram
        Measures HTTP request duration
    error_counter : Counter
        Counts HTTP errors (4xx and 5xx responses)
    active_requests : Gauge
        Monitors currently active HTTP requests

    Methods
    -------
    init_app(app)
        Initializes FastAPI application with metrics middleware

    """

    def __init__(self) -> None:
        """Initialize Prometheus metrics collectors."""
        self.request_counter = Counter(
            name="http_requests_total",
            documentation="Total count of HTTP requests",
            labelnames=["method", "status_code", "endpoint", "service"],
        )

        self.request_latency = Histogram(
            name="http_request_duration_seconds",
            documentation="HTTP request latency in seconds",
            labelnames=["method", "status_code", "endpoint", "service"],
            buckets=(
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
                15.0,
                20.0,
                30.0,
                45.0,
                60.0,
                INF,
            ),
        )

        self.error_counter = Counter(
            name="http_errors_total",
            documentation="Total count of HTTP errors (4xx-5xx)",
            labelnames=["method", "status_code", "endpoint", "service"],
        )

        self.active_requests = Gauge(
            name="http_requests_active",
            documentation="Number of currently active HTTP requests",
            labelnames=["method", "endpoint", "service"],
        )

    def init_app(self, app: FastAPI) -> None:
        """Initialize FastAPI application with metrics middleware.

        Parameters
        ----------
        app : FastAPI
            The FastAPI application instance to instrument

        Notes
        -----
        Adds PrometheusMetricsMiddleware to the application middleware stack
        and configures default paths to skip for metrics collection.

        """
        excluded_paths = {
            "/metrics": True,
            "/health": True,
            "/docs": True,
            "/openapi.json": True,
            "/favicon.ico": True,
        }

        app.add_middleware(
            PrometheusMetricsMiddleware,
            metrics_collector=self,
            excluded_paths=excluded_paths,
        )


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for collecting Prometheus metrics.

    Intercepts HTTP requests to collect RED metrics before forwarding to handlers.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance
    metrics_collector : PrometheusMetricsCollector
        Instance of metrics collector
    excluded_paths : dict[str, bool]
        Paths to exclude from metrics collection

    """

    def __init__(
        self,
        app: FastAPI,
        metrics_collector: PrometheusMetricsCollector,
        excluded_paths: dict[str, bool],
    ) -> None:
        """Initialize the metrics middleware."""
        super().__init__(app)
        self.metrics = metrics_collector
        self.excluded_paths = excluded_paths
        self.service_name = self._format_service_name()

    def _format_service_name(self) -> str:
        """Format service name for metrics labels."""
        app_name = settings.APP_NAME.lower().replace(" ", "-")
        return f"{app_name}--{settings.APP_ENV.lower()}"

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and collect metrics.

        Parameters
        ----------
        request : Request
            Incoming HTTP request
        call_next : Callable
            Next request handler

        Returns
        -------
        Response
            HTTP response from handler

        """
        endpoint = self._normalize_path(request.url.path)
        method = request.method

        if self.excluded_paths.get(endpoint, False):
            return await call_next(request)

        return await self._handle_metrics_collection(
            request,
            call_next,
            method,
            endpoint,
        )

    async def _handle_metrics_collection(
        self,
        request: Request,
        call_next: Callable,
        method: str,
        endpoint: str,
    ) -> Response:
        """Collect metrics for the request-response cycle."""
        self.metrics.active_requests.labels(
            method=method,
            endpoint=endpoint,
            service=self.service_name,
        ).inc()

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            return await self._record_metrics(
                method,
                endpoint,
                response,
                start_time,
            )
        finally:
            self.metrics.active_requests.labels(
                method=method,
                endpoint=endpoint,
                service=self.service_name,
            ).dec()

    async def _record_metrics(
        self,
        method: str,
        endpoint: str,
        response: Response,
        start_time: float,
    ) -> Response:
        """Record metrics for completed request."""
        duration = time.perf_counter() - start_time
        status_code = response.status_code

        self.metrics.request_counter.labels(
            method=method,
            status_code=status_code,
            endpoint=endpoint,
            service=self.service_name,
        ).inc()

        self.metrics.request_latency.labels(
            method=method,
            status_code=status_code,
            endpoint=endpoint,
            service=self.service_name,
        ).observe(duration)

        if status_code >= 400:
            self.metrics.error_counter.labels(
                method=method,
                status_code=status_code,
                endpoint=endpoint,
                service=self.service_name,
            ).inc()

        return response

    def _normalize_path(self, path: str) -> str:
        """Normalize URL path by replacing numeric segments with ':id'.

        Parameters
        ----------
        path : str
            Raw URL path

        Returns
        -------
        str
            Normalized path with numeric segments replaced

        """
        pattern = r"/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"  # noqa: E501
        path = re.sub(pattern, "/:id", path)
        return path

    def exclude_paths(self, paths: list[str]) -> None:
        """Add paths to exclude from metrics collection.

        Parameters
        ----------
        paths : list[str]
            List of paths to exclude

        """
        for path in paths:
            self.excluded_paths[path] = True


async def expose_metrics_endpoint(request: Request) -> Response:
    """Expose Prometheus metrics endpoint.

    Parameters
    ----------
    request : Request
        HTTP request object

    Returns
    -------
    Response
        Prometheus metrics in text format

    """
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# Global metrics collector instance
METRICS_COLLECTOR = PrometheusMetricsCollector()
