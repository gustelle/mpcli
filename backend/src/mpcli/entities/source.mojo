// AudioSource entity and related utilities
// Equivalent to source.py

from tensor import Tensor, TensorSpec
from error import Error
from option import Optional
from string import String
from os.path import Path

from .exceptions import AudioSourceError

// Supported audio formats
enum AudioFormat:
    case wav
    case mp3

// Helper function to convert String to AudioFormat
fn string_to_audio_format(format_str: String) raises -> AudioFormat:
    if format_str == "wav":
        return .wav
    elif format_str == "mp3":
        return .mp3
    else:
        raise AudioSourceError(f"Unsupported audio format: {format_str}")

// Helper function to convert AudioFormat to String
fn audio_format_to_string(format: AudioFormat) -> String:
    match format:
        case .wav:
            return "wav"
        case .mp3:
            return "mp3"

fn ensure_audio_shape(inout data: Tensor[Float32]) raises -> Tensor[Float32]:
    """
    Ensure that the audio data has the expected shape (num_samples, num_channels).
    
    Args:
        data: Audio data as a 2D tensor with shape (num_samples, num_channels) or (num_channels, num_samples).
    
    Returns:
        Tensor[Float32]: Audio data with shape (num_samples, num_channels).
    
    Raises:
        AudioSourceError: If the audio data does not have the expected shape.
    """
    if data.rank() != 2:
        raise AudioSourceError(
            f"Expected audio samples to be a 2D tensor with shape (num_samples, num_channels), but got rank {data.rank()}"
        )
    
    // Transpose if needed to ensure shape is (num_samples, num_channels)
    if data.shape[0] < data.shape[1]:
        data = data.transpose()
    
    return data

struct AudioSource:
    """
    Represents an audio source with its metadata.
    Equivalent to the AudioSource class in source.py.
    """
    var audio_format: AudioFormat
    var audio_bytes: Tensor[UInt8]
    var name: String
    var sample_rate: Int
    
    fn __init__(
        inout self,
        audio_format: AudioFormat,
        audio_bytes: Tensor[UInt8],
        name: String = "unknown",
        sample_rate: Int = 44100,
    ):
        """
        Initialize an AudioSource instance.
        
        Args:
            audio_format: Format of the audio (wav or mp3).
            audio_bytes: Raw audio data as bytes.
            name: Name of the audio source (default: "unknown").
            sample_rate: Sample rate in Hz (default: 44100).
        """
        self.audio_format = audio_format
        self.audio_bytes = audio_bytes
        self.name = name
        self.sample_rate = sample_rate
    
    fn __init__(
        inout self,
        audio_format: String,
        audio_bytes: Tensor[UInt8],
        name: String = "unknown",
        sample_rate: Int = 44100,
    ) raises:
        """
        Initialize an AudioSource instance from a format string.
        
        Args:
            audio_format: Format of the audio as a string ("wav" or "mp3").
            audio_bytes: Raw audio data as bytes.
            name: Name of the audio source (default: "unknown").
            sample_rate: Sample rate in Hz (default: 44100).
        
        Raises:
            AudioSourceError: If the audio format is not supported.
        """
        self.audio_format = string_to_audio_format(audio_format)
        self.audio_bytes = audio_bytes
        self.name = name
        self.sample_rate = sample_rate
    
    fn from_array(
        data: Tensor[Float32],
        audio_format: AudioFormat,
        sample_rate: Int,
        name: Optional[String] = None,
    ) raises -> AudioSource:
        """
        Create an AudioSource instance from an audio tensor.
        
        Args:
            data: Audio data as a 2D tensor with shape (num_samples, num_channels) or (num_channels, num_samples).
            audio_format: Format of the audio (wav or mp3).
            sample_rate: Sample rate of the audio data in Hz.
            name: Optional name for the audio source.
        
        Returns:
            AudioSource: An instance with the provided audio data and metadata.
        
        Raises:
            AudioSourceError: If the audio data cannot be converted.
        """
        from python import Python
        from io import BytesIO
        
        // Ensure the data has the correct shape
        let shaped_data = ensure_audio_shape(data)
        
        // Use soundfile to write the data to bytes
        try:
            sf = Python.import_module("soundfile")
            format_str = audio_format_to_string(audio_format)
            
            // Create a BytesIO object to write the audio data
            let bytes_io = BytesIO()
            sf.write(
                bytes_io,
                shaped_data.numpy(),  // Convert Tensor to NumPy array
                sample_rate,
                format=format_str.upper(),
            )
            
            // Get the bytes from the BytesIO object
            let audio_bytes = bytes_io.getvalue()
            
            return AudioSource(
                audio_format=audio_format,
                audio_bytes=Tensor[UInt8](audio_bytes),
                sample_rate=sample_rate,
                name=name or "unknown",
            )
        except e:
            raise AudioSourceError(
                f"Failed to create AudioSource from array: {e}"
            )
    
    fn to_array(self) raises -> Tensor[Float32]:
        """
        Convert the audio bytes to a 2D tensor (frames, channels).
        
        Returns:
            Tensor[Float32]: Audio data as a 2D tensor with shape (frames, channels).
        
        Raises:
            AudioSourceError: If the audio bytes cannot be converted to an array.
        """
        from python import Python
        from io import BytesIO
        
        try:
            sf = Python.import_module("soundfile")
            format_str = audio_format_to_string(self.audio_format)
            
            // Create a BytesIO object from the audio bytes
            let bytes_io = BytesIO(self.audio_bytes.numpy())
            
            // Read the audio data as a NumPy array
            let data = sf.read(
                bytes_io,
                dtype="float32",
                always_2d=True,
            )[0]  // [0] to get the data (ignore sample_rate)
            
            // Convert to Tensor and ensure correct shape
            let tensor_data = Tensor[Float32](data)
            return ensure_audio_shape(tensor_data)
        except e:
            raise AudioSourceError(
                f"Failed to convert audio bytes to array: {e}"
            )
    
    fn get_format_string(self) -> String:
        """Return the audio format as a string."""
        return audio_format_to_string(self.audio_format)
