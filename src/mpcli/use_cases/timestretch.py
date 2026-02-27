import dataclasses
from typing import Generator

import jinja2

from src.mpcli.entities.config import DetectTempoConfig, TimeStretchConfig
from src.mpcli.entities.result import TempoResult, TimeStretchResult
from src.mpcli.repository.audio_file import (
    iter_sources,
    load_audio_file,
    save_audio_file,
)
from src.mpcli.repository.audio_transform import time_stretch
from src.mpcli.use_cases.tempo import execute_tempo_estimation


def _compute_filename(config: TimeStretchConfig, estimate: TempoResult) -> str:
    """
    TODO:
    - make this a repository function that can be re-used across use cases
    """

    environment = jinja2.Environment()

    tempo_min = round(estimate.tempo * config.min_rate, 2)
    tempo_max = round(estimate.tempo * config.max_rate, 2)

    if config.filename is not None:
        filename_template = config.filename
    elif tempo_min == tempo_max:
        filename_template = "{{ source.stem }}_{{ tempo_min }}_BPM"
    else:
        filename_template = "{{ source.stem }}_{{ tempo_min }}-{{ tempo_max }}_BPM"

    template = environment.from_string(filename_template)

    return template.render(
        **dataclasses.asdict(config), tempo_min=tempo_min, tempo_max=tempo_max
    )


def execute_timestretch(
    config: TimeStretchConfig,
) -> Generator[TimeStretchResult | None, None, None]:
    """Execute time stretching on audio files based on the provided configuration.

    produces an audio file with the same tempo as the original, but with a different duration,
    by applying a time stretch factor to the audio signal. The time stretch factor is computed based on the target tempo and the original tempo of the audio file, or based on the provided min_rate and max_rate.

    NB:
    - if a ``target_tempo`` is provided, the time stretch factor is computed as the ratio of the target tempo to the original tempo.
    - if ``min_rate`` and ``max_rate`` are provided, the time stretch factor is a range of values between the min_rate and max_rate,

    Audio file name contains the tempi applied to the file,
    e.g. "my_file_50-50.5_BPM.mp3" for a file that was time stretched between 50 BPM and 50.5 BPM.

    TODO:
    - yield a BytesIO object instead of writing the file to disk,

    Args:
        config (TimeStretchConfig): Configuration for the time stretching operation.

    Yields:
        Generator[TimeStretchResult | None, None, None]: Results of the time stretching operation.
    """

    for source in iter_sources(config.source):

        # estimate the global tempo
        tempo_config = DetectTempoConfig(source=source)
        estimate = next(execute_tempo_estimation(tempo_config))
        target_tempo = config.target_tempo

        # compute the time stretch factor
        if config.min_rate != 1 or config.max_rate != 1:
            min_rate = config.min_rate
            max_rate = config.max_rate
            target_tempo = round(
                (estimate.tempo * min_rate + estimate.tempo * max_rate) / 2, 2
            )
        else:
            min_rate = target_tempo / estimate.tempo
            max_rate = target_tempo / estimate.tempo

        if min_rate == 1 and max_rate == 1:
            print(
                f"Skipping {source} since the target tempo is the same as the original tempo ({estimate.tempo} BPM)"
            )
            continue

        filename = _compute_filename(config, estimate)

        samples, sample_rate = load_audio_file(source)

        augmented_samples = time_stretch(samples, sample_rate, min_rate, max_rate)

        result = save_audio_file(
            output_dir=config.output,
            filename=filename,
            samples=augmented_samples,
            sample_rate=sample_rate,
            format=config.format,
        )

        yield TimeStretchResult(
            source_path=str(source),
            original_tempo=estimate.tempo,
            target_tempo=target_tempo,
            target_path=str(result.path),
        )
