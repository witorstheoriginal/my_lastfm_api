from __future__ import annotations

from pydantic import BaseModel, Field


class ArtistMissingToNextResponse(BaseModel):
    user: str
    missing_to_next: dict[str, int] = Field(default_factory=dict)
