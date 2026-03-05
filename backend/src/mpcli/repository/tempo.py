from io import BytesIO

import audioread
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features

from src.mpcli.entities.result import TempoResult
from src.mpcli.entities.source import AudioSource


def estimate_tempo(source: AudioSource) -> TempoResult:
    """
    Estimate the tempo of an audio signal in beats per minute (BPM).

    Args:
        source (AudioSource): The audio source.

    Returns:
        TempoResult: The estimated tempo result.
    """
    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    try:

        features = read_features(BytesIO(source.audio_bytes), zero_pad=True)

        # estimate the global tempo
        tempo = classifier.estimate_tempo(features, interpolate=True)

        return TempoResult(
            audio_source=source,
            tempo=tempo,
        )

    except audioread.exceptions.NoBackendError as e:
        raise ValueError(f"Error processing {source}: {e}")
