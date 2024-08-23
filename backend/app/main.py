from fastapi import FastAPI
from app.api.endpoints import auth, users, spotify
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(spotify.router, prefix="/spotify", tags=["spotify"])

@app.get("/")
async def root():
    return {"message": "Welcome to the MelodyMap API"}