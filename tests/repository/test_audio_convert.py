import io

import soundfile as sf

from src.mpcli.entities.source import FileAudioSource
from src.mpcli.repository.audio_convert import convert


def test_convert_wav_to_mp3(wav_source_path):

    source = convert(
        audio_source=FileAudioSource(
            source=wav_source_path,
        ),
        target_format="mp3",
    )

    assert source.audio_format == "mp3"
    assert source.audio_bytes is not None
    assert source.sample_rate is not None

    # try to load the audio bytes to ensure it's a valid mp3 file
    io_obj = io.BytesIO(source.audio_bytes)
    data, sr = sf.read(io_obj)
    assert data is not None
    assert sr == source.sample_rate


def test_convert_mp3_to_wav(mp3_source_path):

    source = convert(
        audio_source=FileAudioSource(
            source=mp3_source_path,
        ),
        target_format="wav",
    )

    assert source.audio_format == "wav"
    assert source.audio_bytes is not None
    assert source.sample_rate is not None

    # try to load the audio bytes to ensure it's a valid wav file
    io_obj = io.BytesIO(source.audio_bytes)
    data, sr = sf.read(io_obj)
    assert data is not None
    assert sr == source.sample_rate
