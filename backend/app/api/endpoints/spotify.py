from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_spotify():
    return {"message": "Spotify endpoint not implemented yet"}