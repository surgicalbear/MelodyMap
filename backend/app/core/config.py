from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MelodyMap API"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()