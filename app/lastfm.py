from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class LastFMError(Exception):
    pass


class LastFMConfigError(LastFMError):
    pass


def get_top_artists(*, api_key: str, username: str, limit: int = 10) -> list[dict[str, int | str]]:
    if not api_key:
        raise LastFMConfigError("Missing LASTFM_API_KEY")
    if not username:
        raise LastFMConfigError("Missing LASTFM_USERNAME")

    query = urlencode(
        {
            "method": "user.getTopArtists",
            "user": username,
            "api_key": api_key,
            "format": "json",
            "limit": str(limit),
            "period": "overall",
        }
    )
    url = f"https://ws.audioscrobbler.com/2.0/?{query}"
    request = Request(url, headers={"User-Agent": "my-lastfm-api/1.0"})

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise LastFMError(f"Last.fm request failed with HTTP {exc.code}") from exc
    except json.JSONDecodeError as exc:
        raise LastFMError("Invalid JSON received from Last.fm") from exc
    except Exception as exc:
        raise LastFMError("Failed to fetch data from Last.fm") from exc

    if "error" in payload:
        message = payload.get("message", "Last.fm API error")
        raise LastFMError(str(message))

    artist_items = payload.get("topartists", {}).get("artist", [])
    return [
        {"name": str(artist["name"]), "playcount": int(artist["playcount"])}
        for artist in artist_items[:limit]
    ]
