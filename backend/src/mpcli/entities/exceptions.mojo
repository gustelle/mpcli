// Custom exceptions for the mpcli project
// Equivalent to exceptions.py and AudioSourceError from source.py

from error import Error

struct AudioSourceError(Error):
    """Raised when an error occurs during AudioSource operations."""
    pass

struct AudioFileNotFoundError(Error):
    """Raised when an audio file is not found at the specified path."""
    pass

struct InvalidAudioFileError(Error):
    """Raised when an audio file is found but cannot be loaded due to an invalid format or other issues."""
    pass

struct AudioTransformError(Error):
    """Raised when an error occurs during audio transformation."""
    pass

struct TextToSpeechError(Error):
    """Raised when an error occurs during text-to-speech generation."""
    pass

struct CLIConfigError(Error):
    """Raised when there is a configuration error in the CLI."""
    pass
