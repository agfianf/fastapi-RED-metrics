from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from app.schemas.example import ProductBase, ProductResponse
from fastapi import APIRouter, Body, HTTPException, Path, Query

router = APIRouter(
    prefix="/api/v1/products",
    tags=["products"],
)


async def simulate_db_latency(operation: str) -> None:
    """Simulate database operation latency with realistic timing."""
    import asyncio
    import random

    latency_ranges = {
        "read": (0.05, 0.2),  # Fast reads
        "write": (0.1, 0.3),  # Slower writes
        "heavy": (0.3, 0.8),  # Heavy operations
        "hell": (1.0, 59.0),  # Hell operations
    }
    await asyncio.sleep(random.uniform(*latency_ranges[operation]))


@router.get("")
async def list_products(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    category: str | None = None,
) -> dict:
    """List products with pagination and optional filtering."""
    await simulate_db_latency("read")

    if page > 10 and limit > 50:  # Simulate overload condition
        raise HTTPException(
            status_code=503,
            detail="Service temporarily overloaded. Please reduce page size.",
        )

    return {
        "items": [
            ProductResponse(
                id=uuid4(),
                name=f"Product {i}",
                description="Sample product",
                price=99.99,
                category="electronics",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ).model_dump()
            for i in range(limit)
        ],
        "total": 100,
        "page": page,
        "limit": limit,
    }


@router.post("")
async def create_product(
    product: Annotated[ProductBase, Body()],
) -> ProductResponse:
    """Create a new product."""
    await simulate_db_latency("write")

    if product.price > 1000:  # Simulate validation error
        raise HTTPException(
            status_code=400,
            detail="Price exceeds maximum allowed value",
        )

    return ProductResponse(
        id=uuid4(),
        **product.model_dump(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.get("/{product_id}")
async def get_product(
    product_id: Annotated[UUID, Path()],
) -> ProductResponse:
    """Retrieve a single product by ID."""
    await simulate_db_latency("read")

    if str(product_id).startswith("0"):  # Simulate not found
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(
        id=product_id,
        name="Sample Product",
        description="Detailed description",
        price=199.99,
        category="electronics",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.put("/{product_id}")
async def update_product(
    product_id: Annotated[UUID, Path()],
    product: Annotated[ProductBase, Body()],
) -> ProductResponse:
    """Update an existing product."""
    await simulate_db_latency("write")

    if str(product_id).startswith("0"):  # Simulate not found
        raise HTTPException(status_code=404, detail="Product not found")

    if str(product_id).startswith("1"):  # Simulate conflict
        raise HTTPException(
            status_code=409,
            detail="Product was modified by another request",
        )

    return ProductResponse(
        id=product_id,
        **product.model_dump(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: Annotated[UUID, Path()],
) -> dict:
    """Delete a product."""
    await simulate_db_latency("write")

    if str(product_id).startswith("0"):  # Simulate not found
        raise HTTPException(status_code=404, detail="Product not found")

    if str(product_id).startswith("9"):  # Simulate server error
        raise HTTPException(
            status_code=500,
            detail="Internal server error during deletion",
        )

    return {"status": "success", "message": f"Product {product_id} deleted"}


@router.post("/{product_id}/process")
async def process_product(
    product_id: Annotated[UUID, Path()],
) -> dict:
    """Process a product (simulating a heavy operation)."""
    await simulate_db_latency("heavy")

    if str(product_id).startswith("0"):  # Simulate not found
        raise HTTPException(status_code=404, detail="Product not found")

    if str(product_id).startswith("5"):  # Simulate timeout
        raise HTTPException(
            status_code=504,
            detail="Processing timed out",
        )

    return {
        "status": "success",
        "product_id": product_id,
        "process_id": uuid4(),
        "completed_at": datetime.now().isoformat(),
    }
