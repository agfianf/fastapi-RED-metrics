from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""

    text: str
    model_version: str = "v1"


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""

    prediction_id: UUID
    result: str
    confidence: float
    processing_time: float
    timestamp: datetime
