from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.db.database import get_db
from app.models.user import User, UserSpotifyData
from app.core.config import settings
from app.api.deps import get_current_user
from requests_oauthlib import OAuth2Session
import requests
import os

router = APIRouter()

# only in dev to fix oauth complaining
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = 'http://127.0.0.1:8000/auth/callback'
authorization_base_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"

scope = [
    "user-read-email",
    "playlist-read-collaborative",
    "user-top-read"
]

@router.get("/login")
async def login():
    spotify = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, _ = spotify.authorization_url(authorization_base_url)
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    spotify = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    
    token = spotify.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=str(request.url)
    )
    
    r = spotify.get('https://api.spotify.com/v1/me')
    user_info = r.json()

    user = db.query(User).filter(User.email == user_info['email']).first()
    if not user:
        user = User(email=user_info['email'])
        db.add(user)
        db.commit()
        db.refresh(user)

    spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == user.id).first()
    if not spotify_data:
        spotify_data = UserSpotifyData(
            user_id=user.id,
            spotify_id=user_info['id'],
            access_token=token['access_token'],
            refresh_token=token.get('refresh_token')
        )
        db.add(spotify_data)
    else:
        spotify_data.access_token = token['access_token']
        if 'refresh_token' in token:
            spotify_data.refresh_token = token['refresh_token']
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
def refresh_token(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == user.id).first()
    if not spotify_data:
        raise HTTPException(status_code=400, detail="No Spotify data found for user")

    refresh_data = {
        "grant_type": "refresh_token",
        "refresh_token": spotify_data.refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=refresh_data)
    new_tokens = response.json()

    spotify_data.access_token = new_tokens['access_token']
    if 'refresh_token' in new_tokens:
        spotify_data.refresh_token = new_tokens['refresh_token']
    db.commit()

    return {"message": "Token refreshed successfully"}