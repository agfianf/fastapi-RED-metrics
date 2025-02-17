from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
