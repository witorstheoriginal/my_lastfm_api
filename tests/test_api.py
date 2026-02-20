from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_lastfm_top_artists_success() -> None:
    mocked_artists = [
        {"name": "Artist 2", "playcount": 300},
        {"name": "Other Artist", "playcount": 200},
        {"name": "Artist 1", "playcount": 120},
    ]

    with (
        patch.dict("os.environ", {"LASTFM_USERNAME": "daniele", "LASTFM_API_KEY": "test-key"}),
        patch("app.api.load_tracked_artists", return_value=["Artist 1", "Artist 2", "Artist 3"]),
        patch("app.api.get_top_artists", return_value=mocked_artists),
    ):
        r = client.get("/lastfm/top-artists")

    assert r.status_code == 200
    assert r.json() == {
        "user": "daniele",
        "missing_to_next": {"Artist 1": 80, "Artist 2": 0, "Artist 3": 0},
    }
    assert list(r.json()["missing_to_next"].items()) == [
        ("Artist 1", 80),
        ("Artist 2", 0),
        ("Artist 3", 0),
    ]


def test_lastfm_top_artists_reads_from_env_file() -> None:
    mocked_artists = [{"name": "Artist 1", "playcount": 120}]

    with (
        patch.dict("os.environ", {}, clear=True),
        patch(
            "app.config.load_env_file",
            return_value={"LASTFM_USERNAME": "daniele", "LASTFM_API_KEY": "file-key"},
        ),
        patch("app.api.load_tracked_artists", return_value=["Artist 1"]),
        patch("app.api.get_top_artists", return_value=mocked_artists) as mocked_get_top_artists,
    ):
        r = client.get("/lastfm/top-artists")

    mocked_get_top_artists.assert_called_once_with(
        api_key="file-key",
        username="daniele",
        limit=1000,
    )
    assert r.status_code == 200
    assert r.json()["user"] == "daniele"
    assert r.json()["missing_to_next"] == {"Artist 1": 0}


def test_lastfm_top_artists_missing_config() -> None:
    with (
        patch.dict("os.environ", {}, clear=True),
        patch("app.config.load_env_file", return_value={}),
        patch("app.api.load_tracked_artists", return_value=["Artist 1"]),
    ):
        r = client.get("/lastfm/top-artists")

    assert r.status_code == 500
    assert r.json()["detail"] == "Missing LASTFM_API_KEY"
