import io
from typing import Literal, Optional, Self

from pydantic import BaseModel, Field


class AudioSourceError(ValueError):
    pass


class AudioSource(BaseModel):
    """Base class for tempo estimation configuration"""

    audio_format: Literal["wav", "mp3"] = Field(
        ..., description="Audio format (e.g., 'wav', 'mp3')"
    )
    audio_bytes: bytes = Field(..., description="Audio data in bytes")
    name: Optional[str] = Field(
        default="unknown", description="Name of the audio source"
    )
    sample_rate: Optional[int] = Field(
        default=44100, description="Sample rate of the audio file in Hz"
    )
