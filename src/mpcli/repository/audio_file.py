import re
from pathlib import Path
from typing import Generator, Literal

import numpy as np
import soundfile as sf
from loguru import logger

from src.mpcli.entities.source import FileAudioSource
from src.mpcli.repository.exceptions import (
    AudioFileNotFoundError,
    InvalidAudioFileError,
)


def iter_sources(
    source_path: str | Path,
    format: Literal["*", "wav", "mp3", "flac", "ogg", "m4a"] = "*",
) -> Generator[FileAudioSource, None, None]:

    if not Path(source_path).exists():
        raise ValueError(f"'{source_path}' does not exist")

    if Path(source_path).is_file():
        yield FileAudioSource(source=Path(source_path))
    else:
        for source in Path(source_path).glob("*.*"):

            if format == "*":
                format_pattern = r".*\.(wav|mp3|flac|ogg|m4a)$"
            else:
                format_pattern = rf".*\.{format}$"

            if source.is_dir() or source.stem.startswith("."):
                logger.info(f"Skipping directory or hidden file: {source}")
                continue

            if not re.match(format_pattern, source.name, re.IGNORECASE):
                logger.info(f"Skipping file with unsupported format: {source}")
                continue

            yield FileAudioSource(source=source)


def save_audio_file(
    output_dir: Path,
    filename: str,
    data: np.ndarray,
    sample_rate: int,
    format: Literal["wav", "mp3"] = "wav",
) -> FileAudioSource:
    """dump the audio file as a numpy array, for debugging purposes"""

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # dump to file
    file_path = output_dir / f"{filename}.{format}"

    try:
        sf.write(file_path, data, sample_rate, format=format.upper())
        return FileAudioSource(source=file_path)
    except Exception as e:
        raise InvalidAudioFileError(f"Error saving audio file '{file_path}': {e}")


def load_audio_file(source: FileAudioSource) -> tuple[np.ndarray, int]:
    """Load an audio file and return the samples and sample rate.

    Args:
        source (FileAudioSource): The audio source.
    Returns:
        tuple[np.ndarray, int]: A tuple containing the audio samples as a numpy array and the sample rate as an integer.
    """
    try:
        data, sample_rate = sf.read(
            source.source, always_2d=True
        )  # always return as 2D array even for mono audio

        logger.info(
            f"Loaded audio file '{source.source}' with shape {data.shape} and sample rate {sample_rate}"
        )

        return data, sample_rate

    except FileNotFoundError:
        raise AudioFileNotFoundError(f"Audio file '{source.source}' not found")
    except Exception as e:
        raise InvalidAudioFileError(f"Error loading audio file '{source.source}': {e}")
