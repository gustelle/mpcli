from io import BytesIO
from typing import Literal

import numpy as np
import soundfile as sf
from audiomentations import Mp3Compression

from src.mpcli.entities.source import AudioSource, ensure_audio_shape
from src.mpcli.repository.exceptions import AudioTransformError


def convert(
    audio_source: AudioSource, target_format: Literal["wav", "mp3"]
) -> AudioSource:

    match target_format:
        case "mp3":

            if audio_source.audio_format == "mp3":
                return audio_source

            transform = Mp3Compression(
                min_bitrate=16,
                max_bitrate=96,
                backend="fast-mp3-augment",
                preserve_delay=False,
                p=1.0,
            )

            # convert the bytes back to a numpy array
            data = audio_source.to_array()

            # audiomentations expects the audio samples to be in shape (channels, frames)
            data = data.astype(np.float32).T

            sr = audio_source.sample_rate

            augmented_sound = transform(data, sample_rate=sr)

            return AudioSource.from_array(
                data=augmented_sound, audio_format="mp3", sample_rate=sr
            )

        case "wav":

            raise NotImplementedError("WAV conversion is not implemented yet")

        case _:
            raise ValueError(f"Unsupported audio format '{target_format}'")
