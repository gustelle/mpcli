// Tempo estimation use case
// Equivalent to tempo.py

from ..entities.source import AudioSource
from ..entities.result import TempoResult
from ..repository.tempo import estimate_tempo

fn execute_tempo_estimation(
    source: AudioSource,
) -> Optional[TempoResult]:
    """
    Execute tempo estimation on an audio source.
    
    Args:
        source: The audio source to analyze.
    
    Returns:
        Optional[TempoResult]: The result of the tempo estimation, or None if it fails.
    """
    try:
        return estimate_tempo(source)
    except e:
        print(f"Error during tempo estimation: {e}")
        return None
