class AudioFileNotFoundError(ValueError):
    """Raised when an audio file is not found at the specified path."""

    pass


class InvalidAudioFileError(ValueError):
    """Raised when an audio file is found but cannot be loaded due to an invalid format or other issues."""

    pass
