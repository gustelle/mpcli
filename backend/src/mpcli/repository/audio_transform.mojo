// Audio transformation operations
// Equivalent to audio_transform.py

from tensor import Tensor
from math import log10, sqrt
from string import String

from ..entities.source import ensure_audio_shape
from ..entities.exceptions import AudioTransformError

fn get_duration(data: Tensor[Float32], sample_rate: Int) raises -> Float64:
    """
    Calculate the duration of audio data in seconds.
    
    Args:
        data: Audio data as a 2D tensor (frames, channels).
        sample_rate: Sample rate in Hz.
    
    Returns:
        Float64: Duration in seconds.
    
    Raises:
        AudioTransformError: If the data shape is invalid.
    """
    if data.rank() != 2:
        raise AudioTransformError(
            f"Expected audio samples to be a 2D tensor with shape (num_samples, num_channels), but got rank {data.rank()}"
        )
    
    // Duration = num_frames / sample_rate
    let num_frames = data.shape[0]
    return Float64(num_frames) / Float64(sample_rate)

fn get_loudness(data: Tensor[Float32], sample_rate: Int) raises -> Float64:
    """
    Calculate the integrated loudness of audio data in LUFS.
    Uses pyloudnorm via Python import.
    
    Args:
        data: Audio data as a 2D tensor (frames, channels).
        sample_rate: Sample rate in Hz.
    
    Returns:
        Float64: Integrated loudness in LUFS.
    
    Raises:
        AudioTransformError: If loudness calculation fails.
    """
    from python import Python
    
    try:
        // Ensure data has the correct shape
        let shaped_data = ensure_audio_shape(data)
        
        pyln = Python.import_module("pyloudnorm")
        meter = pyln.Meter(sample_rate)
        loudness = meter.integrated_loudness(shaped_data.numpy())
        
        return Float64(loudness)
    except e:
        raise AudioTransformError(f"Error calculating loudness: {e}")

fn normalize_loudness(
    samples: Tensor[Float32],
    sample_rate: Int,
    lufs: Float64,
) raises -> Tensor[Float32]:
    """
    Normalize the loudness of audio samples to the specified LUFS level.
    Uses pyloudnorm via Python import.
    
    Args:
        samples: Audio samples as a 2D tensor (frames, channels).
        sample_rate: Sample rate in Hz.
        lufs: Target LUFS level.
    
    Returns:
        Tensor[Float32]: Loudness-normalized audio samples.
    
    Raises:
        AudioTransformError: If normalization fails.
    """
    from python import Python
    
    try:
        // Ensure samples have the correct shape
        let shaped_samples = ensure_audio_shape(samples)
        
        pyln = Python.import_module("pyloudnorm")
        
        // Measure the current loudness
        let current_loudness = get_loudness(shaped_samples, sample_rate)
        
        // Normalize to the target LUFS
        let normalized_samples_np = pyln.normalize.loudness(
            shaped_samples.numpy(),
            current_loudness,
            lufs,
        )
        
        return Tensor[Float32](normalized_samples_np)
    except e:
        raise AudioTransformError(f"Error normalizing loudness: {e}")

fn time_stretch(
    samples: Tensor[Float32],
    sample_rate: Int,
    min_rate: Float64,
    max_rate: Float64,
    leave_length_unchanged: Bool = False,
) raises -> Tensor[Float32]:
    """
    Time stretch audio samples by a random factor between min_rate and max_rate.
    Uses audiomentations via Python import.
    
    Args:
        samples: Audio samples as a 2D tensor (frames, channels).
        sample_rate: Sample rate in Hz.
        min_rate: Minimum time stretch factor (e.g., 0.8 for 20% slower).
        max_rate: Maximum time stretch factor (e.g., 1.2 for 20% faster).
        leave_length_unchanged: If True, resample back to original length.
    
    Returns:
        Tensor[Float32]: Time-stretched audio samples.
    
    Raises:
        AudioTransformError: If time stretching fails.
    """
    from python import Python
    from numpy import np
    
    try:
        augmenter = Python.import_module("audiomentations").TimeStretch(
            min_rate=min_rate,
            max_rate=max_rate,
            method="signalsmith_stretch",
            p=1.0,
            leave_length_unchanged=leave_length_unchanged,
        )
        
        // audiomentations expects shape (channels, frames)
        let shaped_samples = ensure_audio_shape(samples)
        let samples_np = shaped_samples.numpy().astype(np.float32).T
        
        let new_samples_np = augmenter(samples=samples_np, sample_rate=sample_rate)
        
        // Convert back to Mojo tensor and ensure shape
        let new_samples = Tensor[Float32](new_samples_np)
        return ensure_audio_shape(new_samples)
    except e:
        raise AudioTransformError(f"Error during time stretching: {e}")
