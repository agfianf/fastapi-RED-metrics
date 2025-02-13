import asyncio
import random
import uuid

from fastapi import APIRouter, Body, HTTPException

router = APIRouter()


@router.get("/hello")
async def hello() -> dict:  # noqa: D103
    await asyncio.sleep(random.uniform(3, 7))
    return {"message": "Hello, World!"}


@router.get("/random")
async def random_number() -> dict:  # noqa: D103
    # Simulate some processing time
    await asyncio.sleep(random.uniform(0.1, 0.5))

    # Randomly raise an error
    random_value = random.random()
    if random_value < 0.2 and random_value > 0.1:
        raise HTTPException(status_code=500, detail="Random error occurred")
    if random_value > 0.35:
        raise HTTPException(status_code=400, detail="Random error occurred")

    return {"number": random.randint(1, 100)}


@router.get("/unique/{unique_id}")
async def unique_endpoint(unique_id: str) -> dict:  # noqa: D103
    # Simulate some processing time
    await asyncio.sleep(random.uniform(0.2, 0.6))

    # Randomly raise an error
    random_value = random.random()
    if random_value < 0.15:
        raise HTTPException(
            status_code=500,
            detail=f"Error with ID {unique_id}",
        )
    if random_value > 0.4:
        raise HTTPException(
            status_code=400,
            detail=f"Error with ID {unique_id}",
        )

    return {"unique_id": unique_id, "status": "success"}


@router.get("/process/{process_id}")
async def process_endpoint(process_id: str) -> dict:  # noqa: D103
    # Simulate some processing time
    await asyncio.sleep(random.uniform(0.3, 0.7))

    # Randomly raise an error
    random_value = random.random()
    if random_value < 0.1:
        raise HTTPException(
            status_code=500,
            detail=f"Process error with ID {process_id}",
        )
    if random_value > 0.5:
        raise HTTPException(
            status_code=400,
            detail=f"Process error with ID {process_id}",
        )

    return {"process_id": process_id, "result": "completed"}


@router.post("/create")
async def create_item(item: dict = Body(...)) -> dict:
    # Simulate item creation
    await asyncio.sleep(random.uniform(0.1, 0.3))
    return {"item_id": str(uuid.uuid4()), "item": item}


@router.put("/update/{item_id}")
async def update_item(item_id: str, item: dict = Body(...)) -> dict:
    # Simulate item update
    await asyncio.sleep(random.uniform(0.1, 0.3))
    return {"item_id": item_id, "updated_item": item}


@router.delete("/delete/{item_id}")
async def delete_item(item_id: str) -> dict:
    # Simulate item deletion
    await asyncio.sleep(random.uniform(0.1, 0.3))
    return {"item_id": item_id, "status": "deleted"}
