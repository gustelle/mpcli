from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import numpy as np
import pytest

from src.mpcli.entities.source import FileAudioSource
from src.mpcli.repository.audio_file import (
    iter_sources,
    load_audio_file,
    save_audio_file,
)
from src.mpcli.repository.exceptions import InvalidAudioFileError


def test_iter_sources_valid_file():
    # Create a temporary audio file
    with NamedTemporaryFile(suffix=".wav", delete=True) as audio_file:
        # Test iter_sources with a valid file path
        sources = list(iter_sources(audio_file.name))
        assert len(sources) == 1
        assert sources[0].source == Path(audio_file.name)


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
        assert sources[0].source in [audio_file1, audio_file2]
        assert sources[1].source in [audio_file1, audio_file2]


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
        assert sources[0].source in [audio_file1, audio_file2]
        assert sources[1].source in [audio_file1, audio_file2]


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
        assert sources[0].source == audio_file1


def test_load_audio_file_invalid_file():
    with pytest.raises(InvalidAudioFileError, match="Error loading audio file"):
        f = Path(__file__).parent.parent / "assets/invalid_audio.txt"
        load_audio_file(FileAudioSource(source=f))


def test_load_audio_file_valid_file():
    f = Path(__file__).parent.parent / "assets/valid_audio.wav"
    samples, sample_rate = load_audio_file(FileAudioSource(source=f))
    assert isinstance(samples, np.ndarray) and samples.size > 0
    assert isinstance(sample_rate, int) and sample_rate == 44100


def test_save_audio_file_invalid_format():
    with pytest.raises(InvalidAudioFileError, match="Error saving audio file"):
        # load valide bytes data to ensure that the error is due to the unsupported format and not invalid audio data
        f = Path(__file__).parent.parent / "assets/valid_audio.wav"
        data, sample_rate = load_audio_file(FileAudioSource(source=f))
        save_audio_file(
            output_dir=Path("output"),
            filename="test",
            data=data,
            sample_rate=sample_rate,
            format="unsupported",
        )


def test_save_audio_file_wav():
    with TemporaryDirectory() as tmp_path:
        output_dir = Path(tmp_path)

        # given a valid bytes data for a wav file
        f = Path(__file__).parent.parent / "assets/valid_audio.wav"
        data, sample_rate = load_audio_file(FileAudioSource(source=f))

        result = save_audio_file(
            output_dir=output_dir,
            filename="test",
            data=data,
            sample_rate=sample_rate,
            format="wav",
        )

        assert result.sample_rate == sample_rate
        assert Path(result.source).exists()


def test_save_audio_file_valid_format_mp3():
    with TemporaryDirectory() as tmp_path:
        output_dir = Path(tmp_path)

        # load a valid wav file to get valid samples and sample rate for mp3 export
        f = Path(__file__).parent.parent / "assets/valid_audio.wav"
        samples, sample_rate = load_audio_file(FileAudioSource(source=f))

        result = save_audio_file(
            output_dir=output_dir,
            filename="test",
            data=samples,
            sample_rate=sample_rate,
            format="mp3",
        )
        assert Path(result.source).exists()
        assert Path(result.source).suffix == ".mp3"


def test_save_audio_file_output_dir_not_existing():
    with TemporaryDirectory() as tmp_path:
        output_dir = Path(tmp_path) / "non_existent_dir"
        result = save_audio_file(
            output_dir=output_dir,
            filename="test",
            data=np.array([[0, 0], [0, 0]], dtype=np.int16),
            sample_rate=44100,
            format="wav",
        )
        assert Path(result.source).exists()
        assert Path(result.source).suffix == ".wav"


def test_save_audio_file_overwrite_existing_wav():
    with TemporaryDirectory() as tmp_path:
        output_dir = Path(tmp_path)
        wav_output_path = output_dir / "test.wav"
        wav_output_path.touch()
        mod_time_before = wav_output_path.stat().st_mtime

        result = save_audio_file(
            output_dir=output_dir,
            filename="test",
            data=np.array([[0, 0], [0, 0]], dtype=np.int16),
            sample_rate=44100,
            format="wav",
        )
        assert Path(result.source).exists()
        assert Path(result.source).suffix == ".wav"
        mod_time_after = wav_output_path.stat().st_mtime
        assert mod_time_after > mod_time_before


def test_save_audio_file_overwrite_existing_mp3():
    with TemporaryDirectory() as tmp_path:
        existing_mp3 = Path(__file__).parent.parent / "assets/valid_audio.mp3"

        # read the existing mp3 to get valid samples and sample rate for mp3 export
        samples, sample_rate = load_audio_file(FileAudioSource(source=existing_mp3))

        # copy the existing mp3 to the temporary directory to create a file that we can overwrite
        mp3_output_path = Path(tmp_path) / "test.mp3"
        mp3_output_path.write_bytes(existing_mp3.read_bytes())
        mod_time_before = mp3_output_path.stat().st_mtime

        result = save_audio_file(
            output_dir=Path(tmp_path),
            filename="test",
            data=samples,
            sample_rate=sample_rate,
            format="mp3",
        )
        assert Path(result.source).exists()
        assert Path(result.source).suffix == ".mp3"
        mod_time_after = mp3_output_path.stat().st_mtime
        assert mod_time_after > mod_time_before
