// Loudness normalization use case
// Equivalent to normalization.py

from io import BytesIO
from ..entities.source import AudioSource
from ..entities.result import NormalizeResult
from ..repository.audio_transform import normalize_loudness
from tensor import Tensor

fn execute_normalization(
    source: AudioSource,
    lufs: Float64 = -14.0,
) -> Optional[NormalizeResult]:
    """
    Execute loudness normalization on an audio source.
    
    Args:
        source: The audio source to normalize.
        lufs: The target LUFS level (default: -14.0).
    
    Returns:
        Optional[NormalizeResult]: The result of the normalization, or None if it fails.
    """
    from python import Python
    from ..entities.exceptions import AudioTransformError
    
    try:
        // Convert audio_bytes to a tensor
        let data, sample_rate = Python.import_module("soundfile").read(
            BytesIO(source.audio_bytes.numpy()),
            dtype="float32",
            always_2d=True,
        )
        let samples_tensor = Tensor[Float32](data)
        
        // Normalize the loudness
        let normalized_samples = normalize_loudness(samples_tensor, sample_rate, lufs)
        
        // Convert the normalized samples back to bytes
        let bytes_io = BytesIO()
        Python.import_module("soundfile").write(
            bytes_io,
            normalized_samples.numpy(),
            sample_rate,
            format=source.get_format_string().upper(),
        )
        let normalized_audio_bytes = Tensor[UInt8](bytes_io.getvalue())
        
        // Create the normalized AudioSource
        let normalized_source = AudioSource(
            audio_format=source.audio_format,
            audio_bytes=normalized_audio_bytes,
            sample_rate=source.sample_rate,
            name=f"{source.name}_normalized",
        )
        
        return NormalizeResult(
            audio_source=source,
            converted_audio=normalized_source,
            lufs=lufs,
        )
    except e:
        print(f"Error during normalization: {e}")
        return None
