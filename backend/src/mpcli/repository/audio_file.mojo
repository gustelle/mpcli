// Audio file operations
// Equivalent to audio_file.py

from tensor import Tensor
from os.path import Path, exists, isfile, isdir, glob, join
from string import String
from option import Optional
from algorithm import regex

from ..entities.source import AudioSource, AudioFormat, string_to_audio_format
from ..entities.exceptions import AudioFileNotFoundError, InvalidAudioFileError

fn iter_sources(
    source_path: String,
    format: String = "*",
) raises -> Iterator[AudioSource]:
    """
    Iterate over audio sources in the given path.
    
    Args:
        source_path: Path to a file or directory containing audio files.
        format: Audio format filter ("*" for all, or "wav", "mp3", etc.).
    
    Yields:
        AudioSource: Audio sources found in the path.
    
    Raises:
        AudioFileNotFoundError: If the source path does not exist.
    """
    if not exists(source_path):
        raise AudioFileNotFoundError(f"'{source_path}' does not exist")
    
    if isfile(source_path):
        // Handle single file
        let ext = Path(source_path).extension().lower()
        let name = Path(source_path).stem()
        
        let supported_formats = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]
        if ext not in supported_formats:
            raise InvalidAudioFileError(f"Unsupported audio format: '{ext}'")
        
        let audio_bytes = Tensor[UInt8](Path(source_path).read_bytes())
        let audio_format = string_to_audio_format(ext[1:])  // Remove the dot
        
        yield AudioSource(
            audio_format=audio_format,
            audio_bytes=audio_bytes,
            name=name,
        )
    else:
        // Handle directory
        let format_pattern: String
        if format == "*":
            format_pattern = r".*\.(wav|mp3|flac|ogg|m4a)$"
        else:
            format_pattern = regex.quote("." + format) + "$"
        
        let pattern = join(source_path, "*")
        for file_path in glob(pattern):
            if isdir(file_path) or Path(file_path).stem().startswith("."):
                continue  // Skip directories and hidden files
            
            let ext = Path(file_path).extension().lower()
            if not regex.match(format_pattern, Path(file_path).name(), regex.IGNORECASE):
                continue  // Skip unsupported formats
            
            let name = Path(file_path).stem()
            let audio_bytes = Tensor[UInt8](Path(file_path).read_bytes())
            let audio_format = string_to_audio_format(ext[1:])  // Remove the dot
            
            yield AudioSource(
                audio_format=audio_format,
                audio_bytes=audio_bytes,
                name=name,
            )

fn save_audio_file(
    output_dir: String,
    filename: String,
    data: Tensor[Float32],
    sample_rate: Int,
    format: AudioFormat = .wav,
) raises -> AudioSource:
    """
    Save audio data to a file.
    
    Args:
        output_dir: Directory where the file will be saved.
        filename: Name of the output file (without extension).
        data: Audio data as a 2D tensor (frames, channels).
        sample_rate: Sample rate in Hz.
        format: Audio format (wav or mp3).
    
    Returns:
        AudioSource: The saved audio as an AudioSource instance.
    
    Raises:
        InvalidAudioFileError: If the audio file cannot be saved.
    """
    from python import Python
    from io import BytesIO
    from ..entities.source import ensure_audio_shape
    
    // Create output directory if it doesn't exist
    if not exists(output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    // Ensure data has the correct shape
    let shaped_data = ensure_audio_shape(data)
    
    try:
        sf = Python.import_module("soundfile")
        format_str = "wav" if format == .wav else "mp3"
        
        // Create the full file path
        let ext = format_str
        let file_path = join(output_dir, f"{filename}.{ext}")
        
        // Write the audio data to the file
        sf.write(
            file_path,
            shaped_data.numpy(),
            sample_rate,
            format=format_str.upper(),
        )
        
        // Read the file back as bytes
        let audio_bytes = Tensor[UInt8](Path(file_path).read_bytes())
        
        return AudioSource(
            audio_format=format,
            audio_bytes=audio_bytes,
            name=filename,
            sample_rate=sample_rate,
        )
    except e:
        raise InvalidAudioFileError(f"Error saving audio file '{filename}': {e}")

fn load_audio_file(file_path: String) raises -> tuple[Tensor[Float32], Int]:
    """
    Load an audio file and return the samples and sample rate.
    
    Args:
        file_path: Path to the audio file.
    
    Returns:
        tuple[Tensor[Float32], Int]: Audio samples (2D tensor) and sample rate.
    
    Raises:
        AudioFileNotFoundError: If the file does not exist.
        InvalidAudioFileError: If the file cannot be loaded.
    """
    from python import Python
    from ..entities.source import ensure_audio_shape
    
    if not exists(file_path):
        raise AudioFileNotFoundError(f"Audio file '{file_path}' not found")
    
    try:
        sf = Python.import_module("soundfile")
        let data, sample_rate = sf.read(file_path, dtype="float32", always_2d=True)
        
        let tensor_data = Tensor[Float32](data)
        let shaped_data = ensure_audio_shape(tensor_data)
        
        return (shaped_data, Int(sample_rate))
    except e:
        raise InvalidAudioFileError(f"Error loading audio file '{file_path}': {e}")
