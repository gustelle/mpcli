// Audio format conversion
// Equivalent to audio_convert.py

from tensor import Tensor
from string import String

from ..entities.source import AudioSource, AudioFormat
from ..entities.exceptions import AudioTransformError

fn convert(
    audio_source: AudioSource,
    target_format: AudioFormat,
) raises -> AudioSource:
    """
    Convert an audio source to the target format.
    
    Args:
        audio_source: The audio source to convert.
        target_format: The target audio format (wav or mp3).
    
    Returns:
        AudioSource: The converted audio source.
    
    Raises:
        AudioTransformError: If the conversion fails.
    """
    from python import Python
    from numpy import np
    
    match target_format:
        case .mp3:
            if audio_source.audio_format == .mp3:
                return audio_source  // No conversion needed
            
            // Use audiomentations for MP3 compression
            try:
                transform = Python.import_module("audiomentations").Mp3Compression(
                    min_bitrate=16,
                    max_bitrate=96,
                    backend="fast-mp3-augment",
                    preserve_delay=False,
                    p=1.0,
                )
                
                // Convert audio_bytes to numpy array
                let data = audio_source.to_array()
                let data_np = data.numpy().astype(np.float32).T  // audiomentations expects (channels, frames)
                
                let sr = audio_source.sample_rate
                let augmented_sound = transform(data_np, sample_rate=sr)
                
                return AudioSource.from_array(
                    data=Tensor[Float32](augmented_sound),
                    audio_format=.mp3,
                    sample_rate=sr,
                    name=audio_source.name,
                )
            except e:
                raise AudioTransformError(f"MP3 conversion failed: {e}")
        
        case .wav:
            // WAV conversion is not implemented in the original Python code
            raise AudioTransformError("WAV conversion is not implemented yet")
        
        case _:
            raise AudioTransformError(f"Unsupported audio format: {target_format}")
