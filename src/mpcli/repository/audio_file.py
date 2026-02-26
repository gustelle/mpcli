import re
from pathlib import Path
from typing import Generator, Literal

import numpy as np
from audiomentations.core.audio_loading_utils import load_sound_file
from pydub import AudioSegment
from scipy.io import wavfile

from src.mpcli.entities.result import ConvertResult


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
) -> ConvertResult:
    """dump the audio file as a numpy array, for debugging purposes"""

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    wav_output_path = output_dir / f"{filename}.wav"

    if wav_output_path.exists():
        wav_output_path.unlink()

    # always export as wav, even if the output format is mp3,
    wavfile.write(wav_output_path, rate=sample_rate, data=samples)

    match format:
        case "mp3":

            audio = AudioSegment.from_file(wav_output_path)

            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / f"{filename}.{format}"

            if output_path.exists():
                output_path.unlink()

            audio.export(output_path, format=format)

            wav_output_path.unlink()

    return ConvertResult(
        source_path=str(wav_output_path),
        target_path=str(output_path),
    )


def load_audio_file(source: str | Path) -> tuple[np.ndarray, int]:
    """Load an audio file and return the samples and sample rate.

    Args:
        source (str | Path): Path to the audio file.
    Returns:
        tuple[np.ndarray, int]: A tuple containing the audio samples as a numpy array and the sample rate as an integer.
    """
    samples, sample_rate = load_sound_file(source, sample_rate=None, mono=False)

    if len(samples.shape) == 2 and samples.shape[0] > samples.shape[1]:
        samples = samples.transpose()

    return samples, sample_rate
