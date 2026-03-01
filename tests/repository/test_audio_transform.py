import librosa
import numpy as np
import pyloudnorm as pyln

from src.mpcli.entities.source import FileAudioSource
from src.mpcli.repository.audio_file import load_audio_file
from src.mpcli.repository.audio_transform import (
    get_duration,
    normalize_loudness,
    time_stretch,
)


def test_normalize_loudness(wav_source_path):

    data, sample_rate = load_audio_file(FileAudioSource(source=wav_source_path))

    normalized_audio_bytes = normalize_loudness(
        samples=data,
        sample_rate=sample_rate,
        lufs=-14.0,
    )

    # todo, compare the LUFS level of the output audio file with the expected value,
    assert normalized_audio_bytes is not None
    meter = pyln.Meter(sample_rate)  # create BS.1770 meter
    loudness = meter.integrated_loudness(normalized_audio_bytes)
    assert abs(loudness - (-14.0)) < 0.1


def test_time_stretch(mp3_source_path):

    # load mp3 file
    data, sample_rate = load_audio_file(FileAudioSource(source=mp3_source_path))

    initial_duration = get_duration(data, sample_rate)

    stretched_audio = time_stretch(
        samples=data,
        sample_rate=sample_rate,
        min_rate=1.1,
        max_rate=1.2,  # speed up by 10-20%
        leave_length_unchanged=False,
    )

    new_duration = get_duration(stretched_audio, sample_rate)

    print(f"New duration after time stretching: {new_duration:.2f} seconds")

    # compare the duration of the output audio file with the expected value,
    assert new_duration < initial_duration
