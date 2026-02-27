from typing import Generator

from src.mpcli.entities.config import NormalizeConfig
from src.mpcli.entities.result import NormalizeResult
from src.mpcli.repository.audio_file import (
    iter_sources,
    load_audio_file,
    save_audio_file,
)
from src.mpcli.repository.audio_transform import normalize_loudness


def execute_normalization(
    config: NormalizeConfig,
) -> Generator[NormalizeResult | None, None, None]:

    for source in iter_sources(config.source):

        samples, sample_rate = load_audio_file(source)

        samples = normalize_loudness(samples, sample_rate, config.lufs)

        audio = save_audio_file(
            output_dir=config.output,
            filename=source.stem,
            samples=samples,
            sample_rate=sample_rate,
            format=config.format,
        )

        yield NormalizeResult(
            source_path=str(source),
            target_path=str(audio.path),
            lufs=config.lufs,
        )
