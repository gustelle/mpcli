from typing import Generator

from audiomentations.augmentations.loudness_normalization import LoudnessNormalization

from mpcli.entities.config import NormalizeConfig
from mpcli.entities.result import NormalizeResult
from mpcli.repository.audio_file import iter_sources, load_audio_file, save_audio_file


def execute_normalization(
    config: NormalizeConfig,
) -> Generator[NormalizeResult | None, None, None]:

    for source in iter_sources(config.source):

        augmenter = LoudnessNormalization(
            min_lufs=config.lufs,
            max_lufs=config.lufs,
            p=1,  # probability of applying the transformation
        )

        samples, sample_rate = load_audio_file(source)

        augmented_samples = augmenter(samples=samples, sample_rate=sample_rate)

        if len(augmented_samples.shape) == 2:
            augmented_samples = augmented_samples.transpose()

        audio = save_audio_file(
            output_dir=config.output,
            filename=source.stem,
            samples=augmented_samples,
            sample_rate=sample_rate,
            format=config.format,
        )

        yield NormalizeResult(
            source_path=str(source),
            target_path=str(audio.path),
            lufs=config.lufs,
        )
