from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_users():
    return {"message": "Users endpoint not implemented yet"}