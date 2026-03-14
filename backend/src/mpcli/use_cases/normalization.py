import io

import soundfile as sf

from src.mpcli.entities.result import NormalizeResult
from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.audio_transform import normalize_loudness


def execute_normalization(
    config: AudioSource, lufs: float = -14.0
) -> NormalizeResult | None:

    # convert the audio bytes to a numpy array of samples
    data, sample_rate = sf.read(io.BytesIO(config.audio_bytes), dtype="float32")

    samples_array = normalize_loudness(data, sample_rate, lufs)

    # convert the normalized samples back to bytes
    with io.BytesIO() as output:
        sf.write(output, samples_array, sample_rate, format=config.audio_format)
        normalized_audio_bytes = output.getvalue()

    return NormalizeResult(
        audio_source=config,
        converted_audio=AudioSource(
            audio_bytes=normalized_audio_bytes,
            audio_format=config.audio_format,
            sample_rate=config.sample_rate,
            name=f"{config.name}_normalized"
        ),
        lufs=lufs,
    )
