from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from src.mpcli.repository.audio_file import iter_sources


def test_iter_sources_valid_file():
    # Create a temporary audio file
    with NamedTemporaryFile(suffix=".wav", delete=True) as audio_file:
        # Test iter_sources with a valid file path
        sources = list(iter_sources(audio_file.name))
        assert len(sources) == 1
        assert str(sources[0]) == audio_file.name


def test_iter_sources_directory_not_existing():
    # Create a temporary directory with audio files
    source = "non_existent_directory"
    with pytest.raises(ValueError, match="does not exist"):
        list(iter_sources(source))


def test_iter_sources_directory():
    # Create a temporary directory with audio files
    with TemporaryDirectory() as tmp_path:
        audio_file1 = Path(tmp_path) / "audio1.wav"
        audio_file2 = Path(tmp_path) / "audio2.mp3"
        audio_file1.touch()
        audio_file2.touch()

        # Test iter_sources with a valid directory path
        sources = list(iter_sources(tmp_path, "*"))
        assert len(sources) == 2
        assert str(sources[0]) in [str(audio_file1), str(audio_file2)]
        assert str(sources[1]) in [str(audio_file1), str(audio_file2)]


def test_iter_sources_directory_with_hidden_and_unsupported_files():
    # Create a temporary directory with audio files
    with TemporaryDirectory() as tmp_path:
        audio_file1 = Path(tmp_path) / "audio1.wav"
        audio_file2 = Path(tmp_path) / "audio2.mp3"
        hidden_file = Path(tmp_path) / ".hidden.wav"
        unsupported_file = Path(tmp_path) / "unsupported.txt"
        audio_file1.touch()
        audio_file2.touch()
        hidden_file.touch()
        unsupported_file.touch()

        # Test iter_sources with a valid directory path
        sources = list(iter_sources(tmp_path, "*"))
        assert len(sources) == 2
        assert str(sources[0]) in [str(audio_file1), str(audio_file2)]
        assert str(sources[1]) in [str(audio_file1), str(audio_file2)]


def test_iter_sources_directory_with_format_filter():
    # Create a temporary directory with audio files
    with TemporaryDirectory() as tmp_path:
        audio_file1 = Path(tmp_path) / "audio1.wav"
        audio_file2 = Path(tmp_path) / "audio2.mp3"
        audio_file1.touch()
        audio_file2.touch()

        # Test iter_sources with a valid directory path and format filter
        sources = list(iter_sources(tmp_path, "wav"))
        assert len(sources) == 1
        assert str(sources[0]) == str(audio_file1)
