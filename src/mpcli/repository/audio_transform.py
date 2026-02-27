import numpy as np
from audiomentations import TimeStretch
from audiomentations.augmentations.loudness_normalization import LoudnessNormalization
from audiomentations.core.audio_loading_utils import load_sound_file


def normalize_loudness(
    samples: np.ndarray,
    sample_rate: int,
    lufs: float,
) -> np.ndarray:
    """Normalize the loudness of the audio samples to the specified LUFS level."""
    augmenter = LoudnessNormalization(
        min_lufs=lufs,
        max_lufs=lufs,
        p=1,  # probability of applying the transformation
    )

    augmented_samples = augmenter(samples=samples, sample_rate=sample_rate)

    if len(augmented_samples.shape) == 2:
        augmented_samples = augmented_samples.transpose()

    return augmented_samples


def time_stretch(
    samples: np.ndarray,
    sample_rate: int,
    min_rate: float,
    max_rate: float,
) -> np.ndarray:
    """Time stretch the audio samples by a random factor between min_rate and max_rate."""
    augmenter = TimeStretch(
        min_rate=min_rate,
        max_rate=max_rate,
        method="signalsmith_stretch",
        p=1,  # probability of applying the transformation
        leave_length_unchanged=False,  # keep the output length the same as input
    )

    augmented_samples = augmenter(samples=samples, sample_rate=sample_rate)

    if len(augmented_samples.shape) == 2:
        augmented_samples = augmented_samples.transpose()

    return augmented_samples
