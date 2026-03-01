import numpy as np

from src.mpcli.entities.result import TimeStretchResult
from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.audio_transform import time_stretch
from src.mpcli.repository.tempo import estimate_tempo


def execute_timestretch(
    source: AudioSource,
    target_tempo: float | None = None,
    min_rate: float = 1.0,
    max_rate: float = 1.0,
) -> TimeStretchResult | None:
    """Execute time stretching on audio files based on the provided configuration.

    produces an audio file with the same tempo as the original, but with a different duration,
    by applying a time stretch factor to the audio signal. The time stretch factor is computed based on the target tempo and the original tempo of the audio file, or based on the provided min_rate and max_rate.

    NB:
    - if a ``target_tempo`` is provided, the time stretch factor is computed as the ratio of the target tempo to the original tempo.
    - if ``min_rate`` and ``max_rate`` are provided, the time stretch factor is a range of values between the min_rate and max_rate,

    Audio file name contains the tempi applied to the file,
    e.g. "my_file_50-50.5_BPM.mp3" for a file that was time stretched between 50 BPM and 50.5 BPM.

    Args:
        source (AudioSource): Source audio file for the time stretching operation.
        target_tempo (float, optional): Desired tempo for the output audio file. If not provided, the original tempo will be used. Defaults to None.
        min_rate (float, optional): Minimum time stretch factor. Defaults to 1.0 (no time stretch).
        max_rate (float, optional): Maximum time stretch factor. Defaults to 1.0

    Returns:
        TimeStretchResult | None: Result of the time stretching operation.
    """

    # estimate the global tempo
    estimate = estimate_tempo(source)

    # compute the time stretch factor
    if min_rate != 1 or max_rate != 1:
        target_tempo = round(
            (estimate.tempo * min_rate + estimate.tempo * max_rate) / 2, 2
        )
    elif target_tempo is not None:
        min_rate = target_tempo / estimate.tempo
        max_rate = target_tempo / estimate.tempo
    else:
        raise ValueError(
            "Either target_tempo or min_rate and max_rate must be provided"
        )

    if min_rate == 1 and max_rate == 1:
        print(
            f"the target tempo is the same as the original tempo ({estimate.tempo} BPM)"
        )
        return None

    augmented_samples = time_stretch(
        source.audio_bytes, source.sample_rate, min_rate, max_rate
    )

    converted_audio = AudioSource(
        audio_bytes=np.save(augmented_samples, allow_pickle=True),
        audio_format=source.audio_format,
        sample_rate=source.sample_rate,
    )

    return TimeStretchResult(
        audio_source=source,
        converted_audio=converted_audio,
        original_tempo=estimate.tempo,
        target_tempo=target_tempo,
    )
