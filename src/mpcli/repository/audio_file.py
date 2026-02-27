import re
from pathlib import Path
from typing import Generator, Literal

import numpy as np
import soundfile as sf
from audiomentations import Mp3Compression
from audiomentations.core.audio_loading_utils import load_sound_file

from src.mpcli.entities.result import AudioFileResult
from src.mpcli.repository.exceptions import (
    AudioFileNotFoundError,
    InvalidAudioFileError,
)


def iter_sources(
    source_path: str | Path,
    format: Literal["*", "wav", "mp3", "flac", "ogg", "m4a"] = "*",
) -> Generator[Path, None, None]:

    if not Path(source_path).exists():
        raise ValueError(f"'{source_path}' does not exist")

    if Path(source_path).is_file():
        yield Path(source_path)
    else:
        for source in Path(source_path).glob("*.*"):

            if format == "*":
                format_pattern = r".*\.(wav|mp3|flac|ogg|m4a)$"
            else:
                format_pattern = rf".*\.{format}$"

            if source.is_dir() or source.stem.startswith("."):
                print(f"Skipping directory or hidden file: {source}")
                continue

            if not re.match(format_pattern, source.name, re.IGNORECASE):
                print(f"Skipping file with unsupported format: {source}")
                continue

            yield source


def save_audio_file(
    output_dir: Path,
    filename: str,
    samples: np.ndarray,
    sample_rate: int,
    format: Literal["wav", "mp3"] = "wav",
) -> AudioFileResult:
    """dump the audio file as a numpy array, for debugging purposes"""

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    match format:
        case "mp3":

            transform = Mp3Compression(
                min_bitrate=16,
                max_bitrate=96,
                backend="fast-mp3-augment",
                preserve_delay=False,
                p=1.0,
            )

            augmented_sound = transform(samples, sample_rate=sample_rate)

            if len(augmented_sound.shape) == 2:
                augmented_sound = augmented_sound.transpose()

            output_path = output_dir / f"{filename}.mp3"

            if output_path.exists():
                output_path.unlink()

            sf.write(output_path, augmented_sound, sample_rate, format="MP3")

        case "wav":

            output_path = output_dir / f"{filename}.wav"

            if output_path.exists():
                output_path.unlink()

            sf.write(output_path, samples, sample_rate, format="WAV")

        case _:
            raise ValueError(f"Unsupported audio format '{format}'")

    return AudioFileResult(
        path=str(output_path),
        format=format,
        sample_rate=sample_rate,
    )


def load_audio_file(source: str | Path) -> tuple[np.ndarray, int]:
    """Load an audio file and return the samples and sample rate.

    Args:
        source (str | Path): Path to the audio file.
    Returns:
        tuple[np.ndarray, int]: A tuple containing the audio samples as a numpy array and the sample rate as an integer.
    """
    try:
        samples, sample_rate = load_sound_file(source, sample_rate=None, mono=False)

        if len(samples.shape) == 2 and samples.shape[0] > samples.shape[1]:
            samples = samples.transpose()

        return samples, sample_rate
    except FileNotFoundError:
        raise AudioFileNotFoundError(f"Audio file '{source}' not found")
    except Exception as e:
        raise InvalidAudioFileError(f"Error loading audio file '{source}': {e}")
