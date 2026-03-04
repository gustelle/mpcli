import io
from typing import Literal, Optional, Self

import numpy as np
import soundfile as sf
from pydantic import BaseModel, Field


class AudioSourceError(ValueError):
    pass


def ensure_audio_shape(data: np.ndarray) -> np.ndarray:
    """
    Ensure that the audio data has the expected shape (num_samples, num_channels).

    Args:
        data (np.ndarray): Audio data as a NumPy array.

    Raises:
        AudioSourceError: If the audio data does not have the expected shape.
    """
    if not len(data.shape) == 2:
        raise AudioSourceError(
            f"Expected audio samples to be a 2D array with shape (num_samples, num_channels), but got shape {data.shape}"
        )
    if data.shape[0] < data.shape[1]:
        data = data.T

    return data


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

    @classmethod
    def from_array(
        self, data: np.ndarray, audio_format: Literal["wav", "mp3"], sample_rate: int
    ) -> Self:
        """Create an AudioSource instance from an audio array.

        Args:
            data (np.ndarray): Audio data as a NumPy array.
                expected shape is (num_samples, num_channels) or (num_channels, num_samples)
            audio_format (Literal["wav", "mp3"]): Format of the audio data.
            sample_rate (int): Sample rate of the audio data in Hz.

        Returns:
            AudioSource: An instance of AudioSource with the provided audio data and metadata.
        """

        try:

            # eventually, transpose the data to have shape (num_samples, num_channels)
            data = ensure_audio_shape(data)

            bytes_io = io.BytesIO()
            sf.write(bytes_io, data, sample_rate, format=audio_format.upper())

            return AudioSource(
                audio_bytes=bytes_io.getvalue(),
                audio_format=audio_format,
                sample_rate=sample_rate,
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise AudioSourceError(f"Failed to create AudioSource: {e}") from e

    def to_array(self) -> np.ndarray:
        """Convert the audio bytes to a NumPy array.
        Returns:
            np.ndarray: Audio data as a NumPy array, returned in shape (frames, channels)
        """
        data, _ = sf.read(io.BytesIO(self.audio_bytes), dtype="float32", always_2d=True)

        data = ensure_audio_shape(data)

        return data
