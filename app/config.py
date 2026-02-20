from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: str = ".env") -> dict[str, str]:
    env_path = Path(path)
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key] = value

    return values


def get_env_value(name: str, default: str = "") -> str:
    env_value = os.getenv(name)
    if env_value:
        return env_value

    file_values = load_env_file()
    return file_values.get(name, default)


def load_tracked_artists() -> list[str]:
    artists_path = Path(__file__).with_name("tracked_artists.txt")
    return [line for line in artists_path.read_text(encoding="utf-8").splitlines() if line]
