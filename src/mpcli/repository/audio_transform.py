import librosa
import numpy as np
import pyloudnorm as pyln
from audiomentations import TimeStretch
from loguru import logger

from src.mpcli.repository.exceptions import AudioTransformError


def get_duration(data: np.ndarray, sample_rate: int) -> float:

    if not len(data.shape) == 2:
        raise AudioTransformError(
            f"Expected audio samples to be a 2D array with shape (num_samples, num_channels), but got shape {data.shape}"
        )

    if data.shape[0] > data.shape[1]:
        data = data.T

    duration = librosa.get_duration(y=data, sr=sample_rate)
    return duration


def get_loudness(data: np.ndarray, sample_rate: int) -> float:

    if not len(data.shape) == 2:
        raise AudioTransformError(
            f"Expected audio samples to be a 2D array with shape (num_samples, num_channels), but got shape {data.shape}"
        )

    meter = pyln.Meter(sample_rate)  # create BS.1770 meter
    loudness = meter.integrated_loudness(data)

    return loudness


def normalize_loudness(
    samples: np.ndarray,
    sample_rate: int,
    lufs: float,
) -> np.ndarray:
    """Normalize the loudness of the audio samples to the specified LUFS level."""

    if not len(samples.shape) == 2:
        raise AudioTransformError(
            f"Expected audio samples to be a 2D array with shape (num_samples, num_channels), but got shape {samples.shape}"
        )

    # measure the loudness first
    loudness = get_loudness(samples, sample_rate)

    loudness_normalized_audio = pyln.normalize.loudness(samples, loudness, lufs)

    logger.debug(f"Normalized from {loudness} LUFS to {lufs} LUFS, sr: {sample_rate}")

    return loudness_normalized_audio


def time_stretch(
    samples: np.ndarray,
    sample_rate: int,
    min_rate: float,
    max_rate: float,
    leave_length_unchanged: bool = False,
) -> np.ndarray:
    """Time stretch the audio samples by a random factor between min_rate and max_rate.

    Arguments:
        samples: 2D numpy array of shape (num_samples, num_channels)
        sample_rate: sample rate of the audio
        min_rate: minimum time stretch factor (e.g. 0.8 for 20% slower)
        max_rate: maximum time stretch factor (e.g. 1.2 for 20% faster)
        leave_length_unchanged: if True, the output audio will be time-stretched but then resampled back to the original length, so that the duration remains unchanged.

    Returns:
        time-stretched audio samples as a 2D numpy array of shape (num_samples, num_channels)
    """

    try:

        if not len(samples.shape) == 2:
            raise AudioTransformError(
                f"Expected audio samples to be a 2D array with shape (num_samples, num_channels), but got shape {samples.shape}"
            )

        augmenter = TimeStretch(
            min_rate=min_rate,
            max_rate=max_rate,
            method="signalsmith_stretch",
            p=1,  # probability of applying the transformation
            leave_length_unchanged=leave_length_unchanged,  # keep the output length the same as input
        )

        # eventually transpose the shape to have channels first, as expected by audiomentations
        if samples.shape[0] > samples.shape[1]:
            samples = samples.T
            logger.debug(
                f"Transposed audio samples to shape {samples.shape} for time stretching"
            )

        new_samples = augmenter(samples=samples, sample_rate=sample_rate)

        old_duration = get_duration(samples, sample_rate)
        new_duration = get_duration(new_samples, sample_rate)

        logger.info(
            f"Applied time stretching with rates {min_rate} / {max_rate}, old duration: {old_duration:.2f}s, new duration: {new_duration:.2f}s"
        )

        return new_samples
    except Exception as e:
        logger.error(f"Error during time stretching: {e}")
        raise AudioTransformError(f"Error during time stretching: {e}")
