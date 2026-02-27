from pathlib import Path

import audioread
import numpy as np
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features

from src.mpcli.entities.result import TempoResult


def estimate_tempo(source: Path) -> TempoResult:
    """
    Estimate the tempo of an audio signal in beats per minute (BPM).

    Args:
        source (Path): The path to the audio file.

    Returns:
        TempoResult: The estimated tempo result.
    """
    model_name = "cnn"

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    try:

        features = read_features(source, zero_pad=True)

        # estimate the global tempo
        tempo = classifier.estimate_tempo(features, interpolate=True)

        return TempoResult(
            source_path=str(source),
            tempo=tempo,
        )

    except audioread.exceptions.NoBackendError as e:
        raise ValueError(f"Error processing {source}: {e}")
