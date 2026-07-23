// Time stretching use case
// Equivalent to timestretch.py

from ..entities.source import AudioSource
from ..entities.result import TimeStretchResult
from ..repository.audio_transform import time_stretch
from ..repository.tempo import estimate_tempo
from ..entities.exceptions import AudioTransformError

fn execute_timestretch(
    source: AudioSource,
    target_tempo: Optional[Float64] = None,
    min_rate: Float64 = 1.0,
    max_rate: Float64 = 1.0,
) -> Optional[TimeStretchResult]:
    """
    Execute time stretching on an audio source.
    
    Args:
        source: The audio source to process.
        target_tempo: The desired tempo in BPM (optional).
        min_rate: Minimum time stretch factor (default: 1.0).
        max_rate: Maximum time stretch factor (default: 1.0).
    
    Returns:
        Optional[TimeStretchResult]: The result of the time stretching, or None if it fails.
    
    Raises:
        AudioTransformError: If the time stretching fails.
    """
    try:
        // Estimate the original tempo
        let estimate = estimate_tempo(source)
        let original_tempo = estimate.tempo
        
        // Special case: no time stretching needed
        if min_rate == 1.0 and max_rate == 1.0:
            print(
                f"The target tempo is the same as the original tempo ({original_tempo} BPM), " +
                f"skipping time stretching for source '{source.name}'"
            )
            return TimeStretchResult(
                audio_source=source,
                converted_audio=source,
                original_tempo=original_tempo,
                target_tempo=original_tempo,
            )
        
        // Compute the time stretch factor
        let computed_target_tempo: Float64
        let computed_min_rate: Float64
        let computed_max_rate: Float64
        
        if min_rate != 1.0 or max_rate != 1.0:
            // Use provided min_rate and max_rate
            computed_target_tempo = (original_tempo * min_rate + original_tempo * max_rate) / 2.0
            computed_min_rate = min_rate
            computed_max_rate = max_rate
        elif target_tempo is not None:
            // Compute min_rate and max_rate from target_tempo
            computed_target_tempo = target_tempo
            computed_min_rate = target_tempo / original_tempo
            computed_max_rate = target_tempo / original_tempo
        else:
            raise AudioTransformError(
                f"Error on source '{source.name}': " +
                f"Either target_tempo or min_rate and max_rate must be provided. " +
                f"Config provided: target_tempo={target_tempo}, min_rate={min_rate}, max_rate={max_rate}"
            )
        
        // Check if no stretching is needed
        if computed_min_rate == 1.0 and computed_max_rate == 1.0:
            print(
                f"The target tempo is the same as the original tempo ({original_tempo} BPM), " +
                f"skipping time stretching for source '{source.name}'"
            )
            return None
        
        // Apply time stretching
        let data = source.to_array()
        let augmented_samples = time_stretch(
            data,
            source.sample_rate,
            computed_min_rate,
            computed_max_rate,
        )
        
        // Convert the time-stretched samples to AudioSource
        let converted_audio = AudioSource.from_array(
            data=augmented_samples,
            audio_format=source.audio_format,
            sample_rate=source.sample_rate,
        )
        
        return TimeStretchResult(
            audio_source=source,
            converted_audio=converted_audio,
            original_tempo=original_tempo,
            target_tempo=computed_target_tempo,
        )
    except e:
        print(f"Error during time stretching: {e}")
        return None
