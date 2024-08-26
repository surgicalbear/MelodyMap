from fastapi import FastAPI
from app.api.endpoints import auth, users, spotify
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title=settings.PROJECT_NAME)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(spotify.router, prefix="/spotify", tags=["spotify"])

@app.get("/")
async def root():
    return {"message": "Welcome to the MelodyMap API"}