from typing import Generator

from src.mpcli.entities.config import DetectTempoConfig
from src.mpcli.entities.result import TempoResult
from src.mpcli.repository.audio_file import iter_sources
from src.mpcli.repository.tempo import estimate_tempo


def execute_tempo_estimation(
    config: DetectTempoConfig,
) -> Generator[TempoResult | None, None, None]:
    """estimate the tempo of an audio file, and print the result in a human-readable format

    source: the path to the audio file, must be a valid audio file (wav|mp3|flac|ogg|m4a)
    model_name: the name of the model to use for tempo estimation, default is "cnn"
    """

    if not config.source.exists():
        raise ValueError(f"Source file {config.source} does not exist")

    for source in iter_sources(config.source):

        yield estimate_tempo(source)
