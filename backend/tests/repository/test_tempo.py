from pathlib import Path

from src.mpcli.entities.result import TempoResult
from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.tempo import estimate_tempo


def test_estimate_mp3_tempo(mp3_source_path: Path):
    # given a valid audio source

    source = AudioSource(
        audio_bytes=mp3_source_path.read_bytes(),
        audio_format="mp3",
        name=mp3_source_path.name,
    )

    # when estimating tempo
    result = estimate_tempo(source)

    print(f"Estimated tempo for {mp3_source_path.name}: {result.tempo} BPM")
    assert isinstance(result, TempoResult)
    assert result.tempo > 0


def test_estimate_wav_tempo(wav_source_path: Path):
    # given a valid audio source

    source = AudioSource(
        audio_bytes=wav_source_path.read_bytes(),
        audio_format="wav",
        name=wav_source_path.name,
    )

    # when estimating tempo
    result = estimate_tempo(source)

    print(f"Estimated tempo for {wav_source_path.name}: {result.tempo} BPM")
    assert isinstance(result, TempoResult)
    assert result.tempo > 0
