import audioread
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features

from mpcli.entities.config import DetectTempoConfig
from mpcli.entities.result import TempoResult


def execute_tempo_estimation(config: DetectTempoConfig) -> TempoResult | None:
    """estimate the tempo of an audio file, and print the result in a human-readable format

    source: the path to the audio file, must be a valid audio file (wav|mp3|flac|ogg|m4a)
    model_name: the name of the model to use for tempo estimation, default is "cnn"
    """

    if not config.source.exists():
        raise ValueError(f"Source file {config.source} does not exist")

    if not config.source.is_file():
        raise ValueError(f"Source path {config.source} is not a file")

    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    try:

        features = read_features(config.source, zero_pad=True)

        # estimate the global tempo
        tempo = classifier.estimate_tempo(features, interpolate=True)

        return TempoResult(
            source_path=str(config.source),
            tempo=tempo,
        )

    except audioread.exceptions.NoBackendError as e:
        raise ValueError(f"Error processing {config.source}: {e}")
