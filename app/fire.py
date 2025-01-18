from fastapi import APIRouter

fire_router = APIRouter()

@fire_router.post("/api/fire")
async def fire():
    return {"message": "fire"}