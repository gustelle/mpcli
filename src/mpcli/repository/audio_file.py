import re
from pathlib import Path
from typing import Generator, Literal

import numpy as np
import soundfile as sf
from loguru import logger

from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.exceptions import (
    AudioFileNotFoundError,
    InvalidAudioFileError,
)


def iter_sources(
    source_path: str | Path,
    format: Literal["*", "wav", "mp3", "flac", "ogg", "m4a"] = "*",
) -> Generator[AudioSource, None, None]:

    if not Path(source_path).exists():
        raise ValueError(f"'{source_path}' does not exist")

    if Path(source_path).is_file():
        ext = Path(source_path).suffix.lower()
        name = Path(source_path).stem
        if ext not in [".wav", ".mp3", ".flac", ".ogg", ".m4a"]:
            raise ValueError(f"Unsupported audio format: '{ext}'")

        yield AudioSource(
            audio_bytes=Path(source_path).read_bytes(), audio_format=ext[1:], name=name
        )
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

            ext = source.suffix.lower()
            name = source.stem

            yield AudioSource(
                audio_bytes=source.read_bytes(), audio_format=ext[1:], name=name
            )


def save_audio_file(
    output_dir: Path,
    filename: str,
    data: np.ndarray,
    sample_rate: int,
    format: Literal["wav", "mp3"] = "wav",
) -> AudioSource:
    """dump the audio file as a numpy array, for debugging purposes"""

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # dump to file
    file_path = output_dir / f"{filename}.{format}"

    try:
        sf.write(file_path, data, sample_rate, format=format.upper())

        return AudioSource(
            audio_bytes=file_path.read_bytes(), audio_format=format, name=filename
        )
    except Exception as e:
        raise InvalidAudioFileError(f"Error saving audio file '{file_path}': {e}")


def load_audio_file(file_path: Path) -> tuple[np.ndarray, int]:
    """Load an audio file and return the samples and sample rate.

    Args:
        file_path (Path): The path to the audio file.
    Returns:
        tuple[np.ndarray, int]: A tuple containing the audio samples as a numpy array and the sample rate as an integer.
    """
    try:
        data, sample_rate = sf.read(
            file_path, always_2d=True
        )  # always return as 2D array even for mono audio

        logger.info(
            f"Loaded audio file '{file_path}' with shape {data.shape} and sample rate {sample_rate}"
        )

        return data, sample_rate

    except FileNotFoundError:
        raise AudioFileNotFoundError(f"Audio file '{file_path}' not found")
    except Exception as e:
        raise InvalidAudioFileError(f"Error loading audio file '{file_path}': {e}")
