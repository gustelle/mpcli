from src.mpcli.entities.result import TempoResult
from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.tempo import estimate_tempo


def execute_tempo_estimation(
    config: AudioSource,
) -> TempoResult | None:

    return estimate_tempo(config)
