import io
import tempfile
from pathlib import Path

import librosa
import numpy as np
import pytest
import soundfile as sf

from src.mpcli.entities.source import AudioSource, AudioSourceError


def test_audio_source_from_mp3_2d(mp3_source_path):

    # given
    data, sample_rate = sf.read(mp3_source_path, always_2d=True)  #

    # when
    audio_source = AudioSource.from_array(
        data=data, audio_format="mp3", sample_rate=sample_rate
    )

    # then
    assert audio_source is not None
    assert audio_source.audio_format == "mp3"
    assert audio_source.sample_rate == sample_rate
    assert isinstance(audio_source.audio_bytes, bytes)

    # verify that the duration can be obtained without error
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
        temp_file.write(audio_source.audio_bytes)
        temp_file.flush()
        d = librosa.get_duration(path=temp_file.name)
        assert d > 0.0


def test_audio_source_from_mp3_transposed(mp3_source_path):
    # given
    data, sample_rate = sf.read(mp3_source_path, always_2d=True)  #
    data = data.T  # transpose the data to have shape (num_channels, num_samples)

    # when
    audio_source = AudioSource.from_array(
        data=data, audio_format="mp3", sample_rate=sample_rate
    )

    # then
    assert audio_source is not None
    assert audio_source.audio_format == "mp3"
    assert audio_source.sample_rate == sample_rate
    assert isinstance(audio_source.audio_bytes, bytes)

    # verify that the duration can be obtained without error
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
        temp_file.write(audio_source.audio_bytes)
        temp_file.flush()
        d = librosa.get_duration(path=temp_file.name)
        assert d > 0.0


def test_audio_source_from_wav_2d(wav_source_path):

    # given
    data, sample_rate = sf.read(wav_source_path, always_2d=True)  #

    # when
    audio_source = AudioSource.from_array(
        data=data, audio_format="wav", sample_rate=sample_rate
    )

    # then
    assert audio_source is not None
    assert audio_source.audio_format == "wav"
    assert audio_source.sample_rate == sample_rate
    assert isinstance(audio_source.audio_bytes, bytes)

    # verify that the duration can be obtained without error
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        temp_file.write(audio_source.audio_bytes)
        temp_file.flush()
        d = librosa.get_duration(path=temp_file.name)
        assert d > 0.0


def test_audio_source_from_wav_transposed(wav_source_path):

    # given
    data, sample_rate = sf.read(wav_source_path, always_2d=True)  #
    data = data.T  # transpose the data to have shape (num_channels, num_samples)

    # when
    audio_source = AudioSource.from_array(
        data=data, audio_format="wav", sample_rate=sample_rate
    )

    # then
    assert audio_source is not None
    assert audio_source.audio_format == "wav"
    assert audio_source.sample_rate == sample_rate
    assert isinstance(audio_source.audio_bytes, bytes)

    # verify that the duration can be obtained without error
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        temp_file.write(audio_source.audio_bytes)
        temp_file.flush()
        d = librosa.get_duration(path=temp_file.name)
        assert d > 0.0


def test_audio_source_from_mp3_1d(mono_mp3_path):

    # given
    data, sample_rate = sf.read(mono_mp3_path, always_2d=False)  #

    # when
    audio_source = AudioSource.from_array(
        data=data, audio_format="mp3", sample_rate=sample_rate
    )

    # then
    assert audio_source is not None
    assert audio_source.audio_format == "mp3"
    assert audio_source.sample_rate == sample_rate
    assert isinstance(audio_source.audio_bytes, bytes)

    # verify that the duration can be obtained without error
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
        temp_file.write(audio_source.audio_bytes)
        temp_file.flush()
        d = librosa.get_duration(path=temp_file.name)
        assert d > 0.0


def test_audio_source_from_wav_1d(mono_wave_path):

    # given
    pass


def test_audio_source_from_invalid_format(invalid_source_path):

    # given
    format = "txt"
    data = Path(invalid_source_path).read_bytes()
    sample_rate = 44100

    # when / then
    with pytest.raises(AudioSourceError, match="Failed to create AudioSource"):
        AudioSource.from_array(data=data, audio_format=format, sample_rate=sample_rate)


def test_audio_source_inconsistent_format(mp3_source_path):
    # currently not supported,
    # but we should test that an error is raised if the audio format is inconsistent with the actual audio data
    pass


def test_audio_source_mp3_to_array(mp3_source_path):

    # given
    data, sample_rate = sf.read(mp3_source_path, always_2d=True)  #
    bytes_io = io.BytesIO()
    sf.write(bytes_io, data, sample_rate, format="MP3")

    audio_source = AudioSource(
        audio_bytes=bytes_io.getvalue(),
        audio_format="mp3",
        sample_rate=sample_rate,
    )

    # when
    result_array = audio_source.to_array()

    # then
    assert isinstance(result_array, np.ndarray)
    assert result_array.shape == data.shape


def test_audio_source_wav_to_array(wav_source_path):

    # given
    data, sample_rate = sf.read(wav_source_path, always_2d=True)  #
    bytes_io = io.BytesIO()
    sf.write(bytes_io, data, sample_rate, format="WAV")

    audio_source = AudioSource.from_array(
        data=data, audio_format="wav", sample_rate=sample_rate
    )

    # when
    result_array = audio_source.to_array()

    # then
    assert isinstance(result_array, np.ndarray)
    assert result_array.shape == data.shape
