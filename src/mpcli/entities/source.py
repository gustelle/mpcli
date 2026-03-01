from pathlib import Path
from typing import Literal, Optional, Self

from pydantic import BaseModel, Field, model_validator


class AudioSourceError(ValueError):
    pass


class AudioSource(BaseModel):
    """Base class for tempo estimation configuration"""

    audio_format: Optional[Literal["wav", "mp3"]] = Field(
        default=None, description="Audio format (e.g., 'wav', 'mp3')"
    )
    audio_bytes: Optional[bytes] = Field(
        default=None, description="Audio data in bytes"
    )
    name: Optional[str] = None
    sample_rate: Optional[int] = Field(
        default=44100, description="Sample rate of the audio file in Hz"
    )


class FileAudioSource(AudioSource):
    """case where the source is a local file path"""

    source: Path

    @model_validator(mode="after")
    def set_fields(self) -> Self:

        if not self.source.is_file():
            raise AudioSourceError(f"Source path {self.source} is not a file")

        self.audio_format = self.source.suffix[1:].lower()

        try:
            self.audio_bytes = self.source.read_bytes()
            self.name = self.source.name
        except Exception as e:
            raise AudioSourceError(f"Failed to read audio file: {e}")

        return self
