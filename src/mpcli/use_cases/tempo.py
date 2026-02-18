from typing import Generator

import audioread
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features

from mpcli.entities.config import DetectTempoConfig
from mpcli.entities.result import TempoResult
from mpcli.repository.files import iter_sources


def execute_tempo_estimation(
    config: DetectTempoConfig,
) -> Generator[TempoResult | None, None, None]:
    """estimate the tempo of an audio file, and print the result in a human-readable format

    source: the path to the audio file, must be a valid audio file (wav|mp3|flac|ogg|m4a)
    model_name: the name of the model to use for tempo estimation, default is "cnn"
    """

    if not config.source.exists():
        raise ValueError(f"Source file {config.source} does not exist")

    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    for source in iter_sources(config.source):

        try:

            features = read_features(source, zero_pad=True)

            # estimate the global tempo
            tempo = classifier.estimate_tempo(features, interpolate=True)

            yield TempoResult(
                source_path=str(source),
                tempo=tempo,
            )

        except audioread.exceptions.NoBackendError as e:
            raise ValueError(f"Error processing {source}: {e}")
            raise ValueError(f"Error processing {source}: {e}")
