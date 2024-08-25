from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserSpotifyData
from app.api.deps import get_current_user
from typing import Literal
from app.api.endpoints.auth import refresh_token
from app.services.recommend import recommender
import numpy as np
from typing import List
import requests

router = APIRouter()

TIME_RANGES = {
    "short_term": "last 4 weeks",
    "medium_term": "last 6 months",
    "long_term": "last 1 year"
}

async def make_spotify_request(url: str, params: dict, spotify_data: UserSpotifyData, db: Session):
    headers = {"Authorization": f"Bearer {spotify_data.access_token}"}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 401:
        new_token = refresh_token(spotify_data, db)
        headers = {"Authorization": f"Bearer {new_token}"}
        response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from Spotify")
    
    return response.json()

@router.get("/top/{item_type}")
async def get_top_items(
    item_type: Literal["artists", "tracks"],
    time_range: Literal["short_term", "medium_term", "long_term"] = "medium_term",
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == current_user.id).first()
    if not spotify_data:
        raise HTTPException(status_code=400, detail="No Spotify data found for user")
    
    url = f"https://api.spotify.com/v1/me/top/{item_type}"
    params = {"time_range": time_range, "limit": limit, "offset": offset}
    
    data = await make_spotify_request(url, params, spotify_data, db)
    
    return {"time_range": TIME_RANGES[time_range], "limit": limit, "offset": offset, "total": data["total"], "items": data["items"]}

@router.get("/me")
async def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == current_user.id).first()
    return await make_spotify_request("https://api.spotify.com/v1/me", {}, spotify_data, db)

@router.get("/playlists")
async def get_user_playlists(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == current_user.id).first()
    return await make_spotify_request("https://api.spotify.com/v1/me/playlists", {}, spotify_data, db)

@router.get("/recently-played")
async def get_recently_played(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == current_user.id).first()
    return await make_spotify_request("https://api.spotify.com/v1/me/player/recently-played", {}, spotify_data, db)

@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50)
):
    try:
        spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == current_user.id).first()
        if not spotify_data:
            raise HTTPException(status_code=400, detail="No Spotify data found for user")

        top_tracks = await get_top_items("tracks", "medium_term", 50, 0, current_user, db)
        top_track_ids = [track['id'] for track in top_tracks['items']]
        
        audio_features = await get_audio_features(top_track_ids, spotify_data, db)
        
        tracks_with_features = []
        for track, features in zip(top_tracks['items'], audio_features):
            if features is not None:
                track['audio_features'] = features
                tracks_with_features.append(track)
        
        user_ratings = np.linspace(1, 0, num=len(tracks_with_features))
        recommender.fit(tracks_with_features, user_ratings)
        
        seed_tracks = top_track_ids[:5]
        url = "https://api.spotify.com/v1/recommendations"
        params = {"seed_tracks": ",".join(seed_tracks), "limit": 100}
        spotify_recommendations = await make_spotify_request(url, params, spotify_data, db)
        
        recommended_track_ids = [track['id'] for track in spotify_recommendations['tracks']]
        recommended_audio_features = await get_audio_features(recommended_track_ids, spotify_data, db)
        
        recommended_tracks_with_features = []
        for track, features in zip(spotify_recommendations['tracks'], recommended_audio_features):
            if features is not None: 
                track['audio_features'] = features
                recommended_tracks_with_features.append(track)
        
        predictions = recommender.predict(recommended_tracks_with_features)
        
        sorted_recommendations = [x for _, x in sorted(zip(predictions, recommended_tracks_with_features), key=lambda pair: pair[0], reverse=True)]
        
        return {"recommendations": sorted_recommendations[:limit]}
    
    except Exception as e:
        print(f"An error occurred: {str(e)}") 
        raise HTTPException(status_code=500, detail=f"An error occurred while generating recommendations: {str(e)}")

async def get_top_items(item_type: str, time_range: str, limit: int, offset: int, user: User, db: Session):
    spotify_data = db.query(UserSpotifyData).filter(UserSpotifyData.user_id == user.id).first()
    if not spotify_data:
        raise HTTPException(status_code=400, detail="No Spotify data found for user")
    
    url = f"https://api.spotify.com/v1/me/top/{item_type}"
    params = {
        "time_range": time_range,
        "limit": limit,
        "offset": offset
    }
    
    return await make_spotify_request(url, params, spotify_data, db)

async def get_audio_features(track_ids: List[str], spotify_data: UserSpotifyData, db: Session):
    url = "https://api.spotify.com/v1/audio-features"
    all_features = []
    
    for i in range(0, len(track_ids), 100):
        chunk = track_ids[i:i+100]
        params = {"ids": ",".join(chunk)}
        response = await make_spotify_request(url, params, spotify_data, db)
        all_features.extend(response['audio_features'])
    
    return all_features