import tempfile

from mpcli.entities.source import AudioSource
from src.mpcli.entities.result import NormalizeResult
from src.mpcli.repository.audio_file import load_audio_file
from src.mpcli.repository.audio_transform import normalize_loudness


def execute_normalization(
    config: AudioSource, lufs: float = -14.0
) -> NormalizeResult | None:

    samples = normalize_loudness(config.audio_bytes, config.sample_rate, lufs)

    return NormalizeResult(
        audio_source=config,
        converted_audio=AudioSource(
            audio_bytes=samples,
            audio_format=config.audio_format,
            sample_rate=config.sample_rate,
        ),
        lufs=lufs,
    )
