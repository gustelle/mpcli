from io import BytesIO
from typing import Literal

import numpy as np
import soundfile as sf
from audiomentations import Mp3Compression
from loguru import logger

from mpcli.repository.audio_file import load_audio_file
from mpcli.repository.exceptions import AudioTransformError
from src.mpcli.entities.source import AudioSource


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
            data, sr = load_audio_file(audio_source)

            if not len(data.shape) == 2:
                raise AudioTransformError(
                    f"Expected audio samples to be a 2D array with shape (num_samples, num_channels), but got shape {samples.shape}"
                )

            if data.shape[0] > data.shape[1]:
                data = data.T

            augmented_sound = transform(data, sample_rate=sr)

            augmented_sound = augmented_sound.astype(np.float32).T

            io = BytesIO()
            sf.write(io, augmented_sound, sr, format="MP3")

            return AudioSource(
                audio_bytes=io.getvalue(),
                audio_format="mp3",
                sample_rate=sr,
            )

        case "wav":

            if audio_source.audio_format == "wav":
                return audio_source

            # convert the bytes back to a numpy array
            audio_array, sr = load_audio_file(audio_source)

            io = BytesIO()
            sf.write(io, audio_array, sr, format="WAV")

            return AudioSource(
                audio_bytes=io.getvalue(),
                audio_format="wav",
                sample_rate=sr,
            )

        case _:
            raise ValueError(f"Unsupported audio format '{target_format}'")
