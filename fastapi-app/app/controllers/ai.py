import asyncio
import random
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from app.schemas.ai import PredictionRequest, PredictionResponse
from fastapi import APIRouter, Body, HTTPException, Path, Query

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["ai"],
)


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: Annotated[PredictionRequest, Body()],
    simulate_error: Annotated[bool, Query()] = False,
) -> PredictionResponse:
    """Simulate an AI prediction endpoint with variable latency.

    Parameters
    ----------
    request : PredictionRequest
        The prediction request containing text to analyze
    simulate_error : bool, optional
        If True, randomly generates errors for testing

    Returns
    -------
    PredictionResponse
        The prediction results

    Raises
    ------
    HTTPException
        When simulate_error is True (random 4xx/5xx errors)

    """
    # Simulate random processing time between 0.1 and 2 seconds
    processing_time = random.uniform(0.1, 59.0)
    await asyncio.sleep(processing_time)

    # Randomly generate errors if simulate_error is True
    if simulate_error and random.random() < 0.5:
        error_codes = [400, 401, 403, 500, 503]
        error_code = random.choice(error_codes)
        raise HTTPException(
            status_code=error_code,
            detail=f"Simulated error with status code {error_code}",
        )

    return PredictionResponse(
        prediction_id=uuid4(),
        result=f"Processed: {request.text[:50]}...",
        confidence=random.uniform(0.7, 1.0),
        processing_time=processing_time,
        timestamp=datetime.now(UTC),
    )


@router.get("/predict/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: Annotated[UUID, Path()],
    simulate_error: Annotated[bool, Query()] = False,
) -> PredictionResponse:
    """Retrieve a prediction result by ID with simulated behavior.

    Parameters
    ----------
    prediction_id : UUID
        The ID of the prediction to retrieve
    simulate_error : bool, optional
        If True, randomly generates errors for testing

    Returns
    -------
    PredictionResponse
        The prediction results

    Raises
    ------
    HTTPException
        When simulate_error is True or prediction not found

    """
    # Simulate random processing time between 0.05 and 0.5 seconds
    processing_time = random.uniform(0.05, 0.5)
    await asyncio.sleep(processing_time)

    if simulate_error and random.random() < 0.3:
        raise HTTPException(
            status_code=404,
            detail=f"Prediction {prediction_id} not found",
        )

    return PredictionResponse(
        prediction_id=prediction_id,
        result="Cached prediction result",
        confidence=0.95,
        processing_time=processing_time,
        timestamp=datetime.now(UTC),
    )
