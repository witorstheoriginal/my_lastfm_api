from __future__ import annotations

from fastapi import FastAPI, HTTPException, status

from .config import get_env_value, load_tracked_artists
from .lastfm import LastFMConfigError, LastFMError, get_top_artists
from .models import ArtistMissingToNextResponse

app = FastAPI(title="My HTTP API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/lastfm/top-artists", response_model=ArtistMissingToNextResponse)
def get_lastfm_top_artists() -> ArtistMissingToNextResponse:
    username = get_env_value("LASTFM_USERNAME", "")
    api_key = get_env_value("LASTFM_API_KEY", "")
    tracked_artists = load_tracked_artists()

    try:
        artists_raw = get_top_artists(api_key=api_key, username=username, limit=1000)
    except LastFMConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except LastFMError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    ranking = {str(artist["name"]).lower(): idx for idx, artist in enumerate(artists_raw)}
    playcounts = {str(artist["name"]).lower(): int(artist["playcount"]) for artist in artists_raw}
    missing_to_next: dict[str, int] = {}
    counts: dict[str, int] = {}
    for artist in tracked_artists:
        artist_key = artist.lower()
        count = playcounts.get(artist_key, 0)
        counts[artist] = count

        position = ranking.get(artist_key)
        if position is None or position == 0:
            missing_to_next[artist] = 0
        else:
            previous_count = int(artists_raw[position - 1]["playcount"])
            missing_to_next[artist] = previous_count - count

    sorted_artists = sorted(
        tracked_artists,
        key=lambda artist: (-missing_to_next[artist], artist.lower()),
    )
    sorted_missing_to_next = {artist: missing_to_next[artist] for artist in sorted_artists}
    return ArtistMissingToNextResponse(user=username, missing_to_next=sorted_missing_to_next)
